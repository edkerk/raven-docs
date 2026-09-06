# `reference_reactions` — a postmortem

**Status: retired.** `reference_reactions` was implemented on raven-toolbox's
`feat/ftinit-stability-reference-anchor` branch, validated against a real Human-GEM
curation, found to invert on one of two tested cell lines, root-caused, and removed
before ever merging to `develop`. This page is the record of what was tried, how it
was built, and why it didn't clear the bar — kept so the idea isn't quietly retried
without this evidence.

## The problem it targeted

[ftINIT reproducibility](ftinit-determinism.md) separates two properties:

* **Determinism** — same input, different run/seed/solver build → same model.
  `resolve_ties`/`prove_abs_gap` target this, are validated, and remain in raven-toolbox.
* **Stability** — *similar* input (a curated template, a different but comparable
  sample) → *similar* model. Neither `resolve_ties` nor `prove_abs_gap` touches this:
  they pin which optimum a *single* extraction returns, but a re-extraction of an
  edited template re-solves the MILP from scratch and can land on a completely
  different tied optimum, flipping genes that have nothing to do with the edit.

`reference_reactions` was the attempt at stability: bias a re-extraction toward a
*prior* build's choices, on the theory that a real curation should only move what the
curation actually touches.

## Technical design

Built on top of `resolve_ties`'s existing lexicographic tie-break in
`_resolve_ties` (`raven_toolbox/init/ftinit.py`), which already ran two phases after
the primary score objective: minimise the count of kept removable reactions
(parsimony), then minimise their summed id rank. `reference_reactions` inserted a new
phase **before** those two:

```python
# Phase R — among the score-optimal solutions, minimise disagreement with `reference`.
mismatch = add([mul([Real(-1.0 if rid in reference else 1.0), ind])
                for rid, ind in binaries.items()])
_phase(prob.Objective(mismatch, direction="min"), "phaseR-reference")
opt.add(prob.Constraint(mismatch, ub=rmin + 0.5, name="_canon_ref_floor"))
```

Signed sum, not a plain count: −1 per binary the reference wants kept (so minimising
pushes it toward 1), +1 per binary the reference wants dropped. The cascade became
**(score) → (match reference) → (parsimony) → (id-rank)**, each phase floored at the
previous phase's optimum before the next runs — the same floor-constraint mechanism
`resolve_ties` already used for its own two phases, which is what gives the safety
property below.

Two more pieces made it usable end to end:

* **`_translate_reference`** mapped a caller-facing reference (original `ref_model`
  reaction ids, e.g. `{r.id for r in a_prior_build.reactions}`) into each ftINIT step's
  *merged* id space. ftINIT's linear-chain merge (`merge.py`) contracts unbranched
  reaction chains into one combined reaction that keeps one member's id; a merged
  reaction was counted as matching the reference if **any** of its original members
  did — the conservative choice, since for an edited template the merge grouping, or
  even which member becomes the representative id, can differ from the reference's own
  prep.
* **`fill_tasks`** (`taskfill.py`) got the identical mechanism (`_resolve_ties_fill`'s
  own Phase R) for the gap-fill MILP that restores task feasibility after extraction,
  so a re-extraction's gap-fill also preferred a prior build's added reactions.

**Safety property**: because Phase R's floor constraint is applied *after* the primary
score objective is already fixed at *this* build's own optimum, a reaction the data
genuinely prefers is locked in before the reference is ever consulted — the mechanism
can only resolve a genuine tie, never override a real score difference. This was tested
directly (`test_reference_reactions_cannot_override_a_real_score_difference`): anchoring
to a reference that used a strictly worse-scored reaction did not move the extraction
off its own optimum. This property held throughout — it is not what failed.

## Progressively realistic synthetic validation (retracted)

Before ever anchoring to a real curation, four synthetic edits were measured on
Human-GEM/DLD1, each less favorable to the reference than the last:

| Scenario | Edit | Baseline gene drift | Anchored gene drift | Reduction |
|---|---|---:|---:|---:|
| Null-ish | 30 reactions removed, **none** used by the reference build | 13 (112→125) | 1 (112→111) | **13×** |
| Realistic | 15 of the reference's *own kept* reactions removed | 12 (112→122) | 6 (112→110) | 2× |
| Cross-sample | HCT116 vs DLD1, no template edit at all | 60 (112→160) | 62 (112→162) | ~none (slightly worse) |
| Whole subsystem | 352 reactions removed (a used subset) | 6 (112→110) | 4 (112→112) | 1.5× |

