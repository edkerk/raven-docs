# raven-toolbox (Python)

**raven-toolbox** is the Python implementation of RAVEN, built on
[cobrapy](https://opencobra.github.io/cobrapy/). It is distributed on PyPI.

## Requirements

- **Python ≥ 3.11**
- **cobrapy** — installed automatically as a dependency
- A **solver**: GLPK (bundled with cobrapy) works for small and medium models;
  [Gurobi](https://www.gurobi.com/) is recommended for genome-scale work.
  See [Choosing a solver](index.md#choosing-a-solver).

!!! tip "Use a virtual environment"
    ```bash
    python -m venv .venv
    source .venv/bin/activate      # Windows: .venv\Scripts\activate
    ```

---

## Install

=== ":material-package: From PyPI"

    ```bash
    pip install raven-toolbox
    ```

=== ":octicons-git-branch-16: From source"

    For the latest unreleased code or to contribute:

    ```bash
    git clone https://github.com/SysBioChalmers/raven-toolbox.git
    cd raven-toolbox
    pip install -e .
    ```

---

## Verify

```python
import raven_toolbox
print(raven_toolbox.__version__)
```

!!! note
    The import package is `raven_toolbox` (underscore); the PyPI distribution
    name is `raven-toolbox` (hyphen).

---

## Upgrade

=== ":material-package: PyPI install"

    ```bash
    pip install --upgrade raven-toolbox
    ```

=== ":octicons-git-branch-16: Source install"

    ```bash
    git pull origin develop
    ```

---

## Remove

```bash
pip uninstall raven-toolbox
```

---

## Solver configuration

raven-toolbox uses cobrapy's solver interface:

```python
import cobra
cobra.Configuration().solver = "gurobi"   # or "glpk"
```
