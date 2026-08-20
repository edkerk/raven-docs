# Differences and similarities

RAVEN is available as two independent implementations:

- **RAVEN** — the original MATLAB toolbox
- **raven-toolbox** — the Python port, built on [cobrapy](https://opencobra.github.io/cobrapy/)

Both implement the same core methods for genome-scale metabolic modelling, but
differ in language conventions, solver interface, and which features are
available.

See the [function mapping table](matlab-vs-python.md) — generated from the source of
both toolboxes at build time — for the full side-by-side cross-reference.

## Shared functionality

### Homology-based reconstruction

Both toolboxes support building draft models by transferring reactions from
template models based on protein sequence homology (BLAST+, DIAMOND, HMMER).
The underlying algorithm and default parameters are consistent between
implementations.

| RAVEN (MATLAB) | raven-toolbox (Python) |
|---|---|
| `getModelFromHomology` | `get_model_from_homology` |
| `getBlast` | `run_blast` |
| `getDiamond` | `run_diamond` |

### KEGG-based reconstruction

Both support building draft metabolic models from KEGG using organism codes, and
can download and cache KEGG data locally.

| RAVEN (MATLAB) | raven-toolbox (Python) |
|---|---|
| `getKEGGModelForOrganism` | `get_kegg_model_for_organism` |

### Gap-filling

Both provide gap-filling to identify the smallest set of reactions needed to
restore connectivity or growth. RAVEN gathers this in one function; raven-toolbox
splits it by algorithm, so the Python side is a choice rather than a single call.

| RAVEN (MATLAB) | raven-toolbox (Python) |
|---|---|
| `fillGaps` (connectivity mode) | `connect_blocked_reactions` |
| `fillGaps` (targeted mode) | `fill_gaps_fast_lp`, `fill_gaps_kumar_milp` |
| `checkProduction`, `getAllSubGraphs`, `haveFlux` | `analyse_topology` |

### Flux analysis

Flux balance analysis (FBA), gene knockouts, and flux variability analysis (FVA)
are available in both, with equivalent solver interfaces.

### Model import and export

Both read and write SBML (`.xml`) and the RAVEN YAML format (`.yml`), so models
move between the two implementations in either direction. In Python the standard
formats are handled by cobrapy itself, and raven-toolbox adds the RAVEN-specific
ones.

| RAVEN (MATLAB) | raven-toolbox (Python) | |
|---|---|---|
| `importModel` | `cobra.io.read_sbml_model` | cobrapy |
| `exportModel` | `cobra.io.write_sbml_model` | cobrapy |
| `readYAMLmodel` | `read_yaml_model` | |
| `writeYAMLmodel` | `write_yaml_model` | |
| `exportToExcelFormat` | `export_to_excel` | |
| `exportForGit` | `export_for_git` | |

!!! warning "Excel is export-only"
    Neither toolbox reads models from Excel any more. raven-toolbox writes Excel
    but has never had a reader — a deliberate omission. RAVEN's `importExcelModel`
    was removed during the RAVEN 3 refactor, and its tutorial models were
    converted to YAML; released RAVEN 2.x still ships it. Use SBML or YAML to move
    a model between the two implementations.

---

## Python-only features

### KEGG artefact generation

raven-toolbox includes tools to generate KEGG artefact databases — stoichiometric
matrices and reaction lists for arbitrary KEGG organisms. This is used to produce
updated KEGG reference data and is not available in the MATLAB toolbox.

### SIF export for Cytoscape

`export_model_to_sif` writes the reaction/metabolite graph as Cytoscape SIF.
RAVEN had `exportModelToSIF`, but it was dropped in the RAVEN 3 codebase review,
so this is Python-only on the branches documented here.

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

Released RAVEN 2.x ships a `plotting/` folder (`drawMap`, `drawPathway`,
`setOmicDataToRxns`, …) for flux maps drawn on stoichiometric network maps. That
folder was dropped in the RAVEN 3 reorganisation, so neither the documented
RAVEN branch nor raven-toolbox has built-in visualisation today — use Escher or
another cobrapy-compatible tool.

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
[function mapping table](matlab-vs-python.md) for every paired function.
