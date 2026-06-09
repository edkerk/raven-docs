# Tutorial 3 — Knockouts, MOMA and omics data

This exercise shows how to run FBA and **minimization of metabolic adjustment
(MOMA)** simulations, and how a GEM can serve as a scaffold for interpreting
microarray data. It uses a simplified model of yeast central carbon metabolism
(`smallYeast.xlsx`), which adds metabolite compositions and gene associations
on top of the Tutorial 2 model.

It is assumed you have completed Tutorial 2.

## Step by step

### 1. Import and validate

```matlab
model = importExcelModel('smallYeast.xlsx', true);
model = setParam(model, 'ub', {'glcIN' 'o2IN'}, [1 1000]);
model = setParam(model, 'obj', {'ethOUT'}, 1);
sol = solveLP(model);
printFluxes(model, sol.x, true);
```

Try to reproduce the maximal ATP/ethanol yields from Tutorial 2 (note that
glucose is used here, not sucrose), and calculate the maximal yields of biomass,
ethanol, glycerol and acetate on glucose under aerobic conditions.

### 2. Single gene deletions with FBA

FBA can suggest gene deletions that couple a desired product (here, glycerol) to
growth. After running a deletion scan, keep only solutions that still grow:

```matlab
[genes, fluxes, originalGenes, details] = findGeneDeletions(model, 'sgd', 'fba');

I = getIndexes(model, {'biomassOUT'}, 'rxns');
J = getIndexes(model, {'glyOUT'}, 'rxns');
okSolutions = find(fluxes(I,:) > 10^-2);          % still growing
[maxGlycerol, J] = max(fluxes(J, okSolutions));
disp(maxGlycerol);
disp(originalGenes(genes(okSolutions(J), :)));
```

The strongest hit is the `ZWF1` deletion. Visualise the change:

```matlab
model2 = setParam(model, 'eq', {'ZWF'}, 0);
sol2 = solveLP(model2);
load 'pathway.mat' pathway;
drawMap('ZWF1 deletion vs WT', pathway, model, sol.x, sol2.x, [], 'mapZWF.pdf', 10^-5);
followChanged(model, sol2.x, sol.x, 10, 10^-2, 0, {'NADPH' 'NADH' 'NAD' 'NADP'});
```

### 3. MOMA

FBA assumes the cell re-optimises after a perturbation. **MOMA** instead assumes
the perturbed cell changes its metabolism as little as possible — useful when
you have wild-type data and want to predict a mutant. Provide a constrained
wild-type model and an unconstrained model with `ZWF` knocked out:

```matlab
SBMLFromExcel('smallYeast.xlsx', 'smallYeast.xml');
model = importModel('smallYeast.xml', true);

model2 = model;
I = getIndexes(model, getExchangeRxns(model), 'rxns');
model2.lb(I) = 0;  model2.ub(I) = 1000;
model2 = setParam(model2, 'eq', {'ZWF'}, 0);

[fluxA, fluxB, flag] = qMOMA(model, model2);
drawMap('WT vs ZWF1 (MOMA)', pathway, model, fluxA, fluxB, [], 'mapMOMA.pdf', 10^-5);
```

### 4. Reporter metabolites from microarray data

A GEM can highlight the metabolites around which significant transcriptional
changes cluster. Load expression data (ethanol vs. glucose growth) and run the
reporter-metabolites test:

```matlab
[orfs, pvalues] = textread('expression.txt', '%s%f');
repMets = reporterMetabolites(model, orfs, pvalues);
[I, J] = sort(repMets.metPValues);

fprintf('TOP 10 REPORTER METABOLITES:\n');
for i = 1:min(numel(J), 10)
    fprintf([repMets.mets{J(i)} '\t' num2str(I(i)) '\n']);
end
```

The reactions involving the top reporter metabolites can then be drawn on a
trimmed map with `trimPathway` and `drawMap`.

## Full script

```matlab
--8<-- "RAVEN/tutorial/tutorial3.m"
```
