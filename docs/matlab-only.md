# What only RAVEN has

Capabilities in the MATLAB toolbox with no raven-toolbox counterpart. Some are
deliberate omissions, some are simply not ported yet, and a few were removed from
RAVEN itself — the distinction matters, so it is stated for each.

The [mapping table](matlab-vs-python.md) lists this function by function,
including a *Not yet mapped* section for everything whose status is not yet
recorded either way.

## COBRA Toolbox conversion

`ravenCobraWrapper` converts between the RAVEN and COBRA Toolbox model
structures. There is nothing to convert in Python — the model is already a
`cobra.Model` — so no equivalent exists or is needed.

## Dynamic FBA

`runDynamicFBA` has no Python counterpart, deliberately. Several maintained
Python packages already cover dynamic FBA well
([dfba](https://pypi.org/project/dfba/),
[reframed](https://pypi.org/project/reframed/),
[mewpy](https://pypi.org/project/mewpy/)), and reimplementing it would add a
second-rate version of something that already exists.

## Metabolomics-based scoring in ftINIT

ftINIT's production-bonus block, which lets detected metabolites contribute to
the extraction score, is not implemented. Passing metabolomics data to the Python
`ftinit` raises `NotImplementedError` rather than silently ignoring it.

The reason is structural: raven-toolbox's linear merge eliminates the degree-2
metabolites this block scores, so supporting it needs the producer-group mapping
and negative-producer force-flux constraints rebuilt — the most intricate part of
ftINIT, for its least-used input.

## MATLAB-specific plumbing

A large share of RAVEN's function count is MATLAB housekeeping with nothing to
map to: path management (`addRavenToUserPath`, `findRAVENroot`), argument
handling (`parseRAVENargs`, `convertCharArray`), progress and printing
(`setRavenProgress`, `printOrange`), and the solver abstraction
(`optimizeProb`, `setRavenSolver`), which in Python is cobrapy's solver
interface via optlang.

## Removed from RAVEN itself

Not a difference between the toolboxes so much as a change in RAVEN that the
Python package never inherited:

- **Excel import.** `importExcelModel` was removed in the RAVEN 3 refactor and
  its tutorial models converted to YAML. raven-toolbox never had an Excel
  reader. Both still *write* Excel. Released RAVEN 2.x still ships the reader.
- **Flux map visualisation.** The `plotting/` folder (`drawMap`, `drawPathway`,
  `setOmicDataToRxns`, …) was dropped in the RAVEN 3 reorganisation. Neither
  toolbox has built-in visualisation today; use
  [Escher](https://escher.github.io/) or another cobrapy-compatible tool.
- **MetaCyc reconstruction.** `getMetaCycModelForOrganism` and the rest of
  `external/metacyc` were removed in the same reorganisation. It was never
  ported to Python: MetaCyc provides a single representative sequence per
  enzyme, which gives intrinsically low gene-calling precision — measured at
  roughly two-thirds of reaction assignments wrong at the default cutoff, with
  no cutoff that rescues it. Use the KEGG or homology routes.
