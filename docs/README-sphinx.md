# Sphinx / pydata-sphinx-theme exploration

Not part of the site. This is a working note for the `explore/pydata-sphinx-theme`
branch, read by nobody but a maintainer deciding whether to pursue the migration
for real. `mkdocs.yml` and the live MkDocs build are untouched and still what
CI and Read the Docs use; this branch adds a second, parallel toolchain over
the same `docs/` content.

## Building it

```bash
python -m venv .venv-sphinx
.venv-sphinx/Scripts/pip install -r requirements-sphinx.txt
.venv-sphinx/Scripts/sphinx-build -b html docs docs/_build/html
```

## What's converted

- **Admonitions, content tabs, snippet includes.** Mechanical, via
  `scripts/migrate_to_myst.py`, run once across every page. `!!! note "…"` ->
  `:::{note} …`; `=== "MATLAB"` -> a `tab-set`/`tab-item` pair;
  `--8<-- "path"` -> `{literalinclude}`. Re-running it is a no-op (nothing
  left to match).
- **Navigation.** `mkdocs.yml`'s single `nav:` tree is now a `{toctree}` per
  section, living in that section's own `index.md` (or `migrate.md` /
  `reference.md`, two new landing pages mirroring #77's audience-first tabs
  on the MkDocs side). Nested toctrees give the same depth the old nav had.
- **The generated API reference and MATLAB vs Python table.** New
  `scripts/gen_api_pages_sphinx.py`, run from `conf.py`'s `setup()` before
  Sphinx reads the source tree. Reuses `api_index.py`'s collection constants
  and file-walking, extended to keep the *whole* help text instead of only
  the first line, and writes fully static pages: see "Not converted" below
  for why.
- **The home page.** Hand-converted, not mechanical: MkDocs Material's grid
  cards and the custom pip-install JS widget have no equivalent to translate,
  so it's rebuilt with `sphinx-design` grids and a plain tab-set instead.
- **Link underlines.** `docs/_static/custom.css`, wired in via
  `html_css_files`.

## Not converted

- **Per-function docstring rendering.** The MkDocs build defers this to two
  live plugins at render time: mkdocstrings' Python handler (griffe) and a
  separate mkdocstrings-matlab handler (tree-sitter). Neither has a verified
  drop-in Sphinx equivalent, the MATLAB one especially, which is a bespoke
  handler with no autodoc-family counterpart. `gen_api_pages_sphinx.py`
  sidesteps this by extracting the full help text itself and writing static
  pages, which keeps the same no-install, no-MATLAB-runtime constraint the
  MkDocs build has, but by a different route. Worth a closer look before
  treating this as done: real docstring structure (numpydoc parameter
  tables, cross-references) is flattened to a plain text block here, where
  mkdocstrings renders it properly.
- **`scripts/build_hooks.py`, `scripts/check_names.py`.** Both are MkDocs
  plugin hooks (`on_config`, `on_page_markdown`, `on_page_content`), a
  different event API than Sphinx's `app.connect(...)`. `build_hooks.py`'s
  matlab-path pruning and mkdocstrings-matlab output cleanup are moot here,
  since this branch doesn't use mkdocstrings-matlab at all.
  `check_names.py`'s identifier validation is still valuable and doesn't
  need to be a live hook; it can run as a standalone pre-build check either
  way, but re-wiring it wasn't done as part of this exploration.
- **`scripts/run_examples.py`.** Parses MkDocs/pymdownx fence syntax
  (` ```text title="Output" ` in particular) to find and check expected
  output blocks. That fence shape changed here (see "Admonitions, content
  tabs..." above); the script would need to read MyST's fence conventions
  instead before it could check this branch's pages.
- **`<span class="cobrapy-tag">` inline badges.** Scattered across ~40 guide
  pages inside tables. Renders as inert plain text (the CSS class is
  Material-specific and not defined here) rather than a badge. Converting
  every occurrence to a `sphinx-design` badge role is mechanical in the same
  way the tab/admonition conversion is, just not done in this pass.
- **`.readthedocs.yaml`.** Still points at the `mkdocs:` build. The target
  block for a real switch:

  ```yaml
  build:
    os: ubuntu-24.04
    tools:
      python: "3.12"
  sphinx:
    configuration: docs/conf.py
  python:
    install:
      - requirements: requirements-sphinx.txt
  ```

  Left unset here since flipping it would make this branch's incomplete
  build the one Read the Docs actually serves.
- **RST cross-reference roles inside docstrings.** raven-toolbox's
  docstrings use Sphinx's own `:func:`name`` role syntax, expected by a
  proper `sphinx.ext.autodoc` pipeline. Rendered as static text here (see
  above), `:func:` shows as a literal prefix next to a correctly-formatted
  inline code span, rather than becoming a cross-reference link. Cosmetic,
  not a build warning.

## Verified

`sphinx-build -E -b html docs docs/_build/html` (`-E` forces a clean
re-read; an incremental rebuild under-reports the cross-reference count
below, since Sphinx does not always revalidate a link when only the *target*
document changed): **0 errors, 64 warnings.**

Two real fixes got the API-reference-generator's own share of that down to
zero, not just noise-suppression:

- Its Python function headings embedded the full signature
  (`### merge_linear(model, no_merge=())`), so MyST's auto-generated heading
  anchor did not match the plain `#merge_linear` the summary table and
  `matlab-vs-python.md` link to. Moved the signature to its own line below
  the heading instead of inside it.
- `## Title {#custom-id}` (MkDocs' attr_list heading-ID syntax) needed
  converting to an explicit `(custom-id)=` MyST target, added as the
  converter's fifth transform.

What's left, all in hand-authored pages rather than generated ones:

- **21 `myst.header`** ("Non-consecutive header level increase; H1 to H3"),
  across most of `docs/guide/*.md`. Predates this branch: every one of these
  pages goes straight from its H1 title to an H3 "Functions on this page"
  aside, which Python-Markdown never enforced and MyST does. A heading-level
  fix, not a migration one; left alone here.
- **42 `myst.xref_missing`**, almost all in `raven3-migration.md`
  (`installation/raven.md` and `guide/io.md` have a few more): hand-placed
  `<a name="…"></a>` HTML anchors, which work as plain browser URL fragments
  but aren't in MyST's own validated-target registry, so every markdown link
  pointing at one warns without actually being broken.
- **1 `toc.not_included`**: `docs/data/README.md`, the same page the MkDocs
  build also excludes from its nav. Not a regression.
