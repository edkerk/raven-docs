# ftINIT reproducibility vs. real accuracy — ground-truth validation

Follow-up to [ftINIT reproducibility](ftinit-determinism.md). That study measures how much
`resolve_ties`, `prove_abs_gap`, and `reference_reactions` change a build's *reproducibility*
and *stability*. It does not ask the harder question: does any of that machinery make the
build's gene-essentiality predictions **more accurate** against real biology, or does it just
move the arbitrariness somewhere else? This page answers that, using real CRISPR-screen data
as ground truth, and reports two further experiments the answer motivated: whether a
different (non-arbitrary) tie-break criterion does better than the current one, and whether
ftINIT can be steered toward matching known-essential genes directly.

**Headline finding:** every "essential gene" number in the companion study — and everywhere
else in raven-toolbox's ftINIT work to date — is a purely model-internal FBA prediction
(`cobra.flux_analysis.find_essential_genes`), never previously checked against real
experimental essentiality. Once checked, `resolve_ties`/`prove_abs_gap`/`reference_reactions`
turn out to have **no consistent effect on real accuracy in either direction** — they still
do what the companion study says (control reproducibility and stability), just not accuracy.
Two further attempts to buy real accuracy directly — trying other tie-break criteria, and
anchoring construction toward known-essential genes — both came back negative.

