"""Collect public metadata, check a candidate branch, then fast-forward the website."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import stat
import subprocess
import sys
import tempfile
import time
from urllib.request import Request, urlopen

from catalog import DESTINATION, FILES, GitHub, MaintenanceError, collect, validate

WRITE_URL = "ssh://git@ssh.github.com:443/" + DESTINATION + ".git"
CHECK_NAME = "Site content checks"
LIVE = "https://wdblink.github.io/assets/studio/content.js"


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temporary = stream.name
    os.replace(temporary, path)


def git(repo, *arguments, ssh=None, timeout=120):
    environment = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}
    for key in ("GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN"):
        environment.pop(key, None)
    if ssh:
        environment["GIT_SSH_COMMAND"] = ssh
    result = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-C", str(repo), *arguments],
                            capture_output=True, text=True, timeout=timeout, env=environment)
    if result.returncode:
        raise MaintenanceError("Git operation failed: " + arguments[0])
    return result.stdout.strip()


def transport(state):
    key = state / "deploy_key"
    hosts = state / "known_hosts"
    for path in (state, key, hosts):
        info = path.lstat()
        if path.is_symlink() or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
            raise MaintenanceError(f"Insecure state or credential permissions: {path}")
    return shlex.join(["ssh", "-F", "/dev/null", "-i", str(key), "-o", "IdentitiesOnly=yes", "-o", "BatchMode=yes",
                       "-o", "StrictHostKeyChecking=yes", "-o", "UserKnownHostsFile=" + str(hosts),
                       "-o", "HostKeyAlgorithms=ssh-ed25519", "-o", "ConnectTimeout=15"])


@contextmanager
def locked(state):
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (state / "run.lock").open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise MaintenanceError("Another website maintenance run is active") from None
        yield


def allowed_changes(repo, base):
    changed = set(git(repo, "diff", "--name-only", base, "--").splitlines())
    if not changed or not changed.issubset(FILES):
        raise MaintenanceError("Candidate includes changes outside Skills/Apps data")
    return changed


def completed_check(payload, sha):
    matches = [run for run in payload.get("workflow_runs", [])
               if run.get("head_sha") == sha and run.get("name") == CHECK_NAME
               and run.get("path") == ".github/workflows/content-check.yml" and run.get("event") == "push"]
    if not matches:
        return None
    latest = max(matches, key=lambda run: (run["id"], run.get("run_attempt", 1)))
    if latest.get("status") != "completed":
        return None
    if latest.get("conclusion") != "success":
        raise MaintenanceError("Website checks failed: " + latest["html_url"])
    return latest["html_url"]


def wait_checks(github, sha, seconds=1200):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        result = completed_check(github.get(f"repos/{DESTINATION}/actions/runs?head_sha={sha}&per_page=30"), sha)
        if result:
            return result
        time.sleep(15)
    raise MaintenanceError("Website check timed out for commit " + sha)


def promote(github, repo, sha, base, ssh):
    check = wait_checks(github, sha)
    current = github.get(f"repos/{DESTINATION}/git/ref/heads/master")["object"]["sha"]
    if current not in (base, sha):
        raise MaintenanceError("Website master changed during checks; regenerate against the new baseline")
    if current != sha:
        git(repo, "push", WRITE_URL, sha + ":refs/heads/master", ssh=ssh)
    return check


def wait_live(after, sha, seconds=600):
    deadline, reason = time.monotonic() + seconds, "content does not match the checked candidate"
    while time.monotonic() < deadline:
        try:
            request = Request(LIVE + "?maintenance=" + sha, headers={"Cache-Control": "no-cache", "User-Agent": "WdBlink-site-maintenance"})
            with urlopen(request, timeout=30) as response:
                body = response.read(2_000_001).decode("utf-8")
            if len(body) > 2_000_000:
                raise MaintenanceError("Production index is unexpectedly large")
            decoder = json.JSONDecoder()
            live = {}
            for label, path in zip(("skills", "apps"), FILES):
                match = re.search(r"\b" + label + r"\s*:\s*", body)
                if not match:
                    raise ValueError("missing content collection")
                live[path] = decoder.raw_decode(body[match.end():])[0]
            if live == after:
                return
        except (OSError, ValueError) as error:
            reason = type(error).__name__
        time.sleep(15)
    raise MaintenanceError("GitHub Pages verification timed out: " + reason)


def execute(repo, state, github):
    ssh = transport(state)
    origin = git(repo, "remote", "get-url", "origin")
    if origin not in ("https://github.com/" + DESTINATION + ".git", "https://github.com/" + DESTINATION,
                      "git@github.com:" + DESTINATION + ".git", WRITE_URL):
        raise MaintenanceError("This checkout is not the authorized website repository")
    if git(repo, "status", "--porcelain", "--untracked-files=all"):
        raise MaintenanceError("Dedicated website checkout is dirty; user changes are preserved")
    git(repo, "fetch", WRITE_URL, "master", ssh=ssh)
    base = git(repo, "rev-parse", "FETCH_HEAD")
    receipt = {"schema": 1, "started_at": datetime.now(timezone.utc).isoformat(), "base": base, "status": "collecting"}
    save(state / "latest.json", receipt)
    with tempfile.TemporaryDirectory(prefix="website-run-", dir=state) as directory:
        work = Path(directory) / "worktree"
        git(repo, "worktree", "add", "--detach", str(work), base)
        try:
            proposal = collect(work, github)
            receipt.update({"sources": proposal["sources"], "changed": proposal["changed"]})
            save(state / "proposal.json", proposal)
            if not proposal["changed"]:
                receipt["status"] = "verifying_live"
                save(state / "latest.json", receipt)
                wait_live(proposal["after"], base)
                receipt["status"] = "unchanged"
                return receipt
            for path in proposal["changed"]:
                save(work / path, proposal["after"][path])
            allowed_changes(work, base)
            git(work, "add", "--", *proposal["changed"])
            tree = git(work, "write-tree")
            branch = "codex/site-content-" + hashlib.sha256((base + tree).encode()).hexdigest()[:16]
            remote = git(work, "ls-remote", WRITE_URL, "refs/heads/" + branch, ssh=ssh)
            if remote:
                sha = remote.split()[0]
                git(work, "fetch", WRITE_URL, branch, ssh=ssh)
                if git(work, "rev-parse", sha + "^{tree}") != tree or git(work, "rev-parse", sha + "^") != base:
                    raise MaintenanceError("Existing candidate branch does not match this proposal")
            else:
                git(work, "-c", "user.name=Website Maintenance", "-c", "user.email=wdblink@users.noreply.github.com",
                    "commit", "-m", "Update public Skills and Apps metadata", "-m", json.dumps(proposal["sources"], sort_keys=True))
                sha = git(work, "rev-parse", "HEAD")
                git(work, "push", WRITE_URL, sha + ":refs/heads/" + branch, ssh=ssh)
            receipt.update({"status": "waiting_checks", "candidate": sha, "branch": branch})
            save(state / "latest.json", receipt)
            receipt["checks"] = promote(github, work, sha, base, ssh)
            receipt["status"] = "verifying_live"
            save(state / "latest.json", receipt)
            wait_live(proposal["after"], sha)
            receipt["status"] = "published"
            return receipt
        finally:
            # This path is a new worktree owned exclusively by this run.
            git(repo, "worktree", "remove", "--force", str(work))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("plan", "run", "validate"))
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--state", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    try:
        if args.mode == "validate":
            validate(*(json.loads((args.repo / path).read_text()) for path in FILES))
            print("PASS: Skills and Apps content contract")
        elif args.mode == "plan":
            if not args.out:
                parser.error("plan requires --out")
            proposal = collect(args.repo, GitHub())
            save(args.out, proposal)
            print(json.dumps({"changed": proposal["changed"], "proposal": str(args.out)}, ensure_ascii=False))
        else:
            if not args.publish or not args.state or not args.state.is_absolute() or not args.repo.is_absolute():
                parser.error("run requires absolute --repo, --state and explicit --publish")
            with locked(args.state):
                try:
                    receipt = execute(args.repo, args.state, GitHub())
                    receipt["finished_at"] = datetime.now(timezone.utc).isoformat()
                    save(args.state / "latest.json", receipt)
                    save(args.state / "last-success.json", receipt)
                except Exception as error:
                    previous = args.state / "latest.json"
                    receipt = json.loads(previous.read_text()) if previous.exists() else {"schema": 1}
                    receipt.update({"failed_phase": receipt.get("status"), "status": "failed", "failed_at": datetime.now(timezone.utc).isoformat(),
                                    "error": str(error)[:1500]})
                    save(previous, receipt)
                    raise
    except (MaintenanceError, OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        print("网站维护异常，未确认完成。" + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
