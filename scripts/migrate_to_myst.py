"""One-time converter: MkDocs/pymdownx Markdown -> MyST, for the Sphinx exploration.

Run once against every page under docs/ (see __main__ below). Handles, in order:

1. Content tabs (``=== "MATLAB"`` / ``=== "Python"``) -> sphinx-design
   ``::::{tab-set}`` / ``:::{tab-item} MATLAB`` fences.
2. Admonitions (``!!! note "Title"``) -> MyST ``:::{note} Title`` fences.
   ``info`` has no native docutils admonition, so it becomes a generic
   ``:::{admonition} Title`` with ``:class: info``.
3. ```` ```text title="Output" ```` fences -> plain ```` ```text ```` fences;
   MyST/pygments does not accept pymdownx's ``title=`` attribute in the info
   string.
4. ``--8<-- "path"`` snippet includes (the fenced-block form; the only one
   this repo uses) -> a ``{literalinclude}`` directive, path adjusted for the
   including document's depth under ``docs/``.
5. ``## Title {#custom-id}`` (attr_list heading IDs) -> an explicit
   ``(custom-id)=`` MyST target line before the heading.

Both block extractors work on indentation, not a fixed column, so a converted
tab body is dedented before the admonition pass runs over it -- an admonition
nested inside a tab (or vice versa) is picked up on the same pass because the
dedent preserves relative indentation.

Idempotent: re-running on already-converted text is a no-op, since neither
pattern is matched with the MyST spelling as the marker.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

TAB_MARKER = re.compile(r'^( *)=== "([^"]+)"\s*$')
ADMONITION_MARKER = re.compile(r'^( *)!!! (\w+)(?: "([^"]*)")?\s*$')
OUTPUT_TITLE = re.compile(r'^(```text) title="Output(?:, [^"]*)?"\s*$')
# attr_list heading IDs: "## Title {#custom-id}" -> an explicit MyST target
# line before the heading, since MyST does not read this trailing-brace form.
HEADING_ID = re.compile(r'^(#+\s+.*?)\s*\{#([\w-]+)\}\s*$', re.M)
# pymdownx.snippets, fenced-block form only (the only form this repo uses):
#   ```lang
#   --8<-- "path/relative/to/repo/root"
#   ```
SNIPPET_FENCE = re.compile(r'^```(\w+)\n--8<-- "([^"]+)"\n```$', re.M)

ADMONITION_NATIVE = {"note", "tip", "warning", "danger", "attention", "caution", "error", "hint", "important", "seealso"}


def _block_body(lines: list[str], start: int, marker_indent: int) -> tuple[list[str], int]:
    """Lines belonging to a block whose marker sits at ``marker_indent``.

    A line belongs if it is blank, or indented at least ``marker_indent + 4``.
    Returns the body (dedented by ``marker_indent + 4``) and the index of the
    first line after the block.
    """
    body_indent = marker_indent + 4
    body: list[str] = []
    i = start
    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            body.append("")
            i += 1
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent < body_indent:
            break
        body.append(line[body_indent:])
        i += 1
    # Trailing blank lines are trimmed from the rendered block for cosmetics
    # only; `i` already correctly points past them at the line that ended the
    # block (a sibling marker or unrelated content), and must stay there.
    while body and body[-1] == "":
        body.pop()
    return body, i


def convert_tabs(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        m = TAB_MARKER.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue

        indent = m.group(1)
        n = len(indent)
        out.append(f"{indent}::::{{tab-set}}")
        # Consume every sibling "=== " block at this same indent as one set;
        # a line that is not itself such a marker ends the set, regardless of
        # its own indentation (it is sibling content in the parent block).
        while i < len(lines) and (mm := TAB_MARKER.match(lines[i])) and len(mm.group(1)) == n:
            label = mm.group(2)
            body, i = _block_body(lines, i + 1, n)
            body_text = convert_tabs("\n".join(body))  # recurse: nested tab sets
            out.append(f"{indent}:::{{tab-item}} {label}")
            out.append(body_text)
            out.append(f"{indent}:::")
        out.append(f"{indent}::::")
        out.append("")  # docutils wants a blank line after a closed directive
    return "\n".join(out)


def convert_admonitions(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        m = ADMONITION_MARKER.match(lines[i])
        if m:
            indent, kind, title = m.group(1), m.group(2), m.group(3)
            n = len(indent)
            body, i = _block_body(lines, i + 1, n)
            body_text = convert_admonitions("\n".join(body))  # recurse: nested admonitions
            if kind in ADMONITION_NATIVE:
                out.append(f"{indent}:::{{{kind}}}" + (f" {title}" if title else ""))
            else:
                out.append(f"{indent}:::{{admonition}}" + (f" {title}" if title else " Note"))
                out.append(f"{indent}:class: {kind}")
            out.append(body_text)
            out.append(f"{indent}:::")
            out.append("")  # docutils wants a blank line after a closed directive
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def collapse_blank_runs(text: str) -> str:
    """Squash 3+ consecutive blank lines down to 1, a side effect of always
    inserting a blank line after a closed directive even where one already
    followed in the source."""
    return re.sub(r"\n{3,}", "\n\n", text)


def convert_output_titles(text: str) -> str:
    return "\n".join(OUTPUT_TITLE.sub(r"\1", line) for line in text.split("\n"))


def convert_heading_ids(text: str) -> str:
    return HEADING_ID.sub(lambda m: f"({m.group(2)})=\n{m.group(1)}", text)


def convert_snippets(text: str, depth: int) -> str:
    """``--8<-- "path"`` (relative to the repo root) -> a literalinclude,
    relative to the including document -- ``depth`` is how many directories
    the document sits below ``docs/`` (0 for ``docs/index.md`` itself)."""
    up = "../" * (depth + 1)

    def repl(m: re.Match) -> str:
        lang, rel = m.group(1), m.group(2)
        return f"```{{literalinclude}} {up}{rel}\n:language: {lang}\n```"

    return SNIPPET_FENCE.sub(repl, text)


def convert(text: str, depth: int = 0) -> str:
    text = convert_tabs(text)
    text = convert_admonitions(text)
    text = convert_output_titles(text)
    text = convert_heading_ids(text)
    text = convert_snippets(text, depth)
    text = collapse_blank_runs(text)
    return text


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs")
    changed = 0
    for path in sorted(root.rglob("*.md")):
        original = path.read_text(encoding="utf-8")
        depth = len(path.relative_to(root).parent.parts)
        converted = convert(original, depth)
        if converted != original:
            path.write_text(converted, encoding="utf-8", newline="\n")
            changed += 1
    print(f"converted {changed} file(s) under {root}")
