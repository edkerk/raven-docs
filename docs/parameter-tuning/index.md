# Methods & benchmarks

RAVEN — both the MATLAB toolbox and raven-toolbox (Python) — ships a lot of
functions with numerical defaults: solver tolerances, cut-offs, iteration
limits, literature constants. [Tuned parameter defaults](../tuned-parameters.md)
gives the short version of every one of them — current value, one-line reason,
grouped by capability. This section is the detail behind that page: the
methodology used to evaluate a default, the full write-up for every parameter
that got a dedicated measurement campaign (**studies**), and the quicker
per-function working notes produced along the way (**benchmarks**).

## Evaluation methodology

A default value is *well-chosen* when a user who does not read the docstring
gets a result that is correct and useful for the most common case.

**On MATLAB/Python parity:** neither implementation's defaults were
systematically validated from the start — MATLAB RAVEN's were often chosen by
trial-and-error, copied from earlier tools, or never reconsidered, and
raven-toolbox inherited a mix of ported MATLAB values and upstream (cobrapy)
conventions. An existing default in either toolbox is a useful *prior* — it
reflects years of practical use, or a well-tested upstream library — but it is
not a gold standard. Where the two implementations differ, the right response
is to run both and measure, not to assume whichever came first is correct.

The following criteria apply in rough priority order:

1. **Empirical correctness on real models.** Run the function with the
   candidate default on at least one large model (Yeast9, Human-GEM) and one
   small model (iJO1366 or similar). Compare the result against a known-good
   answer (a published reconstruction, a literature flux distribution, a
   validated gene-essentiality set). The default must produce a result that is
   meaningfully better than any reasonable alternative, or at least no worse.
2. **Sensitivity envelope.** Vary the parameter by ±1 order of magnitude (or
   ±50% for non-log-scale values) and measure result change. If output is
   insensitive across the range, the exact default value matters little —
   document that and move on. If output is highly sensitive, the default must
   land in a plateau region (neither too loose nor too tight) and must be
   documented with the sensitivity profile.
3. **Literature anchor.** Algorithm-specific numerical parameters should match
   the value used in the original paper or the most-cited open-source
   implementation (cobrapy, COBRA Toolbox). Treat this as corroborating
   evidence, not authority.
4. **Cross-implementation check.** Where a raven-toolbox function ports a
   MATLAB RAVEN function (or vice versa), note what the other side uses. A
   difference is a question to investigate empirically, not automatically a
   bug in either direction.
5. **User expectation alignment.** Prefer values that match what a competent
   user would supply without thinking (e.g. `verbose=True` for a long-running
   MILP, `sort_ids=False` for round-trip-safe export).
6. **No `None`-surprises.** `None`/empty defaults are fine for optional
   features but should never silently change algorithmic behaviour; document
   the fallback clearly.

### Evaluation workflow per parameter

```
1. Read the current docstring — does it explain *why* this value?
2. Identify candidate values: current default, the other implementation's
   default (if any), paper value (if any), and at least two plausible
   alternatives (e.g. 1 order of magnitude up/down).
3. Run all candidates on iJO1366 (fast) and Yeast9 or Human-GEM (realistic).
   Record: result quality metric, wall time, any solver/numerical warnings.
4. Compute the sensitivity envelope: how much does the result metric change
   across the candidate range? If the function is a reconstruction method,
   use a curated gene-essentiality set or a held-out growth condition as the
   benchmark.
5. Record the finding, with the measurement it rests on.
6. If a change is warranted: state the proposed new value, quote the test
   that supports it, and update the default and its docstring.
```

## Studies

The primary measurement campaigns — full methodology, raw results, and the
reasoning behind each conclusion.

