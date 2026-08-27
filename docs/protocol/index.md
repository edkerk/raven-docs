# Guides

Three sets of worked material, for three different purposes.

<div class="grid cards" markdown>

-   :material-book-open-variant: **[User guide](../guide/index.md)**

    Sixteen short, task-focused pages — load a model, simulate growth, define a
    medium, edit, check, gap-fill, extract a context-specific model. **MATLAB and
    Python side by side**, every example executed and checked on each commit.

    Start at [1. Getting started](../guide/getting-started.md).

-   :material-flask: **[GEM reconstruction protocol](reconstruction.md)**

    Homology-based reconstruction of a genome-scale model for the yeast
    *Hansenula polymorpha* (`hanpo-GEM`), end to end — from template models to a
    growing, methylotrophic draft. A published pipeline, followed from start to
    finish. MATLAB only.

-   :material-school: **[Legacy tutorials](../tutorials/index.md)**

    Five exercises from the original RAVEN paper (Agren et al., 2013), updated to
    run with current RAVEN but otherwise unchanged. MATLAB only.

</div>

## Which one do I want?

| If you want to… | Go to |
|---|---|
| look up how to do one thing, in either language | [User guide](../guide/index.md) |
| follow a complete reconstruction as it was published | [GEM reconstruction](reconstruction.md) |
| work through the exercises from the RAVEN paper | [Legacy tutorials](../tutorials/index.md) |
| extract a context-specific model with ftINIT | [10. Context-specific models](../guide/init.md) |
| find the Python equivalent of a RAVEN function | [MATLAB vs Python](../matlab-vs-python.md) |

## The user guide

| | |
|---|---|
| **Foundations** | [1. Getting started](../guide/getting-started.md) · [2. Model structure and identifiers](../guide/model-structure.md) · [3. Reading and writing models](../guide/io.md) |
| **Simulation** | [4. Simulating growth with FBA](../guide/fba.md) · [5. Growth media and conditions](../guide/media.md) · [6. Solvers and configuration](../guide/solvers.md) |
| **Building and curating** | [7. Building a model from scratch](../guide/building.md) · [8. Editing an existing model](../guide/editing.md) · [9. Quality control](../guide/quality-control.md) · [16. Combining and simplifying](../guide/combining.md) |
| **Reconstruction** | [10. Context-specific models (tINIT / ftINIT)](../guide/init.md) |
| **Analysis and repair** | [11. Deletions and essentiality](../guide/deletions.md) · [12. Metabolic tasks](../guide/tasks.md) · [13. Gap-filling](../guide/gap-filling.md) · [14. Flux variability](../guide/fva.md) · [15. Random sampling](../guide/sampling.md) |

More pages are being added — reconstruction from homology and KEGG, model
comparison.

## Legacy tutorials

Five hands-on tutorials from the original RAVEN paper (Agren et al., 2013),
updated to run with current RAVEN. MATLAB only.

| # | Tutorial | Topic |
|---|---|---|
| 1 | [Import a GEM and run FBA](../tutorials/tutorial1.md) | Load a model, set constraints, run FBA |
| 2 | [Build a small model](../tutorials/tutorial2.md) | Build from scratch in Excel |
| 3 | [Knockouts, MOMA and omics](../tutorials/tutorial3.md) | Gene deletions, MOMA, microarray data |
| 4 | [Fix an erroneous model](../tutorials/tutorial4.md) | Quality control and curation |
| 5 | [Reconstruct from KEGG](../tutorials/tutorial5.md) | *De novo* reconstruction from KEGG |
