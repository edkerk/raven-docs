# Tutorial 2 — Construct a functional small model

This exercise deals with a small glycolysis model in RAVEN-compatible Excel
format and shows the most basic aspects of stoichiometric modelling: building a
model from scratch, setting parameters and running simple simulations.

You will edit `empty.xlsx` (which already contains the first reaction of
glycolysis) until it reproduces the provided solution model `small.xlsx`. The
companion script `tutorial2_solutions.m` imports `small.xlsx` directly.

!!! question "Goal"
    Build a model of glycolysis and answer: **how many units of ATP can be
    generated from one unit of sucrose?**

## Step by step

### 1. Import the starter model

```matlab
smallModel = importExcelModel('empty.xlsx');
sol = solveLP(smallModel);
printFluxes(smallModel, sol.x, true);
```

When you import the (incomplete) model, RAVEN warns that some internal
metabolites are used in only one reaction:

```text
WARNING: The following internal metabolite(s) are only used in one reaction
(zero flux is the only solution):
 (m13 [c]) H2O   (m15 [c]) NAD+   (m18 [c]) phosphate
 (m14 [e]) H2O   (m16 [c]) NADH   (m19 [c]) pyruvate   (m20 [e]) sucrose
```

### 2. Understand internal vs. external metabolites

Under the steady-state assumption, the production rate of each *internal*
metabolite must equal its consumption rate. A metabolite that participates in
only one reaction can therefore carry no flux. The fix is to introduce
**external (boundary) metabolites**, which need not be mass-balanced: they are
flagged `true` in the `UNCONSTRAINED` field of the `METS` sheet and live, by
convention, in the boundary compartment `b`. Reactions involving them are
**exchange reactions**.

### 3. Add the glycolysis reactions and exchanges

In Excel, add the remaining 11 reactions (you may use short abbreviations such
as `g6p`). Then add exchange and transport reactions so that the cell can take
up sucrose and excrete pyruvate and water, for example:

```text
sucrose[b] => sucrose[e]
```

Save often and re-run `importExcelModel` to check the structure.

### 4. Handle cofactors and define the objective

Two problems remain:

- **Regenerating NAD⁺ from NADH.** Either extend the model (e.g. ethanol
  production via pyruvate decarboxylase + alcohol dehydrogenase) or add "fake"
  exchange reactions for NAD⁺/NADH.
- **Measuring ATP yield.** Add a "fake" ATP hydrolysis reaction and maximise its
  flux — because production must match consumption, this reports how much ATP
  the network can make. Watch the directionality so you don't accidentally allow
  free ATP synthesis.

Constrain only the exchange reactions: set the sucrose uptake `UPPER BOUND` to
`1.0` and put `1` in the `OBJECTIVE` column for the ATP-hydrolysis reaction.

### 5. Solve

```matlab
smallModel = importExcelModel('empty.xlsx');   % your completed model
sol = solveLP(smallModel);
printFluxes(smallModel, sol.x, true);          % exchange fluxes; check C balance
printFluxes(smallModel, sol.x, false, 10^-5, [], '%rxnID (%rxnName):\n\t%eqn\n\t%flux\n');
```

??? success "Answer to Question 1"
    **4 mol ATP per mol sucrose.**

## Full script

```matlab
--8<-- "RAVEN/tutorial/tutorial2.m"
```
