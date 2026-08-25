# 11. Deletions and essentiality

Which genes can the organism lose and still grow? Knock each one out, re-solve,
and compare. The same machinery answers "which reactions are essential", "what
happens if I delete two things at once", and "how do I predict a knockout's flux
distribution better than plain FBA does".

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `findGeneDeletions` | `single_gene_deletion` <span class="cobrapy-tag">cobrapy</span> | knock out every gene in turn |
| `findGeneDeletions` (`'sgd'`/`'dgd'`) | `double_gene_deletion` <span class="cobrapy-tag">cobrapy</span> | pairs of genes |
| `getEssentialRxns` | `find_task_essential_reactions` | reactions a task cannot do without |
| `deleteUnusedGenes` | `remove_genes` | remove genes, rather than knock them out |
| `qMOMA` | `moma` <span class="cobrapy-tag">cobrapy</span> | a knockout's fluxes, staying near the wild type |

## Setup

`smallYeast.yml`, with glucose and oxygen open so the model grows. Uptake in
this model is a **positive** flux through a `=> metabolite` reaction, so it is
the upper bound that opens it.

=== "MATLAB"

    ```matlab
    model = readYAMLmodel('smallYeast.yml');
    model = setParam(model, 'ub', {'glcIN', 'o2IN'}, [1 1000]);
    model = setParam(model, 'obj', 'biomassOUT', 1);
    sol = solveLP(model);
    fprintf('wild type: %.4f /h\n', sol.f);
    ```

    ```text title="Output"
    wild type: 0.1222 /h
    ```

=== "Python"

    ```python
    from raven_toolbox.io import read_yaml_model

    model = read_yaml_model("smallYeast.yml")
    model.reactions.get_by_id("glcIN").upper_bound = 1.0
    model.reactions.get_by_id("o2IN").upper_bound = 1000.0
    model.objective = "biomassOUT"
    print(f"wild type: {model.slim_optimize():.4f} /h")
    ```

    ```text title="Output"
    wild type: 0.1222 /h
    ```

## 11.1 Knock out one gene

The question underneath every deletion study: with this gene gone, can the model
still reach its objective? A gene knockout is not a reaction knockout — the GPR
decides. Remove one of two isozymes and nothing happens; remove a subunit of a
complex and the reaction goes.

=== "MATLAB"

    ```matlab
    modelKO = removeGenes(model, {'YBR196C'}, 'removeBlockedRxns', true);
    solKO = solveLP(modelKO);
    fprintf('PGI1 knockout: %.4f /h\n', solKO.f);
    ```

    ```text title="Output"
    PGI1 knockout: -0.0000 /h
    ```

=== "Python"

    ```python
    from cobra.manipulation import knock_out_model_genes

    with model:
        knock_out_model_genes(model, ["YBR196C"])
        print(f"PGI1 knockout: {model.slim_optimize():.4f} /h")

    print(f"wild type again: {model.slim_optimize():.4f} /h")
    ```

    ```text title="Output"
    PGI1 knockout: 0.0000 /h
    wild type again: 0.1222 /h
    ```

    `knock_out_model_genes` sets the bounds of every reaction whose GPR is no
    longer satisfiable to zero, and leaves the rest alone. Inside `with model:`
    it is undone on the way out — the cheapest way to ask a knockout question
    without keeping the answer.

## 11.2 Knock out every gene

=== "MATLAB"

    ```matlab
    [genes, fluxes] = findGeneDeletions(model, 'testType', 'sgd', ...
        'analysisType', 'fba');
    growth = full(fluxes(logical(model.c), :));   % fluxes come back sparse
    fprintf('%d genes tested, %d essential\n', numel(genes), sum(growth < 1e-6));
    ```

    ```text title="Output"
    61 genes tested, 9 essential
    ```

=== "Python"

    ```python
    from cobra.flux_analysis import single_gene_deletion

    results = single_gene_deletion(model)
    essential = results[results.growth < 1e-6]
    print(f"{len(results)} genes tested, {len(essential)} essential")
    print(sorted(next(iter(ids)) for ids in essential.ids)[:5])
    ```

    ```text title="Output"
    61 genes tested, 9 essential
    ['YBR196C', 'YCR012W', 'YDL066W', 'YDR050C', 'YKL060C']
    ```

    `single_gene_deletion` returns a DataFrame indexed by the deleted gene set,
    with the resulting growth rate and solver status — so the usual pandas
    filtering finds the essential ones.

