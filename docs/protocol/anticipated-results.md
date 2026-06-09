# Anticipated results

Following this protocol yields a **draft** genome-scale metabolic model for
*Hansenula polymorpha* (`hanpo-GEM`) that:

- is reconstructed by homology from the *S. cerevisiae* (yeast-GEM) and
  *R. toruloides* (rhto-GEM) templates;
- has an organism-specific biomass composition (DNA, RNA, protein, carbohydrate
  and SLIME-based lipids);
- is gap-filled so it can **produce biomass** on glycerol; and
- after manual curation can also **grow on methanol**, consistent with
  *H. polymorpha* being a methylotroph.

The published hanpo-GEM (the curated result distributed in the repository)
contains on the order of **2,370 reactions, 2,118 metabolites and 984 genes** —
your draft will be in the same ballpark but is expected to differ, since it is a
starting point for the open-ended process of manual curation.

## What "done" looks like

A successful draft returns a positive growth rate from FBA:

```matlab
sol = solveLP(model, 1);
printFluxes(model, sol.x, false);
```

and, after the methanol curation, still grows when glycerol/glucose uptake is
blocked and only methanol uptake is allowed.

## Beyond the draft

Manual curation is open-ended. Typical next steps include constraining the model
with measured uptake/excretion rates, validating predicted gene essentiality
against experimental data, expanding organism-specific pathways, and improving
annotations. The model is version-controlled (`newCommit`, `newRelease`) so each
curation is tracked and the model can be distributed.

## The complete protocol script

The full, runnable reconstruction — the authoritative version of every command
on these pages — is the
[`reconstructionProtocol.m`](https://github.com/SysBioChalmers/hanpo-GEM/blob/main/code/reconstructionProtocol.m)
script in the hanpo-GEM repository, reproduced here:

```matlab
--8<-- "hanpo-GEM/code/reconstructionProtocol.m"
```
