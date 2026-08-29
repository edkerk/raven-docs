# Differences and similarities

RAVEN exists as two independent implementations:

- **RAVEN** — the original MATLAB toolbox, which works entirely on its own,
  including independently of the COBRA Toolbox.
- **raven-toolbox** — the Python package, built on
  [cobrapy](https://cobrapy.readthedocs.io/), so a model is a `cobra.Model` and
  the wider Python ecosystem works on it directly.

They cover the same ground — homology and KEGG reconstruction, metabolic tasks,
gap-filling, context-specific extraction with tINIT/ftINIT, compartment
assignment, model comparison — but they are not transliterations of each other.
Names differ, some capabilities exist on one side only, and a handful of
functions answer the same question differently.

<div class="grid cards" markdown>

-   :material-swap-horizontal: **[Function mapping](matlab-vs-python.md)**

    Which function replaces which, generated from the source of both toolboxes
    at build time — including what cobrapy covers instead, and what is
    deliberately absent.

-   :material-language-python: **[What only raven-toolbox has](python-only.md)**

    cobrapy interoperability, KEGG artefact generation, confidence tracking,
    certified compartment assignment, model diffing.

-   :custom-matlab: **[What only RAVEN has](matlab-only.md)**

    COBRA Toolbox conversion, dynamic FBA, ftINIT metabolomics scoring — and
    what was removed from RAVEN itself.

-   :material-not-equal-variant: **[Same function, different answer](behaviour.md)**

    Where the two agree on the job but differ in what they return, or in what
    they do to the model on the way.

-   :material-scale-balance: **[What "identical results" means](parity.md)**

    Which functions can match exactly, which can only be compared for overlap,
    and which are statistical by nature.

-   :material-tune-variant: **[Tuned parameter defaults](tuned-parameters.md)**

    Which non-obvious defaults have actually been measured, where the two
    sides still disagree, and a couple of assumptions that turned out wrong on
    inspection.

-   :material-flask-outline: **[Methods & benchmarks](parameter-tuning/index.md)**

    The measurement campaigns behind the tuned defaults above — full studies
    and per-function benchmark notes, for whoever wants the evidence rather
    than the summary.

</div>

## Naming

MATLAB uses `camelCase`, Python `snake_case`, but the conversion is **not**
mechanical. Much of the API was deliberately renamed as it was ported —
`getBlast` became `run_blast`, `addRxns` became `add_reactions_from_equations`,
`fillGaps` split into three functions with different algorithms. Guessing a name
by rewriting the case is the most common way to reach for something that does not
exist; check the [mapping table](matlab-vs-python.md) instead.

## Solver interface

| | RAVEN (MATLAB) | raven-toolbox (Python) |
|---|---|---|
| Configuration | `setRavenSolver('gurobi')` | `cobra.Configuration().solver = 'gurobi'` |
| Recommended solver | Gurobi (free academic licence) | Gurobi (free academic licence) |
| Open-source option | GLPK (via COBRA Toolbox) | GLPK (bundled with cobrapy) |

Genome-scale MILP work — ftINIT extraction in particular — is where the choice
matters most; see [Installation](installation/index.md) for the full solver
matrix.

## Model exchange

Models move between the two implementations through **SBML** (`.xml`) and
**YAML** (`.yml`). raven-toolbox's YAML follows the cobrapy layout plus RAVEN's
own per-entry fields, so a model written by either side round-trips through the
other — see [the YAML format reference](yaml-format.md) for the full field-by-field
spec and interoperability matrix.

Excel is **export-only** on both sides: raven-toolbox has never had a reader, and
RAVEN's `importExcelModel` was removed in the RAVEN 3 refactor.
