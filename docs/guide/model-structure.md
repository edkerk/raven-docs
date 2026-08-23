# 2. Model structure and identifiers

The same model is a **struct of parallel arrays** in MATLAB and a **graph of
objects** in Python. Knowing which field corresponds to which attribute is most
of what you need to translate a script between the two.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `checkModelStruct` | `check_model` | report structural problems |
| `sortIdentifiers` | `sort_identifiers` | sort reactions, metabolites and genes by id |
| `getIndexes` | `parse_name_comp` | split a `name[comp]` token |
| — | `subsystem_to_str` | one subsystem string, whatever the source stored |
| `addIdentifierPrefix`, `removeIdentifierPrefix` | handled on read/write <span class="cobrapy-tag">cobrapy</span> | SBML identifier prefixes |
| `ravenCobraWrapper` | not needed | convert between RAVEN and COBRA structs |

## The correspondence

| RAVEN field | cobrapy | Note |
|---|---|---|
| `model.rxns` | `model.reactions` (ids) | a `DictList`, indexable by id or position |
| `model.rxnNames` | `reaction.name` | |
| `model.mets`, `model.metNames` | `model.metabolites`, `metabolite.name` | |
| `model.metFormulas` | `metabolite.formula` | |
| `model.genes` | `model.genes` | |
| `model.grRules` | `reaction.gene_reaction_rule` | same Boolean syntax |
| `model.rxnGeneMat` | `reaction.genes`, `gene.reactions` | the mapping is navigable from either side |
| `model.lb`, `model.ub` | `reaction.bounds` | |
| `model.rev` | derived from the bounds | `reaction.reversibility` is read-only |
| `model.S` | `create_stoichiometric_matrix(model)` | built on demand, not stored |
| `model.comps`, `model.metComps` | `metabolite.compartment`, `model.compartments` | |
| `model.subSystems` | `reaction.subsystem` | RAVEN allows several per reaction |
| `model.c` | `model.objective` | an expression, not a coefficient vector |

The consequence worth internalising: in MATLAB you edit **arrays in parallel and
keep them aligned**, and in Python you edit **objects that know their own
neighbours**. Deleting a reaction in RAVEN means removing the same row from every
reaction-length field — which is why `removeReactions` exists. In cobrapy the
object holds its own links, so `model.remove_reactions([...])` is enough.

## Setup

`smallYeast.yml` from [`docs/data/`](../data/README.md).

=== "MATLAB"

    ```matlab
    model = readYAMLmodel('smallYeast.yml');
    ```

=== "Python"

    ```python
    from raven_toolbox.io import read_yaml_model

    model = read_yaml_model("smallYeast.yml")
    ```

## 2.1 The same lookup, two ways

=== "MATLAB"

    ```matlab
    idx = getIndexes(model, 'PGI', 'rxns');
    fprintf('%s: %s\n', model.rxns{idx}, model.rxnNames{idx});
    fprintf('genes: %s\n', model.grRules{idx});
    ```

    ```text title="Output"
    PGI: Glucose-6-phosphate isomerase
    genes: YBR196C
    ```

    Indices are the currency: nearly every RAVEN function takes or returns them,
    and `getIndexes` is how you go from an identifier to one.

=== "Python"

    ```python
    rxn = model.reactions.get_by_id("PGI")
    print(f"{rxn.id}: {rxn.name}")
    print("genes:", rxn.gene_reaction_rule)
    print("also reachable as:", model.reactions.PGI.id)
    ```

    ```text title="Output"
    PGI: Glucose-6-phosphate isomerase
    genes: YBR196C
    also reachable as: PGI
    ```

    There is no index to carry around: `DictList` looks up by id, and the object
    is the handle.

## 2.2 Compartments

=== "MATLAB"

    ```matlab
    disp(model.comps);                       % compartment ids
    i = getIndexes(model, 'G6P_c', 'mets');
    disp(model.comps{model.metComps(i)});    % the compartment of one metabolite
    ```

    ```text title="Output"
        {'c'}
        {'m'}

    c
    ```

=== "Python"

    ```python
    print(model.compartments)
    print(model.metabolites.get_by_id("G6P_c").compartment)
    ```

    ```text title="Output"
    {'m': 'mitochondria', 'c': 'cytosol'}
    c
    ```

RAVEN also writes metabolite names as `name[comp]` in Excel and text exports.
`parse_name_comp` splits that token back apart, which is what you want when
reading a curation spreadsheet. Note the import path: it lives in
`raven_toolbox.utils.parse`, not in the `raven_toolbox.utils` package namespace,
which re-exports only the curation helpers.

