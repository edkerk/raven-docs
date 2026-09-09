# 21. Table-driven curation

Curation done one function call at a time is hard to review and harder to repeat.
Both toolboxes can instead take the curation as **tables**: one row per
metabolite, gene or reaction, in tab-separated files that a spreadsheet can edit
and a pull request can diff.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `curateModelFromTables` | `batch_curate_from_tsv` | apply curation tables from files |
| `curateModelFromTables` | `batch_curate` | the same, from DataFrames already in memory |

## The tables

Four tables, each optional, except that the two reaction tables go together:

| Table | Columns |
|---|---|
| metabolites | `metNames`, `comps`, `formula`, `charge`, `inchi`, `metNotes`, then one column per MIRIAM namespace |
| genes | `genes`, `geneShortNames`, then MIRIAM |
| reactions | `rxnIdx`, `rxnNames`, `grRules`, `lb`, `ub`, `rev`, `subSystems`, `eccodes`, `rxnNotes`, `rxnReferences`, `rxnConfidenceScores`, then MIRIAM |
| reaction coefficients | `rxnIdx`, `rxnNames`, `metNames`, `comps`, `coefficient`, one row per reaction and metabolite |

Entities are matched by **name**, not by identifier: metabolites on
`metaboliteName[comp]`, genes on the gene name, reactions on the stoichiometry of
their reactants and products. A row that matches nothing adds a new entity; a row
that matches an existing one overwrites it. `rxnIdx` ties the two reaction tables
together and is local to the files, not an identifier in the model.

## Setup

`smallYeast.yml` and [`curation-mets.tsv`](../data/curation-mets.tsv) from
[`docs/data/`](../data/README.md). The model carries formulas but no charges,
which is why the charge half of a mass balance is undecidable in
[1. Getting started](getting-started.md). The table supplies four of them.

```text title="curation-mets.tsv"
metNames	comps	formula	charge	metNotes
(S)-malate	m	C4H6O5	-2	charge assigned at pH 7.3
2-oxoglutarate	m	C5H6O5	-2	charge assigned at pH 7.3
2-phospho-D-glycerate	c	C3H7O7P	-3	charge assigned at pH 7.3
3-phospho-D-glycerate	c	C3H7O7P	-3	charge assigned at pH 7.3
```

## 21.1 Apply a table

=== "MATLAB"

    ```matlab
    model = readYAMLmodel('smallYeast.yml');
    fprintf('before: metCharges %d, metNotes %d\n', ...
        isfield(model, 'metCharges'), isfield(model, 'metNotes'));

    curated = curateModelFromTables(model, 'curation-mets.tsv');
    fprintf('after:  metCharges %d, metNotes %d\n', ...
        isfield(curated, 'metCharges'), isfield(curated, 'metNotes'));

    idx = getIndexes(curated, 'MAL_m', 'mets');
    fprintf('%s formula %s\n', curated.metNames{idx}, curated.metFormulas{idx});
    ```

    ```text title="Output"
    before: metCharges 0, metNotes 0
    [Warning: The following metabolites are already present in the model, their annotation will be overwritten to match the metsInfo file. If you do not particularly want to curate their annotations, it would be better to removes these metabolites from metsInfo: (S)-malate[m]
    		2-oxoglutarate[m]
    		2-phospho-D-glycerate[c]
    		3-phospho-D-glycerate[c]]
    after:  metCharges 0, metNotes 0
    (S)-malate formula C4H6O5
    ```

    A model with no charges has no `metCharges` field at all, rather than a field
    full of `NaN`. RAVEN's optional fields work this way throughout, so code that
    reads one should check with `isfield` first.

    Both fields are still absent afterwards, and that is the point of the
    example. `curateModelFromTables` writes an optional field onto an
    **existing** metabolite only when the model already carries that field.
    `smallYeast.yml` has neither `metCharges` nor `metNotes`, so both columns are
    dropped for these four rows, silently. `metFormulas` does exist, so the
    formula column is applied. A metabolite the table *adds* is unaffected: it
    arrives with every field the table supplies.

    `curateModelFromTables` returns a new struct and leaves its input alone, in
    keeping with the rest of RAVEN.

