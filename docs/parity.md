# What "identical results" means

A reasonable question when two implementations of the same method exist: *do they
give the same answer?* The honest answer depends on which function you mean,
because "the same" is achievable for some and meaningless for others.

Three tiers are worth distinguishing.

## Exact

The output can and should match value for value. Anything deterministic that
transforms a model or a file rather than solving an optimisation problem:

- model I/O — SBML and YAML round-trips, Excel export, SIF export
- task-list parsing
- gene-association normalisation (`grRuleToDNF` / `gpr_to_dnf`)
- elemental balance
- identifier sorting, model merging, reversibility splitting, GPR expansion
- KEGG table parsing and homology ortholog assignment

If these disagree, one of them is wrong.

## Set-level

The output is the solution to a mixed-integer problem that has many optima of
equal value, so identity is not a meaningful target — a different reaction set of
the same objective value is not an error. This covers INIT and ftINIT extraction,
gap-filling, and compartment assignment.

The meaningful comparison is overlap: how similar are the two models, expressed
as a Jaccard index or a containment fraction, against a recorded baseline. Two
extractions agreeing to a Jaccard of 0.97 on a genome-scale model is a strong
result, not a near-miss.

Alternate optima also mean the *solver* matters. The same code with Gurobi and
with GLPK can land on different optima, so a cross-language comparison should
hold the solver fixed before concluding anything about the languages.

## Statistical

Flux sampling and random sampling explore a space rather than compute a point.
Two runs of the *same* implementation differ. Compare distributions — means,
marginals, coverage — at a fixed seed, never individual samples.

## What is actually verified today

raven-toolbox has been validated against MATLAB RAVEN on Human-GEM (five
Hart2015 cell-line models, Jaccard 0.975–0.980), on yeast, and on a
multi-organism set. Those are set-level comparisons of the extraction pipeline,
reported in the raven-toolbox repository.

They are, at present, **reported** rather than **enforced**: no test fails if the
two implementations drift apart. Building that harness — committed fixtures, a
MATLAB driver that records the reference output, and tiered assertions matching
the three levels above — is planned work, not something this page can yet point
at.
