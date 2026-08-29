# 16. Combining and simplifying models

Two operations that look like bookkeeping and are not. **Merging** puts models
together — a draft and a template, two organisms, a curated core and an
extension — and the result is only as sound as the assumption that a metabolite
in one model is the same molecule as in the other. **Simplifying** takes a model
apart again, dropping what cannot carry flux, and the risk is deleting something
you needed.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `mergeModels` | `merge_models` | combine models into one |
| `contractModel` | `remove_duplicate_reactions` | collapse identical reactions |
| `simplifyModel` | `simplify_model` | drop what cannot carry flux |
| `expandModel` | `expand_model` | split reactions with `or` in the GPR |
| `mergeCompartments` | `merge_compartments` | collapse the model to one compartment |

## Setup

`smallYeast.yml`, and a second model to merge it with. Taking a copy and giving
it a new id keeps the example honest: whatever the merge does to two identical
models is the clearest possible statement of what it matches on.

=== "MATLAB"

    ```matlab
    model = readYAMLmodel('smallYeast.yml');
    second = model;
    second.id = 'second';
    fprintf('%d rxns, %d mets, %d genes\n', ...
        numel(model.rxns), numel(model.mets), numel(model.genes));
    ```

    ```text title="Output"
    53 rxns, 52 mets, 61 genes
    ```

=== "Python"

    ```python
    import cobra
    from raven_toolbox.io import read_yaml_model

    cobra.Configuration().processes = 1

    model = read_yaml_model("smallYeast.yml")
    second = model.copy()
    second.id = "second"
    print(f"{len(model.reactions)} rxns, {len(model.metabolites)} mets, "
          f"{len(model.genes)} genes")
    ```

    ```text title="Output"
    53 rxns, 52 mets, 61 genes
    ```

## 16.1 Merging

=== "MATLAB"

    ```matlab
    merged = mergeModels({model, second});
    fprintf('merged: %d rxns, %d mets, %d genes\n', ...
        numel(merged.rxns), numel(merged.mets), numel(merged.genes));
    ```

    ```text title="Output"
    merged: 106 rxns, 52 mets, 61 genes
    ```

=== "Python"

    ```python
    from raven_toolbox.manipulation import merge_models

    merged = merge_models([model, second])
    print(f"merged: {len(merged.reactions)} rxns, "
          f"{len(merged.metabolites)} mets, {len(merged.genes)} genes")
    ```

    ```text title="Output"
    merged: 106 rxns, 52 mets, 61 genes
    ```

Read those numbers carefully. The reactions **doubled** and the metabolites did
**not**: two models that describe the same 52 metabolites end up sharing them,
while every reaction is carried over from both sources and kept.

That asymmetry is the whole behaviour. Metabolites are matched on
**name and compartment** — `metaboliteName[comp]`, not the identifier — and
genes on name, so anything the two models call by the same name becomes one
entity. Reactions are added without any check at all.

!!! warning "Names, not identifiers"
    Two models built from different databases usually share almost no metabolite
    **names** either, in which case merging produces a model with two disconnected
    halves that happen to live in the same struct. Merging is a claim that the
    naming is consistent; check it before you make it, not after.

## 16.2 Merging does not de-duplicate

Every reaction from both models survived, so the merged model now describes each
conversion twice. Collapsing those is a separate step.

=== "MATLAB"

    ```matlab
    contracted = contractModel(merged);
    fprintf('after contracting: %d rxns\n', numel(contracted.rxns));
    ```

    ```text title="Output"
    after contracting: 53 rxns
    ```

=== "Python"

    ```python
    from raven_toolbox.manipulation import remove_duplicate_reactions

    remove_duplicate_reactions(merged)
    print(f"after contracting: {len(merged.reactions)} rxns")
    ```

    ```text title="Output"
    after contracting: 53 rxns
    ```

!!! warning "Which functions mutate"
    Every RAVEN function here returns a new model struct and leaves its input
    alone. The Python side is not uniform, so it is worth knowing which is which:

    | Python | |
    |---|---|
    | `remove_duplicate_reactions`, `simplify_model` | change the model **in place**, return `None` |
    | `merge_models`, `merge_compartments` | return a **new** model |

    `model = simplify_model(model)` is correct MATLAB and sets `model` to `None`
    in Python. Copy first if you want to keep the original.

## 16.3 Dropping what cannot carry flux

`smallYeast` ships with its medium shut, so almost nothing in it can carry flux
at all — the state [9. Quality control](quality-control.md) measures. That makes
it a good subject for simplification, and a good warning about it.

