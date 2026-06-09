# Tutorial 1 — Import a GEM, set parameters and run FBA

This short introduction shows how to load a genome-scale metabolic model (GEM),
set reaction constraints and an objective function, run an optimization through
flux balance analysis (FBA), and visualise the resulting fluxes.

The example uses a GEM for the filamentous fungus *Penicillium chrysogenum*
(`iAL1006`), provided both as a Microsoft Excel file (`iAL1006 v1.00.xlsx`) and
in SBML format (`iAL1006 v1.00.xml`).

!!! note
    You must be able to import GEMs in Excel format with `importExcelModel`. If
    that fails, you can import the SBML version with `importModel` instead — but
    then you will not be able to do Tutorials 2–4, which involve editing Excel
    files.

## Step by step

### 1. Import the model

`importExcelModel` performs a number of structural checks while loading. The
`false` flag imports the model with exchange reactions in their "closed" form —
unsuited for modelling, but useful for quality-control steps.

```matlab
model = importExcelModel('iAL1006 v1.00.xlsx', false);
printModelStats(model, true, true);   % list dead-end reactions / unconnected mets
```

The model contains 1632 reactions, 1395 metabolites and 1006 genes.

### 2. Simplify the model

Mass balancing is done around the *internal* metabolites. The "unconstrained"
(boundary) metabolites that let the system take up or excrete compounds must be
removed before simulating. `simplifyModel` also groups linear reactions and
deletes reactions that cannot carry flux.

```matlab
model = simplifyModel(model, true, false, true, true);
```

The model now contains 1305 reactions, 1037 metabolites and 1006 genes.

### 3. Set constraints and an objective, then solve

As a first validation, compute the theoretical yield of CO₂ from glucose. Use
`setParam` to cap glucose uptake at 1 mmol/gDW/h, block ethanol uptake, and set
CO₂ production as the objective.

```matlab
model = setParam(model, 'ub', {'glcIN' 'etohIN'}, [1 0]);
model = setParam(model, 'obj', {'co2OUT'}, 1);
sol = solveLP(model);
printFluxes(model, sol.x, true, 10^-7);   % exchange fluxes only
```

The system takes up 1 glucose and 6 O₂ while producing 6 CO₂ and 6 H₂O.

### 4. Clean up loops

A plain `solveLP` returns an arbitrary solution that often contains loops (many
reactions at ±1000). Passing `1` as the second argument minimises the sum of
fluxes for a more interpretable result.

```matlab
sol = solveLP(model, 1);
printFluxes(model, sol.x, false, 10^-7);   % all fluxes
```

### 5. Optimise for growth and compare carbon sources

```matlab
model = setParam(model, 'obj', {'bmOUT'}, 1);
sol = solveLP(model, 1);

% Growth on ethanol instead of glucose (3× the molar flux, 2 C vs 6 C)
modelETH = setParam(model, 'eq', {'glcIN' 'etohIN'}, [0 3]);
solETH = solveLP(modelETH, 1);
```

The growth rate on glucose is 0.084/h. `followChanged` highlights the reactions
that differ most between the two conditions:

```matlab
followChanged(modelETH, sol.x, solETH.x, 50, 0.5, 0.5);
followChanged(modelETH, sol.x, solETH.x, 30, 0.4, 0.4, {'ATP'});
```

### 6. Visualise on a metabolic map

```matlab
load 'pcPathway.mat' pathway;
drawMap('Glucose vs ethanol', pathway, model, sol.x, solETH.x, modelETH, 'GLCvsETH.pdf', 10^-5);
```

Green reactions are more used for growth on glucose, red for growth on ethanol.
Open `GLCvsETH.pdf` to zoom in on individual reactions.

## Full script

```matlab
--8<-- "RAVEN/tutorial/tutorial1.m"
```