The pattern — a large win on a contrived edit that shrinks, vanishes, or reverses as
the edit gets more realistic — was visible before any real curation was tested, and in
hindsight should have been the headline finding on its own.

**These four numbers are retracted.** All three synthetic-edit preps
(`axisb_prep_edited.pkl`, `axisb_prep_s1.pkl`, `axisb_prep_s3.pkl`) were later found to
carry `essential_rxns` sets of size **1** instead of the ~206 RAVEN's own `prepINITModel`
would compute for Human-GEM. The cause: `prep_init_model` called
`find_task_essential_reactions` at its *additive* boundary default
(`close_boundaries=False`) instead of the *closed* boundary RAVEN's `prepINITModel`
always uses for this step (`closeModel` + `checkTasks` zeroing every metabolite balance
— `prepINITModel.m:81-82`, `checkTasks.m:63`). On a model whose exchanges all ship open,
like Human-GEM, the additive reading lets the model's own boundary silently satisfy
every task, so essentially no reaction is ever found essential — the task constraint
was absent from every one of these builds. Fixed in raven-toolbox (`prep_init_model`
now passes `close_boundaries=True`, matching RAVEN; the standalone function's own
default is unchanged, since it is correct for a model with no boundary metabolites).

With the task-feasibility constraint effectively switched off, these four builds were
extracting against a materially easier problem than production ftINIT ever runs, and
nothing about the reported drift ratios can be trusted to reflect `reference_reactions`'
real effect. They are kept here only as the historical record of what motivated the
real-curation test below, not as evidence for or against the feature.

!!! warning "This bug affects more than this page"
    `close_boundaries` was wrong for every Human-GEM `prep_init_model` build made
    before the fix — which includes the preps behind [ftINIT
    reproducibility](ftinit-determinism.md)'s own headline seed-to-seed spread numbers
    (16 → 8 → 3). Those have not been re-measured under the fix. Treat that page's
    magnitudes as unconfirmed pending a re-run; the qualitative claim (`resolve_ties`
    reduces spread, `prove_abs_gap` fixes a real suboptimality) is independent of the
    task layer and unlikely to reverse, but the exact numbers might move.

## The decisive test: a real curation

