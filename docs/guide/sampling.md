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
| no equivalent | `find_good_reactions` | reactions usable as random objectives |
| `getAllowedBounds` | `flux_variability_analysis` {bdg-link-secondary}`cobrapy <https://cobrapy.readthedocs.io/en/latest/autoapi/cobra/index.html>` | the ranges sampling fills in |

## Setup

The same glucose-limited `smallYeast.yml` as [14. Flux variability](fva.md), so
the two pages can be read against each other.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
model = readYAMLmodel('smallYeast.yml');
model = setParam(model, 'ub', {'glcIN', 'o2IN'}, [1 1000]);
model = setParam(model, 'obj', 'biomassOUT', 1);
```

```text
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
import cobra
from raven_toolbox.io import read_yaml_model

cobra.Configuration().processes = 1

model = read_yaml_model("smallYeast.yml")
model.reactions.get_by_id("glcIN").upper_bound = 1.0
model.reactions.get_by_id("o2IN").upper_bound = 1000.0
model.objective = "biomassOUT"
```

```text
```
:::
::::

## 15.1 A first sample

Both toolboxes take a `seed`, and you should always set one: without it a chain
is different every run and nothing you report can be reproduced.

A seed does not guarantee identical numbers, though. The Python chain
here reproduces exactly across operating systems; the MATLAB one does not. Its
samplers take a nullspace basis from `null`, which comes from LAPACK, so the
same seed on Linux and on Windows explores the same *distribution* along a
slightly different walk: running this page on both put `FRDS2`'s sampled
minimum at 19.0 and at 18.8. That is why the numbers below are printed to two
decimals: the distribution is the result, the individual draws are not.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
solutions = randomSampling(model, 200, 'seed', 1);
fprintf('%d reactions x %d samples\n', size(solutions, 1), size(solutions, 2));
```

```text
53 reactions x 200 samples
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from raven_toolbox.analysis import random_sampling

result = random_sampling(model, 200, seed=1)
print(f"{result.samples.shape[0]} samples x {result.samples.shape[1]} reactions")
print(f"method: {result.method}")
```

```text
200 samples x 53 reactions
method: achr
```
:::
::::

:::{warning} The two are transposed
RAVEN returns **reactions × samples**; raven-toolbox returns a DataFrame of
**samples × reactions**, the `cobra.sampling` layout. Every mean, histogram
and correlation you compute has to pick the right axis, and getting it wrong
is silent; you get numbers, just not the ones you meant.
:::

## 15.2 What a distribution says that a range does not

[14. Flux variability](fva.md) found that `FRDS2` and `SDH` have the widest
range in this model, 1000 units, and that all of it is a thermodynamically
infeasible cycle. Sampling does not remove that; it shows how much of the space
the cycle occupies.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
idx = getIndexes(model, {'FRDS2', 'biomassOUT'}, 'rxns');
fprintf('FRDS2  sampled %.0f to %.0f\n', ...
    min(solutions(idx(1), :)), max(solutions(idx(1), :)));
fprintf('growth sampled %.2f to %.2f, mean %.2f\n', ...
    min(solutions(idx(2), :)), max(solutions(idx(2), :)), mean(solutions(idx(2), :)));
```

```text
FRDS2  sampled 19 to 1000
growth sampled 0.01 to 0.10, mean 0.05
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
frds2 = result.samples["FRDS2"]
growth = result.samples["biomassOUT"]
print(f"FRDS2  sampled {frds2.min():.0f} to {frds2.max():.0f}")
print(f"growth sampled {growth.min():.2f} to {growth.max():.2f}, "
      f"mean {growth.mean():.2f}")
```

```text
FRDS2  sampled 1 to 998
growth sampled 0.01 to 0.09, mean 0.05
```
:::
::::

The two tabs are separate implementations with separate random number
generators, so their numbers are not expected to match draw for draw, but they
describe the same distribution, and that agreement is the check to make.

`FRDS2` is sampled across nearly its whole 1000-unit range, so the loop is not
some rare corner of the space: it is most of it, and most of the draws land
there. Growth is the opposite. Its range runs from 0 to 0.1222, but the samples
fall between about 0.01 and 0.1 and average about 0.05, because near-uniform
sampling almost never lands on a vertex and the optimum is a corner with no
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

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[chrrSolutions, ~, info] = randomSampling(model, 200, 'method', 'chrr', 'seed', 1);
fprintf('chrr: %d dimensions, MVE converged: %d, %d fixed\n', ...
    info.nDimensions, info.mveConverged, numel(info.fixedRxns));
```

