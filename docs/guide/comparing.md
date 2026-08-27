# 17. Comparing models

You rarely have just one model. There is the draft and the curated version, the
model before and after gap-filling, yours and the one from the paper. Two
different questions follow: **what changed** — an exact, entry-by-entry diff —
and **how alike are these** — an overview across whole sets. The first is for
review and for CI; the second is for deciding whether two models are describing
the same organism at all.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `diffModels` | `diff_models` | every semantic difference between two models |
| `compareRxnsGenesMetsComps` | `compare_models` | overlap in reactions, metabolites, genes |
| `compareMultipleModels` | `compare_models` | the same, across many models |
| `compareFluxes` | — | which fluxes changed between two solutions |

## Setup

`smallYeast.yml` and `smallYeastBad.yml`: the same model, one of them carrying
deliberate errors. Comparing them is the exercise this page exists for.

=== "MATLAB"

    ```matlab
    good = readYAMLmodel('smallYeast.yml');
    bad = readYAMLmodel('smallYeastBad.yml');
    fprintf('good %d rxns, bad %d rxns\n', numel(good.rxns), numel(bad.rxns));
    ```

    ```text title="Output"
    good 53 rxns, bad 54 rxns
    ```

=== "Python"

    ```python
    import cobra
    from raven_toolbox.io import read_yaml_model

    cobra.Configuration().processes = 1

    good = read_yaml_model("smallYeast.yml")
    bad = read_yaml_model("smallYeastBad.yml")
    print(f"good {len(good.reactions)} rxns, bad {len(bad.reactions)} rxns")
    ```

    ```text title="Output"
    good 53 rxns, bad 54 rxns
    ```

## 17.1 What exactly is different?

`diffModels` matches by identifier and compares what it finds: stoichiometry,
bounds, objective coefficients, gene rules, formulas, charges. It answers a yes
or no question first — are these the same model? — and then says why not.

=== "MATLAB"

    ```matlab
    report = diffModels(good, bad);
    fprintf('equal: %d, %d differences\n', report.equal, numel(report.differences));
    for i = 1:min(4, numel(report.differences))
        fprintf('  - %s\n', report.differences{i});
    end
    ```

    ```text title="Output"
    equal: 0, 11 differences
      - 1 reactions only in A: ethIN
      - 2 reactions only in B: ADH2, PDC_2
      - ADH1: coef[ETH_c] A=1 B=2
      - ADH1: bounds A=[-1000,1000] B=[0,1000]
    ```

=== "Python"

    ```python
    from raven_toolbox.comparison import diff_models

    report = diff_models(good, bad)
    print(f"equal: {report.equal}, {len(report.differences)} differences")
    for d in report.differences[:4]:
        print(f"  - {d}")
    ```

    ```text title="Output"
    equal: False, 11 differences
      - reactions only in A (1): ['ethIN']
      - reactions only in B (2): ['ADH2', 'PDC_2']
      - ADH1: coef[ETH_c] A=1 B=2
      - ADH1: bounds A=(-1000.0, 1000.0) B=(0.0, 1000.0)
    ```

This is the comparison to put in a test. `DiffReport` is falsy when the models
differ, so `assert diff_models(before, after)` is a working regression test for a
curation script — and in MATLAB, `report.equal` does the same job.

## 17.2 How alike are they?

The other question is coarser: across the whole reaction set, how much do two
models overlap? `compare_models` builds a presence matrix — one row per
identifier, one column per model — and reduces it to a Jaccard similarity.
`compareRxnsGenesMetsComps` prints a full breakdown (reactions, metabolites,
genes, EC numbers, equations with and without compartments) unless you pass
`'printResults', false`, as here.

=== "MATLAB"

    ```matlab
    good.id = 'smallYeast';
    bad.id = 'smallYeastBad';
    compStruct = compareRxnsGenesMetsComps({good, bad}, 'printResults', false);
    inBoth = all(compStruct.rxns.comparison, 2);
    fprintf('%d reactions shared of %d in the union\n', ...
        compStruct.rxns.nElements(inBoth), sum(compStruct.rxns.nElements));
    ```

    ```text title="Output"
    52 reactions shared of 55 in the union
    ```