[Human-GEM PR #1028](https://github.com/SysBioChalmers/Human-GEM/pull/1028) supplied a
real, surgical curation: an EC 1.5.5.1 ETF reaction's GPR tightened from 9 OR-ed
isozymes to 3 obligate AND-ed subunits, two reactions recoupled from the ETF pathway to
ubiquinone, and one orphaned metabolite removed. Its discussion noted DLD1 and GBM
reacted differently to ftINIT's non-determinism, so both were built — six genome-scale
extractions total (parental/updated template × {DLD1, GBM} reference, unanchored,
anchored), all at `resolve_ties=True, prove_abs_gap=1.0`, on a **corrected**
`prep_init_model` (the `close_boundaries` fix above, landed first).

**Primary metric — essential-gene symmetric difference vs. the parental reference:**

| Cell line | Unanchored | Anchored | Ratio |
|---|---:|---:|---:|
| DLD1 | 7 (112 essential) | 2 | **0.29×** — helps |
| GBM | 11 (124 essential) | **56** (176 essential) | **5.09×** — hurts badly |

DLD1 reproduced the hoped-for result. GBM inverted it: anchoring pushed the essential
gene count from 124 (parental) / 133 (unanchored) to **176** — a 42% jump — dragging in
53 genes that were not drifting at all in the unanchored build.

**Safety falsifier** (does anchoring suppress the real biology?): no. In DLD1, none of
the 9 curation-implicated genes drift essential in any arm. In GBM, the three AND-coupled
ETF subunits (`ETFA`/`ETFB`/`ETFDH`) appear as essential-drifting **only in the anchored
build** — anchoring is what surfaced the correct signal; the unanchored build missed it
entirely. The "can only resolve a genuine tie, never override real data" property held
under a real curation, on both cell lines. That is not what failed either.

**Secondary**: reaction-level symdiff moved in the *opposite* direction from gene drift
for GBM (60 → 42, i.e. anchoring looked like an improvement at the reaction level while
being a 5× regression at the gene level) — the same reaction/gene divergence seen
throughout this line of work, now confirmed on real curation data. Hart2015 (BF>0)
accuracy was roughly a wash to a mild net positive for the anchored GBM build (MCC 0.300
vs. 0.298 vs. 0.284) — this failure mode is not a biological-accuracy problem, it's a
spurious-drift problem, and the two metrics can disagree.

Full experiment script and per-build logs: `humangem_curation_anchor.py` (raven-toolbox
scratchpad, not currently published as a docs artifact).

## Root cause of the GBM inversion

Two hypotheses were tested and one confirmed, by direct ablation on the cached
extraction data (no MILP re-solve needed):

**Hypothesis 1 — merge-group bundling (refuted).** ftINIT's linear-chain merge can
bundle several original reactions, each with its own genes, into one group that is
kept/dropped as a unit; `_translate_reference`'s any-member match means a single Phase R
flip could in principle drag a whole group's genes along with it. Checked directly: of
the 58 reactions that actually differ between GBM's anchored and unanchored builds, only
2 carry any genes at all, and none of the 47 genes newly essential in the anchored
build's drift are reachable via genes on those 58 reactions or their merge groups.
Ruled out.

**Hypothesis 2 — a network-topology regime swap (confirmed).** The 58 differing
reactions are almost entirely (56/58) gene-less "Transport reactions" — compartment
shuttles for CoA, NAD⁺, carnitine derivatives — all but two scored the identical flat
**−2.0** (Human-GEM's default penalty for expression-blind reactions). This is the same
mega-tied block already documented in [ftINIT reproducibility](ftinit-determinism.md):
"the largest block — 5159 reactions scored −2.00, of which 5101 are GPR-less — is
identical across all five Hart2015 cell lines." `reference_reactions` exists precisely
to resolve ties like this one.

Reconstructing the base/anchored networks directly from `prep.ref_model` and testing the
swap in isolation:

* Removing the unanchored build's 30-reaction cluster **without** the anchored build's
  28-reaction replacement collapses growth entirely (essential-gene count → 0, i.e.
  infeasible) — for GBM, that cluster is not a redundant convenience, it is the *only*
  connectivity route the unanchored extraction happens to use.
* Adding the anchored build's 28 reactions **on top of** the unanchored build's 30
  (both routes present) *reduces* essentiality (127 → 115) — more redundancy, as
  expected when nothing is removed.
* The real anchored build does both — drops the 30, adds the 28 — landing on a
  **different, independently viable** route to growth (86.75 vs. 86.95, both fine), but
  one with far less redundancy for dozens of genes that have nothing to do with either
  route.

DLD1's own swapped set is built from the *same* class of reaction (4/88 carry genes,
vs. 2/58 for GBM; six exact reaction ids are shared between the two cell lines' swapped
sets in each direction) — this is not GBM-specific machinery, it is the same generic
tied block, with a consequence that differs by two orders of magnitude depending on how
much of that cell line's own expression-driven network happens to route through it.

## Why this is a design limit, not a bug

`reference_reactions` does not reduce arbitrariness in an absolute sense — it swaps
*this build's own arbitrary tie-break* for *the reference build's own, equally
arbitrary tie-break*. Whether that substitution helps depends entirely on how much
downstream redundancy the tied cluster happens to carry in the *target* model — a
property the mismatch objective has no visibility into, because it counts reaction
**identity** agreement, not reaction **network role**. For DLD1 the reference's pick was
low-consequence. For GBM it sat on a load-bearing fork between two structurally
different, both-valid regimes. Nothing in the design distinguishes those cases in
advance, and the 7-dimension adversarial review that preceded the real-curation test
correctly found the merge-group translation and floor-constraint logic sound — the gap
is structural, not an implementation defect.

A future version that weighted the mismatch objective by something like "is this
reaction the unique route for X" rather than a flat ±1 per reaction might close this
gap; that is a real redesign, not attempted here.

## Disposition

Removed from `raven-toolbox` before merging: `reference_reactions` (both in
`ftinit()`/`run_ftinit`/`_resolve_ties` and in `fill_tasks`/`_gap_fill_task`/
`_resolve_ties_fill`), `_translate_reference`, and their tests. `resolve_ties` and
`prove_abs_gap` are unaffected — they solve a different, validated problem
(determinism) and stay.
