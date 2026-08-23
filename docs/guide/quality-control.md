# 9. Quality control

A model that loads and solves can still be wrong. This page runs the checks worth
running before you trust a result: is the structure sound, do the reactions
balance, is anything disconnected, and can the model make something out of
nothing.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `checkModelStruct` | `check_model` | structural problems |
| `getElementalBalance` | `get_elemental_balance` | mass balance, reaction by reaction |
| `haveFlux` | `find_blocked_reactions` <span class="cobrapy-tag">cobrapy</span> | reactions that can never carry flux |
| `canProduce` | `analyse_topology` | which metabolites the model can make, given its medium |
| `makeSomething`, `findLeakMetabolite` | `Model.optimize` on a demand <span class="cobrapy-tag">cobrapy</span> | can the model make something from **nothing** |
| `gapReport` | `check_model` + `analyse_topology` | one summary of the gaps |

## Setup

`smallYeastBad.yml` is the same small yeast model as elsewhere in this guide,
with deliberate errors left in — exactly what these checks are for.

=== "MATLAB"

    ```matlab
    model = readYAMLmodel('smallYeastBad.yml');
    good = readYAMLmodel('smallYeast.yml');
    fprintf('%d reactions, %d metabolites\n', numel(model.rxns), numel(model.mets));
    ```

    ```text title="Output"
    54 reactions, 52 metabolites
    ```

=== "Python"

    ```python
    from raven_toolbox.io import read_yaml_model

    model = read_yaml_model("smallYeastBad.yml")
    good = read_yaml_model("smallYeast.yml")
    print(len(model.reactions), "reactions,", len(model.metabolites), "metabolites")
    ```

    ```text title="Output"
    54 reactions, 52 metabolites
    ```

## 9.1 Is the structure sound?

The first pass is about the model as a data structure: metabolites no reaction
uses, reactions with no metabolites, genes nothing refers to, a missing
objective.

=== "MATLAB"

    ```matlab
    issues = checkModelStruct(model, 'throwErrors', false);
    fprintf('%d issue(s)\n', numel(issues));
    ```

    ```text title="Output"
    2 issue(s)
    ```

=== "Python"

    ```python
    from raven_toolbox.utils import check_model

    issues = check_model(model)
    print(len(issues), "issue(s)")
    for issue in issues[:5]:
        print(f"  {issue.category}: {issue.message}")
    ```

    ```text title="Output"
    1 issue(s)
      objective: No reaction has a nonzero objective coefficient.
    ```

## 9.2 Do the reactions balance?

An unbalanced reaction can create matter, and one that creates ATP or a redox
carrier will quietly inflate every prediction the model makes.

=== "MATLAB"

    ```matlab
    balance = getElementalBalance(model);
    fprintf('balanced %d, unbalanced %d, undecidable %d\n', ...
        sum(balance.balanceStatus == 1), ...
        sum(balance.balanceStatus == 0), ...
        sum(balance.balanceStatus < 0));
    ```

    ```text title="Output"
    balanced 28, unbalanced 24, undecidable 2
    ```

=== "Python"

    ```python
    from raven_toolbox.utils import get_elemental_balance

    balances = get_elemental_balance(model)
    counts = {"balanced": 0, "unbalanced": 0, "unknown": 0}
    for balance in balances:
        counts[balance.status] += 1
    print(counts)

    for balance in balances:
        if balance.status == "unbalanced":
            print(f"  {balance.reaction_id}: {balance.imbalance}")
    ```

    ```text title="Output"
    {'balanced': 28, 'unbalanced': 24, 'unknown': 2}
      acOUT: {'C': -2.0, 'H': -4.0, 'O': -2.0}
      co2OUT: {'C': -1.0, 'O': -2.0}
      ethOUT: {'C': -2.0, 'H': -6.0, 'O': -1.0}
      glyOUT: {'C': -3.0, 'H': -8.0, 'O': -3.0}
      glcIN: {'C': 6.0, 'H': 12.0, 'O': 6.0}
      o2IN: {'O': 2.0}
      PGI: {'H': 1.0, 'O': 3.0, 'P': 1.0}
      PFK: {'C': 6.0, 'H': 13.0, 'O': 9.0, 'P': 1.0}
      FBP: {'C': 6.0, 'H': 17.0, 'O': 16.0, 'P': 3.0}
      ENO: {'H': -2.0, 'O': -1.0}
      PGL: {'H': 2.0, 'O': 1.0}
      TAL1: {'H': 1.0, 'O': 3.0, 'P': 1.0}
      TKI1TKI2b: {'H': 1.0, 'O': 3.0, 'P': 1.0}
      GPP: {'H': 2.0, 'O': 1.0}
      PDC: {'C': -1.0, 'O': -2.0}
      ADH1: {'C': 2.0, 'H': 6.0, 'O': 1.0}
      ALD6: {'H': 2.0, 'O': 1.0}
      ACS: {'H': 2.0, 'O': 1.0}
      PYC: {'H': 2.0, 'O': 1.0}
      CIT: {'H': 2.0, 'O': 1.0}
      FUM1: {'H': 2.0, 'O': 1.0}
      NADHX: {'H': -8.8, 'O': -4.4}
      FADHX: {'H': -8.799999999999994, 'O': -4.4}
      ATPX: {'H': 2.0, 'O': 1.0}
    ```

    Exchange reactions read as unbalanced by design — they are where mass enters
    and leaves — so filter them out before judging the number.

## 9.3 What can never carry flux?

A reaction that cannot carry flux under any conditions is either a gap or a
mistake. This is the cheapest question that finds real problems.

