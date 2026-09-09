# RAVEN 3 and raven-toolbox

RAVEN exists as two independent implementations:

- **RAVEN**: the original MATLAB toolbox, which works entirely on its own,
  including independently of the COBRA Toolbox.
- **raven-toolbox**: the Python package, built on
  [cobrapy](https://cobrapy.readthedocs.io/), so a model is a `cobra.Model` and
  the wider Python ecosystem works on it directly.

They cover the same ground (homology and KEGG reconstruction, metabolic tasks,
gap-filling, context-specific extraction with ftINIT, compartment assignment,
model comparison), but they are **not transliterations of each other**. Names
differ, some capabilities exist on one side only, and a handful of functions
answer the same question differently.

This page is the whole comparison. The function-by-function view is the
[mapping table](matlab-vs-python.md), generated from both toolboxes' sources at
build time.

## Which one should you use?

Neither is a reduced version of the other, so the choice is usually made by
what surrounds the model rather than by the toolbox itself.

**Use raven-toolbox** if the work lives in Python, if you want the model
to be a `cobra.Model` that every cobrapy tool accepts without conversion, if you
need reproducible environments and CI, or if you need KEGG artefacts built
against a stated release rather than whatever is distributed.

**Use RAVEN** if the work lives in MATLAB, if you need to reproduce a
model built with tINIT, or if you need dynamic FBA or conversion to the COBRA
Toolbox structure.

**Either** covers the core reconstruction and analysis path. Where both have a
function, the mapping table names the pair; where only one does, the sections
below say which and why.

## Names do not convert mechanically

MATLAB uses `camelCase`, Python `snake_case`, but rewriting the case is the
most common way to arrive at a name that does not exist. Much of the API was
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

### Confidence tracking

Per-reaction, multi-facet confidence scoring: evidence for a reaction's presence
graded across several independent facets, with the bands calibrated against
curated models. Used to prioritise manual curation on a draft: reactions the
score is least sure about are where a curator's time goes furthest.

### A newer compartment assignment

Both toolboxes have `assignCompartments`, and they are **not** the same
function. RAVEN's is a port of raven-toolbox's earlier design, in which
functionality is fused into the placement MILP as a hard flux-gating
constraint. raven-toolbox has since separated the two: placement is decided by a
score MILP, then *certified* by a real FBA on the materialised model, so a
placement that breaks biomass production is rejected rather than returned. It
can couple gap-filling into that loop, and keeps a second compartment for a
reaction only when a loopless FVA shows it carries flux there.

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

!!! info "Not a complete list"
    Absence from this section is not a guarantee of identical behaviour. Where
    an exact answer matters (reproducing a published result, comparing two
    pipelines); see [what "identical results" means](#what-identical-results-means).

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

### Metabolic tasks: same verdicts, very different cost

`checkTasks` rebuilds the working model from the original for each task.
`check_tasks` instead applies each task's constraints to one model inside a
`with model:` block and reverts them afterwards, restoring by hand the one kind
of edit cobra's context manager does not track (direct mass-balance bound
changes).

The pass/fail verdicts are the same. The cost is not: at genome scale the copy
dominates the MATLAB runtime, which is why the Python version reuses a single
model. This affects runtime comparisons, not results.

### Gap-filling: one function becomes three

`fillGaps` covers several jobs behind one interface. raven-toolbox splits them,
so porting a `fillGaps` call means choosing:

| What you were doing | Use |
|---|---|
| Connecting blocked reactions against template models | `connect_blocked_reactions` |
| Fast LP-based filling of a large candidate set | `fill_gaps_fast_lp` |
| MILP filling with explicit weights | `fill_gaps_kumar_milp` |
| Only *finding* the gaps (`canExchange`, `checkProduction`, `getAllSubGraphs`, `haveFlux`) | `analyse_topology` |

The choice changes both the reaction set added and the runtime; they are
different algorithms, not one algorithm behind three names.

### Anything solved by MILP

ftINIT extraction, gap-filling, and compartment assignment all solve
mixed-integer problems that routinely have **several optima of equal objective
value**. Two runs can return different reaction sets and both be correct; across
languages, across solvers, and in some configurations across runs of the same
solver.

Do not compare these outputs for identity. Compare them for overlap, and expect
a band rather than a number.

### A note on elemental balance

Both `getElementalBalance` and `get_elemental_balance` grade each reaction rather
than returning a bare balanced/unbalanced flag: a reaction whose metabolites lack
formulas is reported as *unknown*, not as balanced. The two agree.

The distinction matters when moving to plain cobrapy, whose `check_mass_balance`
does not make it, which is the reason raven-toolbox keeps its own function
instead of delegating.

## What "identical results" means

When two implementations of the same method exist, the question is whether they
give the same answer. That depends on which function you
mean, because "the same" is achievable for some and meaningless for others.

### Exact

The output can and should match value for value. Anything deterministic that
transforms a model or a file rather than solving an optimisation problem:

- model I/O: SBML and YAML round-trips, Excel export
- task-list parsing
- gene-association normalisation (`grRuleToDNF` / `gpr_to_dnf`)
- elemental balance
- identifier sorting, model merging, reversibility splitting, GPR expansion
- KEGG table parsing and homology ortholog assignment

If these disagree, one of them is wrong.

### Set-level

The output is the solution to a mixed-integer problem that has many optima of
equal value, so identity is not a meaningful target; a different reaction set of
the same objective value is not an error. This covers ftINIT extraction,
gap-filling, and compartment assignment.

The meaningful comparison is overlap: how similar are the two models, expressed
as a Jaccard index or a containment fraction, against a recorded baseline. Two
extractions agreeing to a Jaccard of 0.97 on a genome-scale model is a strong
result, not a near-miss.

Alternate optima also mean the *solver* matters. The same code with Gurobi and
with GLPK can land on different optima, so a cross-language comparison should
hold the solver fixed before concluding anything about the languages.

### Statistical

Flux sampling and random sampling explore a space rather than compute a point.
Two runs of the *same* implementation differ. Compare distributions (means,
marginals, coverage) at a fixed seed, never individual samples.

### What is actually verified today

raven-toolbox has been validated against MATLAB RAVEN on Human-GEM (five
Hart2015 cell-line models, Jaccard 0.975–0.980), on yeast, and on a
multi-organism set. Those are set-level comparisons of the extraction pipeline,
reported in the raven-toolbox repository.

They are, at present, **reported** rather than **enforced**: no test fails if the
two implementations drift apart. Building that harness (committed fixtures, a
MATLAB driver that records the reference output, and tiered assertions matching
the three levels above) is planned work; this page cannot yet point at it.

## Solvers

| | RAVEN (MATLAB) | raven-toolbox (Python) |
|---|---|---|
| Configuration | `setRavenSolver('gurobi')` | `cobra.Configuration().solver = 'gurobi'` |
| Recommended solver | Gurobi (free academic licence) | Gurobi (free academic licence) |
| Open-source option | GLPK (via COBRA Toolbox) | GLPK (bundled with cobrapy) |

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

raven-toolbox is not a port of RAVEN 2.0; it is a fresh implementation that
made different architectural choices where RAVEN 2.0 showed its age. If you are
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
assignments wrong at the default cutoff, with no cutoff that rescues it. Use the
KEGG or homology routes.

What stayed the same are the algorithms: homology search, gap-filling and KEGG
reconstruction follow the same published methods, and models
move between all three through SBML and YAML.
