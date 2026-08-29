# ftINIT reproducibility — `resolve_ties`, `prove_abs_gap`, `reference_reactions`

How reproducible ftINIT is, what raven-toolbox's opt-in parameters fix, and — the reason
this page exists — what they do and do not fix. Companion to the API documentation in
`raven_toolbox.init.ftinit`.

Two different properties are at stake, and they need separating:

* **Determinism** — same input, different run/machine/solver build → same model.
* **Stability** — *similar* input (a curated template, a different but comparable sample)
  → *similar* model.

`resolve_ties`/`prove_abs_gap` target determinism only. `reference_reactions` (built on
top of `resolve_ties`) is the parameter that targets stability directly — see the
dedicated section below for what it buys and what it still doesn't.

## Why the problem exists

The extraction MILP is massively degenerate. Of the ~6700 negative-score reactions (the
true 0/1 keep-or-drop binaries) on Human-GEM/DLD1, **99.7% sit in tied blocks**, and the
largest block — 5159 reactions scored −2.00, of which 5101 are GPR-less — is *identical
across all five Hart2015 cell lines*. It is the default score for reactions with no gene
association, so no expression dataset changes it. Many reaction subsets reach the same
score optimum and the solver returns an arbitrary one.

`Threads=1` and a fixed `Seed` make that choice reproducible, not unique — a different
Gurobi version, platform, or seed lands on a different member of the tied set, and that
surfaces downstream as gene-essentiality predictions that drift for reasons unrelated to
the model or the data.

`resolve_ties` and `prove_abs_gap` attack that directly:

* **`resolve_ties`** — a lexicographic phase 2 over the removable (binary) reactions: hold
  the score objective at its optimum, minimise the count of kept reactions, then their
  summed id rank. Applied to both each extraction step and the task gap-fill.
* **`prove_abs_gap`** — proves each step to a fixed *absolute* MIP gap in a single solve,
  replacing RAVEN's relative-gap escalation, whose final near-zero-objective run otherwise
  accepts an arbitrary within-gap incumbent.

Both default to off (`resolve_ties=False`, `prove_abs_gap=None`), so the shipped behaviour
is unchanged.

## Method

* **Model / data.** Human-GEM `v2.0.0-38`, Hart2015 DLD1 cell line, tasks on, series
  `1+1`, prep built with raven-toolbox's own `prep_init_model` (12877-reaction reference —
  *not* RAVEN's exported `raven_refModel.xml`, so absolute counts here are not comparable
  to the [Human-GEM validation](humangem-validation.md) run, which uses that export).
* **Solver.** Gurobi 13.0.2, `Threads=1` unless stated, single machine.
* **Determinism probe.** The extraction `seed` is varied (1234, 7, and four more where
  noted) with everything else — inputs, code, solver build, machine — held fixed, so any
  difference between builds is *purely* the solver's tie-break among equal optima. This is
  a lower bound on cross-version drift: a Gurobi upgrade perturbs the search far more than
  a seed change does, and that failure mode is not measured directly — see *Limitations*.
* **Metrics.** Reaction seed-swing (symmetric difference of kept-reaction sets) and
  essential-gene seed-swing (symmetric difference of single-gene-deletion essential sets,
  via `cobra.flux_analysis.find_essential_genes`). The second is what matters for users;
  the first is what the parameters act on directly.

## Results

### Full pipeline, seed 1234 vs 7

| Config | Reaction swing | **Gene swing** | Essential genes | Build |
|---|---:|---:|---:|---:|
| baseline | 106 | **16** | 120 / 136 | ~17 min |
| `resolve_ties=True` | 89 | **8** | 111 / 115 | ~25 min |
| `resolve_ties=True, prove_abs_gap=0.05` | 98 | **3** | 111 / 114 | ~60 min |

Gene-level swing falls monotonically, 16 → 8 → 3. Reaction-level swing barely moves and is
not monotonic — a poor proxy, which follows directly from 5101 of the tied reactions
having no genes at all.

Repeated builds at a **fixed** seed are a separate axis, and the more informative one for
day-to-day use: the baseline still moves 33 reactions and 1 gene between two runs with
nothing at all changed (the second stage terminates on wall clock, so the incumbent
depends on machine load/scheduling), while `resolve_ties` is byte-identical.

### Where the degeneracy actually is

Six seeds through the first stage's single MILP (the cheap ~2 min probe), with and without
`resolve_ties`, and at `Threads` 1 and 4:

