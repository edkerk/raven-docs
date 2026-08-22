"""Execute the Python examples in the guide pages and check their output.

The guide pages promise that the reader can paste a snippet and get the printed
result shown underneath it. Nothing enforces that: ``check_names.py`` only
verifies that the *names* in a page exist, so a page can name real functions,
call them with arguments that no longer work, and show output that was correct
two releases ago.

This script closes that gap for the Python half of the guide. For every page it

* collects the ```python blocks in order (including the ones nested inside
  ``=== "Python"`` content tabs),
* runs a page's blocks in one namespace, in a scratch directory seeded with a
  copy of ``docs/data/``, so the snippets can use the short relative paths the
  reader sees,
* captures what the block prints -- plus the repr of a trailing expression, the
  way a notebook or the REPL would -- and compares it with the ``title="Output"``
  block that follows,
* reports every mismatch as a unified diff and exits non-zero.

The MATLAB tabs are *not* executed here; they need a MATLAB runtime (see
``.github/workflows/examples.yml`` for the intended follow-up).

Usage::

    python scripts/run_examples.py                # check docs/guide
    python scripts/run_examples.py docs/guide/fba.md
    python scripts/run_examples.py --update       # rewrite output blocks in place
    python scripts/run_examples.py --list         # show what would run

Page-level control, written as HTML comments in the markdown:

``<!-- run-examples: skip-file -->``
    anywhere in the page -- the page is not executed at all (use for pages whose
    examples need BLAST, a KEGG download, or a commercial solver).
``<!-- run-examples: skip -->``
    immediately before a ```python block -- that one block is neither executed
    nor checked, but the ones after it still run.

An expected-output block consisting of a single ``...`` matches anything, and
``...`` inside a block matches any run of characters -- the same convention as
doctest's ELLIPSIS. Use it for timings, paths and long tables.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import difflib
import io
import os
import re
import shutil
import sys
import tempfile
import traceback
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_TARGET = ROOT / "docs" / "guide"
DATA_DIR = ROOT / "docs" / "data"

# The solver the pasted numbers are produced with. GLPK ships with cobrapy as a
# wheel, so it is the one solver every reader and every CI runner is guaranteed
# to have; pinning it keeps the output blocks reproducible.
DEFAULT_SOLVER = "glpk"

SKIP_FILE = "run-examples: skip-file"
SKIP_BLOCK = "run-examples: skip"

_FENCE_OPEN = re.compile(r"^(?P<indent>[ \t]*)(?P<ticks>`{3,})(?P<info>.*)$")
_HTML_COMMENT = re.compile(r"<!--(?P<body>.*?)-->")


# --------------------------------------------------------------------------
# Markdown scanning
# --------------------------------------------------------------------------


@dataclass
class Fence:
    """One fenced code block, wherever it sits in the page."""

    indent: str
    info: str
    body: list[str]
    start: int  # index of the opening ``` line
    end: int  # index of the closing ``` line

    @property
    def language(self) -> str:
        return self.info.strip().split(maxsplit=1)[0] if self.info.strip() else ""

    @property
    def code(self) -> str:
        strip = len(self.indent)
        return "\n".join(line[strip:] if line[:strip].isspace() or not line[:strip] else line.lstrip() for line in self.body)


@dataclass
class Example:
    """A ```python block, with the output block that follows it, if any."""

    page: Path
    number: int
    code_fence: Fence
    output_fence: Fence | None = None
    skip: bool = False
    actual: str | None = None
    error: str | None = None
    status: str = "pending"  # pending | ok | mismatch | error | skipped


@dataclass
class PageResult:
    page: Path
    examples: list[Example] = field(default_factory=list)
    skipped_page: bool = False

    @property
    def failures(self) -> list[Example]:
        return [e for e in self.examples if e.status in {"mismatch", "error"}]


def scan_fences(lines: list[str]) -> list[Fence]:
    """Return every fenced block in ``lines``, including indented ones.

    Content tabs indent their code by four spaces, so a naive ``^```` scan finds
    nothing on a dual-language page. Closing fences are matched on the same
    indentation and at least as many backticks as the opening fence, which is
    what CommonMark requires and what pymdownx accepts.
    """
    fences: list[Fence] = []
    i = 0
    while i < len(lines):
        match = _FENCE_OPEN.match(lines[i])
        if not match or "`" in match.group("info"):
            i += 1
            continue
        indent, ticks, info = match.group("indent"), match.group("ticks"), match.group("info")
        close = re.compile(rf"^{re.escape(indent)}`{{{len(ticks)},}}[ \t]*$")
        j = i + 1
        while j < len(lines) and not close.match(lines[j]):
            j += 1
        if j >= len(lines):  # unterminated fence -- leave it to the markdown build
            break
        fences.append(Fence(indent=indent, info=info, body=lines[i + 1 : j], start=i, end=j))
        i = j + 1
    return fences


