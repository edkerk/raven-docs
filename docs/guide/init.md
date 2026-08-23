# 10. Context-specific models with tINIT and ftINIT

A genome-scale model describes what an organism *can* do. tINIT and ftINIT cut it
down to what a particular sample — a tissue, a cell line, a condition — appears to
be doing, using expression data and a set of metabolic tasks the result must
still be able to perform.

!!! info "The worked example lives in the Human-GEM guide"
    ftINIT's usual subject is **Human-GEM**, and the
    [Human-GEM guide](https://sysbiochalmers.github.io/Human-GEM-guide/gem_extraction/)
    is the maintained walkthrough: preparing the human model, formatting
    transcriptomics, running the extraction, and comparing the results. There is
    also a [single-cell version](https://sysbiochalmers.github.io/Human-GEM-guide/gem_extraction_sc/).

    This page does not repeat it. What it adds is the part that guide does not
    cover: **which raven-toolbox function corresponds to which RAVEN function**,
    and the shape of the pipeline, so a Python user can follow the same steps.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `prepINITModel` | `prep_init_model` | the once-per-template preparation |
| `scoreComplexModel` | `score_reactions_from_genes` | gene scores → reaction scores |
| — | `gene_scores_from_expression` | expression → gene scores |
| `ftINIT` | `ftinit` | the staged extraction |
| `runINIT` | `run_init` | the original INIT MILP |
| `getINITModel` | `get_init_model` | the tINIT pipeline |
| `getINITSteps` | `get_init_steps` | the step definitions (`1+0`, `1+1`, …) |
| `ftINITFillGaps` | `fill_tasks` | add reactions back until the tasks pass |
| `removeLowScoreGenes` | `remove_low_score_genes` | prune negative-scoring genes from GPRs |
| `parseHPA`, `scoreModel` | `parse_hpa`, `hpa_gene_scores` | Human Protein Atlas as the data source |
| `parseTaskList` | `parse_task_list` | the tasks the extracted model must satisfy |

## 10.1 The shape of the pipeline

Both toolboxes split the work the same way, and the split is the thing to
understand before running anything:

1. **Prepare the template — once.** `prepINITModel` / `prep_init_model` finds the
   task-essential reactions, classifies every reaction into omics-independent
   categories, merges linear stretches and rescales the stoichiometry so one
   big-M works across the model. It depends only on the template and the task
   list, **not** on your data, so it is done once and reused for every sample. On
   Human-GEM this is the expensive step — the Human-GEM guide quotes 1–2 hours,
   which is why Human-GEM ships
   [`prepHumanModelForftINIT`](https://github.com/SysBioChalmers/Human-GEM/blob/main/code/tINIT/prepHumanModelForftINIT.m)
   and prepared data alongside the model.
2. **Score the genes — once per sample.** Expression becomes a score per gene,
   then a score per reaction through the GPRs.
3. **Extract — once per sample.** A MILP keeps high-scoring reactions and drops
   low-scoring ones, in stages.
4. **Repair.** Reactions are added back until every metabolic task passes, and
   genes that scored negative are pruned from the GPRs of the reactions that
   survived.

## 10.2 Scoring, the step you can see whole

The scoring rule is small enough to demonstrate exactly, and it is where most
surprises come from: RAVEN scores a gene as **5·ln(level / reference)**, clamped
to [−5, 10]. A gene above its reference scores positive and pulls its reactions
into the model; one below scores negative and pushes them out.

=== "MATLAB"

    <!-- run-examples: skip -->

    ```matlab
    arrayData.genes    = {'YBR196C'; 'YGR192C'; 'YLR354C'};
    arrayData.tissues  = {'sample'};
    arrayData.levels   = [12.0; 0.5; 3.0];
    arrayData.threshold = 3.0;
    rxnScores = scoreComplexModel(model, [], arrayData, 'sample');
    ```

    `scoreComplexModel` goes from the data structure straight to reaction scores,
    and expects the same `arrayData` layout that `ftINIT` takes.

=== "Python"

    ```python
    from raven_toolbox.init import gene_scores_from_expression

    expression = {"YBR196C": 12.0, "YGR192C": 0.5, "YLR354C": 3.0}
    scores = gene_scores_from_expression(expression, reference=3.0)
    for gene, score in scores.items():
        print(f"{gene}: {score:+.2f}")
    ```

    ```text title="Output"
    YBR196C: +6.93
    YGR192C: -5.00
    YLR354C: +0.00
    ```

    `YGR192C` sits well below the reference — 5·ln(0.5/3) is −8.96 — but comes
    back as −5.00, the floor. A gene exactly at its reference scores zero, which
    means neither in nor out. Knowing where the clamp bites matters when you are
    wondering why two very different samples produced nearly the same model.

    The two steps are separate in Python: `gene_scores_from_expression` for the
    rule above, then `score_reactions_from_genes(model, scores)` to push the
    scores through the GPRs. Splitting them means any other source of gene scores
    — HPA via `hpa_gene_scores`, proteomics, a hand-curated list — feeds the same
    second step.

## 10.3 Preparing a template

Neither call is quick enough to run in a documentation build; both are shown as
you would write them.

=== "MATLAB"

    <!-- run-examples: skip -->

    ```matlab
    taskStruct = parseTaskList('metabolicTasks_Essential.txt');
    prepData = prepINITModel(model, [], {}, false, {}, 'e', taskStruct);
    ```

=== "Python"

    <!-- run-examples: skip -->

    ```python
    from raven_toolbox.init import prep_init_model
    from raven_toolbox.tasks import parse_task_list

    tasks = parse_task_list("metabolicTasks_Essential.txt")
    prep = prep_init_model(model, tasks, ext_comp="e")
    ```

    `prep_init_model` takes `essential_cache_path`, which stores the slow
    task-essential discovery so a second run on the same template skips it.

## 10.4 Extracting a model

The staged setups are the same in both, and the choice is a trade-off the
Human-GEM guide spells out: **`1+0`** leaves out most reactions without gene
rules and is roughly 30–60 s per sample on Human-GEM, while **`1+1`** adds a
second optimisation over those reactions, takes two to three times longer, and
gives a smaller model.

=== "MATLAB"

    <!-- run-examples: skip -->

    ```matlab
    contextModel = ftINIT(prepData, 'sample', [], 'transcrData', arrayData, ...
        'steps', getINITSteps([], '1+0'));
    ```

=== "Python"

    <!-- run-examples: skip -->

    ```python
    from raven_toolbox.init import ftinit, score_reactions_from_genes

    rxn_scores = score_reactions_from_genes(model, scores)
    context = ftinit(prep, rxn_scores, series="1+0")
    ```

    `ftinit` returns the extracted `cobra.Model`. Pass `gene_scores=scores` as
    well to prune negative-scoring genes from the surviving GPRs, and
    `fill_gaps=False` to skip the task repair.

!!! warning "What can go wrong"
    - **Identifiers that do not match.** Human-GEM speaks ENSEMBL, expression
      tables often speak symbols, and yeast models speak systematic names. Score
      a handful of genes and check they are not all at the floor before running
      anything expensive; `convertGenes` in `prepINITModel` exists for exactly
      this.
    - **No MILP solver.** Both extractions are mixed-integer problems, so GLPK
      will not do — see [6. Solvers and configuration](solvers.md).
    - **Re-preparing the template for every sample.** The preparation depends
      only on the template and the tasks. Do it once, cache it, reuse it.
    - **No task list.** Without tasks there is nothing to repair against, and the
      extracted model can lose the ability to do things you assumed it kept.

## See also

- [Human-GEM guide: GEM extraction using ftINIT](https://sysbiochalmers.github.io/Human-GEM-guide/gem_extraction/)
  — the full worked example, in MATLAB.
- [9. Quality control](quality-control.md) — what to check on the model that
  comes out.
- [MATLAB vs Python](../differences.md) — the complete function mapping.
