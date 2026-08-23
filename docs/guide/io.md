# 3. Reading and writing models

Get a model in and out of both toolboxes: SBML, RAVEN YAML, Excel, tab-delimited
text, and the directory layout a Git-maintained model repository expects.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `importModel` | `read_sbml_model` <span class="cobrapy-tag">cobrapy</span> | read SBML |
| `exportModel` | `write_sbml_model` <span class="cobrapy-tag">cobrapy</span> | write SBML |
| `readYAMLmodel` | `read_yaml_model` | read RAVEN YAML |
| `writeYAMLmodel` | `write_yaml_model` | write RAVEN YAML |
| `exportToExcelFormat` | `export_to_excel` | write the RAVEN Excel format |
| `exportToTabDelimited` | `export_to_excel` (path) | write tab-delimited text |
| `exportForGit` | `export_for_git` | write a Standard-GEM repository layout |

## Setup

This page uses two models from [`docs/data/`](../data/README.md):
`smallYeast.yml` (RAVEN YAML, 45 kB) and `yeast-GEM.xml` (SBML, yeast-GEM v9.1.0).

## 3.1 Read a model

Which function you need depends on the file format, not on the model.

=== "MATLAB"

    ```matlab
    modelSmall = readYAMLmodel('smallYeast.yml');
    modelYeast = importModel('yeast-GEM.xml');

    fprintf('%s %d reactions\n', modelSmall.id, numel(modelSmall.rxns));
    fprintf('%s %d reactions\n', modelYeast.id, numel(modelYeast.rxns));
    ```

    ```text title="Output"
    [Warning: The following fields have prefixes removed from all entries. If this is undesired, run importModel with removePrefix as false. Example: importModel('filename.xml',[],false);]
    smallYeast 53 reactions
    yeastGEM_v9.1.0 4102 reactions
    ```

    `importModel` strips the `R_`, `M_`, `G_` and `C_` prefixes that SBML
    requires on identifiers, provided every identifier of that type carries one.
    Pass `removePrefix` as `false` to keep them.

=== "Python"

    ```python
    from cobra.io import read_sbml_model

    from raven_toolbox.io import read_yaml_model

    small = read_yaml_model("smallYeast.yml")
    yeast = read_sbml_model("yeast-GEM.xml")

    print(small.id, len(small.reactions), "reactions")
    print(yeast.id, len(yeast.reactions), "reactions")
    ```

    ```text title="Output"
    smallYeast 53 reactions
    yeastGEM_v9__46__1__46__0 4102 reactions
    ```

    `read_sbml_model` is cobrapy's and strips the same SBML prefixes.
    `read_yaml_model` is raven-toolbox's, and returns a plain `cobra.Model`, so
    the two are interchangeable from here on.

## 3.2 Watch the identifier mangling

SBML identifiers must be valid XML names, so they cannot contain a dot. Model,
reaction and metabolite ids that do are encoded on the way out and stay encoded
on the way back in — the same model read from YAML and from SBML does not
necessarily report the same id.

=== "MATLAB"

    ```matlab
    disp(modelYeast.id);        % from yeast-GEM.xml
    modelFromYaml = readYAMLmodel('yeast-GEM.yml');
    disp(modelFromYaml.id);     % same release, unencoded
    ```

    ```text title="Output"
    yeastGEM_v9.1.0
    yeastGEM_v9.1.0
    ```

=== "Python"

    ```python
    print("from SBML:", yeast.id)

    from_yaml = read_yaml_model("yeast-GEM.yml")
    print("from YAML:", from_yaml.id)
    print("same size:", len(from_yaml.reactions) == len(yeast.reactions))
    ```

    ```text title="Output"
    from SBML: yeastGEM_v9__46__1__46__0
    from YAML: yeastGEM_v9.1.0
    same size: True
    ```

    `__46__` is an encoded `.`. Only the *identifiers* are affected; the model is
    the same. Reach for the id in `model.name` or the annotation when you need
    something human-readable.

!!! note "Each toolbox is slow in the other's favourite format"
    Reading yeast-GEM takes about **17 s from SBML and 73 s from YAML in
    Python**, and about **78 s from SBML and 17 s from YAML in MATLAB** — the
    ranking is reversed. RAVEN parses YAML itself and goes through libSBML for
    SBML; cobrapy has the opposite balance. Pick the format for what you need
    from it — a readable diff, or the RAVEN-specific fields YAML preserves — and
    if a script is slow, try the other one before optimising anything else.

## 3.3 Write a model

