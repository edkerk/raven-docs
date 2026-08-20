"""Generate the API reference for raven-docs at build time.

Run by the ``mkdocs-gen-files`` plugin. Walks the two submodules and emits a
cobrapy-style ``autoapi`` reference as **two parallel trees** plus a name map:

* **MATLAB API (RAVEN)** -- one page per category folder (``reconstruction``,
  ``manipulation`` ...), each with a *Functions* summary table followed by the
  full help for every function (rendered by the ``matlab`` mkdocstrings
  handler via tree-sitter -- no MATLAB runtime needed).
* **Python API (raven-toolbox)** -- one page per package, same shape, rendered
  by the ``python`` handler (griffe collects from source statically).
* **MATLAB <-> Python** -- a single translation table pairing the two naming
  conventions (``camelCase`` <-> ``snake_case``) by normalised name, for every
  function that exists in both.

Each function gets its own ``## name`` heading (so the summary table can link
to it) followed by a ``:::`` autodoc block. A literate-nav ``SUMMARY.md`` ties
the trees together.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

import mkdocs_gen_files

# The collection layer is shared with scripts/check_names.py, so the prose is
# validated against exactly the index these pages are generated from.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from api_index import (  # noqa: E402
    MATLAB_CATEGORIES,
    PY_PACKAGE_TITLES,
    cell,
    collect_matlab,
    collect_python,
    norm,
    slug,
)


# --------------------------------------------------------------------------- #
# Page rendering                                                              #
# --------------------------------------------------------------------------- #
def render_page(title: str, intro: str, entries: list[dict], handler: str | None) -> str:
    """A cobrapy-style page: summary table, then one section per object.

    ``entries`` items: {name, summary, ref} where ref is the autodoc target
    (function name for matlab, dotted ident for python). ``handler`` is the
    mkdocstrings handler name, or None to use the default (python).
    """
    out = [f"# {title}", "", intro, "", "## Functions", ""]
    out += ["| Function | Summary |", "|---|---|"]
    for e in entries:
        out.append(f"| [`{e['name']}`](#{slug(e['name'])}) | {cell(e['summary'])} |")
    out += ["", "## Reference", ""]
    for e in entries:
        out += [f"### {e['name']}", ""]
        if handler:
            out += [f"::: {e['ref']}", f"    handler: {handler}", ""]
        else:
            out += [f"::: {e['ref']}", ""]
    return "\n".join(out) + "\n"


matlab = collect_matlab()
python_objs = collect_python()

# normalised name -> (python ident, package) ; first definition wins
py_by_norm: dict[str, dict] = {}
for obj in python_objs:
    py_by_norm.setdefault(norm(obj["name"]), obj)

summary: list[str] = ["* [Overview](index.md)"]

# --- MATLAB API tree ------------------------------------------------------- #
summary.append("* MATLAB API (RAVEN)")
for folder, title in MATLAB_CATEGORIES:
    funcs = matlab[folder]
    if not funcs:
        continue
    entries = [{"name": f["name"], "summary": f["summary"], "ref": f["name"]} for f in funcs]
    intro = (
        f"MATLAB functions in `RAVEN/{folder}` of the RAVEN toolbox. Help text "
        "is collected from the source of the tracked branch."
    )
    with mkdocs_gen_files.open(f"api/matlab/{folder}.md", "w") as fh:
        fh.write(render_page(title, intro, entries, handler="matlab"))
    summary.append(f"    * [{title}](matlab/{folder}.md)")

# --- Python API tree ------------------------------------------------------- #
by_package: dict[str, list[dict]] = {}
for obj in python_objs:
    by_package.setdefault(obj["package"], []).append(obj)

summary.append("* Python API (raven-toolbox)")
for package in sorted(by_package, key=lambda p: (p == "_toplevel", PY_PACKAGE_TITLES.get(p, p).lower())):
    objs = sorted(by_package[package], key=lambda o: o["name"].lower())
    title = PY_PACKAGE_TITLES.get(package, package)
    dotted = "raven_toolbox" if package == "_toplevel" else f"raven_toolbox.{package}"
    entries = [{"name": o["name"], "summary": o["summary"], "ref": o["ident"]} for o in objs]
    intro = f"`raven-toolbox` objects in `{dotted}`, collected from the source of the tracked branch."
    with mkdocs_gen_files.open(f"api/python/{package}.md", "w") as fh:
        fh.write(render_page(f"{title} (Python)", intro, entries, handler=None))
    summary.append(f"    * [{title}](python/{package}.md)")

# --- MATLAB vs Python translation table (top-level page) ------------------- #
# Automatic pairs: the names normalise to the same string. That only catches the
# mechanical cases, so scripts/curated_pairs.yml records the rest -- renamed
# counterparts, cobrapy replacements, and deliberate omissions.
CURATED = yaml.safe_load(
    (Path(__file__).resolve().parent / "curated_pairs.yml").read_text(encoding="utf-8")
)

matlab_all = {f["name"]: folder for folder, _t in MATLAB_CATEGORIES for f in matlab[folder]}
py_by_name = {obj["name"]: obj for obj in python_objs}

# Curated entries must resolve, or the build stops: this file is hand-written,
# and an unchecked hand-written name is exactly how the wrong ones got in.
unresolved: list[str] = []
for m_name, p_name in CURATED["aliases"].items():
    if m_name not in matlab_all:
        unresolved.append(f"aliases: RAVEN function '{m_name}' is not on the tracked branch")
    if p_name not in py_by_name:
        unresolved.append(f"aliases: raven-toolbox function '{p_name}' (for {m_name}) does not exist")
for section in ("cobrapy", "not_ported"):
    for m_name in CURATED[section]:
        if m_name not in matlab_all:
            unresolved.append(f"{section}: RAVEN function '{m_name}' is not on the tracked branch")
if unresolved:
    listed = "\n  - ".join(unresolved)
    raise SystemExit(
        f"gen_api_pages: scripts/curated_pairs.yml is out of date:\n  - {listed}"
    )

pairs: list[tuple[str, str, str, str, str, bool]] = []
seen_matlab: set[str] = set()
for folder, _title in MATLAB_CATEGORIES:
    for f in matlab[folder]:
        match = py_by_norm.get(norm(f["name"]))
        if match:
            pairs.append((f["name"], folder, match["name"], match["package"], f["summary"] or match["summary"], False))
            seen_matlab.add(f["name"])
for m_name, p_name in CURATED["aliases"].items():
    if m_name in seen_matlab:
        continue
    folder = matlab_all[m_name]
    obj = py_by_name[p_name]
    m_summary = next((f["summary"] for f in matlab[folder] if f["name"] == m_name), "")
    pairs.append((m_name, folder, p_name, obj["package"], m_summary or obj["summary"], True))

n_auto = sum(1 for r in pairs if not r[5])
lines = [
    "# MATLAB vs Python",
    "",
    "RAVEN ships as a MATLAB toolbox and as the Python package "
    "**raven-toolbox**. The two have large overlap, but differ in important "
    "ways:",
    "",
    "- The **MATLAB** version works completely independently — including "
    "independently of the COBRA Toolbox — although `ravenCobraWrapper` can "
    "translate between the RAVEN and COBRA model formats.",
    "- **raven-toolbox** is built on top of "
    "[cobrapy](https://cobrapy.readthedocs.io/), so anything cobrapy already "
    "does well is used directly rather than reimplemented.",
    "- Names are not always a mechanical `camelCase` → `snake_case` rewrite: "
    "much of the API was deliberately renamed, so check the table rather than "
    "guessing.",
    "",
    "This page is generated from the source of both toolboxes at build time. "
    "Pairs are found automatically where the names match, and completed from a "
    "curated list where they do not; every name is verified to exist.",
    "",
    "## Paired functions",
    "",
    f"**{len(pairs)}** pairs — {n_auto} matched automatically, "
    f"{len(pairs) - n_auto} curated.",
    "",
    "| RAVEN (MATLAB) | raven-toolbox (Python) | Summary |",
    "|---|---|---|",
]
for m_name, m_folder, p_name, p_pkg, text, _curated in sorted(pairs, key=lambda r: r[0].lower()):
    m_link = f"[`{m_name}`](api/matlab/{m_folder}.md#{slug(m_name)})"
    p_link = f"[`{p_name}`](api/python/{p_pkg}.md#{slug(p_name)})"
    lines.append(f"| {m_link} | {p_link} | {cell(text)} |")

lines += [
    "",
    "## Covered by cobrapy",
    "",
    "These RAVEN functions have no raven-toolbox counterpart because cobrapy "
    "already provides the capability. Follow the link for its documentation.",
    "",
    "| RAVEN (MATLAB) | Use instead |",
    "|---|---|",
]
for m_name, target in sorted(CURATED["cobrapy"].items(), key=lambda kv: kv[0].lower()):
    folder = matlab_all[m_name]
    m_link = f"[`{m_name}`](api/matlab/{folder}.md#{slug(m_name)})"
    url = "https://cobrapy.readthedocs.io/en/latest/autoapi/cobra/index.html"
    lines.append(f"| {m_link} | [`{target}`]({url}) |")

lines += [
    "",
    "## Deliberately not ported",
    "",
    "| RAVEN (MATLAB) | Why not |",
    "|---|---|",
]
for m_name, reason in sorted(CURATED["not_ported"].items(), key=lambda kv: kv[0].lower()):
    folder = matlab_all[m_name]
    m_link = f"[`{m_name}`](api/matlab/{folder}.md#{slug(m_name)})"
    lines.append(f"| {m_link} | {cell(reason)} |")

# Whatever is left over is unmapped -- neither paired, nor delegated to cobrapy,
# nor recorded as a deliberate omission. Listing it keeps the table honest about
# its own coverage, and doubles as the work list for extending curated_pairs.yml.
accounted = (
    {r[0] for r in pairs} | set(CURATED["cobrapy"]) | set(CURATED["not_ported"])
)
unmapped = sorted((n for n in matlab_all if n not in accounted), key=str.lower)
if unmapped:
    lines += [
        "",
        "## Not yet mapped",
        "",
        f"**{len(unmapped)}** RAVEN functions are not yet recorded here. Some have "
        "a Python counterpart that has not been curated into the table, some are "
        "MATLAB-specific plumbing (path handling, argument parsing, printing) "
        "with nothing to map to, and some are genuinely absent from "
        "raven-toolbox. Until a function appears in one of the tables above, "
        "treat its status as unknown rather than as \"not ported\".",
        "",
    ]
    for chunk_start in range(0, len(unmapped), 6):
        row = unmapped[chunk_start:chunk_start + 6]
        lines.append(", ".join(f"`{n}`" for n in row) + ("," if chunk_start + 6 < len(unmapped) else ""))

with mkdocs_gen_files.open("matlab-vs-python.md", "w") as fh:
    fh.write("\n".join(lines) + "\n")

# --- literate-nav SUMMARY -------------------------------------------------- #
with mkdocs_gen_files.open("api/SUMMARY.md", "w") as fh:
    fh.write("\n".join(summary) + "\n")
