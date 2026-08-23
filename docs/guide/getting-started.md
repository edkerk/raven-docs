# 1. Getting started

Load a model, find out what is in it, and look at a single reaction, metabolite
and gene. Every other page in the user guide assumes you can do this.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `readYAMLmodel` | `read_yaml_model` | read a RAVEN YAML model |
| `importModel` | `read_sbml_model` <span class="cobrapy-tag">cobrapy</span> | read an SBML model |
| `printModelStats` | model attributes <span class="cobrapy-tag">cobrapy</span> | how big the model is |
| `getIndexes` | `get_by_id` <span class="cobrapy-tag">cobrapy</span> | look something up by identifier |
| `constructEquations` | `Reaction.reaction` <span class="cobrapy-tag">cobrapy</span> | a reaction as a readable string |
| `getElementalBalance` | `check_mass_balance` <span class="cobrapy-tag">cobrapy</span> | is a reaction balanced |

## Setup

The examples use `smallYeast.yml`, a small model of central carbon metabolism in
yeast that ships with RAVEN. Download it from
[`docs/data/smallYeast.yml`](../data/smallYeast.yml) and run everything from the
directory you put it in.

## 1.1 Load the model

=== "MATLAB"

    ```matlab
    model = readYAMLmodel('smallYeast.yml');
    disp(model.id);
    ```

    ```text title="Output"
    smallYeast
    ```

    A RAVEN model is a MATLAB struct: `model.rxns`, `model.mets`, `model.genes`
    and the stoichiometric matrix `model.S` are all fields you can index
    directly.

=== "Python"

    ```python
    from raven_toolbox.io import read_yaml_model

    model = read_yaml_model("smallYeast.yml")
    print(model.id)
    ```

    ```text title="Output"
    smallYeast
    ```

    In Python a RAVEN model **is** a `cobra.Model` — raven-toolbox adds no model
    class of its own, so everything cobrapy can do is available on it.

For SBML use `importModel` in MATLAB and cobrapy's `read_sbml_model` in Python;
*Reading and writing models* (a later page in this guide) covers every
supported format.

## 1.2 How big is it?

=== "MATLAB"

    ```matlab
    printModelStats(model);
    ```

    ```text title="Output"
    Network statistics for smallYeast: Central carbon metabolism for yeast
    Genes*				61
    	cytosol	52
    	mitochondria	17

    Reactions*			53
    	cytosol	45
    	mitochondria	19
    Unique reactions**	53

    Metabolites			52
    	cytosol	35
    	mitochondria	17
    Unique metabolites	45

    * Genes and reactions are counted for each compartment if any of the corresponding metabolites are in that compartment. The sum may therefore not add up to the total number.
    ** Unique reactions are defined as being biochemically unique (no compartmentalization)
    ```

=== "Python"

    ```python
    print(len(model.reactions), len(model.metabolites), len(model.genes))
    ```

    ```text title="Output"
    53 52 61
    ```

    There is no raven-toolbox equivalent of `printModelStats`: the collections
    are attributes of the model, and after a solve `model.summary()` prints an
    overview of the exchange fluxes.

## 1.3 Look at a reaction

Glucose-6-phosphate isomerase, `PGI`, is a good one to start with — it is
reversible, it carries a gene association, and it should be mass balanced.

=== "MATLAB"

    ```matlab
    idx = getIndexes(model, 'PGI', 'rxns');
    disp(model.rxnNames{idx});
    eqn = constructEquations(model, model.rxns(idx));
    fprintf('%s\n', eqn{1});
    fprintf('bounds: [%g %g]\n', model.lb(idx), model.ub(idx));
    disp(model.grRules{idx});
    ```

    ```text title="Output"
    Glucose-6-phosphate isomerase
    alpha-D-glucose 6-phosphate[c] <=> beta-D-fructofuranose 6-phosphate[c]
    bounds: [-1000 1000]
    YBR196C
    ```