=== "MATLAB"

    ```matlab
    % getIndexes accepts the same 'name[comp]' form directly
    i = getIndexes(model, 'alpha-D-glucose 6-phosphate[c]', 'metnames');
    ```

=== "Python"

    ```python
    from raven_toolbox.utils.parse import parse_name_comp

    print(parse_name_comp("alpha-D-glucose 6-phosphate[c]"))
    print(parse_name_comp("ATP"))
    ```

    ```text title="Output"
    ('alpha-D-glucose 6-phosphate', 'c')
    ('ATP', None)
    ```

## 2.3 Subsystems

RAVEN lets a reaction belong to several subsystems, so `model.subSystems` is a
cell array of cell arrays; cobrapy stores one string. A model that came through
RAVEN can therefore carry a list where cobrapy expects text, and
`subsystem_to_str` normalises whichever it finds:

=== "MATLAB"

    ```matlab
    % a cell array, so a reaction can be in several subsystems
    model.subSystems{idx} = {'Glycolysis', 'Pentose phosphate pathway'};
    fprintf('%s\n', strjoin(model.subSystems{idx}, '; '));
    ```

    ```text title="Output"
    Glycolysis; Pentose phosphate pathway
    ```

=== "Python"

    ```python
    from raven_toolbox.utils.parse import subsystem_to_str

    rxn.subsystem = ["Glycolysis", "Pentose phosphate pathway"]
    print(subsystem_to_str(rxn.subsystem))
    print(subsystem_to_str("Glycolysis"))
    ```

    ```text title="Output"
    Glycolysis;Pentose phosphate pathway
    Glycolysis
    ```

## 2.4 Check the model is structurally sound

Before trusting anything a model tells you, ask whether it is put together
correctly: metabolites nothing consumes, reactions with no metabolites, genes no
reaction uses, a missing objective.

=== "MATLAB"

    ```matlab
    issues = checkModelStruct(model, 'throwErrors', false);
    fprintf('%d issue(s)\n', numel(issues));
    ```

    ```text title="Output"
    1 issue(s)
    ```

=== "Python"

    ```python
    from raven_toolbox.utils import check_model

    issues = check_model(model)
    print(len(issues), "issue(s)")
    for issue in issues[:5]:
        print(f"  {issue.category}: {issue.message}")
    ```

    ```text title="Output"
    0 issue(s)
    ```

    `check_model` returns the issues instead of printing them, so you can filter
    by `category` or fail a test on the ones you care about.

## 2.5 Sort the identifiers before you commit

Sorting makes the diff between two versions of a model readable — the reason
`exportForGit` and `export_for_git` offer it too.

=== "MATLAB"

    ```matlab
    sortedModel = sortIdentifiers(model);
    fprintf('%s\n', strjoin(sortedModel.rxns(1:5)', ', '));
    ```

    ```text title="Output"
    ACO, ACS, ADH1, ALD6, ATPX
    ```

=== "Python"

    ```python
    from raven_toolbox.utils import sort_identifiers

    sorted_model = sort_identifiers(model)
    print([r.id for r in sorted_model.reactions[:5]])
    ```

    ```text title="Output"
    ['ACO', 'ACS', 'ADH1', 'ALD6', 'ATPX']
    ```

!!! warning "MATLAB only: converting to and from the COBRA Toolbox"
    RAVEN and the COBRA Toolbox use different field names for the same model.
    `ravenCobraWrapper` converts a struct in either direction. There is no Python
    equivalent because there is nothing to convert: a raven-toolbox model **is** a
    `cobra.Model`.

!!! warning "What can go wrong"
    - **Fields drift out of alignment.** In MATLAB, editing one reaction-length
      field by hand without editing the others leaves a model that looks fine and
      fails later; `checkModelStruct` is how you catch it.
    - **`model.rev` disagrees with the bounds.** RAVEN stores reversibility
      explicitly, so it can contradict `lb`/`ub` after a manual edit. Python
      cannot get into that state.
    - **Subsystems come back as a list.** Code that assumes `reaction.subsystem`
      is a string breaks on a model imported from RAVEN. Use `subsystem_to_str`.

## See also

- [Getting started](getting-started.md) — loading a model and looking around it.
- [Reading and writing models](io.md) — where identifier prefixes come from.
- [MATLAB vs Python](../differences.md) — the full function mapping.
