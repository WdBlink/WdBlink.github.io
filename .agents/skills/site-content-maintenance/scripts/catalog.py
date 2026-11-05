"""Public GitHub facts and the website's two maintained content collections."""
from __future__ import annotations

import base64
import copy
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

DESTINATION = "WdBlink/WdBlink.github.io"
SOURCE = "WdBlink/LLM-Skills"
FILES = ("_data/studio_skills.json", "_data/studio_apps.json")
CATEGORIES = {"Knowledge": "知识与研究", "Multimodal": "图像与多模态", "Presentation": "演示与汇报"}
APP_IDS = ("agent-notebook", "agent-note-cli")
ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
VERSION = re.compile(r"v?(\d+)\.(\d+)\.(\d+)(?:[-+][a-zA-Z0-9.-]+)?\Z")
PREFIX = "https://github.com/" + SOURCE + "/tree/"


class MaintenanceError(RuntimeError):
    pass


def text(value, field, limit=400):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise MaintenanceError(f"Invalid {field}")
    if any(ord(char) < 32 for char in value):
        raise MaintenanceError(f"Control character in {field}")
    return value


def version(value):
    match = VERSION.fullmatch(text(value, "version", 64))
    if not match:
        raise MaintenanceError(f"Unsupported version: {value!r}")
    return tuple(int(part) for part in match.groups())


