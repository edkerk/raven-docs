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

!!! info "Executed examples"
    Every snippet on these pages is run on each commit and checked against the
    output shown beneath it, in both languages. The one exception is
    [10. Context-specific models](init.md), whose steps take hours on Human-GEM:
    that page says so at the top and quotes the wall-clock of the run its numbers
    came from.

## Example data

| File | What it is |
|---|---|
| [`smallYeast.yml`](../data/smallYeast.yml) | central carbon metabolism in yeast; the default example |
| [`smallYeastBad.yml`](../data/smallYeastBad.yml) | the same model with deliberate errors, for the curation pages |
| [`empty.xml`](../data/empty.xml) | an empty model with compartments, for building one from scratch |
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
6. [Solvers and configuration](solvers.md) — which solver, and how to read what
   it returns.

**Building and curating**

7. [Building a model from scratch](building.md) — metabolites, reactions, genes,
   exchanges.
8. [Editing an existing model](editing.md) — stoichiometry, GPRs, bounds,
   deletions.
9. [Quality control](quality-control.md) — structure, mass balance, blocked
   reactions, mass from nothing.

**Reconstruction**

10. [Context-specific models (tINIT / ftINIT)](init.md) — extracting a cell-line
    model from Human-GEM and RNA-seq, end to end.

**Analysis and repair**

11. [Deletions and essentiality](deletions.md) — knockouts, essential genes and
    reactions, MOMA.
12. [Metabolic tasks](tasks.md) — saying what a model must be able to do, and
    checking that it still can.
13. [Gap-filling](gap-filling.md) — closing the holes a draft model has.
14. [Flux variability](fva.md) — how much each flux can still move, and
    which predictions the model has no choice about.
15. [Random sampling](sampling.md) — the distribution behind those ranges, and
    how to condition it on a state worth asking about.
16. [Combining and simplifying models](combining.md) — merging models on
    metabolite names, and taking one apart again.
17. [Comparing models](comparing.md) — what changed between two models, and how
    much that difference costs.

**Planned** — phenotype exploration,
engineering targets; biomass composition and annotation; reconstruction from
homology and KEGG; localization; table-driven curation.
