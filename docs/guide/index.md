# User guide

Short, task-focused pages: one job per page, three to eight functions, in
**MATLAB and Python side by side**. Start at
[Getting started](getting-started.md) and read on, or jump to whichever task you
have in front of you.

This is one of three sets of worked material on this site — see the
[Guides overview](../protocol/index.md) for how it relates to the *H. polymorpha*
reconstruction protocol and the legacy tutorials.

!!! info "cobrapy"
    Functions that come from cobrapy rather than raven-toolbox carry a
    <span class="cobrapy-tag">cobrapy</span> badge, their import line shows where
    they live (`from cobra.io import read_sbml_model`), and the badge links to
    the cobrapy documentation. [MATLAB vs Python](../differences.md) lists every
    such function.

## Example data

| File | What it is |
|---|---|
| [`smallYeast.yml`](../data/smallYeast.yml) | central carbon metabolism in yeast; the default example |
| [`smallYeastBad.yml`](../data/smallYeastBad.yml) | the same model with deliberate errors, for the curation pages |
| [`yeast-GEM.yml`](../data/yeast-GEM.yml) | yeast-GEM v9.1.0, the consensus *S. cerevisiae* model, for pages that need a genome-scale one |
| [`yeast-GEM.xml`](../data/yeast-GEM.xml) | the same model as SBML |
| [`anaerobic.yml`](../data/anaerobic.yml) | a condition file: yeast-GEM under anaerobic conditions |

## Pages

**Foundations**

1. [Getting started](getting-started.md) — load a model and inspect it.
2. [Model structure and identifiers](model-structure.md) — how the RAVEN struct
   and `cobra.Model` correspond, field by field.
3. [Reading and writing models](io.md) — SBML, RAVEN YAML, Excel, text, and the
   layout a model repository expects.

**Simulation**

4. [Simulating growth with FBA](fba.md) — objective, bounds, solve, read the
   fluxes.
5. [Growth media and conditions](media.md) — define a medium, keep a condition as
   data.

**Planned** — solvers and configuration; building, editing, combining models;
flux variability, deletions, sampling, phenotype exploration, engineering
targets; quality control, gap-filling, metabolic tasks, biomass, annotation;
reconstruction from homology, KEGG, tINIT/ftINIT, localization; comparison and
table-driven curation.