!!! warning "Two things to know before reading the numbers below"
    **`reference_reactions` has since been removed from raven-toolbox.** It was validated
    against a real curation, found to invert (help on one cell line, a 5x drift *increase*
    on another), root-caused, and retired — see [the `reference_reactions`
    postmortem](ftinit-reference-reactions.md). Every mention of it below (including the
    known-essential-gene-steering experiment, which reused its tie-break machinery) is
    historical: accurate as a record of what was tried, not a description of current API.

    **The S1/S2/S3 preps behind every number on this page share the same
    `close_boundaries` bug** documented in the [companion study's
    warning](ftinit-determinism.md): `prep_init_model` used the additive boundary default
    instead of RAVEN's closed one for task-essential-reaction discovery, collapsing the
    task constraint to ~1 reaction instead of ~206. None of this page's findings have been
    re-measured since the fix. The core methodological conclusions (essential-gene count is
    a poor accuracy proxy; no tie-break criterion generalises; gene-steering via reference
    reactions doesn't reliably work) do not depend on the task layer being correctly
    constrained, so they are unlikely to reverse — but the exact numbers should be treated
    as illustrative, not final.

## Why this page exists

Every prior ftINIT measurement in this project — the companion determinism study, the
[Human-GEM validation](humangem-validation.md), the reference-anchoring stability numbers —
uses "number of essential genes" or "essential-gene swing" as its outcome metric. That metric
is entirely internal to the model: it says nothing about whether those predictions are
*correct*. A build that predicts 160 essential genes is not obviously better or worse than
one that predicts 110 — both could be equally wrong, or equally right, and the raw count
cannot tell you which. This is a real methodological gap, not a pedantic one: several
conclusions in the companion study (e.g. "`resolve_ties` moved essential-gene count by 39% in
one scenario") describe a *reproducibility* problem correctly but say nothing about whether
either of the two answers was closer to reality.

## Method

* **Ground truth.** Hart2015 CRISPR-screen Bayes factors
  (`data/datasets/Hart2015_TableS2.xlsx`, sheet `bayes-factors-5cell_lines-A375-`), which
  cover the same cell lines already used for expression scoring in this project (DLD1,
  HCT116, HeLa, GBM, RPE1). Threshold: **BF > 0** (the standard BAGEL log-odds cutoff),
  confirmed by sign on known genes (POLR2A/EEF2 strongly positive; OR51E2/TAS2R38 negative).
* **Gene matching.** Model `Gene.name` (HGNC symbol) joined directly against Hart2015's
  `Gene` column — no external ID mapping needed.
* **Cell-line correctness.** DLD1 and HCT116 have genuinely different true-essential-gene
  sets. Every score below uses the Bayes-factor column matching the expression data that
  actually built that model (DLD1 scenarios scored against `BF_dld1`, the HCT116 scenario
  against `BF_hct116`) — scoring against the wrong cell line's ground truth would be a
  correctness bug, not just noise.
* **Evaluation universe.** Restricted to genes the specific extracted model actually contains
  (the union of GPR genes across its kept reactions), not the full genome-scale template. A
  gene a model never included was never tested for essentiality by `find_essential_genes`;
  counting it as a correct non-essential call would be a category error.
* **Metrics.** TP / FP / FN / TN of predicted-essential vs. Hart2015 BF>0, plus
  precision/recall/MCC. TP and FP are reported as the primary numbers per the working
  decision below — see [Which metric](#which-metric-tp-vs-f1-vs-mcc).
* **Scenarios**, reused from the companion study's stability work:
    * **S1** — moderate real edit: 15 real reactions removed from the DLD1 template.
    * **S2** — different sample: unedited template, HCT116 expression instead of DLD1.
    * **S3** — large edit: 352 reactions removed (the FAO subsystem).
* Every build in this page captures warnings (`warnings.catch_warnings(record=True)` +
  `simplefilter("always")`), never suppresses them — an earlier draft of this analysis used
  `warnings.filterwarnings("ignore")` and silently hid real solver-timeout and
  unproven-tie-break warnings; that bug was caught by a self-directed adversarial review
  before any conclusion was drawn from the affected runs, and every number on this page was
  re-measured with warnings enabled.

## Does `resolve_ties` / `prove_abs_gap` / `reference_reactions` change real accuracy?

The full grid — `prove_abs_gap` ∈ {none, 2.0, 1.0, 0.5} × `resolve_ties` ∈ {True, False} × 3
scenarios, plus `reference_reactions` on/off — scored against Hart2015:

| Axis | Range across the whole grid |
|---|---|
| Precision | 0.59 – 0.73 |
| Recall | 0.20 – 0.28 |
| MCC | **0.316 – 0.360** |

A 0.044-wide MCC band across every parameter combination and every scenario is, in practical
terms, noise. None of the three parameters has a consistent direction: within S1,
`resolve_ties=True` (any finite gap) dominates `resolve_ties=False` cleanly — more true
positives (67 vs 59) *and* fewer false positives (26 vs 28). Within S2, the same setting wins
on raw TP (77 vs 61) but loses on precision (FP jumps 28 → 51) — it is not a clean win, just a
shift toward calling more genes essential overall. Within S3 it *reverses*:
`resolve_ties=False` has both more TP (60 vs 57) and more FP (31 vs 24) than `True`. A rule
that helps in one scenario, is a wash in a second, and reverses in a third is not a rule you
can use to pick settings in advance.

`reference_reactions` behaves the same way. Comparing the anchored build against the
unanchored baseline on TP − FP (a same-scenario, apples-to-apples comparison since it doesn't
require picking a threshold):

| Scenario | Baseline TP − FP | Anchored TP − FP |
|---|---:|---:|
| S1 (moderate edit) | **41** | 32 |
| S2 (different sample) | 26 | 24 |
| S3 (large edit) | 33 | **35** |

Anchoring wins in S3, loses in S1, is roughly flat in S2. **This does not contradict the
companion study** — `reference_reactions` still does exactly what it claims: it reduces
run-to-run and re-selection *noise* (proven by construction — it can never override a
genuine score difference). What it does not do, and was never claimed to do, is make the
model more biologically correct. Stability and accuracy are different properties, and this is
the direct evidence that conflating them would be a mistake.

### Which metric: TP vs. F1 vs. MCC

The number most worth reporting turned out not to be F1 or MCC but plain **TP alongside
FP** — more interpretable, but only safe to read jointly. TP alone is confounded by how many
genes a build calls essential in total: a build that simply flags more genes will pick up
more TP *and* more FP for free, which is a recall/precision trade-off, not a real
improvement. The S2 result above (`resolve_ties=True` up 16 TP, up 23 FP) is exactly that
trap — reading TP alone would say `resolve_ties=True` is better for S2; it isn't, it is just
more permissive. TP − FP (or, equivalently, requiring FP to not increase) is the smallest
honest version of "prefer more correct calls": it survives being read at a glance and does not
reward a build for simply flagging more genes.

## Is "which tied answer gets returned" itself steerable toward more accuracy?

`resolve_ties`'s current secondary tie-break, after parsimony, is deliberately arbitrary:
prefer the lowest-numbered reaction IDs among tied solutions. If that specific rule is
arbitrary, would a different arbitrary-looking rule do better — accidentally or otherwise?
Four alternative phase-2b criteria were substituted (parsimony and the reference phase
untouched), fixed at `resolve_ties=True, prove_abs_gap=1.0`, across the same 3 scenarios:

* **`idrank_desc`** — the same rule, reversed (highest reaction IDs preferred). Control: does
  simply flipping an arbitrary order change the outcome?
* **`random_seed7`** — a fixed-seed shuffle, independent of ID or score. Null-model control:
  does *any* fixed order do roughly the same thing as the production rule?
* **`score_mag`** — prefer to keep the reaction with the *weakest* removal evidence (score
  nearest zero). The one criterion with an actual biological rationale.
* **`gene_count`** — prefer to keep reactions with fewer genes in their GPR. A structural
  parsimony-in-gene-space proxy.

| Scenario | Criterion | TP | FP | TP − FP | MCC |
|---|---|---:|---:|---:|---:|
| S1 | **idrank (production)** | 67 | 26 | **41** | **0.360** |
| S1 | idrank_desc | 59 | 24 | 35 | 0.334 |
| S1 | random_seed7 | 59 | 27 | 32 | 0.325 |
| S1 | score_mag | 64 | 37 | 27 | 0.319 |
| S1 | gene_count | 58 | 24 | 34 | 0.330 |
| S2 | idrank (production) | 77 | 51 | 26 | 0.352 |
| S2 | **idrank_desc** | 66 | 27 | **39** | **0.366** |
| S2 | random_seed7 | 78 | 55 | 23 | 0.348 |
| S2 | score_mag | 58 | 26 | 32 | 0.336 |
| S2 | gene_count | 59 | 27 | 32 | 0.337 |
| S3 | idrank (production) | 57 | 24 | 33 | 0.326 |
| S3 | **idrank_desc** | 66 | 26 | **40** | **0.357** |
| S3 | random_seed7 | 59 | 23 | 36 | 0.337 |
| S3 | score_mag | 58 | 26 | 32 | 0.324 |
| S3 | gene_count | 59 | 31 | 28 | 0.314 |

**No criterion is a reliable, generalisable improvement.** The biggest mover was the cheapest
possible change — just reversing the same arbitrary alphabetical order. `idrank_desc` beat
production `idrank` on both TP − FP and MCC in S2 and S3, but lost clearly in S1 (41 vs 35).
Picking the right direction requires already knowing the ground truth, which defeats the
purpose. The two criteria with an actual rationale behind them did not help: `score_mag`
(keep the weakest-evidence-for-removal reaction) was tied-worst or worst in every single
scenario; `gene_count` was similarly mediocre, never best anywhere. `random_seed7` — no
structure at all — performed about as well as the "principled" criteria, which is itself
informative: having *some* rationale behind the tie-break is not what is driving the
differences between runs. **`resolve_ties`'s current `idrank` default is not shown to be
wrong; no evidence here supports replacing it.**

## Can ftINIT be steered toward known-essential genes directly?

Human-GEM's own (non-gating) CI does something adjacent to this already:
`code/test/geneEssentiality.py` builds 5 cell-line-specific ftINIT models and scores them
against Hart2015 (accuracy ≈0.85–0.91, sensitivity ≈0.29–0.46 — consistent with the
precision/recall figures on this page once TN-dominance is accounted for). It measures after
the fact; it never *steers* reconstruction toward the known-essential set. This experiment
tests whether steering is possible using the machinery already validated in this project.

**Mechanism.** Gene essentiality is not a decision variable in ftINIT's MILP — it is an
emergent property of network topology and GPR, only knowable via a downstream FBA knockout.
So this does not add new solver machinery for essentiality itself. Each known-essential gene
is translated into the reactions that are its own, non-redundant contribution (via `cobra`'s
`knock_out_model_genes`, which already respects GPR boolean/isozyme logic), unioned across
the reference gene set, and fed into the existing, already-validated `reference_reactions`
tie-break. Biasing `resolve_ties` to keep those reactions is a best-effort nudge toward the
gene mattering in the final model — it cannot force it, since a redundant pathway elsewhere
in the retained network can still make the knockout non-lethal regardless of whether the
gene's own reactions survive.

**Held-out design, to rule out training-on-the-test-set.** Only *half* of each scenario's
Hart2015 BF>0 genes (188/188 for S1, 173/174 for S2, 188/188 for S3) were used to build the
`reference_reactions` set; the other half was withheld and scored separately. If anchoring
only helps on the half it was pointed at, that is memorisation, not a real result — the
comparison below reports both halves, plus the unrestricted baseline, on identical gene
subsets:

| Scenario | Train-half recall (anchored vs. baseline) | Held-out recall (anchored vs. baseline) | Full-universe MCC (anchored vs. baseline) |
|---|---|---|---|
| S1 | 0.262 vs. 0.262 — identical | 0.203 vs. 0.203 — identical | 0.360 vs. 0.360 — identical |
| S2 | 0.309 vs. 0.309 — identical | 0.250 vs. 0.250 — identical | 0.346 vs. 0.352 — slightly worse |
| S3 | 0.214 vs. 0.221 — slightly worse | 0.188 vs. 0.174 — slightly better | 0.330 vs. 0.326 — roughly flat |

**Negative result.** Not once, in any scenario, does the anchored build even beat baseline on
its *own* train-half genes — the ones it was explicitly biased toward. S1 and S2 are simply
identical to baseline; S3 is marginally worse on train and only marginally better on held-out
(the wrong direction to read as a real effect). This is not the overfitting failure mode the
held-out split was built to catch — there is no train-set benefit to be circular about in the
first place. The mechanism is just too indirect: keeping a gene's own reactions present does
not reliably make the model call it essential, because that also depends on whether a backup
pathway survives elsewhere in the retained network, which reaction-level anchoring does not
control.

**Recommendation: do not pursue this as a shipped feature.** The evidence does not support it
doing what a user would want, and the added complexity (a new translation helper, a
held-out-validation burden on every future claim about it) is not justified by a real
capability gain. A more direct mechanism — biasing the MILP toward FBA-knockout lethality
itself, rather than toward the genes' own reactions — is the only path that could plausibly
work, but it is also the option most exposed to the overfitting risk this experiment was
designed to catch, and this result gives no reason to think the much larger undertaking would
pay off.

## Conclusions

* **Every "essential gene" number produced by ftINIT work to date, before this page, is an
  unvalidated FBA prediction.** It is now validated: precision ≈0.6–0.7, recall ≈0.2–0.28,
  MCC ≈0.32–0.36 — a real but modest signal, unsurprising given a context-specific model only
  predicts essentiality for the (small) subset of genes it actually contains.
* **None of `resolve_ties`, `prove_abs_gap`, or `reference_reactions` moves real accuracy in
  a consistent direction.** They do exactly what the companion study measured —
  reproducibility and stability — and nothing about correctness. This is not a weakness to
  fix; it means the two properties are genuinely independent, and settings should keep being
  chosen for reproducibility/stability reasons, not in a search for an accuracy edge that
  is not there.
* **"Number of essential genes" (or its swing) is not a fit-for-purpose accuracy metric,**
  confirmed directly: two builds with similar essential-gene counts can have meaningfully
  different real accuracy, and a parameter flip's effect on essential-gene count does not
  predict its effect on real accuracy, in either direction. Prefer TP and FP together (or
  precision/recall/MCC against real ground truth where available) over a raw count.
* **Neither attempt to buy real accuracy directly worked.** Substituting the tie-break
  criterion moved the numbers but with no criterion, arbitrary or principled, winning
  reliably across scenarios. Steering construction toward known-essential genes via
  `reference_reactions` failed to beat baseline even on the genes it was pointed at. Both are
  negative results worth keeping on record so they are not re-attempted without new evidence.

## Limitations

* Same single-machine, single-Gurobi-build, 3-scenario caveats as the companion study, plus:
  ground truth is Hart2015 only (5 cell lines; DLD1 and HCT116 used here), so accuracy
  figures reflect that dataset's own coverage and noise, not an independent replication.
* The BF > 0 threshold is the standard BAGEL cutoff, not independently re-derived here — a
  methodological choice, not a discovered constant. A different threshold would shift the
  absolute precision/recall numbers, though there is no reason to expect it would change
  which parameter settings win, since all comparisons here are same-threshold, same-scenario.
* "No criterion wins reliably" was tested on 4 alternative criteria across 3 scenarios (15
  MILP builds) — enough to show the effect is real and not attributable to `idrank`
  specifically, not enough to rule out some other, untested criterion working better.
* The gene-essentiality-reference experiment used a single 50/50 train/test split per
  scenario (fixed seed) rather than repeated cross-validation; a negative result this clean
  (identical-to-baseline in 2 of 3 scenarios) is unlikely to be a split-selection artifact,
  but that has not been independently confirmed with a second split.
* `reference_reactions`'s own headline numbers (13×/2×/1.5× essential-gene-drift reduction
  across increasingly realistic edits) are retracted — see the warning at the top of this
  page and [the postmortem](ftinit-reference-reactions.md) for why, and for the corrected,
  real-curation measurement that replaced them.
