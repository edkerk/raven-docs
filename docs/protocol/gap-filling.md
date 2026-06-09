# 3.6 Perform gap-filling

Homology-based draft models tend to have many **gaps** — missing reactions that
break a pathway needed to produce biomass macromolecules. The pathway is likely
functional in the template, but `getBlast`/`getModelFromHomology` cannot always
find a homolog for every gene, leaving the pathway incomplete. Gap-filling
identifies and resolves these gaps so the draft becomes a functional model.

RAVEN's `fillGaps` adds the smallest set of reactions from the template models
needed to support flux through the draft.

## Force biomass production

Gap-filling is set up to support growth on glycerol as carbon source with
biomass production as objective. The model is forced to carry a small non-zero
biomass flux, and glycerol uptake is raised so the fluxes stay above the MILP
solver tolerance:

```matlab
model = setParam(model, 'obj', 'r_4041', 1);
model = setParam(model, 'lb', 'r_4041', 0.01);   % force biomass production
model = setParam(model, 'lb', 'r_1808', -10);    % allow glycerol uptake
```

## Prepare the template models

Gaps should be resolved with enzymatic and transport reactions, **not** new
exchange reactions (which could, e.g., introduce other carbon sources). So all
exchange reactions — and the biomass pseudoreactions — are removed from the
template copies used as the reaction source. Reactions already shared between the
two templates are also dropped to shrink the MILP search space:

```matlab
modelSce2  = removeReactions(modelSce,  getExchangeRxns(modelSce, 'both'), true, true, true);
modelRhto2 = removeReactions(modelRhto, getExchangeRxns(modelRhto, 'both'), true, true, true);
rxns       = intersect(modelSce2.rxns, modelRhto2.rxns);
modelRhto2 = removeReactions(modelRhto2, rxns);
```

## Run `fillGaps`

```matlab
[~, ~, addedRxns, model] = fillGaps(model, {modelSce2, modelRhto2}, false, true);
```

Setting `allowNetProduction` to `false` prevents additional exchange reactions,
and `useModelConstraints` to `true` ensures the glycerol-to-biomass flux is gap-
filled. Verify that the model now grows, then scale the lipids and restore the
carbon-uptake bounds:

```matlab
sol = solveLP(model, 1);
printFluxes(model, sol.x);
model = scaleLipids(model, 'tails');

model = setParam(model, 'lb', 'r_1808', -1);   % carbon source back to 1 mmol/gDCW/h
model = setParam(model, 'lb', 'r_4041', 0);
model = deleteUnusedGenes(model);
```

The model can now produce all the macromolecules that constitute *H. polymorpha*
biomass.

!!! tip "Semi-automatic gap analysis"
    Beyond automated `fillGaps`, RAVEN offers functions to *find* gaps:
    `canProduce` and `canConsume` (net synthesis/consumption of metabolites),
    `checkProduction` (smallest set of metabolites needing net synthesis),
    `getAllSubGraphs` (disconnected subnetworks) and `haveFlux` (reactions that
    can/cannot carry flux). Absence of a biomass macromolecule from `canProduce`
    indicates a gap.

Next: [Save and simulate](simulation.md).
