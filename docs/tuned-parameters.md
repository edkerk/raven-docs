# Tuned parameter defaults

Both toolboxes carry parameters with non-obvious defaults — an E-value cutoff,
a MILP time limit, an alignment-length filter. Most were never independently
measured on either side; a value was picked once, early, and carried forward
by both convention and by the port. Where that has since been tested, the
answer is sometimes reassuring and sometimes not.

This page collects the cases worth knowing about on their own terms — a wrong
assumption about a default corrupts results quietly, unlike a missing function,
which fails loudly. For the exhaustive table — every tuned parameter, its
current value(s), and a one-line reason — see raven-toolbox's own
[parameter reference](https://github.com/SysBioChalmers/raven-toolbox/blob/develop/docs/reference/tuned_parameters.md).

## Genome-scale flux sampling isn't converged by default

`randomSampling` / `random_sampling` default to `thinning=100` on the Python
side (RAVEN's own ACHR implementation makes the same call). That value is
calibrated for models with a few hundred reactions. On a genome-scale model
such as yeast-GEM (~4,100 reactions), independent Markov chains sampled at
these settings frequently land on different answers for the same reaction —
checked with the Gelman-Rubin diagnostic, the *median* reaction across four
independent chains fails the standard convergence threshold, not just a tail
of hard cases.

Neither of the cheap fixes helps: reallocating the same total step budget onto
a bigger `thinning` makes no measurable difference, and switching to the
rounding-based `chrr` method fixes convergence on a small model but costs
enough at genome scale (a fixed per-chain setup cost alone, before a single
sample is drawn) that it isn't a practical drop-in replacement today. Treat
default-settings genome-scale sampling output as unconverged for most
reactions, not a caveat for a minority of hard ones.

## `predictLocalization` and `predict_localization` solve the problem differently

Both take a time budget — `maxTime` (MATLAB, default 15 minutes) and
`time_limit` (Python, default unlimited) — and the numbers even coincide
(15 min = 900 s, a value that turns up on both sides). They are not
interchangeable settings for the same thing. RAVEN's `predictLocalization`
solves the compartment-assignment problem with simulated annealing — a
stochastic heuristic where more time generally produces a better answer, with
no guarantee of optimality at any point. raven-toolbox's `predict_localization`
formulates and solves a MILP instead, where a time limit is a hard cutoff on a
search that would otherwise terminate with a *proven* optimum. The same
number means a different kind of promise on each side.

## A threshold copied forward for years, never measured

`getModelFromHomology` and `get_model_from_homology` both filter candidate
orthologs on alignment length, and both shipped with `minLen` / `min_align_len`
set to 200 — a value with no recorded justification on either side. Measured
against two independent ortholog references (KEGG annotations and OMA) across
a relatedness series from a close relative to a very distant one, 200 turns
out to discard real orthologs for no reduction in wrong matches; anything at
or below 150 performs identically. `min_align_len` is now `100` on the Python
side; the same change is proposed for MATLAB but not yet made.

The more interesting failure avoided here is methodological. An earlier
version of this measurement scored candidate thresholds against curated
non-model-organism GEMs built by this same homology method — hanpo-GEM among
them. That number peaked exactly at the settings the curated model was built
with, and collapsed one step past them. A reference built by the method being
tested can only confirm the method reproduces itself, not that it is right;
KEGG and OMA don't have that problem.

## An "implicit" MATLAB default that, on inspection, isn't there

`FSEOF`'s target classification compares consecutive iterations directly —
no tolerance, just a bare `>` and `<` on floating-point values. raven-toolbox's
`fseof` compares against an explicit noise floor, `flux_eps`, because genome-scale
solver noise (differences on the order of 1e-7) was otherwise being reported as
real knockdown targets. The Python-side fix was originally described as
tightening a looser MATLAB default of `1e-8` — a reasonable-sounding assumption
that turned out to be wrong on inspection of the MATLAB source: there is no
threshold there at all, fixed or otherwise, which is a stricter comparison than
even the tightest value tested, not a looser one. Adding a floor to `FSEOF` is
proposed but not yet done.

