# Differences and similarities

RAVEN is available as two independent implementations:

- **RAVEN** — the original MATLAB toolbox
- **raven-toolbox** — the Python port, built on [cobrapy](https://opencobra.github.io/cobrapy/)

Both implement the same core methods for genome-scale metabolic modelling, but
differ in language conventions, solver interface, and which features are
available. See the [function mapping table](matlab-vs-python.md) for a full
side-by-side cross-reference.

## Shared functionality

### Homology-based reconstruction

Both toolboxes support building draft models by transferring reactions from
template models based on protein sequence homology (BLAST+, DIAMOND, HMMER).
The underlying algorithm and default parameters are consistent between
implementations.

| RAVEN (MATLAB) | raven-toolbox (Python) |
|---|---|
| `getModelFromHomology` | `get_model_from_homology` |
| `getBlast` | `get_blast` |
| `getDiamond` | `get_diamond` |

### KEGG-based reconstruction

Both support building draft metabolic models from KEGG using organism codes, and
can download and cache KEGG data locally.

| RAVEN (MATLAB) | raven-toolbox (Python) |
|---|---|
| `getKEGGModelForOrganism` | `get_kegg_model_for_organism` |

### Gap-filling

Both provide gap-filling by linear programming to identify the minimum reaction
set needed to restore connectivity or growth.

| RAVEN (MATLAB) | raven-toolbox (Python) |
|---|---|
| `fillGaps` | `fill_gaps` |

### Flux analysis

Flux balance analysis (FBA), gene knockouts, and flux variability analysis (FVA)
are available in both, with equivalent solver interfaces.

### Model import and export

Both can read and write SBML (`.xml`) and RAVEN's Excel format (`.xlsx`), making
models fully portable between implementations.

| RAVEN (MATLAB) | raven-toolbox (Python) |
|---|---|
| `importModel` | `import_model` |
| `exportModel` | `export_model` |
| `importExcelModel` | `import_excel_model` |
| `exportToExcelFormat` | `export_to_excel_format` |

---

## Python-only features

### KEGG artefact generation

raven-toolbox includes tools to generate KEGG artefact databases — stoichiometric
matrices and reaction lists for arbitrary KEGG organisms. This is used to produce
updated KEGG reference data and is not available in the MATLAB toolbox.

### cobrapy interoperability

raven-toolbox is built directly on cobrapy's `cobra.Model`, so any cobrapy-
compatible tool works immediately. The MATLAB toolbox provides `ravenCobraWrapper`
for conversion, but this is an explicit transformation step rather than native
compatibility.

---

## MATLAB-only features

### COBRA Toolbox compatibility

`ravenCobraWrapper` converts between RAVEN and COBRA Toolbox model formats in
both directions. raven-toolbox uses cobrapy natively and has no COBRA Toolbox
dependency.

### Visualisation

RAVEN's `drawMap`-family functions provide flux map visualisation on top of
stoichiometric network maps. raven-toolbox currently has no built-in
visualisation; use Escher or cobrapy-compatible tools instead.

---

## Solver interface

| | RAVEN (MATLAB) | raven-toolbox (Python) |
|---|---|---|
| Configuration | `setRavenSolver('gurobi')` | `cobra.Configuration().solver = 'gurobi'` |
| Recommended solver | Gurobi (free academic licence) | Gurobi (free academic licence) |
| Bundled open-source solver | GLPK (via COBRA Toolbox) | GLPK (bundled with cobrapy) |

---

## Naming conventions

MATLAB uses `camelCase` function names; Python uses `snake_case`. The conversion
is mechanical: `getModelFromHomology` → `get_model_from_homology`. See the
[function mapping table](matlab-vs-python.md) for the full list.
