# API reference

RAVEN ships in two implementations that build the **same** genome-scale
metabolic models with the same algorithms:

- **RAVEN** — the original **MATLAB** toolbox, built on the COBRA Toolbox and
  `libSBML`. Functions use `camelCase` names.
- **raven-toolbox** — the **Python** port, built on cobrapy. Functions use
  `snake_case` names.

The function help on these pages is extracted directly from the source of each
toolbox on the branch tracked by this site, so it stays in sync with the code.

## How these pages are organised

The reference is split into **two parallel trees**, one per language, each
organised by the toolbox's own module layout and each function shown with its
signature, parameters and returns:

- **MATLAB API (RAVEN)** — one page per category (`Reconstruction`,
  `Manipulation`, `Input / output`, …).
- **Python API (raven-toolbox)** — one page per package, mirroring the same
  categories.

Every page opens with a *Functions* table you can scan, followed by the full
help for each function.

To move between the two implementations, see
**[Differences and similarities](../differences.md)**. A generated table pairing every
function `camelCase` ↔ `snake_case` is in preparation.

## How the two line up

The implementations are deliberately kept aligned. The main differences are
mechanical:

| | RAVEN (MATLAB) | raven-toolbox (Python) |
|---|---|---|
| Naming | `camelCase` (`getModelFromHomology`) | `snake_case` (`get_model_from_homology`) |
| Returns | multiple outputs `[a,b] = f(...)` | one return value; objects often mutated in place |
| Indexing | 1-based | 0-based |
| Model object | RAVEN `model` struct | `cobra.Model` with RAVEN extensions |

!!! note "A note on the two docstring styles"
    raven-toolbox's docstrings are NumPy-style, so they render as structured
    parameter/return tables. RAVEN's MATLAB help blocks use the toolbox's own
    indented convention, so they render as faithful help text rather than typed
    tables. The content is the same; only the formatting differs.

Use the navigation to browse either tree, or start from
[Differences and similarities](../differences.md).