def _preceding_comment_marks_skip(lines: list[str], fence: Fence) -> bool:
    """True when ``<!-- run-examples: skip -->`` sits just above the block."""
    k = fence.start - 1
    while k >= 0 and not lines[k].strip():
        k -= 1
    if k < 0:
        return False
    for comment in _HTML_COMMENT.finditer(lines[k]):
        if comment.group("body").strip() == SKIP_BLOCK:
            return True
    return False


def collect_examples(page: Path) -> PageResult:
    lines = page.read_text(encoding="utf-8").splitlines()
    result = PageResult(page=page)
    if any(SKIP_FILE in line for line in lines):
        result.skipped_page = True
        return result

    fences = scan_fences(lines)
    for index, fence in enumerate(fences):
        if fence.language != "python":
            continue
        output = None
        if index + 1 < len(fences):
            nxt = fences[index + 1]
            gap = lines[fence.end + 1 : nxt.start]
            if all(not line.strip() for line in gap) and 'title="Output"' in nxt.info:
                output = nxt
        result.examples.append(
            Example(
                page=page,
                number=len(result.examples) + 1,
                code_fence=fence,
                output_fence=output,
                skip=_preceding_comment_marks_skip(lines, fence),
            )
        )
    return result


# --------------------------------------------------------------------------
# Execution
# --------------------------------------------------------------------------


def _exec_block(code: str, namespace: dict) -> str:
    """Run one block and return what a notebook cell would have shown.

    Everything printed is captured, and if the block ends in a bare expression
    its repr is appended -- so ``model.reactions.get_by_id("r_0001")`` on the
    last line produces output without the page having to wrap it in ``print``.
    """
    tree = ast.parse(code)
    buffer = io.StringIO()
    last_expr: ast.Expr | None = None
    body = tree.body
    if body and isinstance(body[-1], ast.Expr):
        last_expr = body[-1]  # type: ignore[assignment]
        body = body[:-1]

    with contextlib.redirect_stdout(buffer):
        if body:
            exec(compile(ast.Module(body=body, type_ignores=[]), "<example>", "exec"), namespace)
        if last_expr is not None:
            value = eval(  # noqa: S307 -- documentation snippets, run deliberately
                compile(ast.Expression(last_expr.value), "<example>", "eval"), namespace
            )
            if value is not None:
                print(repr(value), file=buffer)
    return buffer.getvalue()


def run_page(result: PageResult, solver: str | None) -> None:
    """Execute a page's blocks in one namespace inside a scratch directory."""
    namespace: dict = {"__name__": "__main__"}
    workdir = Path(tempfile.mkdtemp(prefix="raven-docs-examples-"))
    if DATA_DIR.is_dir():
        for item in DATA_DIR.iterdir():
            if item.is_file() and item.name != "README.md":
                shutil.copy2(item, workdir / item.name)
    previous_cwd = Path.cwd()
    try:
        os.chdir(workdir)
        if solver:
            _pin_solver(solver)
        for example in result.examples:
            if example.skip:
                example.status = "skipped"
                continue
            try:
                example.actual = _exec_block(example.code_fence.code, namespace)
                example.status = "ok"  # provisional; compared below
            except BaseException:  # noqa: BLE001 -- a failing snippet is a finding
                example.error = traceback.format_exc(limit=3)
                example.status = "error"
                break  # later blocks depend on this one, so stop the page here
    finally:
        os.chdir(previous_cwd)
        shutil.rmtree(workdir, ignore_errors=True)


def _pin_solver(solver: str) -> None:
    try:
        import cobra  # noqa: PLC0415 -- optional, and only needed at run time
    except ImportError:
        return
    try:
        cobra.Configuration().solver = solver
    except Exception as exc:  # noqa: BLE001 -- report, do not abort the run
        print(f"warning: could not select solver {solver!r}: {exc}", file=sys.stderr)


# --------------------------------------------------------------------------
# Comparison
# --------------------------------------------------------------------------


def normalise(text: str) -> str:
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def matches(expected: str, actual: str) -> bool:
    """Compare with doctest-style ``...`` wildcards."""
    expected, actual = normalise(expected), normalise(actual)
    if expected.strip() == "...":
        return True
    if "..." not in expected:
        return expected == actual
    pattern = ".*?".join(re.escape(part) for part in expected.split("..."))
    return re.fullmatch(pattern, actual, flags=re.S) is not None


def compare(result: PageResult) -> None:
    for example in result.examples:
        if example.status != "ok" or example.output_fence is None:
            continue
        expected = "\n".join(
            line[len(example.output_fence.indent) :] if line.startswith(example.output_fence.indent) else line
            for line in example.output_fence.body
        )
        if not matches(expected, example.actual or ""):
            example.status = "mismatch"


# --------------------------------------------------------------------------
# --update
# --------------------------------------------------------------------------


