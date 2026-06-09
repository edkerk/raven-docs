# API reference

RAVEN ships in two implementations that build the **same** genome-scale
metabolic models with the same algorithms:

- **RAVEN** — the original **MATLAB** toolbox, built on the COBRA Toolbox and
  `libSBML`. Source layout: `core/`, `io/`, `solver/`, `pathway/`, `plotting/`,
  `hpa/`, `struct_conversion/`, `utils/`.
- **raven-python** — the **Python** port, built on cobrapy. Source layout:
  `reconstruction/`, `manipulation/`, `analysis/`, `gapfilling/`, `io/`,
  `tasks/`, and more.

The function help on these pages is extracted directly from the source of each
toolbox on its `main` branch, so it is always in sync with the code.

## How the two line up

The two implementations are deliberately kept aligned. The main differences are
mechanical:

| | RAVEN (MATLAB) | raven-python (Python) |
|---|---|---|
| Naming | `camelCase` (`getModelFromHomology`) | `snake_case` (`get_model_from_homology`) |
| Returns | multiple outputs `[a,b] = f(...)` | one return value; objects often mutated in place |
| Indexing | 1-based | 0-based |
| Model object | RAVEN `model` struct | `cobra.Model` with RAVEN extensions |

## How these pages are organised

On their released `main` branches the two toolboxes use **different folder
layouts** (RAVEN keeps its classic flat structure; raven-python uses a newer
modular one), but the underlying functions correspond by name. So this
reference:

- is **organised by RAVEN's categories** (`Core`, `Input / output`, …);
- shows each MATLAB function together with its `raven-python` counterpart in
  **tabs**, whenever a counterpart exists on `main`;
- collects Python functions that have **no** MATLAB counterpart yet on the
  separate *raven-python (Python-only)* pages.

Each function is shown with both implementations in tabs — click between them:

=== "MATLAB · RAVEN"

    ```matlab
    model = getModelFromHomology(models, blast, 'hanpo', {'sce','rhto'});
    ```

=== "Python · raven-python"

    ```python
    from raven_python.reconstruction import get_model_from_homology
    ```

!!! note "A note on the two docstring styles"
    raven-python's docstrings are NumPy-style, so they render as structured
    parameter/return tables. RAVEN's MATLAB help blocks use the toolbox's own
    indented convention, so they render as faithful help text rather than typed
    tables. The content is the same; only the formatting differs.

Use the navigation to browse the reference by category.
