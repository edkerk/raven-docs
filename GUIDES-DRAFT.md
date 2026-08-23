# Draft: a cobrapy-style user guide for RAVEN and raven-toolbox

> **Status: proposal, with the plumbing built.** A plan for a new documentation
> section under **Guides**, modelled on the cobrapy documentation
> (<https://cobrapy.readthedocs.io/en/latest/getting_started.html>). The existing
> hanpo-GEM protocol and the legacy tutorials 1–5 stay exactly as they are; this
> is an addition, not a rewrite. Once agreed, fold the decisions into
> `DESIGN.md` §4.4 and delete this file.
>
> **Already in the working tree** (the machinery, plus one page to prove the
> format):
>
> | Path | What it is |
> |---|---|
> | `docs/data/` | the example models, copied from `RAVEN/tutorial/` (§7) |
> | `scripts/run_examples.py` | executes and verifies the Python snippets (§6) |
> | `.github/workflows/examples.yml` | runs it on every relevant push, PR and weekly (§6) |
> | `docs/guide/index.md` | user-guide landing page |
> | `docs/guide/getting-started.md` | page 1 (§4.1 #1) |
> | `docs/guide/model-structure.md` | §4.1 #2 |
> | `docs/guide/io.md` | §4.1 #3 |
> | `docs/guide/fba.md` | §4.3 #9 |
> | `docs/guide/media.md` | §4.3 #10 |
> | `docs/guide/solvers.md` | §4.1 #4 |
> | `docs/guide/building.md` | §4.2 #5 |
> | `docs/guide/editing.md` | §4.2 #6 |
> | `docs/guide/quality-control.md` | §4.4 #16 |
>
> Both languages are executed and re-checked in CI. **9 of the 13 P1 pages are
> written**; the remainder are deletions and essentiality, gap-filling, metabolic
> tasks, and tINIT/ftINIT.
>
> Everything else below is still a plan.

## 1. What cobrapy does, and what we would copy

cobrapy's prose documentation is 16 short pages (Getting Started, Global
Configuration, Building a Model, Reading and Writing Models, Simulating with FBA,
Simulating Deletions, Production envelopes, Flux sampling, Loopless FBA,
Consistency testing, Gapfilling, Growth media, Solvers, Tailored constraints,
dFBA, FAQ). Each page:

- covers **one task**, not one module — usually 3–8 functions;
- is a runnable narrative: load something small, do the thing, show the result;
- shows **real output** under every snippet, so the page is readable without
  running it;
- links to the generated API reference for the details it deliberately omits.

Worth copying: the granularity (many small task pages), the show-the-output
style, and the discipline of one page = one task.

Not worth copying: cobrapy's pages are executed Jupyter notebooks. We need MATLAB
and Python in the same page, so pages must be plain Markdown with linked content
tabs (§2), and outputs are pasted in rather than rendered by nbconvert — see §6
for how to keep them honest.

## 2. Recommendation: one page, two tabs — not two page sets

**Yes — combine MATLAB and Python on the same page**, exactly like the Quick
start on the homepage: one narrative, every code block a linked `=== "MATLAB"` /
`=== "Python"` pair. Reasons:

1. **It is already the site's stated principle.** `DESIGN.md` §2 and §5 commit to
   dual-language parity with linked, persistent tabs defaulting to MATLAB. A
   separate Python guide tree would contradict the one thing that makes this site
   different from the two upstream READMEs.
2. **The prose is the expensive part, and it is identical.** What FVA is, why a
   biomass pseudo-reaction needs scaling, what ftINIT's steps mean — none of it is
   language-specific. Splitting the tree means writing and maintaining it twice,
   and it *will* drift.
3. **The differences become visible instead of invisible.** Side by side, a reader
   immediately sees that `getExchangeRxns` has no Python twin because
   `model.exchanges` covers it. In two separate trees, that is an absence nobody
   notices.
4. **It matches how people arrive.** Many users move between a MATLAB pipeline and
   a Python one, or read a colleague's MATLAB script while writing Python. The
   toggle is the feature.

Three rules keep it from becoming awkward:

- **Never fake a pairing.** If a step is `getExchangeRxns` in MATLAB and plain
  cobrapy in Python, the Python tab shows the cobrapy call with the cobrapy badge.
  If nothing equivalent exists, the tab says so in one line and links to the
  workaround. A tab that silently invents `get_exchange_rxns` is worse than no tab
  — and `scripts/check_names.py` already fails the build on it.
- **Divergent behaviour gets a callout, not a footnote.** Where the two give
  genuinely different answers, use an admonition linking to
  [Same function, different answer](docs/behaviour.md).
- **A section may be single-language.** Some topics have no counterpart
  (`ravenCobraWrapper`; cobrapy's `Configuration` object). Keep those as clearly
  labelled sections inside the nearest task page rather than inventing a parallel
  page, and mark them "MATLAB only" / "Python only" in the page's function table.

## 3. Where it goes in the nav

`Guides` gains a third child, ahead of the existing two, which are untouched:

The first two entries are wired up in `mkdocs.yml` already; the rest follow as
the pages are written. The Guides overview stays at `protocol/index.md` until it
is rewritten to introduce all three sub-sections.

```yaml
  - Guides:
      - Overview: protocol/index.md
      - User guide:
          - Overview: guide/index.md               # written
          - Getting started: guide/getting-started.md   # written
          - Model structure and identifiers: guide/model-structure.md
          - Reading and writing models: guide/io.md
          - Solvers and configuration: guide/solvers.md
          - Building a model from scratch: guide/building.md
          - Editing an existing model: guide/editing.md
          - Compartments and transport: guide/compartments.md
          - Combining and simplifying models: guide/combining.md
          - Simulating growth with FBA: guide/fba.md
          - Growth media and conditions: guide/media.md
          - Flux variability and alternative optima: guide/fva.md
          - Deletions and essentiality: guide/deletions.md
          - Flux sampling: guide/sampling.md
          - Phenotype exploration: guide/phenotype.md
          - Finding engineering targets: guide/targets.md
          - Quality control: guide/quality-control.md
          - Gap-filling: guide/gap-filling.md
          - Metabolic tasks: guide/tasks.md
          - Biomass composition: guide/biomass.md
          - Annotation and metadata: guide/annotation.md
          - Draft models from homology: guide/homology.md
          - Draft models from KEGG: guide/kegg.md
          - Context-specific models (tINIT / ftINIT): guide/init.md
          - Subcellular localization: guide/localization.md
          - Comparing models: guide/comparison.md
          - Curating from tables: guide/curation.md
      - GEM reconstruction (H. polymorpha):   # unchanged
          - ...
      - Legacy tutorials:                     # unchanged
          - ...
```

26 pages versus cobrapy's 16 — deliberately, because we document two toolboxes
and the reconstruction half of RAVEN has no cobrapy equivalent at all. A separate
`docs/guide/` directory keeps the new set clearly apart from `docs/protocol/` and
`docs/tutorials/`.

Naming: **"User guide"** for the new set, **"Protocols"** for hanpo-GEM (a
published, end-to-end pipeline), **"Legacy tutorials"** unchanged. The Guides
overview page explains all three in two sentences each so nobody has to guess
which one they want.

## 4. The pages

Priority: **P1** = first wave (a coherent, useful set on its own), **P2** =
second wave, **P3** = completes the set. Every function listed exists today on
the tracked branches.

### 4.1 Foundations

| # | Page | MATLAB | Python | P |
|---|---|---|---|---|
| 1 | **Getting started** — load a model, count what is in it, look at one reaction, metabolite and gene | `importModel`, `readYAMLmodel`, `printModelStats`, `modelSummary`, `constructEquations`, `getIndexes` | `read_yaml_model`, cobrapy `read_sbml_model`, `Model.reactions` / `.metabolites` / `.genes` | P1 |
| 2 | **Model structure and identifiers** — the RAVEN struct vs `cobra.Model`, what maps to what, id prefixes, field order | `checkModelStruct`, `standardizeModelFieldOrder`, `sortIdentifiers`, `addIdentifierPrefix`, `removeIdentifierPrefix`, `ravenCobraWrapper` | `check_model`, `sort_identifiers`, `parse_name_comp`, `subsystem_to_str` | P1 |
| 3 | **Reading and writing models** — SBML, RAVEN YAML, Excel, tab-delimited, git-friendly export | `importModel`, `exportModel`, `readYAMLmodel`, `writeYAMLmodel`, `exportToExcelFormat`, `exportToTabDelimited`, `exportForGit` | `read_yaml_model`, `write_yaml_model`, `export_to_excel`, `export_for_git`, `export_model_to_sif`, cobrapy `write_sbml_model` | P1 |
| 4 | **Solvers and configuration** — choose and verify a solver, read a solution object | `setRavenSolver`, `solveLP`, `optimizeProb`, `checkSolution`, `checkInstallation` | cobrapy `Configuration`, `model.solver`, `Solution` | P1 |

### 4.2 Building and editing

| # | Page | MATLAB | Python | P |
|---|---|---|---|---|
| 5 | **Building a model from scratch** — three metabolites, two reactions, a gene, an exchange | `addMets`, `addRxns`, `addGenesRaven`, `addExchangeRxns`, `constructEquations` | `add_reactions_from_equations`, cobrapy `Reaction` / `Metabolite` | P1 |
| 6 | **Editing an existing model** — change stoichiometry, bounds and GPRs; delete things safely | `changeRxns`, `changeGrRules`, `standardizeGrRules`, `setParam`, `removeReactions`, `removeMets`, `removeGenes`, `deleteUnusedGenes` | `change_reaction_equations`, `change_gene_reaction_rules`, `gpr_to_dnf`, `remove_metabolites`, `remove_genes`, `set_variance_bounds` | P1 |
| 7 | **Compartments and transport** — move reactions between compartments, add transport, query by compartment | `copyToComps`, `mergeCompartments`, `addTransport`, `getRxnsInComp`, `getTransportRxns` | `copy_to_compartment`, `merge_compartments`, `add_transport_reactions` | P2 |
| 8 | **Combining and simplifying models** — merge two models, pull reactions across, contract, prune | `mergeModels`, `addRxnsGenesMets`, `contractModel`, `simplifyModel`, `findDuplicateRxns`, `expandModel`, `convertToIrrev` | `merge_models`, `add_reactions_from_model`, `find_duplicate_reactions`, `remove_duplicate_reactions`, `remove_dead_end_reactions`, `expand_model`, `convert_to_irreversible`, `group_linear_reactions` | P2 |

### 4.3 Simulation

| # | Page | MATLAB | Python | P |
|---|---|---|---|---|
| 9 | **Simulating growth with FBA** — objective, bounds, solve, read the fluxes | `setParam`, `solveLP`, `printFluxes`, `haveFlux` | cobrapy `model.optimize`, `model.summary`, `pfba` | P1 |
| 10 | **Growth media and conditions** — define a medium, close the model, minimal media, reusable condition files | `getExchangeRxns`, `setExchangeBounds`, `closeModel`, `getMinimalMedium`, `applyCondition` | `load_condition`, `apply_condition`, `set_reaction_bounds`, cobrapy `model.medium`, `model.exchanges` | P1 |
| 11 | **Flux variability and alternative optima** — ranges, blocked reactions, minimal-flux solutions | `getAllowedBounds`, `haveFlux`, `getMinNrFluxes` | `find_good_reactions`, cobrapy `flux_variability_analysis`, `pfba`, `loopless_solution` | P2 |
| 12 | **Deletions and essentiality** — single and double knockouts, essential reactions, MOMA | `findGeneDeletions`, `getEssentialRxns`, `qMOMA` | cobrapy `single_gene_deletion`, `double_reaction_deletion`, `knock_out_model_genes`, `moma` | P1 |
| 13 | **Flux sampling** — sample the solution space and interpret the result | `randomSampling`, `analyzeSampling`, `sampleCHRR`, `sampleACHR`, `sampleWarmupPoints`, `sampleMaxVolEllipse` | `random_sampling`, `max_volume_ellipsoid`, cobrapy `sample` | P2 |
| 14 | **Phenotype exploration** — production envelopes, phase planes, robustness, dFBA | `runProductionEnvelope`, `runPhenotypePhasePlane`, `runRobustnessAnalysis`, `runDynamicFBA` | cobrapy `production_envelope` (dFBA: cobrapy recipe) | P3 |
| 15 | **Finding engineering targets** — FSEOF, OptKnock-style screens, reporter metabolites | `FSEOF`, `runSimpleOptKnock`, `reporterMetabolites`, `compareFluxes`, `followChanged` | `fseof`, `reporter_metabolites` | P2 |

### 4.4 Quality and gaps

| # | Page | MATLAB | Python | P |
|---|---|---|---|---|
| 16 | **Quality control** — structural checks, mass and charge balance, dead ends, leaks, "can it produce X" | `checkModelStruct`, `getElementalBalance`, `findPotentialErrors`, `gapReport`, `canProduce`, `canConsume`, `checkProduction`, `makeSomething`, `consumeSomething`, `findLeakMetabolite`, `checkRxn` | `check_model`, `get_elemental_balance`, `analyse_topology`, cobrapy `check_mass_balance` | P1 |
| 17 | **Gap-filling** — connectivity gaps vs growth gaps, with a template model | `fillGaps`, `gapFillFastLP`, `gapFillMILP`, `gapFillTopological`, `gapFillFastCore`, `gapFillSwiftCore` | `fill_gaps_fast_lp`, `fill_gaps_kumar_milp`, `analyse_topology`, `connect_blocked_reactions`, cobrapy `gapfill` | P1 |
| 18 | **Metabolic tasks** — write a task list, check it, find what a task needs, fit a model to tasks | `parseTaskList`, `checkTasks`, `fitTasks` | `parse_task_list`, `check_tasks`, `apply_task_constraints`, `find_task_essential_reactions`, `task_name_maps` | P1 |
| 19 | **Biomass composition** — fractions, rescaling, GAM | `getBiomassFractions`, `scaleBiomassFraction`, `scaleBiomassPseudoreaction`, `setGAM`, `fitParameters` | `sum_biomass`, `scale_biomass`, `rescale_pseudoreaction`, `set_gam` | P2 |
| 20 | **Annotation and metadata** — SBO terms, MIRIAM annotations, ΔG data | `assignSBOterms`, `editMiriam`, `extractMiriam`, `deltaGCSV` | `add_sbo_terms`, `load_delta_g_csv`, `save_delta_g_csv` | P3 |

### 4.5 Reconstruction

| # | Page | MATLAB | Python | P |
|---|---|---|---|---|
| 21 | **Draft models from homology** — BLAST/DIAMOND a proteome against templates, transfer reactions | `getBlast`, `getDiamond`, `getModelFromHomology`, `makeFakeBlastStructure` | `run_blast`, `run_diamond`, `blast_from_table`, `make_ortholog_hits`, `validate_hits`, `get_model_from_homology` | P2 |
| 22 | **Draft models from KEGG** — from a KEGG organism id, or from sequences via HMMs | `getKEGGModelForOrganism`, `getModelFromKEGG`, `getPhylDist` | `get_kegg_model_for_organism`, `get_kegg_model_from_sequences`, `build_hmm_library`, `phyl_dist` | P2 |
| 23 | **Context-specific models (tINIT / ftINIT)** — expression → reaction scores → extracted model | `getINITModel`, `ftINIT`, `prepINITModel`, `getINITSteps`, `scoreComplexModel`, `removeLowScoreGenes`, `parseHPA`, `parseHPArna`, `scoreModel` | `get_init_model`, `run_ftinit`, `prep_init_model`, `get_init_steps`, `gene_scores_from_expression`, `score_reactions_from_genes`, `remove_low_score_genes`, `parse_hpa`, `hpa_gene_scores`, `rna_gene_scores` | P1 |
| 24 | **Subcellular localization** — predictor scores → compartmentalised model | `predictLocalization`, `getUniProtScores`, `parseScores`, `assignCompartments`, `mapCompartments` | `predict_localization`, `apply_localization`, `load_wolfpsort`, `load_deeploc` | P3 |

### 4.6 Working with several models

| # | Page | MATLAB | Python | P |
|---|---|---|---|---|
| 25 | **Comparing models** — structural comparison of two or many models | `compareMultipleModels`, `compareRxnsGenesMetsComps`, `diffModels` | `compare_models`, `diff_models` | P2 |
| 26 | **Curating from tables** — spreadsheet-driven curation, gene renaming | `curateModelFromTables`, `renameModelGenes`, `getGeneData` | `batch_curate`, `batch_curate_from_tsv` | P3 |

**First wave (P1) = 13 pages**: 1, 2, 3, 4, 5, 6, 9, 10, 12, 16, 17, 18, 23 —
already broader than cobrapy's core, and it stands on its own.

## 5. Page anatomy

Every page follows one skeleton so the set reads as a single document:

1. **Title and a one-paragraph statement of the task** — what you have at the
   end, in one sentence.
2. **Functions on this page** — a three-column table (MATLAB | Python | note),
   every name linking into the API reference, cobrapy entries badged. This is the
   "clearly demonstrated" contract: the reader sees the scope before reading.

   Pages are **numbered** (`1. Getting started`, `2. Model structure and
   identifiers`, …) in the nav and in the page title, and their steps carry the
   page number (`4.1`, `4.2`), matching the protocol section's scheme. The
   how-to-read boilerplate lives once on the user-guide overview, not on every
   page; only the cobrapy clarification is repeated where it matters.
3. **Setup** — the model and data files used, in tabs. Always the same small
   example unless the topic demands otherwise (§7).
4. **Two to five numbered steps.** Each: one or two sentences of *why*, one tabbed
   code block, one output block. Never a code block without an explanation, never
   an explanation longer than the code.
5. **"What can go wrong"** — an admonition with the two or three failures people
   actually hit (infeasible LP, unbalanced reaction, mismatched gene ids).
6. **See also** — the neighbouring guide pages, the relevant API category, and
   cobrapy where cobrapy owns the topic.

Markdown conventions:

````markdown
=== "MATLAB"

    ```matlab
    sol = solveLP(model);
    ```

    ```text title="Output"
    ans = 0.0873
    ```

=== "Python"

    ```python
    sol = model.optimize()
    ```

    ```text title="Output"
    0.0873
    ```
````

Tabs are already linked and persistent site-wide (`content.tabs.link` in
`mkdocs.yml`), so choosing MATLAB once holds across every page of the guide.

### Marking cobrapy — yes, explicitly, in three places

A large part of the Python column *is* cobrapy, and hiding that would be the
single most misleading thing this guide could do: a reader who thinks
`get_by_id` is a raven-toolbox function looks for it in the wrong reference, and
files bugs in the wrong tracker. So every cobrapy call is marked, at three levels
of granularity:

1. **In the page's function table** — the Python cell carries the existing
   `<span class="cobrapy-tag">cobrapy</span>` badge (already styled in
   `docs/stylesheets/extra.css`, previously unused) and links to the cobrapy
   docs, not to our API reference.
2. **In the code itself** — imports are always explicit and never re-exported:
   `from cobra.io import read_sbml_model` next to
   `from raven_toolbox.io import read_yaml_model`. The reader sees the provenance
   in the snippet they paste, with no markup at all.
3. **In one line of prose under the block**, whenever a step is cobrapy's and the
   MATLAB tab makes it look like RAVEN's — e.g. "`check_mass_balance` is
   cobrapy's". Where raven-toolbox deliberately has no counterpart, the page says
   why in the same line.

Each guide page repeats the short version of this in its opening admonition, and
the user-guide overview states it once in full. It is the same convention the
generated mapping table uses ("Covered by cobrapy"), so the two agree.

Other callouts:

- `!!! warning "MATLAB only"` / `"Python only"` for genuinely unpaired steps;
- `!!! note "Different answer"` where results legitimately differ, linking to
  [`behaviour.md`](docs/behaviour.md).

## 6. Keeping the examples true — `scripts/run_examples.py`

**Built.** The build already fails on invented function names
(`scripts/check_names.py`); this covers the other half, the arguments and the
output. For every page under `docs/guide/` the runner:

- collects the ```` ```python ```` blocks in order, **including the ones indented
  inside `=== "Python"` content tabs** — a plain `^```` scan finds nothing on a
  dual-language page;
- runs one page's blocks in a single namespace, in a scratch directory seeded
  with a copy of `docs/data/`, so snippets can use the short relative paths the
  reader sees (`read_yaml_model("smallYeast.yml")`) without writing into the
  repo;
- captures stdout **plus the repr of a trailing bare expression**, the way a
  notebook cell would, and compares it with the `title="Output"` block that
  follows;
- reports mismatches as unified diffs and exits non-zero.

Authoring affordances:

| | |
|---|---|
| `--update` | rewrites the output blocks to what the snippets actually printed, at the right indentation, inserting a block where there was none. Blocks that already match are left alone, so deliberate `...` wildcards survive. |
| `--list` | shows what would run, with line numbers |
| `<!-- run-examples: skip -->` | before a block: not executed (BLAST, KEGG downloads, hour-long jobs) |
| `<!-- run-examples: skip-file -->` | anywhere in a page: the page is not executed at all |
| `...` in an output block | matches any run of characters, doctest ELLIPSIS style. A block that is *only* `...` matches anything and is the placeholder to write while drafting — `--update` fills those in, and leaves inline wildcards alone. |

The solver is pinned to **GLPK** (`--solver`), because it arrives as a wheel with
cobrapy and is therefore the one solver every reader and every runner has — so
the pasted numbers are reproducible without a Gurobi licence.

### Yes, it runs on GitHub Actions — `.github/workflows/examples.yml`

Nothing about it needs special infrastructure:

- `actions/checkout@v4` with `submodules: recursive`, then
  `pip install "./raven-toolbox[excel]"` — the examples are checked against the
  **exact submodule commit** the API reference is generated from, so a docs build
  and its example run can never disagree about which version they document;
- **no system packages**: GLPK comes in via cobrapy's `optlang`/`swiglpk`
  dependency as a wheel, so there is no `apt-get` step and no solver licence;
- triggers: pushes and PRs touching `docs/guide/`, `docs/data/`,
  the runner or the `raven-toolbox` submodule pointer — plus a **weekly cron**,
  which is the one that matters, since the submodules are bumped automatically
  and an upstream signature change is exactly the failure this catches;
- runtime is a couple of minutes; `timeout-minutes: 20` bounds a hung solve.

Cost is zero for a public repository. If it ever gets slow, the pages that need
downloads or long solves carry `skip-file` and are checked by a separate,
manually-triggered job.

**MATLAB runs too.** `--language matlab` writes each page's MATLAB blocks to
files, runs them in one MATLAB session per page (one workspace per page, so the
blocks build on each other), captures `evalc` output and diffs it exactly like
the Python half. RAVEN comes from the submodule with its bundled GLPK and
libSBML mex files, so nothing else is installed; `feature('hotlinks','off')` and
`warning('off','backtrace')` keep warning text stable, since the links and stack
traces name temporary paths that change every run.

In CI it runs in three steps rather than one: **MATLAB on a GitHub-hosted runner
is licensed only when a `matlab-actions` run-* action starts it**, and starting
`matlab` ourselves fails the license checkout. So `--matlab-prepare` writes the
harness, `matlab-actions/run-command@v2` runs the driver, and `--matlab-collect`
checks what it captured. Locally, where MATLAB has its own licence, the single
`--language matlab` command still does all three.

Two things the MATLAB half cannot do:

- `applyCondition` parses YAML through MATLAB's Python bridge, so it needs a
  linked CPython with `pyyaml`. That block carries a `skip` marker and the page
  says why.
- MATLAB is slower on the big model: `importModel` on yeast-GEM takes ~80 s, so
  the MATLAB job runs in minutes where the Python one runs in seconds.

## 7. Example data — copied into `docs/data/`

**Done.** cobrapy can lean on `cobra.io.load_model("textbook")`; we need a model
**both** toolboxes read from the same file, or the tabs stop being comparable.
Copied rather than read from the submodule, so the snippets can use short stable
paths that work identically for a reader who downloads the file and for CI:

| File | Size | From |
|---|---|---|
| `docs/data/smallYeast.yml` | 45 kB | `RAVEN/tutorial/smallYeast.yml` — the default example model |
| `docs/data/smallYeastBad.yml` | 45 kB | `RAVEN/tutorial/smallYeastBad.yml` — same model with deliberate errors, for the QC and gap-filling pages |
| `docs/data/yeast-GEM.yml` | 3.6 MB | yeast-GEM **v9.1.0** — the genome-scale model for sampling, deletions, ftINIT, gap-filling |
| `docs/data/yeast-GEM.xml` | 11.6 MB | the same release as SBML, for the I/O and annotation pages |

yeast-GEM replaces the *P. chrysogenum* model `iAL1006` as the genome-scale
example: it is the model this group develops and works with routinely, so a
reader recognises it and the guide's examples stay close to real work. It is
**pinned at v9.1.0** — the model keeps developing, and every number the guide
prints from it would otherwise change under it.

`docs/data/README.md` records the provenance, the licences (RAVEN MIT,
yeast-GEM CC-BY-4.0) and the refresh commands. The copies do **not** follow the
`RAVEN` submodule or the yeast-GEM releases automatically; moving to a newer
yeast-GEM means bumping the tag, re-downloading both files and re-generating the
affected output blocks in one commit.

Two measured facts that should shape which file a page reaches for:

- **Loading `yeast-GEM.yml` takes ~73 s in Python, against ~17 s for
  `yeast-GEM.xml`** (cobra 0.32.1, Python 3.14). Both give the identical model —
  4102 reactions, 2748 metabolites, 1143 genes. A page that only needs *a*
  genome-scale model should load the SBML; the YAML is for pages about the RAVEN
  YAML format itself. The runner executes a page's blocks in one namespace, so
  the cost is paid once per page, not once per block.
- **The SBML model id is mangled**: `yeastGEM_v9__46__1__46__0` in the XML versus
  `yeastGEM_v9.1.0` in the YAML, because SBML ids cannot contain dots. Worth a
  callout on the I/O page — it is exactly the kind of difference this guide
  exists to surface.

Pages that want a well-known annotated model (yeast-GEM, Human-GEM) fetch it by
URL and carry `<!-- run-examples: skip-file -->`.

## 8. Suggested order of work

1. Rewrite the Guides overview to introduce the three sub-sections.
2. P1 pages 1, 3, 9, 10 — the shortest path to a usable getting-started arc.
3. P1 pages 2, 4, 5, 6 — foundations complete.
4. P1 pages 12, 16, 17, 18, 23 — the RAVEN-specific value.
5. `run_examples.py` in CI once ~6 pages exist and the format has settled.
6. P2, then P3.

## 9. Open questions

- Section name: **"User guide"**, or something else ("Essentials", "How-to")?
- 26 pages, or fewer — merge 7 into 6, 14 into 13, 20 into 2?
- Which yeast-GEM release do we track, and how often do we move it forward?
- When do we add the MATLAB half of the example runner (§6)?

**Resolved:** example data lives in `docs/data/`, with yeast-GEM v9.1.0 as the
genome-scale model in both formats; the example runner is built and wired into
GitHub Actions; cobrapy calls are marked explicitly (§5).

---

## Appendix A — a drafted page

What page 1 would look like, to judge the format. Copy into
`docs/guide/getting-started.md` to try it.

---

# Getting started

Load a model, find out what is in it, and look at a single reaction, metabolite
and gene. Everything else in this guide assumes you can do this.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `importModel` | cobrapy `read_sbml_model` | read SBML |
| `readYAMLmodel` | `read_yaml_model` | read RAVEN YAML |
| `printModelStats` | cobrapy `Model` attributes | size of the model |
| `constructEquations` | cobrapy `Reaction.reaction` | a reaction as a string |
| `getIndexes` | cobrapy `DictList.get_by_id` | find things by id |

## 1. Load a model

We use `smallYeast.yml`, a small yeast model shipped with RAVEN.

=== "MATLAB"

    ```matlab
    model = readYAMLmodel('smallYeast.yml');
    ```

=== "Python"

    ```python
    from raven_toolbox.io import read_yaml_model

    model = read_yaml_model("smallYeast.yml")
    ```

    In Python a RAVEN model *is* a `cobra.Model` — there is no separate RAVEN
    model class, so every cobrapy method is available on it.

## 2. How big is it?

=== "MATLAB"

    ```matlab
    printModelStats(model);
    ```

    ```text title="Output"
    ...
    ```

=== "Python"

    ```python
    print(len(model.reactions), len(model.metabolites), len(model.genes))
    ```

    ```text title="Output"
    ...
    ```

    raven-toolbox has no `printModelStats` equivalent: cobrapy's `Model` exposes
    the collections directly, and `model.summary()` prints an overview after a
    solve.

## 3. Look at one reaction

...

## 4. Look at one metabolite

...

## 5. Look at one gene

...

!!! warning "What can go wrong"
    - **`importModel` warns about unbalanced reactions.** ...
    - **Gene ids differ between the model and the FASTA.** ...

## See also

- [Reading and writing models](io.md) — every format both toolboxes support.
- [Model structure and identifiers](model-structure.md) — how the RAVEN struct and
  `cobra.Model` correspond.
- API reference: [io](../api/io.md).
