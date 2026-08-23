# 5. Growth media and conditions

An FBA result is a statement about a medium. This page is about setting that
medium deliberately: which exchange reactions are open, how wide, and how to keep
a condition as reviewable data instead of a paragraph of bound-setting code.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `getExchangeRxns` | `Model.exchanges` <span class="cobrapy-tag">cobrapy</span> | find the exchange reactions |
| `setExchangeBounds` | `Model.medium` <span class="cobrapy-tag">cobrapy</span> | set a whole medium, closing the rest |
| `setParam` | `set_reaction_bounds` | set one reaction's bounds |
| `getMinimalMedium` | `minimal_medium` <span class="cobrapy-tag">cobrapy</span> | the smallest medium that still supports growth |
| `applyCondition` | `apply_condition`, `load_condition` | apply a condition file |

## Setup

`yeast-GEM.xml` from [`docs/data/`](../data/README.md), which ships with an
aerobic minimal glucose medium already applied.

## 5.1 What is currently open

An exchange reaction connects a boundary metabolite to nothing, so its flux is
the rate at which that metabolite enters (negative) or leaves (positive) the
system. The medium is exactly the set of exchanges with a negative lower bound.

=== "MATLAB"

    ```matlab
    model = importModel('yeast-GEM.xml');
    [exchangeRxns, exchangeIdx] = getExchangeRxns(model);
    fprintf('%d exchange reactions\n', numel(exchangeRxns));

    open = sort(exchangeIdx(model.lb(exchangeIdx) < 0));
    for i = 1:numel(open)
        fprintf('  %s  %-28s %8.1f\n', model.rxns{open(i)}, ...
            model.rxnNames{open(i)}, -model.lb(open(i)));
    end
    ```

    ```text title="Output"
    [Warning: The following fields have prefixes removed from all entries. If this is undesired, run importModel with removePrefix as false. Example: importModel('filename.xml',[],false);]
    273 exchange reactions
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

!!! note "270 or 273?"
    The two toolboxes count exchange reactions differently, and both are right.
    cobrapy sorts single-metabolite reactions into `exchanges`, `demands` and
    `sinks`; `getExchangeRxns` returns all of them together. In yeast-GEM the
    difference is three reactions — `r_2111` (growth) and the sinks `r_4062` and
    `r_4064` — so MATLAB reports 273 where `model.exchanges` reports 270.

## 5.2 Change one nutrient

=== "MATLAB"

    ```matlab
    model = setParam(model, 'lb', 'r_1714', -10);   % D-glucose exchange
    sol = solveLP(model);
    idx = getIndexes(model, 'r_1714', 'rxns');
    fprintf('[%g %g] -> %.4f /h\n', model.lb(idx), model.ub(idx), -sol.f);
    ```

    ```text title="Output"
    [-10 1000] -> -0.8370 /h
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

## 5.3 Define a whole medium

Assigning to the medium is **not** a patch: everything not in the dict is closed.
That makes it the right tool for "this exact recipe and nothing else", and a trap
if you meant "the shipped medium, but with more glucose".

=== "MATLAB"

    ```matlab
    % every uptake closed
    [~, exchIdx] = getExchangeRxns(model);
    modelClosed = setParam(model, 'lb', model.rxns(exchIdx), 0);
    sol = solveLP(modelClosed);
    fprintf('growth with nothing to eat: %.4f /h\n', -sol.f);

    % the shipped recipe, with more glucose
    model = setParam(model, 'lb', 'r_1714', -10);
    sol = solveLP(model);
    fprintf('complete medium:           %.4f /h\n', -sol.f);
    ```

    ```text title="Output"
    growth with nothing to eat:  /h
    complete medium:           -0.8370 /h
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

## 5.4 Anaerobic growth, and why a condition is more than bounds

Switching yeast-GEM to anaerobic conditions is not just "close the oxygen
exchange". Without oxygen the model cannot make sterols or unsaturated fatty
acids, so those have to be supplied; heme a leaves the cofactor pseudoreaction;
the biomass gains an FADH2 term; and two reactions that are repressed on glucose
are blocked. Those edits belong together, so both toolboxes read them from one
YAML file — a *condition* — which can be reviewed as data rather than buried in a
script.

[`anaerobic.yml`](../data/anaerobic.yml) is that file, transcribed from
yeast-GEM's own `anaerobicModel.m`:

```yaml title="anaerobic.yml (abridged)"
cofactor_pseudoreaction:
  rxn_id: r_4598
  remove_mets:
    - { met: s_3714 }        # heme a
  charge_balance_met: s_0794 # H+