| Study | Covers |
|---|---|
| [Homology cut-off calibration](studies/homology-cutoff-calibration.md) | `min_align_len`, `min_identity`, `max_evalue` in homology-based reconstruction, measured against independent KEGG and OMA ortholog references across a 4-organism relatedness series |
| [KEGG HMM cut-off calibration](studies/kegg-hmm-cutoff-calibration.md) | `cutoff`, `min_score_ratio_ko`, `min_score_ratio_g` in KEGG HMM-based reconstruction, measured against real KEGG gene→KO annotations across 4 organisms |
| [Sampling convergence calibration](studies/sampling-convergence-calibration.md) | Between-chain (Gelman-Rubin R-hat) convergence of ACHR/CHRR flux sampling at genome scale |
| [INIT parameter calibration](studies/init-param-calibration.md) | `mip_gap`, `time_limit` in INIT/ftINIT, measured on genome-scale Human-GEM (multiple cell lines) |
| [INIT solver benchmark](studies/init-solver-benchmark.md) | Solver-backend behaviour (Gurobi / GLPK / HiGHS) for the INIT/ftINIT MILP |
| [ftINIT reproducibility](studies/ftinit-determinism.md) | What `resolve_ties`/`prove_abs_gap` buy (and cost) on genome-scale Human-GEM |
| [`reference_reactions` postmortem](studies/ftinit-reference-reactions.md) | A stability-anchoring parameter, implemented and validated against a real Human-GEM curation — helped on DLD1, caused a 5x *increase* in spurious essential-gene drift on GBM, root-caused to a network-topology regime swap, and removed |
| [ftINIT reproducibility vs ground truth](studies/ftinit-ground-truth-validation.md) | Whether any of that reproducibility machinery improves real gene-essentiality accuracy against Hart2015 CRISPR-screen ground truth (it doesn't, in either direction) — plus two negative results from trying to buy accuracy directly: alternative tie-break criteria, and anchoring toward known-essential genes |
| [Human-GEM validation vs MATLAB RAVEN](studies/humangem-validation.md) | raven-toolbox's INIT/ftINIT output validated against MATLAB RAVEN on Human-GEM across 5 cell lines (Jaccard 0.975–0.980) |
| [Yeast-GEM localisation benchmark](studies/yeast-localization-benchmark.md) | `time_limit`, `transport_cost` in sub-cellular localisation prediction, measured on real yeast-GEM data with a predictor-noise sweep |
| [predictLocalization head-to-head](studies/predictlocalization-comparison.md) | `predict_localization` (deterministic MILP) vs MATLAB RAVEN's `predictLocalization` (stochastic simulated annealing) on identical inputs — accuracy, determinism, and runtime |

## Benchmarks

Per-function working notes: quicker parameter-by-parameter records produced
alongside (and sometimes instead of) a full study, plus the master
cross-toolbox to-do list.

| Benchmark | Function(s) |
|---|---|
| [Master index](benchmarks/index.md) | All parameters with non-trivial defaults, MATLAB/Python parity decisions, master to-do list |
| [Flux sampling](benchmarks/sampling.md) | `random_sampling`, `find_good_reactions`, `max_volume_ellipsoid` |
| [FSEOF](benchmarks/fseof.md) | `fseof` |
| [INIT / ftINIT](benchmarks/init.md) | `run_init`, `get_init_model`, `run_ftinit`, `gene_scores_from_expression` |
| [Gap-filling](benchmarks/gapfilling.md) | `fill_gaps_fast_lp`, `connect_blocked_reactions`, `fill_gaps_kumar_milp` |
| [Homology-based reconstruction](benchmarks/reconstruction-homology.md) | `run_blast`, `run_diamond`, `get_model_from_homology` |
| [KEGG-based reconstruction](benchmarks/reconstruction-kegg.md) | `assign_kos`, `run_hmmsearch`, `build_ko_hmm`, `get_kegg_model_*` |
| [Sub-cellular localisation](benchmarks/localization.md) | `predict_localization` |
| [Model manipulation](benchmarks/manipulation.md) | `remove_genes`, `merge_models`, `constrain_reversible_reactions`, `find_duplicate_reactions`, `add_transport_reactions` |
| [Tasks](benchmarks/tasks.md) | `check_tasks`, `find_task_essential_reactions` |

See also the [flux sampling algorithms reference](flux-sampling-algorithms.md)
(CHRR/ACHR, cross-linked from the sampling study and benchmark above).
