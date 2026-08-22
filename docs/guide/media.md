# Growth media and conditions

An FBA result is a statement about a medium. This page is about setting that
medium deliberately: which exchange reactions are open, how wide, and how to keep
a condition as reviewable data instead of a paragraph of bound-setting code.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `getExchangeRxns` | `Model.exchanges` <span class="cobrapy-tag">cobrapy</span> | find the exchange reactions |
| `setExchangeBounds` | `Model.medium` <span class="cobrapy-tag">cobrapy</span> | open a set of uptakes |
| `closeModel` | `Model.medium = {}` <span class="cobrapy-tag">cobrapy</span> | close every uptake |
| `setParam` | `set_reaction_bounds` | set one reaction's bounds |
| `getMinimalMedium` | `minimal_medium` <span class="cobrapy-tag">cobrapy</span> | the smallest medium that still supports growth |
| `applyCondition` | `apply_condition`, `load_condition` | apply a condition file |

## Setup

`yeast-GEM.xml` from [`docs/data/`](../data/README.md), which ships with an
aerobic minimal glucose medium already applied.

## 1. What is currently open

An exchange reaction connects a boundary metabolite to nothing, so its flux is
the rate at which that metabolite enters (negative) or leaves (positive) the
system. The medium is exactly the set of exchanges with a negative lower bound.

=== "MATLAB"

    ```matlab
    model = importModel('yeast-GEM.xml');
    [exchangeRxns, exchangeRxnsIndexes] = getExchangeRxns(model);
    open = exchangeRxnsIndexes(model.lb(exchangeRxnsIndexes) < 0);
    printModel(model, open);
    ```

=== "Python"

    ```python
    from cobra.io import read_sbml_model

    model = read_sbml_model("yeast-GEM.xml")
    shipped = dict(model.medium)          # keep it; later steps restore from here
    print(len(model.exchanges), "exchange reactions")

    for rxn_id, uptake in sorted(model.medium.items()):
        print(f"  {rxn_id}  {model.reactions.get_by_id(rxn_id).name:<28} {uptake:>8}")
    ```

    ```text title="Output"
    270 exchange reactions
      r_1654  ammonium exchange              1000.0
      r_1714  D-glucose exchange                1.0
      r_1832  H+ exchange                    1000.0
      r_1861  iron(2+) exchange              1000.0
      r_1992  oxygen exchange                1000.0
      r_2005  phosphate exchange             1000.0
      r_2020  potassium exchange             1000.0
      r_2049  sodium exchange                1000.0
      r_2060  sulphate exchange              1000.0
      r_2100  water exchange                 1000.0
      r_4593  chloride exchange              1000.0
      r_4594  Cu2(+) exchange                1000.0
      r_4595  Mn(2+) exchange                1000.0
      r_4596  Zn(2+) exchange                1000.0
      r_4597  Mg(2+) exchange                1000.0
      r_4600  Ca(2+) exchange                1000.0
    ```

    `model.medium` is a dict of `{exchange id: maximum uptake rate}`, given as a
    **positive** number — cobrapy flips the sign for you, so a medium entry of
    `1.0` means a lower bound of `-1.0`.

## 2. Change one nutrient

=== "MATLAB"

    ```matlab
    model = setParam(model, 'lb', 'r_1714', -10);   % D-glucose exchange
    ```

=== "Python"

    ```python
    from raven_toolbox.conditions import set_reaction_bounds

    glucose = model.reactions.get_by_id("r_1714")
    set_reaction_bounds(glucose, -10.0, 1000.0)
    print(glucose.bounds, "->", f"{model.slim_optimize():.4f} /h")
    ```

    ```text title="Output"
    (-10.0, 1000.0) -> 0.8370 /h
    ```

    `set_reaction_bounds` sets both bounds at once and in the right order, which
    matters: assigning a lower bound above the current upper bound raises in
    cobrapy. `slim_optimize` returns just the objective value, without building a
    full `Solution`.

## 3. Define a whole medium

Assigning to the medium is **not** a patch: everything not in the dict is closed.
That makes it the right tool for "this exact recipe and nothing else", and a trap
if you meant "the shipped medium, but with more glucose".

=== "MATLAB"

    ```matlab
    modelClosed = closeModel(model);                  % every uptake to zero
    sol = solveLP(modelClosed);
    fprintf('growth with nothing to eat: %.4f /h\n', -sol.f);

    % a complete medium: reopen what the recipe contains
    model = setExchangeBounds(model, {'r_1714'}, -10, 1000);
    ```

