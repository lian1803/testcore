#!/usr/bin/env python
"""
Shortcut runner for Design Scouting Team

Usage:
  python run_디자인스카우팅팀.py

This simply executes teams/디자인스카우팅팀/pipeline.py
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run the design scouting team pipeline"""
    team_pipeline = Path(__file__).parent / "teams" / "디자인스카우팅팀" / "pipeline.py"

    if not team_pipeline.exists():
        print(f"❌ Pipeline not found: {team_pipeline}")
        return 1

    try:
        result = subprocess.run(
            [sys.executable, str(team_pipeline)],
            cwd=Path(__file__).parent
        )
        return result.returncode
    except Exception as e:
        print(f"❌ Error running pipeline: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