=== "Python"

    ```python
    pgi = model.reactions.get_by_id("PGI")
    print(pgi.name)
    print(pgi.reaction)
    print("bounds:", pgi.bounds, "reversible:", pgi.reversibility)
    print(pgi.gene_reaction_rule)
    ```

    ```text title="Output"
    Glucose-6-phosphate isomerase
    G6P_c <=> F6P_c
    bounds: (-1000.0, 1000.0) reversible: True
    YBR196C
    ```

Reversibility is not stored in the Python model: cobrapy derives it from the
bounds, so a reaction is reversible exactly when its lower bound is negative.
RAVEN keeps an explicit `model.rev` field alongside the bounds, which is the
subject of the *Model structure and identifiers* page.

## 1.4 Look at a metabolite

=== "MATLAB"

    ```matlab
    idx = getIndexes(model, 'G6P_c', 'mets');
    fprintf('%s (%s) in compartment %s\n', model.metNames{idx}, ...
        model.metFormulas{idx}, model.comps{model.metComps(idx)});
    fprintf('takes part in %d reactions\n', nnz(model.S(idx, :)));
    ```

    ```text title="Output"
    alpha-D-glucose 6-phosphate (C6H13O9P) in compartment c
    takes part in 4 reactions
    ```

=== "Python"

    ```python
    g6p = model.metabolites.get_by_id("G6P_c")
    print(f"{g6p.name} ({g6p.formula}) in compartment {g6p.compartment}")
    print(f"takes part in {len(g6p.reactions)} reactions")
    ```

    ```text title="Output"
    alpha-D-glucose 6-phosphate (C6H13O9P) in compartment c
    takes part in 4 reactions
    ```

## 1.5 Look at a gene

=== "MATLAB"

    ```matlab
    gi = find(strcmp(model.genes, 'YBR196C'));
    rxnIds = model.rxns(model.rxnGeneMat(:, gi) ~= 0);
    fprintf('%s -> %s\n', model.geneShortNames{gi}, strjoin(rxnIds, ', '));
    ```

    ```text title="Output"
    PGI1 -> PGI
    ```

=== "Python"

    ```python
    gene = model.genes.get_by_id("YBR196C")
    print(gene.name, "->", [rxn.id for rxn in gene.reactions])
    ```

    ```text title="Output"
    PGI1 -> ['PGI']
    ```

## 1.6 Is the reaction balanced?

Draft models routinely contain reactions that do not balance. Checking one
reaction is the same operation in both toolboxes; doing it for a whole model is
covered on the *Quality control* page.

=== "MATLAB"

    ```matlab
    balance = getElementalBalance(model, 'rxns', {'PGI'});
    fprintf('elemental %d, charge %d\n', balance.balanceStatus, balance.chargeStatus);
    ```

    ```text title="Output"
    elemental 1, charge -1
    ```

=== "Python"

    ```python
    print(pgi.check_mass_balance())
    ```

    ```text title="Output"
    {}
    ```

    `check_mass_balance` is cobrapy's. An empty result means the reaction
    balances; anything listed is the element and the amount by which it does not.
    `getElementalBalance` answers the same question as a status code: `1`
    balanced, `0` unbalanced, `-1` not decidable from the information in the
    model. It reports the charge balance separately, which cobrapy folds into the
    same dictionary.

!!! warning "What can go wrong"
    - **`KeyError` / empty index.** Identifiers are case-sensitive and carry the
      compartment suffix (`G6P_c`, not `G6P`). `getIndexes` returns `0` for a
      name it cannot find, so check the result before using it.
    - **The model loads but nothing grows.** In `smallYeast.yml` every uptake
      reaction is closed (`glcIN` has bounds `[0 0]`). Opening a medium is the
      subject of the *Growth media and conditions* page.
    - **Gene identifiers differ between model and FASTA.** Systematic names
      (`YBR196C`) and standard names (`PGI1`) are not interchangeable; RAVEN
      stores the systematic name as the identifier and the standard name as the
      gene name.

## See also

- [User guide overview](index.md) — the other pages, and what is still planned.
- [MATLAB vs Python](../differences.md) — what each toolbox has, and where
  cobrapy takes over.
- [API reference](../api/index.md) — every function in both toolboxes.