```text
[Warning: The maximum-volume ellipsoid rounding did not converge; the samples may be poorly mixed. Inspect the mveConverged field of the second output.]
chrr: 9 dimensions, MVE converged: 0, 1 fixed
```

On RAVEN before [#696](https://github.com/SysBioChalmers/RAVEN/pull/696) this
call failed on `smallYeast` with `sampleChebyshevCenter: LP infeasible - flux
polytope has empty interior`. The polytope was fine; the equality system is
square and rank-deficient there, and the particular solution came back `NaN`.
If you see that error, update RAVEN.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
chrr = random_sampling(model, 200, method="chrr", seed=1)
print(f"chrr: {chrr.n_dimensions} dimensions, "
      f"MVE converged: {chrr.mve_converged}, "
      f"{len(chrr.fixed_reactions)} fixed")
```

```text
chrr: 9 dimensions, MVE converged: False, 1 fixed
```
:::
::::

The dimension is a property of the polytope, not of the sampler: it is how many
degrees of freedom the network really has once the implicitly-determined
reactions are folded out. A model with 53 reactions has far fewer than 53, and
the two toolboxes, which implement CHRR separately, both compute **9**.

`MVE converged: False` is a warning, not a failure. The rounding step stopped
before reaching its tolerance, so the last ellipsoid is still a valid rounding
and the samples are usable, but on a polytope this elongated mixing is slower
than the defaults assume, and more thinning helps if the distribution
is uneven.

## 15.4 Sample a state, not a model

Sampling an unconstrained model answers "what could this network do?", which is
rarely the question. The useful version is to constrain first (hold growth near
its optimum, fix a measured flux) and sample the space that is left.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
sol = solveLP(model);
atOptimum = setParam(model, 'lb', 'biomassOUT', 0.9 * sol.f);
constrained = randomSampling(atOptimum, 200, 'seed', 1);
ethIdx = getIndexes(model, 'ethOUT', 'rxns');
fprintf('ethanol: free %.2f, at 90%% growth %.2f\n', ...
    mean(solutions(ethIdx, :)), mean(constrained(ethIdx, :)));
```

```text
ethanol: free 0.80, at 90% growth 0.04
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
at_optimum = model.copy()
at_optimum.reactions.get_by_id("biomassOUT").lower_bound = 0.9 * model.slim_optimize()
constrained = random_sampling(at_optimum, 200, seed=1)
print(f"ethanol: free {result.samples['ethOUT'].mean():.2f}, "
      f"at 90% growth {constrained.samples['ethOUT'].mean():.2f}")
```

```text
ethanol: free 0.72, at 90% growth 0.04
```
:::
::::

## 15.5 Which reactions to sample over

The `randomObjective` method needs reactions that can carry real flux to use as
objectives. Reactions that move only through a loop are useless for that, so
both toolboxes screen them out with a loopless FVA first, the same test
[14. Flux variability](fva.md) used by hand.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[~, goodRxns] = randomSampling(model, 20, 'method', 'randomObjective', 'seed', 1);
fprintf('%d of %d reactions usable as objectives\n', numel(goodRxns), numel(model.rxns));
```

```text
50 of 53 reactions usable as objectives
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from raven_toolbox.analysis import find_good_reactions

good = find_good_reactions(model)
print(f"{len(good)} of {len(model.reactions)} reactions usable as objectives")
```

```text
50 of 53 reactions usable as objectives
```

Passing the list back as `good_reactions=` on a later call skips the FVA,
which on a genome-scale model skips the expensive part of the run.
:::
::::

:::{warning} What can go wrong
- **No seed.** The numbers change every run. Set one, and report it, and do
  not expect a seed alone to reproduce a MATLAB chain on another machine
  (see 15.1). Report the distribution, not the draws.
- **Too little thinning.** Consecutive MCMC steps are correlated; the default
  of 100 steps between recorded samples exists for that reason. Lowering it
  gains speed and loses independence.
- **Reading a mean as a prediction.** The mean of a sample describes the
  *feasible space*, not the cell. A reaction can average 5 while no
  individual feasible state puts it near 5.
- **Sampling a model that is wide open.** With an unconstrained medium the
  space is enormous and the distribution says nothing. Constrain first.
- **Loops.** They inflate the space being sampled, and every sample drawn
  inside a cycle is wasted. See [14. Flux variability](fva.md).
- **Genome-scale runtime.** Sampling is many LPs per recorded sample. Start with
  a few hundred samples to see the shape, not tens of thousands.
:::

## See also

- [14. Flux variability](fva.md), the ranges this page fills in.
- [4. Simulating growth with FBA](fba.md), the single point sampling surrounds.
- [11. Deletions and essentiality](deletions.md), the other way to ask what the
  model depends on.