def parse_registry(raw):
    # This source uses a flat key/value format, including unquoted ': ' in prose.
    rows, current, seen, schema = [], None, set(), False
    for number, line in enumerate(raw.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line in ("version: 1", "skills:"):
            schema |= line == "version: 1"
            continue
        match = re.fullmatch(r"  - name: (.+)", line)
        if match:
            current = {"name": match[1].strip()}
            rows.append(current)
            continue
        match = re.fullmatch(r"    ([a-z_]+): (.+)", line)
        if not match or current is None or match[1] in current:
            raise MaintenanceError(f"Unsupported source registry line {number}")
        value = match[2].strip()
        if value.startswith(("|", ">", "[", "{")):
            raise MaintenanceError(f"Unsupported source value on line {number}")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        current[match[1]] = value
    if not schema or not rows or len(rows) > 1000:
        raise MaintenanceError("Missing or unsupported source registry")
    for row in rows:
        name = text(row.get("name"), "skill name", 100)
        if not ID.fullmatch(name) or name in seen:
            raise MaintenanceError(f"Duplicate or invalid skill ID: {name}")
        seen.add(name)
    return rows


def validate(skills, apps):
    if not isinstance(skills, list) or not skills or len(skills) > 1000:
        raise MaintenanceError("Empty or invalid Skills collection")
    seen = set()
    for skill in skills:
        if not isinstance(skill, dict):
            raise MaintenanceError("Invalid Skill record")
        name = text(skill.get("id"), "skill ID", 100)
        if not ID.fullmatch(name) or name in seen:
            raise MaintenanceError(f"Duplicate or invalid skill ID: {name}")
        seen.add(name)
        for field in ("title", "name", "description"):
            text(skill.get(field), "skill " + field)
        version(skill.get("version"))
        if skill.get("category") not in CATEGORIES.values() or skill.get("license") not in ("MIT", "Proprietary"):
            raise MaintenanceError(f"Unknown category or license: {name}")
        source = skill.get("source")
        if source is not None and (not isinstance(source, str) or not source.startswith("https://github.com/WdBlink/") or re.search(r"[\s<>\"']", source)):
            raise MaintenanceError(f"Invalid source URL: {name}")
    if not isinstance(apps, list) or not all(isinstance(app, dict) for app in apps) or tuple(app.get("id") for app in apps) != APP_IDS:
        raise MaintenanceError("Unexpected Apps collection")
    for app in apps:
        repo = "https://github.com/WdBlink/" + app["id"]
        if app.get("repository") != repo or app.get("url") not in (repo + "/releases/latest", repo + "#readme"):
            raise MaintenanceError("Unexpected App repository or action URL")
        for field in ("title", "label", "action", "headline", "description"):
            text(app.get(field), "app " + field)
        version(app.get("version"))
        if app.get("license") != "MIT":
            raise MaintenanceError("App license requires review")
    if apps[1].get("installCommand") != "brew install wdblink/tap/agent-note-cli":
        raise MaintenanceError("App install command requires review")


def build_skills(rows, current, paths, branch="main"):
    if not re.fullmatch(r"[a-zA-Z0-9._-]+", branch):
        raise MaintenanceError("Unsupported source branch name")
    source = {row["name"]: row for row in rows}
    current_ids = {item["id"] for item in current}
    if len(source) - len(current_ids & source.keys()) > 20:
        raise MaintenanceError("More than 20 additions require review")
    missing = [item["id"] for item in current if str(item.get("source", "")).startswith(PREFIX) and item["id"] not in source]
    if missing:
        raise MaintenanceError("Source removed existing Skills: " + ", ".join(missing))
    result = []
    ordered = [item["id"] for item in current] + [row["name"] for row in rows if row["name"] not in current_ids]
    old = {item["id"]: item for item in current}
    for name in ordered:
        if name not in source:
            result.append(copy.deepcopy(old[name]))
            continue
        row = source[name]
        path = text(row.get("path"), "source path", 160)
        if not re.fullmatch(r"skills/[a-z0-9]+(?:-[a-z0-9]+)*", path) or path + "/SKILL.md" not in paths:
            raise MaintenanceError(f"Missing public Skill file: {name}")
        if row.get("category") not in CATEGORIES or row.get("license") not in ("MIT", "Proprietary"):
            raise MaintenanceError(f"Unknown source category or license: {name}")
        new_version = version(row.get("version"))
        if name in old and new_version < version(old[name]["version"]):
            raise MaintenanceError(f"Version downgrade requires review: {name}")
        result.append({"id": name, "title": text(row.get("name_zh"), "Chinese title"),
                       "name": text(row.get("display_name"), "display name"),
                       "category": CATEGORIES[row["category"]],
                       "description": text(row.get("tagline_zh"), "Chinese summary"),
                       "license": row["license"], "version": row["version"],
                       "source": PREFIX + branch + "/" + path})
    return result


class GitHub:
    def __init__(self):
        self.binary = os.environ.get("SITE_GH_BIN") or shutil.which("gh")
        if not self.binary:
            raise MaintenanceError("GitHub CLI is not installed")

    def get(self, endpoint, raw=False):
        for attempt in range(3):
            command = [self.binary, "api", "--method", "GET", endpoint]
            if raw:
                command += ["-H", "Accept: application/vnd.github.raw+json"]
            try:
                reply = subprocess.run(command, capture_output=True, text=True, timeout=45,
                                       env={**os.environ, "GH_PROMPT_DISABLED": "1"})
            except subprocess.TimeoutExpired:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                raise MaintenanceError(f"GitHub request timed out: {endpoint}") from None
            if reply.returncode == 0:
                try:
                    return reply.stdout if raw else json.loads(reply.stdout)
                except json.JSONDecodeError:
                    raise MaintenanceError(f"Invalid GitHub JSON: {endpoint}") from None
            if attempt < 2 and any(code in reply.stderr for code in ("HTTP 429", "HTTP 500", "HTTP 502", "HTTP 503", "HTTP 504")):
                time.sleep(2 ** attempt)
                continue
            raise MaintenanceError(f"GitHub GET failed: {endpoint}")


def collect(site: Path, github):
    skills, apps = [json.loads((site / path).read_text(encoding="utf-8")) for path in FILES]
    validate(skills, apps)
    metadata = github.get("repos/" + SOURCE)
    if metadata.get("private") is not False or metadata.get("archived"):
        raise MaintenanceError("Skills repository is not an active public source")
    branch = metadata["default_branch"]
    commit = github.get(f"repos/{SOURCE}/commits/{branch}")["sha"]
    if not re.fullmatch(r"[a-f0-9]{40}", commit):
        raise MaintenanceError("Invalid source commit")
    registry = github.get(f"repos/{SOURCE}/contents/skills.yaml?ref={commit}", raw=True)
    tree = github.get(f"repos/{SOURCE}/git/trees/{commit}?recursive=1")
    if tree.get("truncated") is not False:
        raise MaintenanceError("Source tree is incomplete")
    paths = {item["path"] for item in tree["tree"] if item["type"] == "blob" and item.get("mode") in ("100644", "100755")}
    proposed_skills = build_skills(parse_registry(registry), skills, paths, branch)
    proposed_apps = copy.deepcopy(apps)
    provenance = {SOURCE: commit}
    for app in proposed_apps:
        repo = "WdBlink/" + app["id"]
        info = github.get("repos/" + repo)
        if info.get("private") is not False or info.get("archived") or (info.get("license") or {}).get("spdx_id") != "MIT":
            raise MaintenanceError(f"App privacy, archive state or license requires review: {repo}")
        release = github.get(f"repos/{repo}/releases/latest")
        if release.get("draft") or release.get("prerelease") or version(release["tag_name"]) < version(app["version"]):
            raise MaintenanceError(f"Unexpected App release: {repo}")
        if app["id"] == "agent-notebook":
            if not any(asset["name"].endswith(".dmg") for asset in release.get("assets", [])):
                raise MaintenanceError("Desktop release has no macOS installer")
        else:
            readme = github.get(f"repos/{repo}/readme")
            body = base64.b64decode(readme["content"], validate=False).decode("utf-8")
            if not re.search(r"^" + re.escape(app["installCommand"]) + r"\s*$", body, re.M):
                raise MaintenanceError("Published CLI install command is no longer in the README")
        app["version"] = release["tag_name"]
        provenance[repo] = {"release": release["tag_name"], "release_url": release["html_url"]}
    validate(proposed_skills, proposed_apps)
    before = dict(zip(FILES, (skills, apps)))
    after = dict(zip(FILES, (proposed_skills, proposed_apps)))
    return {"schema": 1, "sources": provenance, "before": before, "after": after,
            "changed": [path for path in FILES if before[path] != after[path]]}
