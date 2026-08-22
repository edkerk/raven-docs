# User guide

Short, task-focused pages: one job per page, three to eight functions, in
**MATLAB and Python side by side**. Start at
[Getting started](getting-started.md) and read on, or jump to whichever task you
have in front of you.

This is one of three sets of worked material on this site — see the
[Guides overview](../protocol/index.md) for how it relates to the *H. polymorpha*
reconstruction protocol and the legacy tutorials.

## How to read these pages

- **Every code block has a MATLAB and a Python tab.** Choosing one switches all
  of them, on every page, and the choice is remembered between visits.
- **cobrapy is marked.** raven-toolbox is built on cobrapy and deliberately does
  not re-implement what cobrapy already provides. Where a Python step is
  cobrapy's rather than raven-toolbox's, it carries a
  <span class="cobrapy-tag">cobrapy</span> badge, the import line shows it
  (`from cobra.io import read_sbml_model`), and the link goes to the cobrapy
  documentation. See [MATLAB vs Python](../differences.md) for the full picture.
- **Where a step exists in only one language, the page says so** rather than
  inventing a counterpart.
- **Outputs are real.** The Python snippets are executed in CI against the
  models in [`docs/data/`](../data/README.md), and the build fails if a page
  prints something other than what it claims.

## Example data

| File | What it is |
|---|---|
| [`smallYeast.yml`](../data/smallYeast.yml) | central carbon metabolism in yeast; the default example |
| [`smallYeastBad.yml`](../data/smallYeastBad.yml) | the same model with deliberate errors, for the curation pages |
| [`yeast-GEM.yml`](../data/yeast-GEM.yml) | yeast-GEM v9.1.0, the consensus *S. cerevisiae* model, for pages that need a genome-scale one |
| [`yeast-GEM.xml`](../data/yeast-GEM.xml) | the same model as SBML |

## Pages

**Foundations**

- [Getting started](getting-started.md) — load a model and inspect it.
- Model structure and identifiers *(planned)*
- Reading and writing models *(planned)*
- Solvers and configuration *(planned)*

**Building and editing** *(planned)* — building from scratch, editing,
compartments and transport, combining and simplifying.

**Simulation** *(planned)* — FBA, growth media, flux variability, deletions and
essentiality, sampling, phenotype exploration, engineering targets.

**Quality and gaps** *(planned)* — quality control, gap-filling, metabolic
tasks, biomass composition, annotation.

**Reconstruction** *(planned)* — homology, KEGG, tINIT/ftINIT, localization.

**Several models** *(planned)* — comparison, curation from tables.
