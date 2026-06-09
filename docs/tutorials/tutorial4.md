# Tutorial 4 — Fix an erroneous model

The power of GEMs comes from their size — but that size makes errors almost
inevitable, whether you build a model yourself or use someone else's. This
exercise is a systematic round of quality control on a deliberately broken
version of the small yeast model.

Model validation is **iterative**: some errors only surface once others are
fixed. The RAVEN philosophy is that it is more valuable to try to make a model
do something it *should not* (e.g. create mass from nothing) than to test only
for what it should do.

`tutorial4.m` leaves several gaps for you to fill; the completed version is in
`tutorial4_solutions.m`. Most of these checks are also wrapped by the
`gapReport` function, but doing them step by step is far more instructive.

## Step by step

### 1. Can the model make something from nothing?

With all uptake closed, maximise the sum of producing exchange reactions. Any
non-zero solution is a problem.

### 2. Provoke hidden errors

An error may be masked because it costs energy or redox power. Relax constraints
and add temporary "free" cofactor reactions (ATP ⇌ ADP + Pᵢ, and similar for
NADH/NADPH) to provoke the model, then minimise the sum of fluxes for an
interpretable solution:

```matlab
sol = solveLP(model, 1);
printFluxes(model, sol.x, false, 10^-5, [], '%rxnID (%rxnName):\n\t%eqn\n\t%flux\n');
```

??? success "Answer to Question 2 — production of ethanol from nothing"
    `ADH1` is unbalanced. Change
    `acetaldehyde[c] + NADH[c] => 2 ethanol[c] + NAD(+)[c]` to
    `acetaldehyde[c] + NADH[c] => ethanol[c] + NAD(+)[c]`.

### 3. Allow every metabolite to be excreted

Add a second column to `model.b` so RAVEN treats it as lower/upper bounds on the
equality constraints — letting anything be excreted. This exposes errors that
need a partner metabolite to be dumped. The SBML-from-Excel warnings point at
the unbalanced reactions.

```matlab
model.b = [model.b inf(numel(model.b), 1)];
```

??? success "Answer to Question 3 — two unbalanced reactions"
    `FBP`: change `… => 2 beta-D-fructofuranose 6-phosphate[c] + phosphate[c]`
    to `… => beta-D-fructofuranose 6-phosphate[c] + phosphate[c]`.
    `PFK`: change `… => ADP[c] + 2 beta-D-fructofuranose 1,6-bisphosphate[c]`
    to `… => ADP[c] + beta-D-fructofuranose 1,6-bisphosphate[c]`.

### 4. `canProduce` / `canConsume`

```matlab
I = canConsume(model);
disp(model.mets(I));
```

`canConsume` reports metabolites the model can consume even when no production is
allowed. Force the uptake of one (set its lower bound non-zero) and relax
`model.b` to allow uptake of all metabolites, then study the fluxes.

??? success "Answer to Question 4"
    `PDC` is missing a product. Change `pyruvate[c] => acetaldehyde[c]` to
    `pyruvate[c] => acetaldehyde[c] + CO2[c]`.

### 5. Naming errors with `simplifyModel`

Switch to `smallYeastBad2.xlsx`. Metabolites that are meant to be the same but
named differently create dead ends. `simplifyModel` removes reactions that
cannot carry flux, which you can use to spot them; check the `importExcelModel`
warnings for the obvious spelling error.

```matlab
[reducedModel, deletedReactions, deletedMetabolites] = ...
    simplifyModel(model, false, false, false, true);
```

??? success "Answer to Question 5 — spelling error"
    `6-O-phosphono-D-glucono-1,5-lactonec]` in `ZWF1` should be
    `6-O-phosphono-D-glucono-1,5-lactone[c]`.

### 6. `checkProduction` and gap-filling

```matlab
[notProducedMets, ~, neededForProductionMat, minToConnect] = ...
    checkProduction(model, true, model.comps, false);
disp(minToConnect);

refModel = importExcelModel('smallYeast.xlsx');
[newConnected, cannotConnect, addedRxns, newModel] = fillGaps(model, {refModel}, false);
disp(addedRxns);
```

`checkProduction` reports the smallest set of metabolites that must be
synthesised for everything else to be producible; ignore the cofactors and look
at the top non-cofactor hit.

??? success "Answer to Question 6 — suspicious similarity"
    Dihydroxyacetone phosphate (DHAP) and glycerone phosphate (GLYP) are the
    same metabolite.

Finally, fill remaining gaps from a reference model (here the Tutorial 3 small
yeast model) with `fillGaps`. And remember: `gapReport` automates this whole
workflow.

## Full script

```matlab
--8<-- "RAVEN/tutorial/tutorial4.m"
```
