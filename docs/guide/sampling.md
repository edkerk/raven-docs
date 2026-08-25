# 15. Random sampling

Flux variability gives the extremes a reaction can reach. Sampling gives the
**distribution** in between: draw many flux vectors from the feasible space and
look at how they are spread. A range of 0–10 says nothing about whether the flux
is usually 0, usually 10, or evenly spread; a sample does.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `randomSampling` | `random_sampling` | sample the flux space |
| `sampleACHR` | `random_sampling` (`method='achr'`) | hit-and-run MCMC, the default |
| `sampleCHRR` | `random_sampling` (`method='chrr'`) | hit-and-run with rounding, for thin polytopes |
| — | `find_good_reactions` | reactions usable as random objectives |
| `getAllowedBounds` | `flux_variability_analysis` <span class="cobrapy-tag">cobrapy</span> | the ranges sampling fills in |

## Setup

The same glucose-limited `smallYeast.yml` as [14. Flux variability](fva.md), so
the two pages can be read against each other.

=== "MATLAB"

    ```matlab
    model = readYAMLmodel('smallYeast.yml');
    model = setParam(model, 'ub', {'glcIN', 'o2IN'}, [1 1000]);
    model = setParam(model, 'obj', 'biomassOUT', 1);
    ```

    ```text title="Output"
    ```

=== "Python"

    ```python
    import cobra
    from raven_toolbox.io import read_yaml_model

    cobra.Configuration().processes = 1

    model = read_yaml_model("smallYeast.yml")
    model.reactions.get_by_id("glcIN").upper_bound = 1.0
    model.reactions.get_by_id("o2IN").upper_bound = 1000.0
    model.objective = "biomassOUT"
    ```

    ```text title="Output"
    ```

## 15.1 A first sample

Both toolboxes take a `seed`, and you should always set one: without it a chain
is different every run and nothing you report can be reproduced.

=== "MATLAB"

    ```matlab
    solutions = randomSampling(model, 200, 'seed', 1);
    fprintf('%d reactions x %d samples\n', size(solutions, 1), size(solutions, 2));
    ```

    ```text title="Output"
    53 reactions x 200 samples
    ```

=== "Python"

    ```python
    from raven_toolbox.analysis import random_sampling

    result = random_sampling(model, 200, seed=1)
    print(f"{result.samples.shape[0]} samples x {result.samples.shape[1]} reactions")
    print(f"method: {result.method}")
    ```

    ```text title="Output"
    200 samples x 53 reactions
    method: achr
    ```

!!! warning "The two are transposed"
    RAVEN returns **reactions × samples**; raven-toolbox returns a DataFrame of
    **samples × reactions**, the `cobra.sampling` layout. Every mean, histogram
    and correlation you compute has to pick the right axis, and getting it wrong
    is silent — you get numbers, just not the ones you meant.

## 15.2 What a distribution says that a range does not

[14. Flux variability](fva.md) found that `FRDS2` and `SDH` have the widest
range in this model, 1000 units, and that all of it is a thermodynamically
infeasible cycle. Sampling does not rescue you from that -- it shows how much of
the space the cycle occupies.

=== "MATLAB"

    ```matlab
    idx = getIndexes(model, {'FRDS2', 'biomassOUT'}, 'rxns');
    fprintf('FRDS2  sampled %.1f to %.1f\n', ...
        min(solutions(idx(1), :)), max(solutions(idx(1), :)));
    fprintf('growth sampled %.4f to %.4f, mean %.4f\n', ...
        min(solutions(idx(2), :)), max(solutions(idx(2), :)), mean(solutions(idx(2), :)));
    ```

    ```text title="Output"
    FRDS2  sampled 19.0 to 999.9
    growth sampled 0.0084 to 0.0964, mean 0.0496
    ```

=== "Python"

    ```python
    frds2 = result.samples["FRDS2"]
    growth = result.samples["biomassOUT"]
    print(f"FRDS2  sampled {frds2.min():.1f} to {frds2.max():.1f}")
    print(f"growth sampled {growth.min():.4f} to {growth.max():.4f}, "
          f"mean {growth.mean():.4f}")
    ```

    ```text title="Output"
    FRDS2  sampled 0.6 to 998.4
    growth sampled 0.0098 to 0.0911, mean 0.0534
    ```

The two tabs are separate implementations with separate random number
generators, so their numbers are not expected to match draw for draw — but they
describe the same distribution, and that agreement is the check worth making.

`FRDS2` is sampled across nearly its whole 1000-unit range, so the loop is not
some rare corner of the space: it is most of it, and most of the draws are spent
there. Growth is the opposite. Its range runs from 0 to 0.1222, but the samples
sit between roughly 0.01 and 0.09 and average about 0.05 -- near-uniform
sampling almost never lands on a vertex, and the optimum is a corner with no
volume around it.

That is the distinction this page turns on. A sampled mean is a statement about
the *shape of the feasible space*, not a prediction: this model's mean sampled
growth is less than half its optimum, and no biology changed to make it so.

## 15.3 Choosing a method

`achr` and `chrr` both draw the near-uniform interior distribution;
`randomObjective` (`random_objective` in Python) instead maximises a small
random objective each time, so it returns **vertices** rather than interior
points. Vertices are what FBA gives you, which makes that method a way to survey
alternative optima rather than to describe the space.