=== "Python"

    ```python
    from raven_toolbox.comparison import compare_models

    good.id, bad.id = "smallYeast", "smallYeastBad"
    comparison = compare_models([good, bad])
    shared = int((comparison.reactions.sum(axis=1) == 2).sum())
    print(f"{shared} reactions shared of {len(comparison.reactions)} in the union")
    print(f"similarity: {comparison.similarity.iloc[0, 1]:.3f}")
    ```

    ```text title="Output"
    52 reactions shared of 55 in the union
    similarity: 0.945
    ```

!!! warning "A high similarity is not a clean bill of health"
    These two models are **0.945** alike on the reaction set, and one of them is
    broken. The differences 17.1 lists are a doubled stoichiometric coefficient
    and a reaction made irreversible — changes that alter what the model
    *predicts* while barely moving a set-overlap score. Similarity is for
    grouping models, not for validating one.

## 17.3 Compare what they do, not what they contain

Two models with the same reactions can behave differently, and two models with
different reactions can behave identically. The comparison that settles it is of
the fluxes.

=== "MATLAB"

    ```matlab
    openGood = setParam(good, 'ub', {'glcIN', 'o2IN'}, [1 1000]);
    openGood = setParam(openGood, 'obj', 'biomassOUT', 1);
    openBad = setParam(bad, 'ub', {'glcIN', 'o2IN'}, [1 1000]);
    openBad = setParam(openBad, 'obj', 'biomassOUT', 1);
    solGood = solveLP(openGood);
    solBad = solveLP(openBad);
    fprintf('growth: good %.4f, bad %.4f\n', solGood.f, solBad.f);
    ```

    ```text title="Output"
    growth: good 0.1222, bad -0.0000
    ```

=== "Python"

    ```python
    for model in (good, bad):
        model.reactions.get_by_id("glcIN").upper_bound = 1.0
        model.reactions.get_by_id("o2IN").upper_bound = 1000.0
        model.objective = "biomassOUT"
    print(f"growth: good {good.slim_optimize():.4f}, bad {bad.slim_optimize():.4f}")
    ```

    ```text title="Output"
    growth: good 0.1222, bad 0.0000
    ```

The errors in `smallYeastBad` are not cosmetic. On the same medium, with the same
objective, the good model grows and **the bad one does not grow at all** — from a
model that a set-overlap score called 94.5 % similar. A diff tells you the models
differ; only a simulation tells you what the difference costs. (MATLAB reports
that zero as `-0.0000`; the minus sign is a formatting artefact of a zero
objective, not a negative growth rate.)

The two tabs also show what `compareRxnsGenesMetsComps` and `compare_models`
count differently. RAVEN's matrix has one row per *combination of models* —
in-first-only, in-second-only, in-both — with `nElements` counting each;
raven-toolbox's has one row per *identifier* with a column per model. Both
answer the same question, but you index them in opposite directions.

!!! warning "What can go wrong"
    - **Comparing on identifiers alone.** Both functions match by id. Two models
      from different databases share few ids and will look unrelated even when
      they describe the same metabolism — see
      [16. Combining and simplifying](combining.md), where merging matches on
      names instead.
    - **Reading similarity as quality.** It measures overlap, not correctness.
    - **Forgetting the medium.** A flux comparison compares conditions as much as
      models. Set the same bounds on both, explicitly, before drawing any
      conclusion.
    - **Diffing a model against a reloaded copy of itself.** Writing and reading
      a model can change formatting, ordering and rounding; a diff that reports
      differences after a round trip may be telling you about the file format —
      see [3. Reading and writing models](io.md).

## See also

- [9. Quality control](quality-control.md) — checking one model rather than two.
- [16. Combining and simplifying](combining.md) — putting models together, and
  what has to line up first.
- [4. Simulating growth with FBA](fba.md) — the simulation a flux comparison
  rests on.
