# Simulating growth with FBA

Set an objective, constrain the uptake rates, solve, and read the fluxes back.
This is the loop every other analysis on this site is built from.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `setParam` | `Reaction.bounds`, `Model.objective` <span class="cobrapy-tag">cobrapy</span> | set bounds and the objective |
| `solveLP` | `Model.optimize` <span class="cobrapy-tag">cobrapy</span> | solve the LP |
| `printFluxes` | `Model.summary` <span class="cobrapy-tag">cobrapy</span> | show the interesting fluxes |
| `getMinNrFluxes` | `pfba` <span class="cobrapy-tag">cobrapy</span> | pick a parsimonious solution among the optima |
| `haveFlux` | `Solution.fluxes` <span class="cobrapy-tag">cobrapy</span> | which reactions can carry flux |

!!! info "Simulation is cobrapy's job"
    Almost every Python step here is cobrapy: raven-toolbox deliberately does not
    re-implement FBA, and adds reconstruction and curation on top of it instead.
    In MATLAB, RAVEN's `solveLP` is self-contained and needs neither COBRA
    Toolbox nor cobrapy. The concepts are identical; only the spelling differs.

## Setup

`yeast-GEM.xml` from [`docs/data/`](../data/README.md) — yeast-GEM v9.1.0, which
arrives with a growth objective and an aerobic glucose medium already set.

## 1. Solve

=== "MATLAB"

    ```matlab
    model = importModel('yeast-GEM.xml');
    sol = solveLP(model);
    fprintf('growth: %.4f /h\n', -sol.f);
    ```

    `solveLP` **minimises**, so the objective value of a maximisation comes back
    negated — hence the minus sign. `sol.x` holds the flux vector, in the order of
    `model.rxns`.

=== "Python"

    ```python
    from cobra.io import read_sbml_model

    model = read_sbml_model("yeast-GEM.xml")
    solution = model.optimize()

    print(f"objective: {model.objective.expression}")
    print(f"status:    {solution.status}")
    print(f"growth:    {solution.objective_value:.4f} /h")
    ```

    ```text title="Output"
    objective: 1.0*r_2111 - 1.0*r_2111_reverse_58b69
    status:    optimal
    growth:    0.0809 /h
    ```

    `optimize` maximises by default and returns a `Solution` whose `fluxes` is a
    pandas Series indexed by reaction id.

## 2. Change the objective

The objective is a reaction to maximise — growth, a product exchange, an ATP
demand.

=== "MATLAB"

    ```matlab
    model = setParam(model, 'obj', 'r_2111', 1);   % growth
    ```

=== "Python"

    ```python
    model.objective = "r_2111"
    print(model.reactions.get_by_id("r_2111").name)
    ```

    ```text title="Output"
    growth
    ```

## 3. Constrain an uptake rate

Uptake is a **negative** flux through an exchange reaction, so the lower bound is
what limits it. yeast-GEM ships with glucose already capped at 1 mmol/gDW/h,
which is where the growth rate above comes from; ten times the glucose should buy
roughly ten times the growth.

=== "MATLAB"

    ```matlab
    model = setParam(model, 'lb', 'r_1714', -10);   % D-glucose exchange
    sol = solveLP(model);
    fprintf('growth on 10 mmol glucose: %.4f /h\n', -sol.f);
    ```

=== "Python"

    ```python
    glucose = model.reactions.get_by_id("r_1714")
    print("shipped bounds:", glucose.bounds)

    glucose.lower_bound = -10.0
    faster = model.optimize()
    print(f"growth on 10 mmol glucose: {faster.objective_value:.4f} /h")

    glucose.lower_bound = -1.0   # back to the shipped medium
    ```

    ```text title="Output"
    shipped bounds: (-1.0, 1000.0)
    growth on 10 mmol glucose: 0.8370 /h
    ```

## 4. Try something without keeping it

A knockout or a tighter bound is usually a question, not a decision. cobrapy's
model is a context manager: changes made inside `with model:` are rolled back on
the way out. MATLAB has no equivalent — copy the struct, change the copy, and let
it go out of scope.