=== "MATLAB"

    <!-- run-examples: skip -->

    ```matlab
    [chrrSolutions, ~, info] = randomSampling(model, 200, 'method', 'chrr', 'seed', 1);
    fprintf('chrr: %d dimensions, MVE converged: %d, %d fixed\n', ...
        info.nDimensions, info.mveConverged, numel(info.fixedRxns));
    ```

    ```text title="Output"
    [Warning: The maximum-volume ellipsoid rounding did not converge; the samples may be poorly mixed. Inspect the mveConverged field of the second output.]
    chrr: 9 dimensions, MVE converged: 0, 1 fixed
    ```

    On RAVEN before [#696](https://github.com/SysBioChalmers/RAVEN/pull/696) this
    call fails on `smallYeast` with `sampleChebyshevCenter: LP infeasible - flux
    polytope has empty interior`. The polytope is fine; the equality system is
    square and rank-deficient, so the particular solution came back `NaN`. The
    output above is from a patched RAVEN, and the example runner skips this block
    until the fix is released.

=== "Python"

    ```python
    chrr = random_sampling(model, 200, method="chrr", seed=1)
    print(f"chrr: {chrr.n_dimensions} dimensions, "
          f"MVE converged: {chrr.mve_converged}, "
          f"{len(chrr.fixed_reactions)} fixed")
    ```

    ```text title="Output"
    chrr: 9 dimensions, MVE converged: False, 1 fixed
    ```

The dimension is a property of the polytope, not of the sampler: it is how many
degrees of freedom the network really has once the implicitly-determined
reactions are folded out. A model with 53 reactions has far fewer than 53 — and
the two toolboxes, which implement CHRR separately, both arrive at **9**.

`MVE converged: False` is a warning, not a failure. The rounding step stopped
before reaching its tolerance, so the last ellipsoid is still a valid rounding
and the samples are usable -- but on a polytope this elongated, mixing is slower
than the defaults assume, and more thinning is the answer if the distribution
looks lumpy.

## 15.4 Sample a state, not a model

Sampling an unconstrained model answers "what could this network do?", which is
rarely the question. The useful version is to constrain first — hold growth near
its optimum, fix a measured flux — and sample the space that is left.

=== "MATLAB"

    ```matlab
    sol = solveLP(model);
    atOptimum = setParam(model, 'lb', 'biomassOUT', 0.9 * sol.f);
    constrained = randomSampling(atOptimum, 200, 'seed', 1);
    ethIdx = getIndexes(model, 'ethOUT', 'rxns');
    fprintf('ethanol: free %.2f, at 90%% growth %.2f\n', ...
        mean(solutions(ethIdx, :)), mean(constrained(ethIdx, :)));
    ```

    ```text title="Output"
    ethanol: free 0.80, at 90% growth 0.04
    ```

=== "Python"

    ```python
    at_optimum = model.copy()
    at_optimum.reactions.get_by_id("biomassOUT").lower_bound = 0.9 * model.slim_optimize()
    constrained = random_sampling(at_optimum, 200, seed=1)
    print(f"ethanol: free {result.samples['ethOUT'].mean():.2f}, "
          f"at 90% growth {constrained.samples['ethOUT'].mean():.2f}")
    ```

    ```text title="Output"
    ethanol: free 0.72, at 90% growth 0.04
    ```

## 15.5 Reactions worth sampling over

The `randomObjective` method needs reactions that can carry real flux to use as
objectives. Reactions that move only through a loop are useless for that, so
both toolboxes screen them out with a loopless FVA first — the same test
[14. Flux variability](fva.md) used by hand.

=== "MATLAB"

    ```matlab
    [~, goodRxns] = randomSampling(model, 20, 'method', 'randomObjective', 'seed', 1);
    fprintf('%d of %d reactions usable as objectives\n', numel(goodRxns), numel(model.rxns));
    ```

    ```text title="Output"
    50 of 53 reactions usable as objectives
    ```

=== "Python"

    ```python
    from raven_toolbox.analysis import find_good_reactions

    good = find_good_reactions(model)
    print(f"{len(good)} of {len(model.reactions)} reactions usable as objectives")
    ```

    ```text title="Output"
    50 of 53 reactions usable as objectives
    ```

    Passing the list back as `good_reactions=` on a later call skips the FVA,
    which is worth doing on a genome-scale model — it is the expensive part.

!!! warning "What can go wrong"
    - **No seed.** The numbers change every run. Set one, and report it.
    - **Too little thinning.** Consecutive MCMC steps are correlated; the default
      of 100 steps between recorded samples exists for that reason. Lowering it
      buys speed and costs independence.
    - **Reading a mean as a prediction.** The mean of a sample describes the
      *feasible space*, not the cell. A reaction can average 5 while no
      biologically sensible state has it anywhere near 5.
    - **Sampling a model that is wide open.** With an unconstrained medium the
      space is enormous and the distribution says nothing. Constrain first.
    - **Loops.** They inflate the space being sampled, and every sample drawn
      inside a cycle is wasted. See [14. Flux variability](fva.md).
    - **Genome-scale cost.** Sampling is many LPs per recorded sample. Start with
      a few hundred samples to see the shape, not tens of thousands.

## See also

- [14. Flux variability](fva.md) — the ranges this page fills in.
- [4. Simulating growth with FBA](fba.md) — the single point sampling surrounds.
- [11. Deletions and essentiality](deletions.md) — the other way to ask what the
  model depends on.
