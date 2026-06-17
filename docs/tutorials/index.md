# Legacy tutorials

These five hands-on tutorials were part of the original **RAVEN 1** paper
(Agren et al., 2013). The code has been updated to run with current RAVEN, but
the exercises themselves are otherwise unchanged. They use the **MATLAB**
toolbox and build up from running a simulation on an existing model to
reconstructing a genome-scale model from sequence data. The scripts and all the
data files they use live in the
[`tutorial/`](https://github.com/SysBioChalmers/RAVEN/tree/main/tutorial)
folder of the RAVEN repository.

| # | Tutorial | What you learn |
|---|---|---|
| 1 | [Import a GEM and run FBA](tutorial1.md) | Load a model, set constraints and an objective, run FBA, visualise fluxes |
| 2 | [Construct a functional small model](tutorial2.md) | Build a model from scratch in Excel; exchange reactions and the steady-state assumption |
| 3 | [Knockouts, MOMA and omics data](tutorial3.md) | Gene deletions, MOMA, and using a GEM as a scaffold for microarray data |
| 4 | [Fix an erroneous model](tutorial4.md) | Systematic quality control: find and fix mass-balance and naming errors |
| 5 | [Reconstruct a GEM from KEGG](tutorial5.md) | *De novo* reconstruction from protein sequences using KEGG |

## Before you start

- These tutorials use the **MATLAB** toolbox. Make sure RAVEN is installed and
  `checkInstallation` passes — see [Installation](../installation.md).
- Tutorials 2–4 involve editing models in **RAVEN-compatible Excel format**, so
  you need a working `importExcelModel` (i.e. the Excel parser must pass
  `checkInstallation`).
- To run a section of a script in MATLAB, highlight it, right-click, and choose
  *"Evaluate selection"*.
- Tutorials 2, 3 and 4 ship with a `*_solutions.m` companion script containing
  the completed exercise.

!!! tip "Python users"
    The reconstruction concepts carry over directly to raven-toolbox. Look up the
    `snake_case` equivalent of each function in the [API reference](../api/index.md)
    (for example `importExcelModel` → `import_excel_model`, `solveLP` →
    `solve_lp`).