biomass_stoichiometry_delta:
  rxn_id: r_4041             # biomass pseudoreaction
  add:
    - { met: s_0689, coef:  0.08 }   # FADH2
    - { met: s_0687, coef: -0.08 }   # FAD
    - { met: s_0794, coef: -0.16 }   # H+

bounds:
  - { rxn: r_1992, lb: 0 }         # no oxygen
  - { rxn: r_1757, lb: -1000 }     # ergosterol, supplied
  - { rxn: r_2189, lb: -1000 }     # oleate, supplied
  - { rxn: r_1967, lb: -1000 }     # nicotinate
  - { rxn: r_0714, lb: 0, ub: 0 }  # MDH2, repressed on glucose
```

The schema is narrow on purpose: an optional `prelude` that resets the exchanges,
an optional cofactor-pseudoreaction edit, an optional biomass-stoichiometry
delta, a list of per-reaction `bounds`, and an `expected_uptake_count` that fails
loudly when the condition no longer matches the model.

=== "MATLAB"

    <!-- run-examples: skip -->

    ```matlab
    modelAnaerobic = applyCondition(model, 'anaerobic.yml');
    sol = solveLP(modelAnaerobic);
    fprintf('anaerobic growth: %.4f /h\n', -sol.f);
    ```

    `applyCondition` reads the file with `parseYAML`, which goes through
    MATLAB's Python bridge — so it needs a linked CPython with `pyyaml`
    installed (`pyenv` in MATLAB shows which interpreter is linked). That is
    also why this block carries no output here: the documentation build has
    no linked interpreter.

=== "Python"

    ```python
    from raven_toolbox.conditions import apply_condition, load_condition

    condition = load_condition("anaerobic.yml")
    print("bounds changed:", len(condition["bounds"]))

    anaerobic = apply_condition(model.copy(), condition)
    print(f"anaerobic growth: {anaerobic.slim_optimize():.4f} /h")
    ```

    ```text title="Output"
    bounds changed: 12
    anaerobic growth: 0.1615 /h
    ```

    `apply_condition` edits the model **in place** and returns it, so pass a copy
    when you want to keep the aerobic model as well. It also takes the path
    directly: `apply_condition(model, "anaerobic.yml")`.

## 5.5 What is the model actually living on?

A medium copied from a paper usually contains more than the model needs.
`getMinimalMedium` and cobrapy's `minimal_medium` search for the smallest set of
uptakes that still supports a given growth rate — useful to find out which
component is doing the work, and to catch a nutrient the model can quietly do
without because a gap-filled reaction produces it internally.

=== "MATLAB"

    <!-- run-examples: skip -->

    ```matlab
    sol = solveLP(model);
    medium = getMinimalMedium(model, 'minGrowth', 0.9 * -sol.f);
    ```

    `getMinimalMedium` solves a **MILP**, which the GLPK that ships with
    RAVEN cannot do — it reports `glpk is not suitable for solving MILPs`.
    Point `setRavenSolver` at Gurobi or SCIP first. cobrapy's
    `minimal_medium` defaults to an LP relaxation, which is why the Python
    tab runs on any solver.

=== "Python"

    ```python
    from cobra.medium import minimal_medium

    minimal = minimal_medium(model, model.slim_optimize() * 0.9)
    print(minimal.round(3).to_string())
    ```

    ```text title="Output"
    r_1654     4.959
    r_1714     9.004
    r_1861     0.000
    r_1992    20.139
    r_2005     0.210
    r_2020     0.003
    r_2049     0.003
    r_2060     0.105
    r_4593     0.001
    r_4594     0.000
    r_4595     0.002
    r_4596     0.001
    r_4597     0.001
    r_4600     0.000
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
