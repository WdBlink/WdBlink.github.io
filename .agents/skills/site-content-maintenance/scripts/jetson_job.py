"""Hermes no-agent cron entry. Successful runs deliberately emit no stdout."""
import os
from pathlib import Path
import subprocess
import sys

BASE = Path("/var/lib/codex-orin_agx/site-content-maintenance")
REPO = BASE / "repo"
RUNNER = REPO / ".agents/skills/site-content-maintenance/scripts/maintain.py"


def main():
    environment = {**os.environ, "SITE_GH_BIN": "/home/orin_agx/.local/bin/gh", "GH_PROMPT_DISABLED": "1",
                   "PYTHONDONTWRITEBYTECODE": "1", "TZ": "Asia/Shanghai"}
    try:
        return subprocess.run(["/usr/bin/python3", str(RUNNER), "run", "--repo", str(REPO),
                               "--state", str(BASE / "state"), "--publish"],
                              cwd=REPO, env=environment, timeout=3000).returncode
    except (OSError, subprocess.TimeoutExpired) as error:
        print("网站维护启动失败，未确认完成。" + type(error).__name__, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
