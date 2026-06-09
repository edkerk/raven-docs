# Installation

RAVEN is available as a MATLAB toolbox and as a Python package. Pick whichever
fits your workflow — both build the same models with the same algorithms.

## RAVEN (MATLAB)

### Requirements

- **MATLAB** R2013b or later (no additional MathWorks toolboxes required).
- **[libSBML](http://sbml.org/Software/libSBML)** MATLAB API — for reading and
  writing models in the community-standard SBML (`.xml`) format.
- A **linear-programming solver**. RAVEN supports
  [Gurobi](https://www.gurobi.com/) (free academic license, recommended),
  the GLPK solver bundled with the
  [COBRA Toolbox](https://github.com/opencobra/cobratoolbox), or SCIP.
- For reconstruction from sequence data, the bundled binaries **BLAST+**,
  **DIAMOND** and **HMMER** (shipped with RAVEN for Windows, macOS and Linux).

### Install

1. Download the latest release of RAVEN from
   [GitHub](https://github.com/SysBioChalmers/RAVEN/releases), or clone the
   repository:

    ```bash
    git clone https://github.com/SysBioChalmers/RAVEN.git
    ```

2. Add RAVEN (and the `libSBML` and solver subfolders) to the MATLAB path with
   the `pathtool` function, or run `RavenScripts`/`checkInstallation` from the
   RAVEN root.

3. Verify the installation from the MATLAB command window:

    ```matlab
    checkInstallation
    ```

    This reports whether RAVEN is on the path, whether Excel and SBML models can
    be parsed, which solver is active, and whether the BLAST+/DIAMOND/HMMER
    binaries are available. Its output is the first thing to check when
    troubleshooting.

!!! warning "Excel parsing conflict"
    MATLAB's **Text Analytics Toolbox** (R2017b and later) can conflict with
    RAVEN's Excel parser. If `checkInstallation` reports
    *"Checking if it is possible to parse a model in Microsoft Excel
    format... FAILED"*, uninstall the Text Analytics Toolbox. See
    [RAVEN issue #55](https://github.com/SysBioChalmers/RAVEN/issues/55).

Detailed instructions and dependency notes are kept on the
[RAVEN GitHub Wiki](https://github.com/SysBioChalmers/RAVEN/wiki/Installation).

## raven-python (Python)

### Requirements

- **Python ≥ 3.11**.
- [cobrapy](https://opencobra.github.io/cobrapy/), installed automatically as a
  dependency.
- A solver: the open-source **GLPK** works for small and medium models;
  **Gurobi** is recommended for genome-scale optimization (tINIT/ftINIT).

### Install

```bash
pip install raven-python
```

Or install the development version from source:

```bash
git clone https://github.com/SysBioChalmers/raven-python.git
cd raven-python
pip install -e .
```

Import the package as `raven_python`:

```python
import raven_python
```

## Choosing a solver

| Solver | License | Good for |
|---|---|---|
| Gurobi | Free academic | Genome-scale models, tINIT/ftINIT, gap-filling |
| GLPK   | Open source   | Small to medium models, getting started |
| SCIP   | Open source   | MILP problems (MATLAB) |

Set the active solver in MATLAB with `setRavenSolver('gurobi')`; in
raven-python, the cobra solver is configured through `cobra.Configuration`.
