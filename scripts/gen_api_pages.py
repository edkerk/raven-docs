"""Generate the API reference for raven-docs at build time.

Run by the ``mkdocs-gen-files`` plugin. Walks the two submodules:

* ``RAVEN``         -- the MATLAB toolbox (released ``main``), classic flat
                       layout (``core``, ``io``, ``solver`` ...).
* ``raven-python``  -- the Python port, modern modular layout
                       (``reconstruction``, ``manipulation`` ...).

The two implementations expose the *same* functions under
``camelCase`` (MATLAB) / ``snake_case`` (Python) names, but on ``main`` they
live in different folders. So functions are paired **globally by normalised
name**, the reference is organised by RAVEN's categories (every MATLAB
function is documented, with the Python counterpart shown beside it when it
exists), and any Python functions without a MATLAB counterpart are documented
on their own per-package pages. A literate-nav ``SUMMARY.md`` ties it together.

No MATLAB runtime or installed package is needed: docstrings are collected
statically by mkdocstrings (tree-sitter for MATLAB, griffe for Python).
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import mkdocs_gen_files

ROOT = Path(__file__).resolve().parent.parent
RAVEN = ROOT / "RAVEN"
PYPKG = ROOT / "raven-python" / "src" / "raven_python"

# RAVEN top-level categories to document, in nav order: (folder, page title).
# Mirrors the matlab handler `paths:` in mkdocs.yml. legacy/ and external/ are
# intentionally excluded (deprecated / third-party).
MATLAB_CATEGORIES = [
    ("reconstruction", "Reconstruction"),
    ("manipulation", "Manipulation"),
    ("analysis", "Analysis"),
    ("gapfilling", "Gap-filling"),
    ("annotation", "Annotation"),
    ("biomass", "Biomass"),
    ("curation", "Curation"),
    ("conversion", "Format conversion"),
    ("conditions", "Conditions"),
    ("comparison", "Comparison"),
    ("omics", "Omics integration"),
    ("localization", "Localization"),
    ("queries", "Queries"),
    ("io", "Input / output"),
    ("solver", "Solvers"),
    ("tasks", "Metabolic tasks"),
    ("utils", "Utilities"),
]

# Friendly titles for raven-python packages (Python-only leftovers).
PY_PACKAGE_TITLES = {
    "reconstruction": "Reconstruction",
    "manipulation": "Manipulation",
    "analysis": "Analysis",
    "gapfilling": "Gap-filling",
    "tasks": "Metabolic tasks",
    "omics": "Omics integration",
    "localization": "Localization",
    "io": "Input / output",
    "comparison": "Comparison",
    "init": "Initialization",
    "utils": "Utilities",
    "plotting": "Plotting",
    "_toplevel": "Top-level",
}


def norm(name: str) -> str:
    """Normalise a function name for cross-language matching."""
    return re.sub(r"[_\s]", "", name).lower()


# --------------------------------------------------------------------------- #
# Collect MATLAB functions                                                    #
# --------------------------------------------------------------------------- #
def is_matlab_function(path: Path) -> bool:
    """True if the .m file declares a function (i.e. not a plain script)."""
    try:
        with path.open(encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                stripped = line.strip()
                if not stripped or stripped.startswith("%"):
                    continue
                return stripped.startswith("function")
    except OSError:
        return False
    return False


def collect_matlab() -> dict[str, list[str]]:
    """category -> sorted list of MATLAB function names."""
    cats: dict[str, list[str]] = {}
    for folder, _title in MATLAB_CATEGORIES:
        names = []
        base = RAVEN / folder
        for m in base.rglob("*.m"):
            if m.stem == "Contents":
                continue
            if not is_matlab_function(m):
                continue
            names.append(m.stem)
        cats[folder] = sorted(set(names), key=str.lower)
    return cats


# --------------------------------------------------------------------------- #
# Collect Python functions and classes                                        #
# --------------------------------------------------------------------------- #
def module_dotted(path: Path) -> str:
    """raven-python/src/raven_python/io/excel.py -> raven_python.io.excel"""
    rel = path.relative_to(PYPKG.parent)  # relative to src/
    parts = list(rel.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def collect_python() -> list[dict]:
    """List of {name, ident, package} for every public top-level def/class."""
    objects: list[dict] = []
    for py in PYPKG.rglob("*.py"):
        if any(part.startswith("_") and part != "__init__.py" for part in py.parts):
            # skip private modules / packages (but keep __init__.py)
            pass
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except (SyntaxError, OSError):
            continue
        dotted = module_dotted(py)
        rel = py.relative_to(PYPKG)
        package = rel.parts[0] if len(rel.parts) > 1 else "_toplevel"
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name.startswith("_"):
                    continue
                ident = f"{dotted}.{node.name}" if dotted else node.name
                objects.append(
                    {"name": node.name, "ident": ident, "package": package}
                )
    return objects


# --------------------------------------------------------------------------- #
# Rendering helpers                                                           #
# --------------------------------------------------------------------------- #
def matlab_block(name: str, indent: str = "") -> str:
    lines = [f"{indent}::: {name}", f"{indent}    handler: matlab"]
    return "\n".join(lines)


def python_block(ident: str, indent: str = "") -> str:
    return f"{indent}::: {ident}"


def paired_section(title: str, matlab_name: str | None, python_ident: str | None) -> str:
    """One ## entry: MATLAB and/or Python, in tabs when both exist."""
    out = [f"## {title}", ""]
    if matlab_name and python_ident:
        out += ['=== "MATLAB · RAVEN"', "", matlab_block(matlab_name, "    "), ""]
        out += ['=== "Python · raven-python"', "", python_block(python_ident, "    "), ""]
    elif matlab_name:
        out += [matlab_block(matlab_name), ""]
    elif python_ident:
        out += [python_block(python_ident), ""]
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------- #
# Build the pages                                                             #
# --------------------------------------------------------------------------- #
matlab = collect_matlab()
python_objs = collect_python()