| Config | Threads | Distinct solutions / 6 | Mean pairwise swing |
|---|---:|---:|---:|
| baseline | 1 | 6 | 38.5 |
| baseline | 4 | 6 | 36.9 |
| `resolve_ties=True` | 1 | 2 | 2.7 |
| `resolve_ties=True` | 4 | 2 | 2.7 |

**`Threads` has no measurable effect** on this benchmark — raising it did not open up the
degeneracy the way a seed change does, despite being the reproducibility lever RAVEN's own
implementation comment singles out as dominant.

Conditioning on the objective is the cleanest result of the whole study. At a *fixed*
objective value, baseline returned 7 distinct solutions from 8 runs (pairwise differences
8–48 reactions); `resolve_ties` returned **one**. Its entire residual variation at this
stage came from the primary solve landing on one of two objectives 2.0 apart — not from
the tie-break itself.

### What `prove_abs_gap` is actually for

Sweeping the value on the first stage (4 seeds) and second stage (3 seeds):

| `prove_abs_gap` | Stage 1: distinct / objectives | Stage 2: objective | Stage 2 status | Stage 2 time |
|---|---|---|---|---:|
| `None` (escalation) | 2 / 2 | −716.87 (**suboptimal**) | 1 of 3 timed out | 604 s |
| 5.0 | 2 / 2 | −712.87 | proven | 1330 s |
| **2.0** | **1 / 1** | −712.87 | proven | 1401 s |
| **1.0** | **1 / 1** | −712.87 | proven | 1538 s |
| 0.5 | 1 / 1 | −712.87 | 2 of 3 timed out | 1864 s |
| 0.1 | 1 / 1 | −712.87 | all timed out | 1858 s |
| 0.05 | 1 / 1 | −712.87 | all timed out | 1948 s |

The headline is not determinism: **the default escalation returns a suboptimal
extraction.** It lands 2.0 below the true optimum in stage 1 and 4.0 below in stage 2 —
351 kept reactions where the optimum keeps 349 — silently, with no warning.

The two stages pull in opposite directions. Stage 1 needs a gap ≤ 2.0 to collapse to one
objective; stage 2 stops being provable within the time limit below roughly 1.0. They
overlap at **1.0–2.0**, which is the recommended value. Tighter is actively
counter-productive: 0.05 costs 3x the escalation's runtime, never proves, and returns
exactly the same model as 1.0.

### The limit of `resolve_ties` at genome scale

At a fixed, proven objective in stage 2, all three seeds still returned **three different
reaction sets** (12–82 reactions apart) despite an identical objective and an identical
count of 349 kept reactions. Instrumenting the tie-break (raven-toolbox's
`FTINIT_DEBUG=1`) shows why:

```
[ftinit] final solve:                  status=optimal     achieved_gap=0.0028
[ftinit] tie-break phase2a-parsimony:  status=time_limit  obj=349.0
[ftinit] tie-break phase2b-idrank:     status=time_limit  obj=inf
```

The primary solve proves its optimum, but **both tie-break phases exhaust the time
limit.** Their incumbent is still adopted — it measurably reduces the spread relative to
no tie-break at all — but it is itself an arbitrary within-gap pick, so at genome scale
`resolve_ties` reduces rather than removes the run-to-run variation. raven-toolbox now
warns when this happens (`resolve_ties=True` no longer silently implies a proven
selection); raising `time_limit` is the available lever.

This is why the parameter is exact in unit tests and at the cheap first stage, yet only
partial in a full genome-scale build: the tie-break phases prove in milliseconds at toy
scale and can time out at genome scale.

## Recommendation

* **`resolve_ties=True`** — makes repeated builds at a fixed seed identical and halves the
  seed-to-seed gene swing, at ~1.4x runtime. Heed its warning if raised: an unproven
  tie-break means a reduction, not a guarantee.
* **`prove_abs_gap=1.0`** — fixes a genuine optimality defect in the default escalation and
  collapses the objective variation, at ~2.4x runtime. Do not go tighter than 1.0 — it
  buys nothing further and costs more.
* **Pinning the solver stack** (raven-toolbox commit + `gurobipy` version) remains the
  zero-cost lever for run-to-run identity, and is unaffected by anything above.

## Stability under a small template change

Baseline and `resolve_ties` on **identical** inputs already differ by 164 reactions and 11
essential-gene calls (120 vs 111, ~10%) — both fully score-optimal, differing only in
which tied optimum was selected. That is the ceiling on how much a re-extraction can move
even when nothing about the biology changed.

That matters for two common workflows:

* **Curating the template.** Fix one or a few reactions, re-extract, and compare. The MILP
  re-solves globally and can move far more than the edit warrants, because the optimum is
  a discontinuous function of the input — genes flip that have nothing to do with the
  curation. A deterministic extractor does not fix this; determinism is not continuity.