=== "MATLAB"

    ```matlab
    canCarry = haveFlux(model);
    fprintf('%d of %d reactions can carry flux\n', sum(canCarry), numel(model.rxns));
    ```

    ```text title="Output"
    2 of 54 reactions can carry flux
    ```

=== "Python"

    ```python
    from cobra.flux_analysis import find_blocked_reactions

    blocked = find_blocked_reactions(model)
    print(f"{len(model.reactions) - len(blocked)} of {len(model.reactions)} "
          f"reactions can carry flux")
    print("blocked:", sorted(blocked)[:5])
    ```

    ```text title="Output"
    2 of 54 reactions can carry flux
    blocked: ['ACO', 'ACS', 'ADH1', 'ADH2', 'ALD6']
    ```

## 9.4 Can the model make something from nothing?

With every uptake closed, a correct model can produce nothing at all. If it still
makes a metabolite, some reaction is unbalanced or a loop is creating mass — the
most damaging class of error there is, because such a model will happily "grow"
without a carbon source.

=== "MATLAB"

    ```matlab
    exchangeRxns = getExchangeRxns(model);
    closed = setParam(model, 'eq', exchangeRxns, 0);

    produced = canProduce(closed);
    fprintf('%d of %d metabolites producible from nothing\n', ...
        sum(produced), numel(produced));

    [~, metabolite] = makeSomething(closed);
    fprintf('one leak: %s\n', strjoin(closed.mets(metabolite), ', '));
    ```

    ```text title="Output"
    33 of 52 metabolites producible from nothing
    one leak: F6P_c
    ```

    `canProduce` counts them; `makeSomething` — a wrapper for
    `findLeakMetabolite` — finds one, using as few reactions as possible, so you
    have somewhere to start.

=== "Python"

    ```python
    with model:
        for exchange in model.exchanges:
            exchange.bounds = (0, 0)

        # a demand for every metabolite, so by-products can leave: the same
        # assumption findLeakMetabolite makes with allowExcretion
        demands = {
            metabolite.id: model.add_boundary(metabolite, type="demand")
            for metabolite in list(model.metabolites)
        }

        leaks = []
        for met_id, demand in demands.items():
            model.objective = demand
            if (model.slim_optimize() or 0) > 1e-6:
                leaks.append(met_id)
        print(f"{len(leaks)} metabolite(s) producible from nothing: {sorted(leaks)[:5]}")
    ```

    ```text title="Output"
    33 metabolite(s) producible from nothing: ['ACA_c', 'AC_c', 'AKG_m', 'BIOMASS_c', 'CI_m']
    ```

    raven-toolbox has no single call for this: the loop is what it amounts to —
    close everything, let every metabolite leave, then maximise each one in turn
    and see whether anything comes out. That last assumption matters: without a
    way for by-products to leave, a leaking reaction is blocked by its own
    stoichiometry and the test finds nothing. `analyse_topology` answers the
    connectivity half of the same question without solving an LP.

!!! note "Give by-products a way out, or you will find nothing"
    Both RAVEN functions assume every metabolite can be excreted while the test
    runs — `canProduce` adds an output reaction for each metabolite it checks, and
    `findLeakMetabolite` takes `allowExcretion` as true by default. The Python
    loop has to do it explicitly, and the difference is not subtle: testing one
    demand reaction at a time, with no outlet for the by-products, reports **zero**
    leaks in this model instead of 33, because a leaking reaction is then blocked
    by its own stoichiometry.

## 9.5 Compare against a model you trust

When a check reports something, the fastest way to see whether it is new is to
compare against the last version that was good.

=== "MATLAB"

    ```matlab
    report = diffModels(good, model);
    fprintf('equal: %d, %d difference(s)\n', report.equal, numel(report.differences));
    fprintf('only in the good model: %d reactions\n', numel(report.rxnsOnlyInA));
    fprintf('only in this one:       %d reactions\n', numel(report.rxnsOnlyInB));
    ```

    ```text title="Output"
    equal: 0, 11 difference(s)
    only in the good model: 1 reactions
    only in this one:       2 reactions
    ```

=== "Python"

    ```python
    from raven_toolbox.comparison import diff_models

    difference = diff_models(good, model)
    print(difference)
    ```

    ```text title="Output"
    Models differ (11 differences):
      - reactions only in A (1): ['ethIN']
      - reactions only in B (2): ['ADH2', 'PDC_2']
      - ADH1: coef[ETH_c] A=1 B=2
      - ADH1: bounds A=(-1000.0, 1000.0) B=(0.0, 1000.0)
      - FBP: coef[F6P_c] A=1 B=2
      - PDC: stoichiometry has different mets
      - PFK: coef[F16P_c] A=1 B=2
      - biomassOUT: objective A=1.0 B=0.0
      - glcIN: bounds A=(0.0, 0.0) B=(0.0, 1000.0)
      - o2IN: bounds A=(0.0, 0.0) B=(0.0, 1000.0)
      - met F6P_c: formula A=C6H13O9P B=C6H14O12P2
    ```

!!! warning "What can go wrong"
    - **Judging a model by whether it solves.** An unbalanced reaction makes it
      solve *better*. Balance first, then believe the growth rate.
    - **Treating every unbalanced reaction as a bug.** Exchange, demand, sink and
      biomass pseudo-reactions are unbalanced on purpose.
    - **`unknown` instead of `unbalanced`.** A metabolite with no formula, or a
      polymer formula cobrapy cannot parse, makes the balance undecidable rather
      than wrong. Fill in the formula and check again.

## See also

- [8. Editing an existing model](editing.md) — fixing what these checks find.
- [2. Model structure and identifiers](model-structure.md) — what the structural
  checks are checking.
- [5. Growth media and conditions](media.md) — closing the medium, as in 9.4.