## 11.3 Essential reactions

Reaction essentiality asks the same question one level down, and RAVEN frames it
in terms of a **task**: which reactions must stay for the model to still do this
particular thing?

=== "MATLAB"

    ```matlab
    essential = getEssentialRxns(model);
    fprintf('%d essential reactions\n', numel(essential));
    ```

    ```text title="Output"
    0 essential reactions
    ```

=== "Python"

    ```python
    from cobra.flux_analysis import single_reaction_deletion

    results = single_reaction_deletion(model)
    essential = results[results.growth < 1e-6]
    print(f"{len(essential)} essential reactions")
    ```

    ```text title="Output"
    24 essential reactions
    ```

    For essentiality with respect to a *task* rather than the objective,
    raven-toolbox has `find_task_essential_reactions` — see
    [12. Metabolic tasks](tasks.md).

## 11.4 Two at a time

Double deletions find the redundancy single deletions miss: two genes that each
look dispensable but cannot both go. The cost is quadratic, so this is where a
small model earns its keep.

=== "MATLAB"

    ```matlab
    [genes, fluxes] = findGeneDeletions(model, 'testType', 'dgd', ...
        'analysisType', 'fba');
    fprintf('%d gene pairs tested\n', size(genes, 1));
    ```

    ```text title="Output"
    1830 gene pairs tested
    ```

=== "Python"

    ```python
    from cobra.flux_analysis import double_gene_deletion

    subset = [gene for gene in model.genes][:8]
    pairs = double_gene_deletion(model, gene_list1=subset)
    print(f"{len(pairs)} combinations tested")
    print(f"lowest growth: {pairs.growth.min():.4f} /h")
    ```

    ```text title="Output"
    36 combinations tested
    lowest growth: 0.0000 /h
    ```

## 11.5 A knockout's fluxes, not just its growth rate

FBA assumes the knockout re-optimises perfectly, which a cell that just lost a
gene does not do. MOMA instead looks for the flux distribution closest to the
wild type that the mutant can actually achieve — usually a better predictor of a
knockout's physiology, and a different answer.

=== "MATLAB"

    <!-- run-examples: skip -->

    ```matlab
    modelKO = removeGenes(model, {'YBR196C'}, 'removeBlockedRxns', true);
    solMOMA = qMOMA(modelKO, model);
    fprintf('MOMA growth: %.4f /h\n', solMOMA.f);
    ```

    `qMOMA` solves a quadratic problem with `quadprog`, from MATLAB's
    **Optimization Toolbox**. Without it the call fails with
    `Undefined function 'quadprog'` whatever solver RAVEN is set to, which is
    why this block carries no output here.

=== "Python"

    ```python
    from cobra.flux_analysis import moma

    with model:
        knock_out_model_genes(model, ["YBR196C"])
        solution = moma(model, solution=None, linear=True)
        print(f"MOMA growth: {solution.fluxes['biomassOUT']:.4f} /h")
    ```

    ```text title="Output"
    MOMA growth: 0.0000 /h
    ```

!!! warning "What can go wrong"
    - **Confusing gene and reaction knockouts.** Deleting a gene only silences a
      reaction when the GPR says so. Isozymes hide single knockouts; that is the
      point of the double deletions.
    - **A knockout that looks lethal because the medium is wrong.** Essentiality
      is relative to the medium and the objective. State both when you report it
      — see [5. Growth media and conditions](media.md).
    - **Reading essentiality off a threshold.** `growth < 1e-6` is a numerical
      cut-off, not biology. A mutant at 1 % of wild-type growth is not dead.
    - **Double deletions on a genome-scale model.** Quadratic in the gene count;
      restrict the lists, or accept the wait.

## See also

- [4. Simulating growth with FBA](fba.md) — the solve underneath all of this.
- [12. Metabolic tasks](tasks.md) — essentiality with respect to a task.
- [9. Quality control](quality-control.md) — before trusting any of it.