* **Comparable but distinct samples.** Two RNA-seq samples from ostensibly the same
  healthy tissue, differing only by ordinary inter-patient variation, can independently
  reselect within the same tied set and produce two models with reaction-level and
  gene-level differences that look like biology but are not.

### `reference_reactions`: anchoring a re-extraction to a prior build

`resolve_ties=True` also accepts `reference_reactions`: a set of reaction ids a reference
build kept. It adds a phase, ahead of parsimony/id-rank, that prefers the tied solution
closest to the reference — so a re-extraction of a lightly edited template stays close to
the reference wherever the data does not force a difference, instead of the MILP
re-deriving the sparsest set from scratch. It can only ever resolve a genuine tie: the
reference phase runs after the primary score objective is fixed at *this* build's own
optimum, so a reaction the data actually prefers is never overridden. Applies to both the
main extraction (translated through merge groups automatically) and the task gap-fill.

**Measured on Human-GEM/DLD1 with a null-ish edit** — 30 reactions removed from the
template, all of them unused by the reference build M0 (`resolve_ties=True,
prove_abs_gap=1.0`, 8777 reactions, 112 essential genes, growth 84.716), so a
perfectly-stable extractor would show zero downstream change outside the edit itself:

| Re-extraction | Reaction symdiff vs M0 | **Essential-gene drift** | Growth |
|---|---:|---:|---:|
| Baseline (no reference) | 58 | **13** (112 → 125, all gains) | 84.716 → 72.654 (**−14%**) |
| `reference_reactions=M0` | 46 | **1** (112 → 111) | 84.716 → 84.706 (−0.01%) |

Anchoring cuts the spurious essential-gene drift **13× (13 → 1)** and leaves growth
essentially untouched, where the unanchored re-extraction — from an edit that touched
*nothing* the reference model used — swings growth by 14% and flips 13 genes essential
that have no relationship to the removed reactions. The reaction-level swing drops less
dramatically (58 → 46): consistent with the rest of this study, reaction-level movement is
a poor proxy for what a user actually cares about, and the flags that help most at the
gene level help least at the reaction level.

**The control that separates a real effect from re-selection noise remains worth using
alongside anchoring, not instead of it: apply the edit to the *extracted* model as well,
not only to the template.** Comparing an extraction of the edited template against the
extracted baseline model with the same edit applied directly gives an exact, causal
before/after diff for the reactions the edit actually touches; anchoring reduces the noise
in a *re-extraction* diff but does not eliminate it (46 reactions and 1 gene still moved
in a template edit that used none of the reference's kept reactions).

## Limitations

One cell line, one seed pair for the full-pipeline determinism table (six seeds for the
single-stage probes), one edit (30 unused reactions removed) for the stability
measurement, one machine, one Gurobi build. Enough for direction and rough magnitude, not
for error bars on any number. Cross-Gurobi-version drift — the failure mode
`resolve_ties`/`prove_abs_gap` are really aimed at — is not measured at all; the seed
probe stands in for it and is expected to understate it. The stability measurement used a
"null-ish" edit chosen to touch nothing the reference build used, which isolates
re-selection noise cleanly but is gentler than a typical real curation (which usually
removes or changes something the model *does* use, so both baseline and anchored drift
would likely be larger there — the relative gap between them, which is the actual claim,
has no particular reason to shrink). Wall-clock figures include some suspend-inflated
outliers from an overnight run and should be read as approximate; the swing/objective
columns are set comparisons unaffected by wall-clock noise.

## Reproducing

Requires Gurobi and a Human-GEM checkout.

```python
from raven_toolbox.init import ftinit

# Determinism: same input, different seed.
model_a = ftinit(prep, scores, seed=1234, resolve_ties=True, prove_abs_gap=1.0)
model_b = ftinit(prep, scores, seed=7,    resolve_ties=True, prove_abs_gap=1.0)
print(len({r.id for r in model_a.reactions} ^ {r.id for r in model_b.reactions}))

# Stability: a lightly edited template, anchored to the original build.
m0 = ftinit(prep, scores, resolve_ties=True, prove_abs_gap=1.0)
m0_kept = {r.id for r in m0.reactions}
prep_edited = prep_init_model(edited_template, tasks)  # tasks unchanged, template edited
m1 = ftinit(prep_edited, scores, resolve_ties=True, prove_abs_gap=1.0,
           reference_reactions=m0_kept)
```

Set `FTINIT_DEBUG=1` to log each solve's status and each tie-break phase — the fastest way
to see whether a build rests on a proven optimum or an unproven incumbent.