=== "MATLAB"

    ```matlab
    writeYAMLmodel(modelSmall, 'smallYeast-copy.yml');
    exportModel(modelSmall, 'smallYeast.xml');

    roundtrip = importModel('smallYeast.xml');
    fprintf('%d %d %d\n', numel(roundtrip.rxns), numel(roundtrip.mets), ...
        numel(roundtrip.genes));
    ```

    ```text title="Output"
    [Warning: The following fields have one or more entries that do not start with a letter or _ (conflicting with SBML specifications). Prefixes are added to all entries in those fields:]
    Document written
    [Warning: The following fields have prefixes removed from all entries. If this is undesired, run importModel with removePrefix as false. Example: importModel('filename.xml',[],false);]
    53 52 61
    ```

=== "Python"

    ```python
    from cobra.io import write_sbml_model

    from raven_toolbox.io import write_yaml_model

    write_yaml_model(small, "smallYeast-copy.yml")
    write_sbml_model(small, "smallYeast.xml")

    roundtrip = read_sbml_model("smallYeast.xml")
    print(len(roundtrip.reactions), len(roundtrip.metabolites), len(roundtrip.genes))
    ```

    ```text title="Output"
    53 52 61
    ```

Both writers take `sortIds` / `sort_ids` to sort reactions, metabolites and genes
by identifier first, which keeps the diff between two versions of a model small.

## 3.4 Spreadsheets and text

The Excel format is the one people curate by hand; the tab-delimited one is what
you grep.

=== "MATLAB"

    ```matlab
    exportToExcelFormat(modelSmall, 'smallYeast.xlsx');

    mkdir('txt');
    exportToTabDelimited(modelSmall, 'txt/');
    fprintf('%s\n', strjoin({dir('txt/*.txt').name}, ', '));
    ```

    ```text title="Output"
    excelComps.txt, excelGenes.txt, excelMets.txt, excelModel.txt, excelRxns.txt
    ```

=== "Python"

    ```python
    from raven_toolbox.io import export_to_excel

    export_to_excel(small, "smallYeast.xlsx")

    from openpyxl import load_workbook

    print(load_workbook("smallYeast.xlsx").sheetnames)
    ```

    ```text title="Output"
    ['RXNS', 'METS', 'COMPS', 'GENES', 'MODEL']
    ```

    `export_to_excel` needs the `excel` extra (`pip install raven-toolbox[excel]`).
    raven-toolbox has no separate tab-delimited writer; use pandas on the model's
    collections, or the Excel file, whichever suits.

## 3.5 Export for a model repository

A Git-maintained model repository (yeast-GEM, Human-GEM, and the models built
from `standard-GEM`) keeps the same model in several formats under `model/`, so
that a release is usable without a toolbox and a diff is readable in a pull
request. Both toolboxes write that layout directly.

=== "MATLAB"

    ```matlab
    exportForGit(modelSmall, 'prefix', 'smallYeast', 'path', 'repo', ...
        'formats', {'yml', 'xml'});

    written = dir(fullfile('repo', 'model', '**', '*'));
    written = written(~[written.isdir]);
    fprintf('%s\n', strjoin(sort({written.name}), ', '));
    ```

    ```text title="Output"
    [Warning: The following fields have one or more entries that do not start with a letter or _ (conflicting with SBML specifications). Prefixes are added to all entries in those fields:]
    Document written
    dependencies.txt, smallYeast.xml, smallYeast.yml
    ```

=== "Python"

    ```python
    from pathlib import Path

    from raven_toolbox.io import export_for_git

    root = export_for_git(small, "repo", prefix="smallYeast", formats=("yml", "xml"))
    print(sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()))
    ```

    ```text title="Output"
    ['dependencies.txt', 'xml/smallYeast.xml', 'yml/smallYeast.yml']
    ```

!!! warning "What can go wrong"
    - **The SBML writer refuses an identifier.** SBML ids must start with a
      letter or underscore. Both toolboxes add a prefix to ids that do not, which
      is why `importModel` and `read_sbml_model` strip prefixes on the way back.
    - **Excel export fails with a missing module.** The Python side needs
      `openpyxl`; install `raven-toolbox[excel]`.
    - **A YAML round trip loses a field neither format defines.** RAVEN YAML
      carries the RAVEN model fields; anything a plugin added outside them is not
      guaranteed to survive. Check with a diff, not by eye.

## See also

- [Getting started](getting-started.md) — what to do with the model once it is
  loaded.
- [User guide overview](index.md) — the other pages and what is planned.
- [MATLAB vs Python](../differences.md) — the full function mapping, including
  everything that resolves to cobrapy.
