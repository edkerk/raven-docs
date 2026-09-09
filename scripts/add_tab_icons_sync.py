"""One-time pass: add a language marker and :sync: to every MATLAB/Python
code-example tab-item, site-wide.

Only touches tab-items whose title is *exactly* "MATLAB" or "Python" (the
code-example convention every guide page uses) -- an install-method tab like
"MATLAB (Add-Ons)" or "Python (pip)" does not match and is left alone, since
syncing a 4-way install-method choice against a 2-way language choice would
be wrong.

Idempotent: a tab-item that already carries a marker or :sync: line is left
untouched on a second run.
"""

from __future__ import annotations

import re
from pathlib import Path

MATLAB_RE = re.compile(r'^( *):::\{tab-item\} MATLAB[ \t]*$', re.M)
PYTHON_RE = re.compile(r'^( *):::\{tab-item\} Python[ \t]*$', re.M)

MATLAB_MARK = "Ⓜ️"  # circled M
PYTHON_MARK = "\U0001f40d"  # snake


def convert(text: str) -> str:
    text = MATLAB_RE.sub(
        lambda m: f"{m.group(1)}:::{{tab-item}} {MATLAB_MARK} MATLAB\n{m.group(1)}:sync: matlab",
        text,
    )
    text = PYTHON_RE.sub(
        lambda m: f"{m.group(1)}:::{{tab-item}} {PYTHON_MARK} Python\n{m.group(1)}:sync: python",
        text,
    )
    return text


if __name__ == "__main__":
    import sys

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs")
    changed = 0
    for path in sorted(root.rglob("*.md")):
        original = path.read_text(encoding="utf-8")
        converted = convert(original)
        if converted != original:
            path.write_text(converted, encoding="utf-8", newline="\n")
            changed += 1
    print(f"converted {changed} file(s) under {root}")