def update_page(result: PageResult) -> bool:
    """Rewrite each output block to what the snippet actually printed.

    Blocks that produced no output lose their output block; blocks that gained
    output get one inserted, indented to match the code block above it.
    Returns True when the file changed.
    """
    lines = result.page.read_text(encoding="utf-8").splitlines()
    edits: list[tuple[int, int, list[str]]] = []  # (start, end_exclusive, replacement)

    for example in result.examples:
        if example.status in {"skipped", "error"} or example.actual is None:
            continue
        if example.status == "ok" and example.output_fence is not None:
            # Already matches, so leave the author's wording alone -- including
            # deliberate inline ``...`` wildcards. The one exception is a block
            # that is *only* ``...``: that is the placeholder an author writes
            # while drafting, and filling it in is the point of --update.
            body = normalise("\n".join(example.output_fence.body))
            if body.strip() != "...":
                continue
        actual = normalise(example.actual)
        indent = example.code_fence.indent
        if actual:
            block = [f'{indent}```text title="Output"']
            block += [f"{indent}{line}".rstrip() for line in actual.split("\n")]
            block += [f"{indent}```"]
        else:
            block = []
        if example.output_fence is not None:
            start, end = example.output_fence.start, example.output_fence.end + 1
            if not block:  # also drop the blank line that separated the blocks
                while start > example.code_fence.end + 1 and not lines[start - 1].strip():
                    start -= 1
            edits.append((start, end, block))
        elif block:
            insert_at = example.code_fence.end + 1
            edits.append((insert_at, insert_at, ["", *block]))

    if not edits:
        return False
    changed = False
    for start, end, block in sorted(edits, reverse=True):
        if lines[start:end] != block:
            lines[start:end] = block
            changed = True
    if changed:
        result.page.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changed


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------


def rel(path: Path) -> str:
    """Repo-relative path where possible -- pages may be passed from anywhere."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def report(results: list[PageResult]) -> int:
    failures = 0
    for result in results:
        page = rel(result.page)
        if result.skipped_page:
            print(f"  skip  {page}  (skip-file)")
            continue
        counts = {"ok": 0, "skipped": 0, "mismatch": 0, "error": 0}
        for example in result.examples:
            counts[example.status] = counts.get(example.status, 0) + 1
        state = "FAIL" if result.failures else "ok  "
        print(
            f"  {state}  {page}  "
            f"{counts['ok']} passed, {counts['skipped']} skipped, "
            f"{counts['mismatch']} mismatched, {counts['error']} errored"
        )
        for example in result.failures:
            failures += 1
            line = example.code_fence.start + 1
            print(f"\n    {page}:{line}  example {example.number}")
            if example.status == "error":
                for text in example.error.splitlines():
                    print(f"      {text}")
            else:
                expected = "\n".join(
                    li[len(example.output_fence.indent) :] if li.startswith(example.output_fence.indent) else li
                    for li in example.output_fence.body
                )
                diff = difflib.unified_diff(
                    normalise(expected).split("\n"),
                    normalise(example.actual or "").split("\n"),
                    fromfile="documented output",
                    tofile="actual output",
                    lineterm="",
                )
                for text in diff:
                    print(f"      {text}")
            print()
    return failures


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def gather_pages(targets: list[str]) -> list[Path]:
    if not targets:
        return sorted(DEFAULT_TARGET.rglob("*.md")) if DEFAULT_TARGET.is_dir() else []
    pages: list[Path] = []
    for target in targets:
        path = Path(target)
        if not path.is_absolute():
            path = ROOT / path
        pages.extend(sorted(path.rglob("*.md")) if path.is_dir() else [path])
    return pages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("targets", nargs="*", help="markdown files or directories (default: docs/guide)")
    parser.add_argument("--update", action="store_true", help="rewrite output blocks to the actual output")
    parser.add_argument("--list", action="store_true", help="list the examples without running them")
    parser.add_argument("--solver", default=DEFAULT_SOLVER, help=f"cobrapy solver to pin (default: {DEFAULT_SOLVER}; '' to leave alone)")
    args = parser.parse_args(argv)

    pages = gather_pages(args.targets)
    if not pages:
        print("run_examples: no pages found -- nothing to check.")
        return 0

    os.environ.setdefault("MPLBACKEND", "Agg")

    results = [collect_examples(page) for page in pages]

    if args.list:
        for result in results:
            page = rel(result.page)
            if result.skipped_page:
                print(f"{page}: skipped (skip-file)")
                continue
            for example in result.examples:
                mark = " (skip)" if example.skip else ""
                has_output = " +output" if example.output_fence else ""
                print(f"{page}:{example.code_fence.start + 1}  example {example.number}{mark}{has_output}")
        return 0

    for result in results:
        if result.skipped_page or not result.examples:
            continue
        run_page(result, args.solver or None)
        compare(result)

    if args.update:
        for result in results:
            if update_page(result):
                print(f"  updated  {rel(result.page)}")
        # Re-check so the exit status reflects the updated files.
        results = [collect_examples(page) for page in pages]
        for result in results:
            if result.skipped_page or not result.examples:
                continue
            run_page(result, args.solver or None)
            compare(result)

    total = sum(len(r.examples) for r in results)
    print(f"run_examples: {total} example(s) in {len(pages)} page(s)")
    failures = report(results)
    if failures:
        print(f"\nrun_examples: {failures} failing example(s).")
        print("Fix the snippet, or re-generate the output blocks with:")
        print("    python scripts/run_examples.py --update")
        return 1
    print("run_examples: all examples match their documented output.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
