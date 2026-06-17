# Installation

RAVEN is available as a **MATLAB toolbox** and as the **Python package
raven-toolbox**. Both build the same models with the same algorithms, so pick
whichever fits your workflow:

<div class="grid cards" markdown>

-   :custom-matlab: **[RAVEN (MATLAB)](raven.md)**

    Install the MATLAB toolbox — via the MATLAB Add-Ons manager, a release
    download, or `git`. Includes upgrading and removal.

-   :material-language-python: **[raven-toolbox (Python)](python.md)**

    `pip install raven-toolbox`, plus development installs, upgrading and
    removal.

</div>

## Choosing a solver

Both versions need a linear-programming solver. The choice is the same for
either language:

| Solver | License | Good for |
|---|---|---|
| Gurobi | Free academic | Genome-scale models, tINIT/ftINIT, gap-filling (recommended) |
| GLPK   | Open source   | Small to medium models, getting started |
| SCIP   | Open source   | MILP problems (MATLAB) |

In **MATLAB**, select the active solver with `setRavenSolver('gurobi')`. In
**raven-toolbox**, the solver is configured through cobrapy
(`cobra.Configuration`).