=== "MATLAB"

    ```matlab
    modelKO = setParam(model, 'eq', 'r_1992', 0);   % close oxygen uptake
    solKO = solveLP(modelKO);
    fprintf('anaerobic: %.4f /h\n', -solKO.f);
    % `model` itself is untouched -- MATLAB copied it on assignment
    ```

=== "Python"

    ```python
    with model:
        model.reactions.get_by_id("r_1992").bounds = (0, 0)   # oxygen exchange
        print(f"anaerobic: {model.optimize().objective_value:.4f} /h")

    print(f"back to aerobic: {model.optimize().objective_value:.4f} /h")
    ```

    ```text title="Output"
    anaerobic: -0.0000 /h
    back to aerobic: 0.0809 /h
    ```

    Without `with`, the bound change would persist and every later result on this
    page would silently be an anaerobic one.

    Two things in that output are worth reading carefully. The anaerobic growth
    rate is **zero**, not a smaller positive number: closing the oxygen exchange is
    not enough to make yeast-GEM grow fermentatively — it also needs sterol and
    fatty-acid uptake and a different biomass composition, which is what a
    *condition* does. See [Growth media and conditions](media.md). And the minus
    sign on that zero is solver noise, not a negative growth rate; compare against
    a tolerance rather than to `0`.

## 5. Look at the fluxes

An FBA solution has thousands of numbers, most of them zero and most of the rest
uninteresting. Both toolboxes offer a filtered view.

=== "MATLAB"

    ```matlab
    printFluxes(model, sol.x, true);    % true = only exchange reactions
    ```

=== "Python"

    ```python
    solution = model.optimize()
    exchanges = {
        "r_1714": "glucose",
        "r_1992": "oxygen",
        "r_1672": "CO2",
        "r_1761": "ethanol",
    }
    for rxn_id, label in exchanges.items():
        print(f"{label:>8}: {solution.fluxes[rxn_id]:9.4f}")
    ```

    ```text title="Output"
     glucose:   -1.0000
      oxygen:   -2.3592
         CO2:    2.6597
     ethanol:    0.0000
    ```

    `model.summary()` prints the same picture — uptake, secretion and the
    objective — as a table, and `solution.fluxes` is a pandas Series, so the usual
    filtering works: `solution.fluxes[solution.fluxes.abs() > 1e-6]`.

## 6. Pick a parsimonious solution

An FBA optimum is rarely unique: many flux distributions reach the same growth
rate, and a plain solve returns an arbitrary one, often with pointless internal
loops. Parsimonious FBA keeps the objective at its optimum and then minimises the
total flux, which is both more biological and reproducible.

=== "MATLAB"

    ```matlab
    [~, sol] = getMinNrFluxes(model);
    ```

=== "Python"

    ```python
    from cobra.flux_analysis import pfba

    parsimonious = pfba(model)
    print(f"growth:     {parsimonious.fluxes['r_2111']:.4f} /h")
    print(f"total flux: {parsimonious.fluxes.abs().sum():.1f}")
    ```

    ```text title="Output"
    growth:     0.0809 /h
    total flux: 100.6
    ```

    The growth rate is unchanged and the total flux is now the smallest that
    achieves it. The *number* of active reactions still varies between solves —
    pFBA pins the total flux, not which reactions carry it — so do not build a
    test on that count.

!!! warning "What can go wrong"
    - **The status is `infeasible`.** Something is over-constrained — most often
      an uptake that is closed, or a bound set to the wrong sign. See
      [Growth media and conditions](media.md).
    - **Growth is zero but the solve succeeded.** The model is feasible and the
      optimum really is zero: a nutrient is missing, or a gap blocks the biomass
      pseudoreaction.
    - **The same model gives different flux distributions.** Expected — alternative
      optima. Use pFBA, or compare ranges with FVA, rather than one solution.
    - **`solveLP` returns a positive `f` for a maximisation.** It minimises
      internally; negate it, as above.

## See also

- [Getting started](getting-started.md) — loading and inspecting a model.
- [Growth media and conditions](media.md) — what the exchange bounds mean and how
  to define a medium.
- [MATLAB vs Python](../differences.md) — the full function mapping.
