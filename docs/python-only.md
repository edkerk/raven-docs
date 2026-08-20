# What only raven-toolbox has

Capabilities in the Python package with no counterpart in the MATLAB toolbox.
For the function-level view, see the [mapping table](matlab-vs-python.md).

## Built on cobrapy

The largest difference is not a feature but a foundation: a raven-toolbox model
**is** a `cobra.Model`. Every cobrapy tool, and everything in the wider COBRA
Python ecosystem, works on it without conversion. RAVEN's own model is a MATLAB
struct, and `ravenCobraWrapper` converts between that and the COBRA Toolbox
format as an explicit step.

The practical consequence: FBA, FVA, knockouts, media handling and the rest come
from cobrapy rather than from raven-toolbox, which is why so many RAVEN functions
have a *cobrapy* row rather than a Python counterpart in the mapping table.

## KEGG artefact generation

raven-toolbox can build the KEGG reference artefacts themselves — parsing a KEGG
release into reaction and compound tables, assembling the reference model,
building the per-KO FASTA sets and HMM libraries, and deriving the phylogenetic
distance matrix. RAVEN consumes pre-built artefacts; it does not produce them.

This is what keeps the KEGG route reproducible against a stated KEGG release
rather than against whatever artefact happens to be distributed.

## Confidence tracking

Per-reaction, multi-facet confidence scoring — evidence for a reaction's presence
graded across several independent facets, with the bands calibrated against
curated models. Used to prioritise manual curation on a draft: reactions the
score is least sure about are where a curator's time goes furthest.

## Functionality-constrained compartment assignment

Both toolboxes can place reactions into compartments, and both now offer
`assignCompartments`. raven-toolbox additionally certifies the result: placement
is decided by a score MILP and then confirmed by a real FBA on the materialised
model, so a placement that breaks biomass production is rejected rather than
returned. It can also couple gap-filling into the same step, and keeps a second
compartment for a reaction only when a loopless FVA shows it carries flux there.

## Model diffing and comparison

`diff_models` reports the semantic differences between two models — including
comparing gene associations as logic rather than as strings, so `A or B` and
`B or A` are recognised as the same rule. `compare_models` handles the N-model
case.

## SIF export

`export_model_to_sif` writes the reaction/metabolite graph for Cytoscape. RAVEN
had `exportModelToSIF`, but it was removed in the RAVEN 3 codebase review, so
this is Python-only on the branches documented here.

## Smaller additions

- **Growth conditions** — apply a named, versioned growth condition to a model.
- **Batch curation** — apply a table of curation edits to a model in one pass.
- **ΔG and SBO annotation** — load and save thermodynamic data through CSV, and
  assign SBO terms.
- **Biomass helpers** — sum a biomass composition, rescale a pseudoreaction, and
  scale a fraction to a measured value.
- **Binary and data provisioning** — fetch and verify BLAST+, DIAMOND, HMMER and
  the KEGG artefacts on demand, against a checksummed manifest.
