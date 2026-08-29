#!/usr/bin/env python3
"""Regenerate every derived file: all guide PDFs, then index.html.

Use this for a full refresh. Day to day, the pre-commit hook rebuilds only
what changed. Run individual steps with build_study_pdfs.py / build_index.py.
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    for step in (["build_study_pdfs.py"], ["build_index.py"]):
        print(f"--- {step[0]} ---")
        result = subprocess.run([sys.executable, str(HERE / step[0]), *step[1:]])
        if result.returncode != 0:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
