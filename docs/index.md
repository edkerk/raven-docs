# RAVEN

**Reconstruction, Analysis and Visualization of Metabolic Networks**

A toolkit for building, curating, and simulating genome-scale metabolic
models, available as a MATLAB toolbox and a Python package built on cobrapy.

MIT license · Python ≥ 3.11 · MATLAB R2016b+ · cobrapy · SBML · Gurobi · GLPK
· Windows · macOS · Linux · DOI
[10.1371/journal.pcbi.1006541](https://doi.org/10.1371/journal.pcbi.1006541)

## Install

::::{tab-set}
:::{tab-item} Python (pip)

```bash
pip install raven-toolbox
```
:::
:::{tab-item} MATLAB (Add-Ons)

Home → Add-Ons → Get Add-Ons → search "RAVEN Toolbox"
:::
:::{tab-item} Python (git)

```bash
git clone https://github.com/SysBioChalmers/raven-toolbox.git
pip install -e raven-toolbox/
```
:::
:::{tab-item} MATLAB (git)

```bash
git clone --depth=1 https://github.com/SysBioChalmers/RAVEN.git
```
:::
::::

## Key features

::::{grid} 1 2 3 3

:::{grid-item-card} Homology reconstruction
Build draft models by transferring reactions from template models using
BLAST+, DIAMOND, or HMMER.
:::

:::{grid-item-card} KEGG-based reconstruction
Reconstruct metabolic networks directly from KEGG organism annotations and
pathway databases.
:::

:::{grid-item-card} Flux analysis
FBA, FVA, gene knockouts, and flux sampling with Gurobi or GLPK solvers.
:::

:::{grid-item-card} ftINIT
Fast task-and-data-driven INIT for extracting context-specific models from
transcriptomics data.
:::

:::{grid-item-card} Gap-filling
Identify and fill stoichiometric gaps by LP to restore connectivity or
enable predicted growth.
:::

:::{grid-item-card} Model curation
Check mass and charge balance, dead-end metabolites, and metabolic task
fulfilment.
:::

::::

## Quick start

::::{tab-set}
:::{tab-item} Python

```python
from raven_toolbox.io import read_yaml_model

# load yeast-GEM from RAVEN YAML -- returns a plain cobra.Model
model = read_yaml_model("yeast-GEM.yml")

# set growth as the objective
model.objective = "r_2111"

# constrain glucose uptake to 1 mmol/gDW/h
model.reactions.get_by_id("r_1714").lower_bound = -1.0

# run FBA -- simulation comes from cobrapy, unchanged
sol = model.optimize()
print(f"Growth rate: {sol.objective_value:.4f} h⁻¹")
```
:::
:::{tab-item} MATLAB

```matlab
% load yeast-GEM from RAVEN YAML
model = readYAMLmodel('yeast-GEM.yml');

% set growth as the objective
model = setParam(model, 'obj', 'r_2111', 1);

% constrain glucose uptake to 1 mmol/gDW/h
model = setParam(model, 'lb', 'r_1714', -1);

% run FBA
sol = solveLP(model);
fprintf('Growth rate: %.4f h-1\n', sol.f);
```
:::
::::

## Documentation

::::{grid} 1 2 2 2

:::{grid-item-card} User guide
:link: guide/index
:link-type: doc

Nineteen task-focused pages, MATLAB and Python side by side, every example
executed and checked on each commit.
:::

:::{grid-item-card} API reference
:link: api/index
:link-type: doc

Complete function reference for both MATLAB and Python.
:::

:::{grid-item-card} Installation
:link: installation/index
:link-type: doc

Set up RAVEN in MATLAB or raven-toolbox in Python with a solver.
:::

:::{grid-item-card} RAVEN 3 and raven-toolbox
:link: raven3-vs-raven-toolbox
:link-type: doc

Which to use for what, what only one of them has, and where the same
function gives a different answer.
:::

::::

## Citing RAVEN

If you use RAVEN in your research, please cite:

> Wang H, Marcišauskas S, Sánchez BJ, Domenzain I, Hermansson D, Agren R,
> Nielsen J, Kerkhoven EJ (2018). **RAVEN 2.0: A versatile toolbox for
> metabolic network reconstruction and a case study on *Streptomyces
> coelicolor*.** *PLoS Computational Biology* 14(10): e1006541.
> <https://doi.org/10.1371/journal.pcbi.1006541>

> Agren R, Liu L, Shoaie S, Vongsangnak W, Nookaew I, Nielsen J (2013).
> **The RAVEN toolbox and its use for generating a genome-scale metabolic model
> for *Penicillium chrysogenum*.** *PLoS Computational Biology* 9(3): e1002980.
> <https://doi.org/10.1371/journal.pcbi.1002980>

If you use the GEM reconstruction protocol, also cite:

> Zorrilla F, Kerkhoven EJ (2022). **Reconstruction of Genome-Scale Metabolic
> Model for *Hansenula polymorpha* Using RAVEN.** In: Mapelli V, Bettiga M
> (eds), *Yeast Metabolic Engineering: Methods and Protocols*, Methods in
> Molecular Biology, vol. 2513. Humana, New York, NY, pp. 271–290.
> <https://doi.org/10.1007/978-1-0716-2399-2_16>

See [References](references.md) for the full list including methods cited in the protocol.

```{toctree}
:hidden:

guide/index
migrate
reference
parameter-tuning/index
```
