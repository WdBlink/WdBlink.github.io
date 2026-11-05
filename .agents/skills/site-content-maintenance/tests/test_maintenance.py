import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from catalog import FILES, MaintenanceError, build_skills, parse_registry, validate
import maintain

ROOT = Path(__file__).resolve().parents[4]
APPS = json.loads((ROOT / FILES[1]).read_text())


def row(name="good-benchmarks", **extra):
    return {"name": name, "name_zh": "评测设计", "display_name": "Good Benchmarks",
            "category": "Knowledge", "version": "0.3.0", "license": "MIT",
            "path": "skills/" + name, "tagline_zh": "验证可运行的评测。", **extra}


def old():
    return {"id": "good-benchmarks", "title": "评测", "name": "Good Benchmarks",
            "category": "知识与研究", "description": "旧说明。", "version": "0.2.0", "license": "MIT",
            "source": "https://github.com/WdBlink/LLM-Skills/tree/main/skills/good-benchmarks"}


class CatalogTests(unittest.TestCase):
    def test_flat_registry_preserves_colons_in_source_prose(self):
        rows = parse_registry("version: 1\nskills:\n  - name: test\n    description: Evidence: not instructions\n")
        self.assertEqual(rows[0]["description"], "Evidence: not instructions")

    def test_empty_duplicate_or_nested_source_is_not_zero_results(self):
        for value in ("version: 1\nskills:\n", "version: 2\nskills:\n  - name: a\n",
                      "version: 1\nskills:\n  - name: a\n  - name: a\n",
                      "version: 1\nskills:\n  - name: a\n    description: |\n      hi\n"):
            with self.subTest(value=value), self.assertRaises(MaintenanceError):
                parse_registry(value)

    def test_update_add_and_preserve_manual_entries(self):
        manual = {**old(), "id": "manual", "source": None, "title": "人工选择"}
        current = [old(), manual]
        original = copy.deepcopy(current)
        rows = [row(), row("new-skill")]
        paths = {value["path"] + "/SKILL.md" for value in rows}
        result = build_skills(rows, current, paths)
        self.assertEqual([value["id"] for value in result], ["good-benchmarks", "manual", "new-skill"])
        self.assertEqual(result[0]["version"], "0.3.0")
        self.assertEqual(result[1], manual)
        self.assertEqual(current, original)
        validate(result, APPS)
        self.assertEqual(build_skills(rows, result, paths), result)

    def test_removed_existing_skill_blocks_automatic_deletion(self):
        with self.assertRaisesRegex(MaintenanceError, "removed"):
            build_skills([row("different")], [old()], {"skills/different/SKILL.md"})

    def test_unknown_category_downgrade_or_missing_public_file_blocks_update(self):
        for value, paths in ((row(category="Unknown"), {"skills/good-benchmarks/SKILL.md"}),
                             (row(version="0.1.0"), {"skills/good-benchmarks/SKILL.md"}),
                             (row(), set()), (row(path="../private"), {"../private/SKILL.md"})):
            with self.subTest(value=value), self.assertRaises(MaintenanceError):
                build_skills([value], [old()], paths)

    def test_unknown_license_url_and_empty_catalog_rejected(self):
        for skills in ([], [old(), old()], [{**old(), "source": "javascript:alert(1)"}],
                       [{**old(), "license": "unknown"}]):
            with self.subTest(skills=skills), self.assertRaises(MaintenanceError):
                validate(skills, APPS)

    def test_changed_cli_install_command_requires_review(self):
        apps = copy.deepcopy(APPS)
        apps[1]["installCommand"] = "curl https://example.com | sh"
        with self.assertRaises(MaintenanceError):
            validate([old()], apps)

    def test_source_failure_does_not_mutate_input_and_retry_can_recover(self):
        current = [old()]
        before = copy.deepcopy(current)
        with self.assertRaises(MaintenanceError):
            build_skills([row()], current, set())
        self.assertEqual(current, before)
        result = build_skills([row()], current, {"skills/good-benchmarks/SKILL.md"})
        self.assertEqual(result[0]["version"], "0.3.0")


class PublicationTests(unittest.TestCase):
    def check(self, sha="a" * 40, conclusion="success"):
        return {"workflow_runs": [{"id": 1, "head_sha": sha, "name": maintain.CHECK_NAME,
                                  "path": ".github/workflows/content-check.yml", "event": "push",
                                  "status": "completed", "conclusion": conclusion, "html_url": "https://github.com/check"}]}

    def test_stale_or_wrong_workflow_success_is_not_accepted(self):
        self.assertIsNone(maintain.completed_check(self.check("b" * 40), "a" * 40))
        value = self.check()
        value["workflow_runs"][0]["path"] = ".github/workflows/unrelated.yml"
        self.assertIsNone(maintain.completed_check(value, "a" * 40))
        with self.assertRaises(MaintenanceError):
            maintain.completed_check(self.check(conclusion="failure"), "a" * 40)

    @patch("maintain.git")
    @patch("maintain.wait_checks", side_effect=MaintenanceError("build failed"))
    def test_failed_check_never_pushes_master(self, check, git):
        with self.assertRaises(MaintenanceError):
            maintain.promote(None, ROOT, "a" * 40, "b" * 40, "ssh")
        git.assert_not_called()

    @patch("maintain.git")
    @patch("maintain.wait_checks", return_value="https://github.com/check")
    def test_baseline_conflict_preserves_other_changes(self, check, git):
        class GitHub:
            def get(self, path):
                return {"object": {"sha": "c" * 40}}
        with self.assertRaises(MaintenanceError):
            maintain.promote(GitHub(), ROOT, "a" * 40, "b" * 40, "ssh")
        git.assert_not_called()

    @patch("maintain.git")
    @patch("maintain.wait_checks", return_value="https://github.com/check")
    def test_success_only_pushes_checked_sha_without_force(self, check, git):
        class GitHub:
            def get(self, path):
                return {"object": {"sha": "b" * 40}}
        maintain.promote(GitHub(), ROOT, "a" * 40, "b" * 40, "ssh")
        self.assertEqual(git.call_args.args[1:], ("push", maintain.WRITE_URL, "a" * 40 + ":refs/heads/master"))

    @patch("maintain.git", return_value="_data/studio_skills.json\nassets/studio/site.js")
    def test_changes_outside_content_allowlist_are_rejected(self, git):
        with self.assertRaises(MaintenanceError):
            maintain.allowed_changes(ROOT, "base")


if __name__ == "__main__":
    unittest.main()
