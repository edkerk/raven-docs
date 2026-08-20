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
pairs: list[tuple[str, str, str, str, str]] = []  # (matlab, folder, python, package, summary)
for folder, _title in MATLAB_CATEGORIES:
    for f in matlab[folder]:
        match = py_by_norm.get(norm(f["name"]))
        if match:
            text = f["summary"] or match["summary"]
            pairs.append((f["name"], folder, match["name"], match["package"], text))

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
    "[cobrapy](https://cobrapy.readthedocs.io/).",
    "- As a result, some functions are **MATLAB-only**: they are not ported "
    "because cobrapy already provides the equivalent. In that case, look for "
    "the function in the "
    "[cobrapy API](https://cobrapy.readthedocs.io/en/latest/autoapi/cobra/index.html).",
    "",
    "The table below pairs the functions that exist in both implementations "
    "(MATLAB `camelCase` ↔ Python `snake_case`); click a name to jump to its "
    "full reference. Functions that exist in only one implementation appear in "
    "that language's [API reference](api/index.md) tree but not here.",
    "",
    f"**{len(pairs)}** paired functions.",
    "",
    "| RAVEN (MATLAB) | raven-toolbox (Python) | Summary |",
    "|---|---|---|",
]
for m_name, m_folder, p_name, p_pkg, text in sorted(pairs, key=lambda r: r[0].lower()):
    m_link = f"[`{m_name}`](api/matlab/{m_folder}.md#{slug(m_name)})"
    p_link = f"[`{p_name}`](api/python/{p_pkg}.md#{slug(p_name)})"
    lines.append(f"| {m_link} | {p_link} | {cell(text)} |")
with mkdocs_gen_files.open("matlab-vs-python.md", "w") as fh:
    fh.write("\n".join(lines) + "\n")

# --- literate-nav SUMMARY -------------------------------------------------- #
with mkdocs_gen_files.open("api/SUMMARY.md", "w") as fh:
    fh.write("\n".join(summary) + "\n")
