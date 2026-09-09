# RAVEN 3 and raven-toolbox

RAVEN exists as two independent implementations:

- **RAVEN**: the original MATLAB toolbox, which works entirely on its own,
  including independently of the COBRA Toolbox.
- **raven-toolbox**: the Python package, built on
  [cobrapy](https://cobrapy.readthedocs.io/), so a model is a `cobra.Model` and
  the wider Python ecosystem works on it directly.

They do the same things (homology and KEGG reconstruction, metabolic tasks,
gap-filling, context-specific extraction with ftINIT, compartment assignment,
model comparison), but one is not a direct translation of the other. Names
differ, some capabilities exist on one side only, and a handful of functions
answer the same question differently.

This page is the whole comparison. The function-by-function view is the
[mapping table](matlab-vs-python.md), generated from both toolboxes' sources at
build time.

## Which one should you use?

Neither is a reduced version of the other, so the right choice usually depends
on the rest of your code, not on the toolbox itself.

**Use raven-toolbox** if the surrounding code is Python, if you want the model
to be a `cobra.Model` that every cobrapy tool accepts without conversion, if
you need reproducible environments and CI, or if you need KEGG artefacts built
against a stated release rather than whatever is distributed.

**Use RAVEN** if the surrounding code is MATLAB, if you need to reproduce a
model built with tINIT, or if you need dynamic FBA or conversion to the COBRA
Toolbox structure.

**Either** covers the core reconstruction and analysis path. Where both have a
function, the mapping table names the pair; where only one does, the sections
below say which and why.

## Changing the case does not give the matching name

MATLAB uses `camelCase` and Python uses `snake_case`, but changing only the
case usually produces a name that does not exist. Much of the API was
deliberately renamed as it was ported:

| MATLAB | Python |
|---|---|
| `getBlast` | `run_blast` |
| `addRxns` | `add_reactions_from_equations` |
| `fillGaps` | three functions with different algorithms |

Check the [mapping table](matlab-vs-python.md) rather than guessing. It also
records what cobrapy covers instead of raven-toolbox, and what is deliberately
absent.

## What only raven-toolbox has

### Built on cobrapy

The largest difference is not a feature but a foundation: a raven-toolbox model
**is** a `cobra.Model`. Every cobrapy tool, and everything in the wider COBRA
Python ecosystem, works on it without conversion. RAVEN's own model is a MATLAB
struct, and `ravenCobraWrapper` converts between that and the COBRA Toolbox
format as an explicit step.

The practical consequence: FBA, FVA, knockouts, media handling and the rest come
from cobrapy rather than from raven-toolbox, which is why so many RAVEN
functions have a *cobrapy* row rather than a Python counterpart in the mapping
table.

### KEGG artefact generation

raven-toolbox can build the KEGG reference artefacts themselves, parsing a KEGG
release into reaction and compound tables, assembling the reference model,
building the per-KO FASTA sets and HMM libraries, and deriving the phylogenetic
distance matrix. RAVEN consumes pre-built artefacts; it does not produce them.

This is what keeps the KEGG route reproducible against a stated KEGG release
rather than against whichever artefact is currently distributed.

### Smaller additions

- **Growth conditions**: apply a named, versioned growth condition to a model.
- **Batch curation**: apply a table of curation edits to a model in one pass.
- **ΔG and SBO annotation**: load and save thermodynamic data through CSV, and
  assign SBO terms.
- **Biomass helpers**: sum a biomass composition, rescale a pseudoreaction, and
  scale a fraction to a measured value.
- **Checksummed provisioning**: both toolboxes now fetch BLAST+, DIAMOND,
  HMMER and the KEGG artefacts on demand rather than bundling them, from the
  same release. What is Python-only is the baked registry that pins a given
  release to the exact assets it was tested against; RAVEN resolves from the
  published release each time. See
  [Downloaded data and binaries](installation/data-and-binaries.md).

## What only RAVEN has

### tINIT

`getINITModel` and `runINIT` are the original tINIT implementation. RAVEN keeps
them for the models already built with them; raven-toolbox, a new
implementation with no such installed base, carries ftINIT alone. A tINIT model
has to be reproduced in MATLAB; see
[10. Context-specific models](guide/init.md).

### COBRA Toolbox conversion

`ravenCobraWrapper` converts between the RAVEN and COBRA Toolbox model
structures. There is nothing to convert in Python: the model is already a
`cobra.Model`, so no equivalent exists or is needed.

### Dynamic FBA

`runDynamicFBA` has no Python counterpart, deliberately. Several maintained
Python packages already cover dynamic FBA well
([dfba](https://pypi.org/project/dfba/),
[reframed](https://pypi.org/project/reframed/),
[mewpy](https://pypi.org/project/mewpy/)), and reimplementing it would add a
second-rate version of something that already exists.

### MATLAB-specific plumbing

A large share of RAVEN's function count is MATLAB housekeeping with nothing to
map to: path management (`addRavenToUserPath`, `findRAVENroot`), argument
handling (`parseRAVENargs`, `convertCharArray`), progress and printing
(`setRavenProgress`, `printOrange`), and the solver abstraction
(`optimizeProb`, `setRavenSolver`), which in Python is cobrapy's solver
interface via optlang.

## Same function, different answer

Where the two agree on the job but differ in what they hand back, how they order
it, or what they do to the model on the way. Deliberately short: an entry is
added only once the difference has been confirmed in both sources.

:::{admonition} Not a complete list
:class: info
Absence from this section is not a guarantee of identical behaviour. It only
means the difference has not been confirmed and written up yet.
:::

### Duplicate reactions: gene associations are not merged

`contractModel` merges duplicate reactions **and their gene associations**: when
it collapses a set of duplicates it joins the distinct `grRules` with `or`, so
every gene that pointed at any of the duplicates still points at the survivor.

`remove_duplicate_reactions` keeps one reaction of each duplicate set and removes
the rest, without merging gene associations. A gene that was associated *only*
with a removed duplicate is no longer associated with anything.

The stoichiometric network is the same either way; the gene–reaction mapping is
not. If you are contracting a draft assembled from several templates, where the
same reaction commonly arrives with different gene associations, check the GPRs
of the survivors afterwards.

### Metabolic tasks: the same result, a different runtime

`checkTasks` rebuilds the working model from the original for each task.
`check_tasks` instead applies each task's constraints to one model inside a
`with model:` block and reverts them afterwards, restoring by hand the one kind
of edit cobra's context manager does not track (direct mass-balance bound
changes).

The pass and fail results are the same. The runtime is not: at genome scale,
copying the model for each task dominates the MATLAB runtime, which is why the
Python version reuses a single model. This changes runtime comparisons, not
results.

### Gap-filling: `fillGaps` splits into three functions in raven-toolbox

`fillGaps` does several different jobs through one function call.
raven-toolbox splits them, so porting a `fillGaps` call means choosing:

| What you were doing | Use |
|---|---|
| Connecting blocked reactions against template models | `connect_blocked_reactions` |
| Fast LP-based filling of a large candidate set | `fill_gaps_fast_lp` |
| MILP filling with explicit weights | `fill_gaps_kumar_milp` |
| Only *finding* the gaps (`canExchange`, `checkProduction`, `getAllSubGraphs`, `haveFlux`) | `analyse_topology` |

The choice changes both the reaction set added and the runtime, because each
of the three functions uses a different algorithm; they are not the same
algorithm under three different names.

### Anything solved by MILP

ftINIT extraction, gap-filling, and compartment assignment all solve
mixed-integer problems that routinely have **several optima of equal objective
value**. Two runs can return different reaction sets and both be correct; across
languages, across solvers, and in some configurations across runs of the same
solver.

Do not compare these outputs for identity. Compare them for overlap, and
expect a range of acceptable values, not one exact number.

### Elemental balance: an unknown result is not the same as balanced

Elemental balance checks whether a reaction has the same count of each
chemical element (carbon, hydrogen, oxygen, and so on) on both sides, the way
a correct chemical equation must. `getElementalBalance` and
`get_elemental_balance` each report one of three results per reaction, not
two: `balanced`, `unbalanced`, or `unknown`. A reaction is `unknown` when one
of its metabolites has no chemical formula recorded, so the element counts
cannot be computed at all; that is different from `unbalanced`, which means
the counts were computed and did not match. The two functions agree on this
three-way result.

That third case is lost if you switch to plain cobrapy: its
`check_mass_balance` has no separate `unknown` result, so a reaction with a
missing formula and a reaction that is genuinely unbalanced can look the
same. raven-toolbox keeps its own function instead of using cobrapy's
directly, specifically to keep that distinction.

## Solvers

| | RAVEN (MATLAB) | raven-toolbox (Python) |
|---|---|---|
| Configuration | `setRavenSolver('gurobi')` | `cobra.Configuration().solver = 'gurobi'` |
| Recommended solver | Gurobi (free academic licence) | Gurobi (free academic licence) |
| Open-source option | GLPK (bundled with RAVEN) | GLPK (bundled with cobrapy) |

Genome-scale MILP work (ftINIT extraction in particular) is where the choice
matters most; see [Installation](installation/index.md) for the full solver
matrix.

## Moving a model between them

Models move through **SBML** (`.xml`) and **YAML** (`.yml`). raven-toolbox's
YAML follows the cobrapy layout plus RAVEN's own per-entry fields, so a model
written by either side round-trips through the other; see
[the YAML format reference](yaml-format.md) for the field-by-field spec and
interoperability matrix.

Excel is **export-only** on both sides: raven-toolbox has never had a reader,
and RAVEN's `importExcelModel` was removed in the RAVEN 3 refactor.

## Coming from RAVEN 2.0 to Python

raven-toolbox is not a port of RAVEN 2.0; it is a new implementation that
made different design choices where RAVEN 2.0's design had become outdated. If you are
moving a RAVEN 2.0 workflow straight to Python rather than to RAVEN 3, three
differences matter beyond everything above.

**The model data structure.** RAVEN 2.0 represents a model as a MATLAB struct
with `.rxns`, `.mets`, `.S`, `.lb`, `.ub`. raven-toolbox loads directly into a
`cobra.Model`; the struct format is not used internally at all, and solver calls
go through cobrapy's unified interface.

**Packaging and typing.** raven-toolbox installs from PyPI
(`pip install raven-toolbox`), so environments are reproducible and CI is
straightforward. Every public function carries type annotations and passes
`mypy`.

**MetaCyc reconstruction is gone, on both sides.** RAVEN 2.0 shipped
`getMetaCycModelForOrganism`; RAVEN 3 removed the whole `external/metacyc`
folder, and raven-toolbox never had it. The reason is not neglect: MetaCyc
provides a single representative sequence per enzyme, which gives intrinsically
low gene-calling precision, measured at roughly two-thirds of reaction
assignments wrong at the default cutoff, with no cutoff value that fixes the
problem. Use the KEGG or homology routes.

What stayed the same are the algorithms: homology search, gap-filling and KEGG
reconstruction follow the same published methods, and models
move between all three through SBML and YAML.
