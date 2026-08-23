# 6. Solvers and configuration

Every simulation on this site ends in a linear program, and something has to
solve it. This page is about which solver that is, how to change it, and how to
read what it gives back.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `setRavenSolver` | `Configuration` <span class="cobrapy-tag">cobrapy</span> | choose the solver |
| `checkInstallation` | `Configuration` <span class="cobrapy-tag">cobrapy</span> | check the solver works |
| `solveLP` | `Model.optimize` <span class="cobrapy-tag">cobrapy</span> | solve, and get a solution object |
| `optimizeProb` | `Model.solver` <span class="cobrapy-tag">cobrapy</span> | solve a problem the toolbox built for you |

## Setup

`smallYeast.yml` from [`docs/data/`](../data/README.md), with glucose and oxygen
opened so there is something to solve.

=== "MATLAB"

    ```matlab
    model = readYAMLmodel('smallYeast.yml');
    model = setParam(model, 'lb', {'glcIN', 'o2IN'}, [-1 -1000]);
    ```

=== "Python"

    ```python
    from raven_toolbox.io import read_yaml_model

    model = read_yaml_model("smallYeast.yml")
    model.reactions.get_by_id("glcIN").lower_bound = -1.0
    model.reactions.get_by_id("o2IN").lower_bound = -1000.0
    ```

## 6.1 Which solver is in use

=== "MATLAB"

    ```matlab
    fprintf('RAVEN solver preference: %s\n', getpref('RAVEN', 'solver'));
    ```

    ```text title="Output"
    RAVEN solver preference: ...
    ```

    RAVEN keeps the choice in MATLAB's preferences, so it survives restarts —
    and the answer is whatever *this* installation was last told, which is why
    the output above is elided. `checkInstallation` prints it along with a test
    solve.

=== "Python"

    ```python
    from cobra import Configuration

    print("default:", Configuration().solver.__name__)
    print("this model:", model.solver.__class__.__module__)
    ```

    ```text title="Output"
    default: optlang.glpk_interface
    this model: optlang.glpk_interface
    ```

    cobrapy has two levels: `Configuration()` is the default applied to models
    created from then on, and `model.solver` is the interface this model is
    actually using.

## 6.2 Change it

Both toolboxes ship with **GLPK**, which is enough for every LP on this site.
Gurobi is worth having for large models and for the mixed-integer problems that
gap-filling and `getMinimalMedium` solve; it is free for academic use.

=== "MATLAB"

    ```matlab
    setRavenSolver('glpk');     % 'gurobi', or 'cobra' to hand over to the COBRA Toolbox
    ```

=== "Python"

    ```python
    model.solver = "glpk"       # or "gurobi", "cplex", "osqp", ...

    from cobra import Configuration
    Configuration().solver = "glpk"     # the default for models loaded later
    ```

    Assigning to `model.solver` rebuilds this model's problem; assigning to
    `Configuration().solver` changes the default for models created afterwards
    and leaves existing ones alone.

## 6.3 What comes back

The two solution objects carry the same information under different names.

| MATLAB `solveLP` | cobrapy `Solution` | |
|---|---|---|
| `sol.f` | `solution.objective_value` | objective value, same sign in both |
| `sol.x` | `solution.fluxes` | fluxes — a vector in `model.rxns` order, or a Series by id |
| `sol.stat` | `solution.status` | `1` optimal, `0` feasible, `-1` infeasible |
| `sol.msg` | `solution.status` | what the solver said |
| `sol.sPrice`, `sol.rCost` | `solution.shadow_prices`, `solution.reduced_costs` | duals |

=== "MATLAB"

    ```matlab
    model = setParam(model, 'obj', 'biomassOUT', 1);
    sol = solveLP(model);
    fprintf('stat %d: %s\n', sol.stat, sol.msg);
    fprintf('growth %.4f /h\n', sol.f);
    ```

    ```text title="Output"
    stat 1: Optimal solution found
    growth -0.0000 /h
    ```

=== "Python"

    ```python
    model.objective = "biomassOUT"
    solution = model.optimize()
    print(f"status {solution.status}")
    print(f"growth {solution.objective_value:.4f} /h")
    ```

    ```text title="Output"
    status optimal
    growth 0.0000 /h
    ```

## 6.4 When the solve fails

An infeasible problem is the most common outcome of a bad edit, and the two
toolboxes report it differently: RAVEN sets `sol.stat` to `-1` and returns an
empty flux vector, while cobrapy raises nothing at all — `optimize` returns a
solution with status `infeasible`, and `slim_optimize` returns `nan`.

=== "MATLAB"

    ```matlab
    broken = setParam(model, 'lb', 'biomassOUT', 1);   % demand growth with no glucose
    broken = setParam(broken, 'eq', 'glcIN', 0);
    sol = solveLP(broken);
    fprintf('stat %d: %s\n', sol.stat, sol.msg);
    ```

    ```text title="Output"
    stat -1: The problem is infeasible
    ```

=== "Python"

    ```python
    with model:
        model.reactions.get_by_id("biomassOUT").lower_bound = 1.0
        model.reactions.get_by_id("glcIN").bounds = (0, 0)
        print("status:", model.optimize().status)
        print("slim_optimize:", model.slim_optimize())
    ```

    ```text title="Output"
    status: infeasible
    slim_optimize: nan
    ```

    Check the status before you use a number. `slim_optimize` skips building a
    full solution, so it is the fast option inside a loop — at the cost of
    returning `nan` instead of telling you why.

!!! warning "What can go wrong"
    - **A solver that is set but not installed.** `setRavenSolver('gurobi')`
      stores the preference whether or not Gurobi is there; the failure appears
      at the next solve. `checkInstallation` tests it directly.
    - **MILP with GLPK.** GLPK solves LPs only, in RAVEN. Anything mixed-integer
      — `getMinimalMedium`, some gap-filling — needs Gurobi.
    - **Tiny differences between solvers.** Alternative optima mean two solvers
      can return different flux distributions for the same objective value. Pin
      one solver for anything you intend to compare.

## See also

- [4. Simulating growth with FBA](fba.md) — the solve itself.
- [5. Growth media and conditions](media.md) — the constraints that decide
  whether a problem is feasible at all.
- [Installation](../installation/index.md) — installing and testing a solver.
