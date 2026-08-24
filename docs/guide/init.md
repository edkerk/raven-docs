<!-- run-examples: skip-file -->

# 10. Context-specific models with tINIT and ftINIT

A genome-scale model describes what an organism *can* do. tINIT and ftINIT cut it
down to what a particular sample — a tissue, a cell line, a condition — appears to
be doing, from expression data plus a list of metabolic tasks the result must
still be able to perform.

This page walks through it on **Human-GEM**, with the RNA-seq data Human-GEM
ships, in both toolboxes.

!!! warning "The outputs on this page were produced by hand, not by the build"
    Every other page in this guide is re-executed on every commit. This one is
    not: preparing Human-GEM took **113 minutes** in MATLAB and **126 minutes**
    in Python, the MATLAB run producing a **159 MB** artefact — which no
    documentation build should attempt. The numbers below come
    from one real run — Human-GEM `main`, RAVEN `develop3`, Gurobi 13.0.2 — and
    are quoted with their wall-clock so you can plan around them.

    For the MATLAB workflow in its natural habitat, including comparison of the
    extracted models, see the
    [Human-GEM guide](https://sysbiochalmers.github.io/Human-GEM-guide/gem_extraction/),
    which is maintained alongside the model.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `prepINITModel` | `prep_init_model` | the once-per-template preparation |
| `parseTaskList` | `parse_task_list` | the tasks the extracted model must satisfy |
| `getINITSteps` | `get_init_steps` | the step definitions (`1+0`, `1+1`, …) |
| `ftINIT` | `ftinit` | the staged extraction |
| `scoreComplexModel` | `score_reactions_from_genes` | gene scores → reaction scores |
| — | `gene_scores_from_expression` | expression → gene scores |
| `runINIT`, `getINITModel` | `run_init`, `get_init_model` | the original tINIT, for comparison |
| `removeLowScoreGenes` | `remove_low_score_genes` | prune negative-scoring genes from GPRs |
| `checkTasks` | `check_tasks` | confirm the result still does what it must |

## Setup

Human-GEM ships everything needed except the toolbox:

```bash
git clone --depth=1 https://github.com/SysBioChalmers/Human-GEM.git
```

| File | What it is |
|---|---|
| `model/Human-GEM.mat` (or `.xml`, `.yml`) | the template — 12 931 reactions, 2 848 genes |
| `model/reactions.tsv` | reaction annotations, including which reactions are spontaneous |
| `data/metabolicTasks/metabolicTasks_Essential.txt` | 57 tasks the extracted model must still pass |
| `data/datasets/Hart2015_RNAseq.txt` | TPM for five cell lines — DLD1, GBM, HCT116, HELA, RPE1 |

Both extractions are mixed-integer problems, so **GLPK will not do**: set Gurobi
up first ([6. Solvers and configuration](solvers.md)).

## 10.1 Prepare the template — once

The preparation finds the task-essential reactions, classifies every reaction
into omics-independent categories, merges linear stretches, and rescales the
stoichiometry so that a single big-M works across the model. It depends only on
the template and the task list, **not on your data**, so it is done once and
reused for every sample.

=== "MATLAB"

    ```matlab
    load('Human-GEM/model/Human-GEM.mat');          % the struct is called humanGEM
    tasks = parseTaskList('Human-GEM/data/metabolicTasks/metabolicTasks_Essential.txt');

    % spontaneous reactions are flagged in the model's own annotation table
    tsv   = readtable('Human-GEM/model/reactions.tsv', 'FileType', 'text', 'Delimiter', '\t');
    spont = tsv.rxns(tsv.spontaneous == 1);

    prepData = prepINITModel(humanGEM, tasks, 'spontRxnNames', spont, 'extComp', 'e');
    save('prepData.mat', 'prepData', '-v7.3');
    ```

    ```text title="Output — 113 minutes"
    prepData.mat: 159 MB
    ```

    Human-GEM also has a wrapper, `prepHumanModelForftINIT`, which reads those
    two files for you. It does **not** run against RAVEN `develop3`: its
    `importTsvFile` returns the `spontaneous` column as text, so the `== 1`
    inside it throws. Calling `prepINITModel` directly, as above, sidesteps that.

=== "Python"

    ```python
    import cobra
    from cobra.io import read_sbml_model

    from raven_toolbox.init import prep_init_model
    from raven_toolbox.tasks import parse_task_list

    cobra.Configuration().processes = 1     # see the note below

    model = read_sbml_model("Human-GEM/model/Human-GEM.xml")
    model.solver = "gurobi"
    tasks = parse_task_list("Human-GEM/data/metabolicTasks/metabolicTasks_Essential.txt")

    prep = prep_init_model(model, tasks, ext_comp="e")
    ```

    ```text title="Output — 126 minutes"
    load 115s
    prep_init_model 7552s
    ```

    Reading Human-GEM from SBML alone takes about **two minutes**, and the
    preparation itself **126 minutes** — the same order as MATLAB's 113, on the
    same machine and solver. Two things worth knowing before starting it:

    - `prep_init_model` runs cobrapy's FVA, which spawns worker processes. Where
      that is not permitted — a locked-down Windows machine, some CI runners — it
      fails with `PermissionError: [WinError 5] Access is denied`. Setting
      `processes = 1` trades the parallelism for a run that finishes.
    - `essential_cache_path` caches the slow task-essential discovery, so a
      second preparation of the same template skips it.

## 10.2 Bring in the expression data

RAVEN wants one struct: the genes, the sample names, and a genes × samples matrix
of levels. `threshold` is the level above which a gene counts as expressed; leave
it out and the mean across samples is used per gene instead.

=== "MATLAB"

    ```matlab
    tbl = readtable('Human-GEM/data/datasets/Hart2015_RNAseq.txt', ...
        'FileType', 'text', 'Delimiter', '\t');

    arrayData.genes     = tbl.gene;
    arrayData.tissues   = tbl.Properties.VariableNames(2:end)';
    arrayData.levels    = table2array(tbl(:, 2:end));
    arrayData.threshold = 1;
    ```

    ```text title="Output"
    18687 genes x 5 samples
    ```

=== "Python"

    ```python
    import pandas as pd

    from raven_toolbox.init import gene_scores_from_expression, score_reactions_from_genes

    tpm = pd.read_csv("Human-GEM/data/datasets/Hart2015_RNAseq.txt", sep="\t", index_col="gene")
    print(f"{tpm.shape[0]} genes x {tpm.shape[1]} samples")

    gene_scores = gene_scores_from_expression(tpm["HCT116"].to_dict(), reference=1.0)
    rxn_scores = score_reactions_from_genes(model, gene_scores)
    ```

    The two steps are separate in Python: `gene_scores_from_expression` applies
    RAVEN's rule — **5·ln(level / reference)**, clamped to [−5, 10] — and
    `score_reactions_from_genes` pushes the result through the GPRs. Splitting
    them means any other source of gene scores (HPA via `hpa_gene_scores`,
    proteomics, a curated list) feeds the same second step.

    The clamp is worth seeing directly, because it explains why two very
    different samples can produce nearly the same model:

    ```python
    print(gene_scores_from_expression({"a": 12.0, "b": 0.5, "c": 3.0}, reference=3.0))
    ```

    ```text title="Output"
    {'a': 6.93, 'b': -5.0, 'c': 0.0}
    ```

    `b` computes to −8.96 and comes back at the floor; a gene exactly at its
    reference scores zero — neither in nor out.

## 10.3 Extract a model for one sample

=== "MATLAB"

    ```matlab
    contextModel = ftINIT(prepData, 'HCT116', [], [], ...
        'transcrData', arrayData, ...
        'INITSteps', getINITSteps([], '1+0'));
    ```

    ```text title="Output — 70 seconds"
    9595 rxns, 1761 genes
    ```

    Two argument traps, both of which fail without mentioning the argument you
    got wrong:

    - `hpaData` is the **fourth positional** argument. Skip it and the expression
      struct lands on `metabolomicsData`, reporting `Metabolomics contains the
      same metabolite multiple times`.
    - the step list is `'INITSteps'`, not `'steps'`. An unrecognised name is
      taken as a positional value, and you get that same misleading error.

=== "Python"

    ```python
    from raven_toolbox.init import ftinit

    context = ftinit(prep, rxn_scores, series="1+0", gene_scores=gene_scores)
    print(len(context.reactions), "reactions,", len(context.genes), "genes")
    ```

    `ftinit` takes the reaction scores directly rather than the expression
    struct, which is why the scoring is a separate step above. `gene_scores` is
    optional and prunes negative-scoring genes from the GPRs that survive;
    `fill_gaps=False` skips the task repair.

**`1+0` or `1+1`?** `1+0` leaves out most reactions that have no gene rule and
takes 30–60 s per sample; `1+1` adds a second optimisation over those reactions,
takes two to three times longer, and gives a smaller model. The run above is
`1+0`: **12 931 → 9 595 reactions and 2 848 → 1 761 genes, in 70 seconds.**

## 10.4 Check what came out

An extracted model is a hypothesis. The tasks it was built to satisfy are the
first thing to re-check, and the cheapest.

=== "MATLAB"

    ```matlab
    taskReport = checkTasks(contextModel, [], true, false, false, tasks);
    ```

=== "Python"

    ```python
    from raven_toolbox.tasks import check_tasks

    report = check_tasks(context, tasks)
    print(sum(1 for result in report if result.ok), "of", len(report), "tasks pass")
    ```

Then compare the result against the template and against the other samples:
[9. Quality control](quality-control.md) covers the structural checks, and the
Human-GEM guide's
[GEM comparison](https://sysbiochalmers.github.io/Human-GEM-guide/gem_comparison/)
covers comparing many extracted models at once.

!!! warning "What can go wrong"
    - **Identifiers that do not match.** Human-GEM speaks ENSEMBL, and so does
      `Hart2015_RNAseq.txt` — which is why no mapping step appears above. With
      symbols or systematic names you need one; score a handful of genes and
      check they are not all at the floor before spending two hours on the
      preparation.
    - **Re-preparing per sample.** The preparation depends only on the template
      and the tasks. Do it once, save it, reuse it — that is the entire point of
      the split.
    - **No MILP solver.** Both extractions are mixed-integer; GLPK cannot.
    - **A model that no longer does what you assumed.** Without a task list there
      is nothing to repair against, and the extraction is free to remove
      capabilities you never thought to check.

## See also

- [Human-GEM guide: GEM extraction using ftINIT](https://sysbiochalmers.github.io/Human-GEM-guide/gem_extraction/)
  — the same workflow in MATLAB, maintained with the model.
- [Human-GEM guide: extraction from single-cell data](https://sysbiochalmers.github.io/Human-GEM-guide/gem_extraction_sc/).
- [9. Quality control](quality-control.md) — checking the model that comes out.