# normalised name -> python ident (first definition wins)
py_by_norm: dict[str, str] = {}
for obj in python_objs:
    py_by_norm.setdefault(norm(obj["name"]), obj["ident"])

used_python: set[str] = set()
summary: list[str] = ["* [Overview](index.md)", "* MATLAB ↔ Python"]

for folder, title in MATLAB_CATEGORIES:
    names = matlab[folder]
    if not names:
        continue
    page = f"{folder}.md"
    lines = [
        f"# {title}",
        "",
        f"MATLAB functions in `RAVEN/{folder}`, paired with their "
        "`raven-python` counterpart where one exists on the tracked `main` "
        "branch.",
        "",
    ]
    for name in names:
        ident = py_by_norm.get(norm(name))
        if ident:
            used_python.add(ident)
        lines.append(paired_section(name, name, ident))
    with mkdocs_gen_files.open(f"api/{page}", "w") as fh:
        fh.write("\n".join(lines))
    summary.append(f"    * [{title}]({page})")

# Python-only objects, grouped by package.
leftover: dict[str, list[dict]] = {}
for obj in python_objs:
    if obj["ident"] in used_python:
        continue
    leftover.setdefault(obj["package"], []).append(obj)

if leftover:
    summary.append("* raven-python (Python-only)")
    for package in sorted(leftover, key=lambda p: (p == "_toplevel", p)):
        objs = sorted(leftover[package], key=lambda o: o["name"].lower())
        title = PY_PACKAGE_TITLES.get(package, package)
        page = f"python/{package}.md"
        lines = [
            f"# {title} (Python)",
            "",
            f"`raven-python` objects in `raven_python"
            f"{'' if package == '_toplevel' else '.' + package}` that do not "
            "have a direct MATLAB counterpart on RAVEN's `main` branch.",
            "",
        ]
        for obj in objs:
            lines.append(paired_section(obj["name"], None, obj["ident"]))
        with mkdocs_gen_files.open(f"api/{page}", "w") as fh:
            fh.write("\n".join(lines))
        summary.append(f"    * [{title}]({page})")

with mkdocs_gen_files.open("api/SUMMARY.md", "w") as fh:
    fh.write("\n".join(summary) + "\n")