=== "MATLAB"

    ```matlab
    shut = readYAMLmodel('smallYeast.yml');
    fprintf('%d of %d reactions can carry flux\n', ...
        sum(haveFlux(shut)), numel(shut.rxns));
    reduced = simplifyModel(shut, 'deleteMinMax', true);
    fprintf('simplified: %d rxns, %d mets\n', numel(reduced.rxns), numel(reduced.mets));
    ```

    ```text title="Output"
    2 of 53 reactions can carry flux
    simplified: 2 rxns, 4 mets
    ```

=== "Python"

    ```python
    from raven_toolbox.manipulation import simplify_model

    shut = read_yaml_model("smallYeast.yml")
    reduced = shut.copy()
    simplify_model(reduced, delete_no_flux=True, open_exchanges=False)
    print(f"simplified: {len(reduced.reactions)} rxns, "
          f"{len(reduced.metabolites)} mets")
    ```

    ```text title="Output"
    simplified: 2 rxns, 4 mets
    ```

A model that has been simplified against a shut medium is a model of that
medium, not of the organism. Open the conditions you intend to simulate
**before** simplifying, or you will delete the pathways you were about to study —
see [5. Growth media and conditions](media.md).

## 16.4 Collapsing compartments

Sometimes the compartments are the problem: a draft with unreliable
localisation, or a comparison against a model that has none.

=== "MATLAB"

    ```matlab
    [flat, deletedRxns] = mergeCompartments(model);
    fprintf('%d compartments -> %d, %d -> %d mets, %d -> %d rxns\n', ...
        numel(model.comps), numel(flat.comps), ...
        numel(model.mets), numel(flat.mets), numel(model.rxns), numel(flat.rxns));
    fprintf('%d transport reactions dropped\n', numel(deletedRxns));
    ```

    ```text title="Output"
    2 compartments -> 1, 52 -> 45 mets, 53 -> 50 rxns
    0 transport reactions dropped
    ```

=== "Python"

    ```python
    from raven_toolbox.manipulation import merge_compartments

    flat, dropped, _ = merge_compartments(model)
    print(f"{len(model.compartments)} compartments -> {len(flat.compartments)}, "
          f"{len(model.metabolites)} -> {len(flat.metabolites)} mets, "
          f"{len(model.reactions)} -> {len(flat.reactions)} rxns")
    print(f"{len(dropped)} transport reactions dropped")
    ```

    ```text title="Output"
    2 compartments -> 1, 52 -> 45 mets, 53 -> 50 rxns
    3 transport reactions dropped
    ```

Seven metabolites in this model exist in both compartments, so 52 collapse to
45; the three reactions that merely moved something across the mitochondrial
membrane become `A -> A`, carry no information, and are dropped.

!!! note "The two count the removals differently"
    Both toolboxes end at 50 reactions, but the second line disagrees: RAVEN
    reports **0** dropped where raven-toolbox reports **3** (`CAT2`, `CO2TRANS`,
    `ShuttleX`). The same three reactions go in both cases. RAVEN clears them
    when it removes reactions the merge left empty, and its `deletedRxns` counts
    only what the `deleteRxnsWithOneMet` path deleted — which is nothing, since
    that flag is `false` by default.

    A reaction left holding a single metabolite after merging carries no
    information and should go; an **exchange** had a single metabolite all along
    (`=> glucose`) and must be kept. raven-toolbox used to delete those too,
    along with the objective, taking this model from growth `0.1222` to `0.0000`
    with no error and no warning. Fixed in
    [raven-toolbox#96](https://github.com/SysBioChalmers/raven-toolbox/pull/96);
    if a flattened model comes back with no boundary reactions, update
    raven-toolbox.

That is a real loss. A model that distinguishes mitochondrial from cytosolic
acetyl-CoA cannot be recovered from the flattened one, and the flattened model
will happily let a pathway run on a pool that no membrane separates any more.
Flatten a copy, for a specific question, and keep the original.

!!! warning "What can go wrong"
    - **Merging on inconsistent names.** The match is on name and compartment.
      Different naming conventions give you two disconnected networks in one
      model, and nothing warns you loudly.
    - **Expecting de-duplication.** Merging keeps every reaction from every
      source. Contract afterwards, and check what got collapsed.
    - **Simplifying against the wrong condition.** Reactions are removed because
      they cannot carry flux *under the current bounds*. Change the medium first.
    - **In place or a copy.** The Python functions mutate; the MATLAB ones
      return. Mixing the conventions up loses either your original or your
      result.
    - **`deleteUnconstrained` has no Python counterpart.** RAVEN models mark
      boundary metabolites with an `unconstrained` field; cobra models use
      explicit boundary reactions instead, so that flag has nothing to act on.

## See also

- [9. Quality control](quality-control.md) — deciding what *should* be removed.
- [13. Gap-filling](gap-filling.md) — the opposite operation, and the usual
  reason for having a template model to merge from.
- [10. Context-specific models](init.md) — cutting a model down by evidence
  rather than by connectivity.
