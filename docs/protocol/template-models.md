# 3.2 Import template models

RAVEN creates a draft GEM by using models of phylogenetically related organisms
as templates. For *H. polymorpha*, the *S. cerevisiae* model (yeast-GEM) is the
primary template and the *R. toruloides* model (rhto-GEM) the complementary one.

## Load the primary template

`importModel` loads an SBML file into a RAVEN-format MATLAB structure:

```matlab
modelSce = importModel('yeastGEM.xml');
```

yeast-GEM is written by the COBRA Toolbox, which appends the compartment to each
metabolite ID. RAVEN keeps the compartment in a separate field (`.metComps`), so
the redundant suffix is removed, and the model is given the id `sce` (used later
by `getModelFromHomology` to match the model with its protein FASTA):

```matlab
modelSce.mets = regexprep(modelSce.mets, '\[[a-z]+\]$', '');
modelSce.id = 'sce';
```

## Inspect the model

It is often easier to browse a model as a spreadsheet. `exportToExcelFormat`
writes an `.xlsx` with five sheets — `RXNS`, `METS`, `COMPS`, `GENES` and
`MODEL`:

```matlab
exportToExcelFormat(modelSce, 'modelSce.xlsx');
```

!!! tip "Use a scrap folder"
    During reconstruction you often write files you don't want to track in git.
    The hanpo-GEM repository keeps these in a `scrap/` folder that is excluded
    from version control.

Make changes to the model **in MATLAB**, not in the Excel file, and export to
SBML when desired:

```matlab
exportModel(modelSce, 'modelSce.xml');
```

## Load the complementary template

The *R. toruloides* model is loaded the same way. It was written by RAVEN, so it
has no redundant compartment suffix to clean up:

```matlab
modelRhto = importModel('rhto.xml', true);
modelRhto.id = 'rhto';
```

It can be useful to store intermediate states of the MATLAB workspace so you can
resume later:

```matlab
save('scrap/importModels.mat')
% load('scrap/importModels.mat')
```

Next: [Draft from homology](homology.md).