=== "Python"

    ```python
    with model:
        model.medium = {}                             # every uptake closed
        print(f"growth with nothing to eat: {model.slim_optimize():.4f} /h")

    with model:
        model.medium = {"r_1714": 10.0, "r_1992": 1000.0}   # only glucose and oxygen
        print(f"glucose and oxygen alone:  {model.slim_optimize():.4f} /h")

    model.medium = {**shipped, "r_1714": 10.0}        # the shipped recipe, more glucose
    print(f"complete medium:           {model.slim_optimize():.4f} /h")
    ```

    ```text title="Output"
    growth with nothing to eat: nan /h
    glucose and oxygen alone:  0.0000 /h
    complete medium:           0.8370 /h
    ```

    Glucose and oxygen alone are not enough — yeast-GEM also needs nitrogen,
    phosphate, sulphate and a handful of ions, which is why building a medium from
    `dict(model.medium)` and editing the entries you care about is usually safer
    than writing the whole recipe out.

    With **everything** closed the growth rate is not zero but `nan`:
    `slim_optimize` returns `nan` when the LP has no solution at all, which is a
    different answer from "the optimum is zero". When a result surprises you, ask
    `model.optimize().status` before believing the number.

## 4. Anaerobic growth, and why a condition is more than bounds

Switching yeast-GEM to anaerobic conditions is not just "close the oxygen
exchange": the model also has to gain sterol and fatty-acid uptake, and its
biomass composition changes. That is a *condition* — several coordinated edits
that belong together — and both toolboxes read one from a YAML file, so it can be
reviewed as data rather than buried in a script.

=== "MATLAB"

    ```matlab
    model = applyCondition(model, 'anaerobic.yml');
    sol = solveLP(model);
    fprintf('anaerobic growth: %.4f /h\n', -sol.f);
    ```

=== "Python"

    ```python
    from pathlib import Path

    from raven_toolbox.conditions import apply_condition, load_condition

    Path("anaerobic.yml").write_text(
        """
        bounds:
          - { rxn: r_1992, lb: 0, ub: 0 }
          - { rxn: r_1714, lb: -20 }
        """.replace("        ", ""),
        encoding="utf-8",
    )

    condition = load_condition("anaerobic.yml")
    print("condition:", condition)

    apply_condition(model, condition)
    print(f"anaerobic growth: {model.slim_optimize():.4f} /h")

    model.medium = shipped        # put the aerobic medium back
    ```

    ```text title="Output"
    condition: {'bounds': [{'rxn': 'r_1992', 'lb': 0, 'ub': 0}, {'rxn': 'r_1714', 'lb': -20}]}
    anaerobic growth: -0.0000 /h
    ```

    The schema is deliberately narrow — a `prelude` that resets the exchanges, an
    optional cofactor-pseudoreaction edit, an optional biomass-stoichiometry
    delta, a list of per-reaction `bounds`, and an `expected_uptake_count` that
    fails loudly when the condition no longer matches the model. `apply_condition`
    edits the model in place and returns it, so it composes.

    The growth rate is zero, and that is the point: yeast-GEM does not ferment
    just because oxygen is gone. A real anaerobic condition also opens sterol and
    fatty-acid uptake and adjusts the biomass composition — take the maintained one
    from the yeast-GEM repository rather than writing your own from memory. The
    last line restores the aerobic medium, since `apply_condition` edits in place.

## 5. What is the model actually living on?

A medium copied from a paper usually contains more than the model needs.
`getMinimalMedium` and cobrapy's `minimal_medium` search for the smallest set of
uptakes that still supports a given growth rate — useful to find out which
component is doing the work, and to catch a nutrient the model can quietly do
without because a gap-filled reaction produces it internally.

=== "MATLAB"

    ```matlab
    [medium, fluxes] = getMinimalMedium(model);
    ```

=== "Python"

    ```python
    from cobra.medium import minimal_medium

    minimal = minimal_medium(model, model.slim_optimize() * 0.9)
    print(minimal.round(3).to_string())
    ```

    ```text title="Output"
    r_1654    0.480
    r_1714    0.904
    r_1861    0.000
    r_1992    2.145
    r_2005    0.020
    r_2020    0.000
    r_2049    0.000
    r_2060    0.010
    r_4593    0.000
    r_4594    0.000
    r_4595    0.000
    r_4596    0.000
    r_4597    0.000
    r_4600    0.000
    ```

!!! warning "What can go wrong"
    - **`infeasible` right after setting a medium.** Something essential is
      closed. Reopen the medium one component at a time, or start from
      `minimal_medium` on the working model and compare.
    - **The sign convention bites.** Uptake is a *negative* flux, but
      `model.medium` takes *positive* numbers. Both are right; mixing them is not.
    - **The model grows without a carbon source.** Usually a leak: some reaction
      produces carbon from nothing. [Quality control](../guide/index.md) is where
      that gets diagnosed, with `checkProduction` / `analyse_topology`.
    - **Results that cannot be reproduced.** If a medium lives in a script, the
      next person runs a different one. A condition file is data, and it diffs.

## See also

- [Simulating growth with FBA](fba.md) — the solve this page feeds.
- [Reading and writing models](io.md) — keeping a model and its conditions in a
  repository.
- [MATLAB vs Python](../differences.md) — the full function mapping.