=== "Python"

    ```python
    from raven_toolbox.curation import batch_curate_from_tsv
    from raven_toolbox.io import read_yaml_model

    model = read_yaml_model("smallYeast.yml")
    print("charges before:", sum(1 for m in model.metabolites if m.charge is not None))

    result = batch_curate_from_tsv(model, mets_tsv="curation-mets.tsv")
    print("charges after: ", sum(1 for m in model.metabolites if m.charge is not None))
    print("updated:", result.updated_metabolites)

    mal = model.metabolites.get_by_id("MAL_m")
    print(f"{mal.name} charge {mal.charge}")
    ```

    ```text title="Output"
    charges before: 0
    charges after:  4
    updated: ['MAL_m', 'AKG_m', 'P2G_c', 'P3G_c']
    (S)-malate charge -2
    ```

    `batch_curate_from_tsv` edits the model **in place** and returns a
    `CurationResult` listing what was added and what was updated, split by entity
    type. It warns when a row overwrites an existing entity, naming the ids, so a
    table meant to add is easy to tell from one that quietly replaced something.

    `batch_curate` takes the same four tables as DataFrames, for a pipeline that
    builds them rather than reading them from disk.

!!! warning "An absent field silently swallows a column"
    The same table gives two different results on a model that lacks the field
    being curated. raven-toolbox sets the value on every matched metabolite,
    creating the attribute as needed. RAVEN sets it only on metabolites the table
    *adds*, and drops the column for metabolites that already exist, because the
    field it would write into is not there and it does not create it.

    So a table written to add charges to an uncharged model does nothing in
    MATLAB and works in Python. Check the field afterwards rather than assuming
    the table was applied in full, and note that this is a divergence between the
    two toolboxes rather than a difference in the tables.

## 21.2 Adding rather than updating

A row whose name matches nothing in the model adds a new entity, and the
identifier is minted rather than taken from the file. Both toolboxes find the
largest existing zero-padded number carrying the prefix and count on from there,
so the new ids continue the model's own scheme.

The prefixes are arguments: `metPrefix` and `rxnPrefix` in MATLAB,
`met_id_prefix` and `rxn_id_prefix` in Python. Their defaults are `M_` and `R_`,
the cobrapy and BiGG convention. A yeast-GEM-derived model wants `s_` and `r_`
instead, and passing the wrong ones leaves a model with two id schemes in it.

Adding a reaction needs both reaction tables. The row in the reactions table
carries the bounds, the gene rule and the annotation; the rows in the
coefficients table carry the stoichiometry, one per metabolite, negative for
substrates and positive for products, linked by `rxnIdx`. Any metabolite named
there that the model does not have is created, which is why the metabolite table
is usually applied in the same pass.

!!! warning "A blank cell is an instruction, not an omission"
    In MATLAB an empty cell **overwrites** the model's existing value, so a table
    written to fix one charge will erase every annotation whose column is present
    but blank. In Python an empty cell reads as `NaN` and that field is skipped
    instead. The safe habit for both: include only the columns being curated, and
    keep the values that should survive in the file rather than trusting the
    blank.

!!! warning "What can go wrong"
    - **Matching on names that do not match.** A trailing space, a different
      capitalisation, or `name[comp]` written with the wrong compartment, and the
      row adds a duplicate entity instead of curating the one meant.
    - **Reactions matched on stoichiometry.** Two reactions with the same
      reactants and products, differing only in direction or bounds, are one
      reaction to the matcher.
    - **The wrong id prefix.** The default is `M_`/`R_`. On a model using `s_`
      and `r_` the additions are still correct, but their ids will not look like
      anything else in the model.
    - **No record of what changed.** The tables are the record. Commit them
      alongside the model, or the curation is as unreviewable as the function
      calls it replaced.

## See also

- [8. Editing an existing model](editing.md), the same changes one call at a
  time.
- [9. Quality control](quality-control.md), checking what a curation pass did.
- [3. Reading and writing models](io.md), the Excel format, which is the other
  tabular route in and out.
