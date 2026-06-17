# raven-toolbox (Python)

**raven-toolbox** is the Python implementation of RAVEN, built on
[cobrapy](https://opencobra.github.io/cobrapy/). It is distributed on PyPI.

## Requirements

- **Python ≥ 3.11**.
- [cobrapy](https://opencobra.github.io/cobrapy/) — installed automatically as a
  dependency.
- A **solver**: the open-source **GLPK** (bundled with cobrapy) works for small
  and medium models; **Gurobi** is recommended for genome-scale optimization.
  See [Choosing a solver](index.md#choosing-a-solver).

It is good practice to install into a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

## Install

```bash
pip install raven-toolbox
```

### Development install (from source)

To work with the latest, unreleased code or to contribute:

```bash
git clone https://github.com/SysBioChalmers/raven-toolbox.git
cd raven-toolbox
pip install -e .
```

## Verify the installation

```python
import raven_toolbox
print(raven_toolbox.__version__)
```

The import package is `raven_toolbox` (underscore), while the PyPI distribution
is `raven-toolbox` (hyphen).

## Upgrading

```bash
pip install --upgrade raven-toolbox
```

For a development (`-e`) install, pull the latest changes instead:

```bash
git pull origin develop
```

## Removing

```bash
pip uninstall raven-toolbox
```

## Solver configuration

raven-toolbox uses cobrapy's solver interface. Set the active solver through
cobrapy, for example:

```python
import cobra
cobra.Configuration().solver = "gurobi"   # or "glpk"
```
