# Changes from RAVEN 2

raven-toolbox is not a direct port of RAVEN 2.0 — it is a fresh Python
implementation that makes deliberate architectural choices where RAVEN 2.0
showed its age or where the Python ecosystem offers better alternatives. This
page documents the most significant departures and the reasoning behind them.

## What is not in raven-toolbox

### MetaCyc / BioCyc

RAVEN 2.0 includes `getMetaCycModelForOrganism` for building draft models from
the MetaCyc / BioCyc databases. raven-toolbox **does not** include MetaCyc
support. Reasons:

- The MetaCyc API and data formats have changed substantially since the original
  implementation, making the RAVEN 2.0 connector unreliable with current database
  releases.
- Maintaining an up-to-date connector requires ongoing manual upkeep tied to
  MetaCyc licensing and format changes.
- In practice, homology-based reconstruction from a curated template model or
  KEGG produces better-quality drafts for most organisms; MetaCyc is more useful
  as an annotation cross-reference than as a primary reconstruction source.

If you rely on MetaCyc reconstruction, continue using RAVEN 2.0 or extract the
relevant reactions manually and import them via SBML or Excel.

---

## Architectural changes

### Model data structure

RAVEN 2.0 represents models as MATLAB structs with fields `.rxns`, `.mets`,
`.S`, `.lb`, `.ub`, etc. raven-toolbox uses cobrapy's `cobra.Model` as its
native data structure. This means:

- All cobrapy-compatible tools work directly with raven-toolbox models.
- Solver calls go through cobrapy's unified interface.
- The MATLAB struct format is not used internally; models are loaded directly
  into `cobra.Model` objects.

### Python packaging

raven-toolbox is distributed via PyPI (`pip install raven-toolbox`), enabling
standard reproducible environments and straightforward CI integration.

### Type annotations

All public functions in raven-toolbox carry full Python type annotations and pass
static analysis with `mypy`. This was not possible in the MATLAB toolbox.

---

## What stayed the same

- Core algorithms (homology search, gap-filling, KEGG reconstruction) use the
  same logic as RAVEN 2.0 with equivalent default parameters.
- SBML (`.xml`) and YAML (`.yml`) model formats are fully interoperable between
  RAVEN 2.0 and raven-toolbox. Excel is export-only in raven-toolbox — see
  [Differences and similarities](differences.md).
- Function naming follows the same conceptual structure, converted to `snake_case`
  (see the [function mapping table](matlab-vs-python.md)).
