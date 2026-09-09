# Migrating from RAVEN 2 to RAVEN 3

:::{admonition} If you read nothing else
:class: important

Run `checkRaven` (replaces `checkInstallation`) right after upgrading: it
offers to fetch any missing on-demand binaries/data, and its checks catch
several of the changes below before your scripts do. Beyond that, the two
changes most likely to break silently rather than error are homology/KEGG
reconstruction returning a different draft model from the same call
([§7](#kegg-reconstruction)), and WoLF PSORT-based localization scores having
no in-toolbox migration path ([§3](#backward-incompatible-changes)).
:::

This guide describes what changed between RAVEN 2 and RAVEN 3. It is written
for existing RAVEN 2 users who need to know what will break in their scripts,
what moved, what was removed outright, and what new capabilities are
available.

**Versions covered:** the latest released RAVEN 2 is **2.11.3**. RAVEN 3 is
unreleased; it is being developed on the `develop3` branch and is targeting
version **3.0.0**. This guide compares `develop3` against RAVEN 2's `develop`
branch (functionally identical to the 2.11.3 release; the commits between
them are only version-bump/tag merges). **This document will be frozen once
3.0.0 is tagged**; until then, `develop3` can still change.

RAVEN 3 is a deliberate breaking release: the codebase was reorganized, a large
number of low-value or duplicate functions were removed, several external
dependencies were dropped, and the calling convention for optional function
arguments changed almost everywhere. None of this was accidental; see the
project's [v3 development review](https://github.com/SysBioChalmers/RAVEN/blob/develop3/docs/v3_review.md)
for the rationale, but it means that **most non-trivial RAVEN 2 scripts need to
be checked**, even if most of the core reconstruction/analysis behavior is
unchanged in spirit.

:::{note} This is the MATLAB-to-MATLAB axis
This page is about RAVEN 2 → RAVEN 3, both MATLAB. How the Python package
differs from the MATLAB one is a separate question, answered in
[RAVEN 3 and raven-toolbox](raven3-vs-raven-toolbox.md).
:::

Start with the [upgrade checklist](#upgrade-checklist) below, then read
[Backward-incompatible changes](#backward-incompatible-changes); it is the
punch list. The sections after it go into the detail behind each item.

---

(upgrade-checklist)=
## Upgrade checklist

1. Update to RAVEN 3.0.0 (or later) and run `checkRaven` (replaces
   `checkInstallation`); it will offer to fetch any missing on-demand
   binaries/data (§11).
2. Search your scripts for the functions listed in [§4](#removed-functionality)
   (removed) and [§5](#renamed-merged-and-consolidated-functions)
   (renamed/merged) and update or remove those calls.
3. If you use `getModelFromKEGG`/`getKEGGModelForOrganism` or
   `getModelFromHomology`: expect a different draft reconstruction even from an
   unmodified call: default cutoffs, the KEGG data source, and the homology
   best-hit criterion all changed ([§7](#kegg-reconstruction)). Rebuild and
   re-validate any KEGG- or homology-derived draft models.
4. If you use `.xlsx` curation templates or `importExcelModel`: convert your
   curation data to the `.tsv` format `curateModelFromTables` expects; there
   is no drop-in Excel importer ([§6](#excel-io)).
5. If you use WoLF PSORT-based localization scores: switch to one of the
   modern predictors (DeepLoc2, MULocDeep, COMPARTMENTS, UniProt); there is no
   in-toolbox migration path ([§10](#new-functionality)).
6. If your workflows include metabolic-task gap-filling (`fitTasks`,
   `checkTasks`, `ftINIT`): re-run and check task pass/fail results; a fixed
   bug means a previously "passing" task can now correctly fail
   ([§9](#ftinit)).
7. If your model files are under version control (YAML/SBML): expect diffs on
   the next export even with no content changes (quoting style, EC-code
   annotation, ΔG fields; [§6](#file-formats-and-model-io)).
8. Re-run your own test suite / validation pipeline and diff key outputs
   (model size, growth rate, task results) against your RAVEN 2 baseline
   before trusting RAVEN 3 results in production.

---

## 1. Repository reorganization

RAVEN 2's top-level layout (`core/`, `external/`, `hpa/`, `io/`, `legacy/`,
`pathway/`, `plotting/`, `solver/`, `struct_conversion/`, `installation/`,
`utils/`) has been replaced with functional folders that group functions by what
they do rather than by legacy history:

| RAVEN 3 folder | Contents | Mostly came from (RAVEN 2) |
|---|---|---|
| `INIT/` | `ftINIT`, `INIT/tINIT/` for `getINITModel`/`runINIT`, and HPA/expression parsing + gene scoring (`parseHPA`, `parseHPArna`, `scoreModel`) | `INIT/`, `hpa/` |
| `analysis/` | FBA-adjacent analyses: FVA, sampling, FSEOF, OptKnock, robustness, production envelope, flux comparison/tracing | `core/` |
| `annotation/` | MIRIAM editing, SBO term assignment, ΔG CSV I/O | `struct_conversion/` (+ new) |
| `biomass/` | Biomass composition fitting/scaling, GAM | `core/` (+ new) |
| `comparison/` | Multi-model comparison, structured model diffing | `core/` (+ new) |
| `conditions/` | Applying a data-driven growth/media condition to a model | *new folder* |
| `conversion/` | RAVEN⇄COBRA conversion, identifier prefixing, field ordering | `struct_conversion/` |
| `curation/` | Genome-annotation-driven gene/model curation | *new folder* |
| `gapfilling/` | `fillGaps` and its pluggable algorithms, task fitting, leak-metabolite/exchange checks | `core/` (+ new) |
| `installation/` | Path setup, on-demand binary/data download | `installation/` |
| `io/` | Model import/export (SBML, YAML, Excel), FASTA I/O | `io/` |
| `localization/` | Subcellular localization prediction/scoring, compartment assignment | `external/` (+ new) |
| `manipulation/` | Structural edits: add/remove/change rxns, mets, genes; merge, sort, simplify | `core/` |
| `queries/` | Non-mutating lookups: indexes, exchange/transport reactions, stoichiometry construction, model checking | `core/` |
| `reconstruction/` | KEGG- and homology-based draft reconstruction | `external/` |
| `solver/` | LP/MILP solving | `solver/` |
| `tasks/` | Metabolic task list parsing/checking | `core/` |
| `testing/` | `matlab.unittest` suite (`function_tests/`) | `testing/` |
| `utils/` | Generic helpers, including the new argument-parsing/registry infrastructure | `utils/` |
| `deprecated/` | Thin backward-compatible wrappers for merged/renamed functions | *new folder* |

Entirely removed (no successor folder): `external/metacyc/` (MetaCyc
reconstruction), `pathway/` and `plotting/` (visualization), `legacy/`
(CellDesigner import and other pre-2.0 code), `struct_conversion/`'s Excel-POI
helpers.

**Practical impact is smaller than it looks.** If your scripts call RAVEN
functions by name (the normal usage pattern, with the whole RAVEN folder tree,
including subfolders, added to the MATLAB path via `addRavenToUserPath` or
`addpath(genpath(...))`), moving a file to a new subfolder does not break the
call: MATLAB resolves functions by name across the whole path, not by a
hard-coded relative location. The reorganization only matters if you (a)
hard-coded a path to a specific `.m` file, (b) called one of the functions that
was actually removed or merged (see below), or (c) shadowed a RAVEN function
name with your own; folder names are irrelevant otherwise.

The full moved-file mapping (RAVEN 2 path → RAVEN 3 path) for every relocated
function is available on request / in the repository's git history
(`git diff --stat -M develop...develop3`); it is not reproduced in full here
because it is large and, per the point above, rarely something you need to act
on.

---

## 2. Calling convention: positional or named arguments

RAVEN 2 functions took optional arguments strictly positionally
(`f(model, a, b, c)`), which made it easy to lose track of argument order and
impossible to skip an early optional argument to set a later one without also
specifying all of the ones in between.

RAVEN 3 introduces `utils/parseRAVENargs.m`, used by 112 functions across the
toolbox. Required leading arguments stay as explicit, positional parameters;
everything optional is collected into `varargin` and can be supplied three ways,
interchangeably:

```matlab
removeReactions(model, rxnList, true, true, true)                       % positional (RAVEN 2 style, still works)
removeReactions(model, rxnList, "removeUnusedGenes", true)              % named
removeReactions(model, rxnList, true, "removeUnusedComps", true)        % hybrid
```

The rule: parsing scans for the first argument that is a string matching a known
parameter name. Everything before that point is assigned positionally, in the
order the function's `parseRAVENargs` specification declares; everything from
that point on must be valid name-value pairs.

**This means old positional calls keep working, *provided* the function's new
parameter order still matches the old positional order.** In every function
spot-checked for this guide (`importModel`, `exportModel`,
`exportToExcelFormat`, `removeReactions`, `ftINIT`, `fillGaps`, `fitTasks`,
`getModelFromHomology`, `addIdentifierPrefix`/`removeIdentifierPrefix`, and
`exportForGit`), new optional parameters were appended at the end of the list,
so old positional calls keep working unchanged.

One caveat from the parser's own documentation: if a positional argument you're
passing is itself a string that happens to match one of the function's parameter
names, use the explicit name-value form for that argument to avoid ambiguity.

---

(backward-incompatible-changes)=
## 3. Backward-incompatible changes

This is the consolidated list of everything a RAVEN 2 script could plausibly
break on, or silently produce different output from, when run against RAVEN 3.
Items are grouped by how they manifest.

### Will error / undefined function

| RAVEN 2 usage | What happens in RAVEN 3 |
|---|---|
| `importExcelModel(...)` | Removed. Use `curation/curateModelFromTables.m` (different input format: `.tsv`, not `.xlsx`; see [§6](#excel-io)) or convert your template to YAML/SBML and use `importModel`. |
| `importModel(...)` on SBML Level < 3, Level 3 without FBC v2, or any non-FBC SBML | Errors. Only SBML **Level 3 Version 1, FBC package version 2** is accepted (see [§6](#sbml-io)). |
| `exportToExcelFormat(model, fileName)` where `fileName` is a bare path (no `.xlsx`) | No longer falls back to tab-delimited text export; errors with "only export to xlsx format is supported". |
| `exportToTabDelimited(...)` | Removed outright (was a dead-code path anyway). |
| `getWoLFScores(...)` / `parseScores(..., 'wolf', ...)` | WoLF PSORT support is fully removed. `parseScores` now errors on `'predictor','wolf'` with a message pointing to `'deeploc'`, `'mulocdeep'`, `'compartments'`, or `'uniprot'`. **No in-toolbox migration path for existing WoLF PSORT output files.** |
| `qMOMA(...)`, `solveQP(...)` | Removed (RAVEN's last `quadprog`/Optimization Toolbox dependency). `findGeneDeletions`'s `analysisType`/`refModel`/`oeFactor` arguments (MOMA-based over-expression analysis) were removed with them; only FBA-based single/double gene deletion (`sgd`/`dgd`) remains. |
| `checkRxn(...)` | Removed, no direct successor. For debugging why a reaction can't carry flux, use `gapfilling/findLeakMetabolite.m` / `gapfilling/canExchange.m`, or `gapfilling/checkProduction.m`. |
| `dispEM(...)`, `followFluxes(...)`, `followChanged(...)`, `printModel(...)`, `mapCompartments(...)`, `getExpressionStructure(...)`, `getMetsInComp(...)`, `parallelPoolRAVEN(...)` | All removed (see [§4](#removed-functionality) for what replaces each, where anything does). |
| Anything under `external/metacyc/`, `pathway/`, `plotting/`, `legacy/` | Entire subsystems removed: MetaCyc-based reconstruction and all visualization/plotting functionality (`drawMap`, `drawPathway`, `markPathwayWithFluxes`, `setOmicDataToRxns`, etc.). No in-toolbox replacement; use COBRA Toolbox or Escher for visualization. |
| `getGenesFromKEGG`, `getMetsFromKEGG`, `getRxnsFromKEGG`, `constructMultiFasta`, `getWSLpath`, `getBlastFromExcel` | Removed along with the old local-KEGG-FTP-dump workflow (see [§7](#kegg-reconstruction)). |
| `getToolboxVersion(...)` | Removed as a standalone function; folded into an internal helper of `exportForGit`. |

### Will silently produce different results

Same call, same input model, different output. Grouped by function; see the
linked section for the full explanation of each.

| Function | New behavior (default, unless noted) |
|---|---|
| `getModelFromHomology`, `strictness=3` | Best-hit tie-break now uses **bitscore** instead of E-value (`"scoreBy","evalue"` restores the old criterion); [§7](#kegg-reconstruction) |
| `getModelFromHomology`, `minLen` | Default lowered from `200` to `100`; [§7](#kegg-reconstruction) |
| `getModelFromHomology`, GPR merging | Gene substitution is exact-token-based instead of regex/`strrep`-based; [§7](#kegg-reconstruction) |
| `getKEGGModelForOrganism`, `cutOff` | Default lowered from `10^-50` to `10^-30`; [§7](#kegg-reconstruction) |
| `getKEGGModelForOrganism`, `minScoreRatioG` | Default raised from `0.8` to `0.9`; [§7](#kegg-reconstruction) |
| `removeGenes`, `expandModel`, `findPotentialErrors`, `addRxns` | grRules are now parsed correctly (exact gene-token matching, structure-aware isozyme/complex handling) instead of via substring/regex matching; [§8](#gpr-parsing) |
| `changeGrRules(..., 'replace', false)` onto a gene-less reaction | Produces a valid grRule instead of an unparseable one; [§8](#gpr-parsing) |
| `simplifyModel` (used by task-based gap-filling) | No longer drops a task's boundary constraint on a metabolite with no reactions: a task that used to silently pass may now correctly fail; [§9](#ftinit) |
| `ftINITInternalAlg` | `allowExcretion` constraint sign corrected |
| `ravenCobraWrapper` | Gene-ID-to-MIRIAM matching no longer breaks on gene IDs containing regex metacharacters; [§6](#raven-cobra-interoperability) |
| `permuteModel`, `randomSampling`, `optimizeProb`, `getFluxZ`, `mergeCompartments`, `convertToIrrev`, `replaceMets`, `setExchangeBounds`, `fitParameters`, `guessComposition` | Each had a pre-existing bug fixed; output differs only for models/inputs that triggered it |

None of these are API changes; the same call with the same arguments now
returns a different, corrected result.

### Will warn, but keep working

- **Error/warning identifiers changed.** `dispEM` (RAVEN 2's universal
  error/warning function) always raised errors with an **empty** identifier
  (`MException('', ...)`), so no RAVEN 2 script could have legitimately caught
  on `err.identifier`. RAVEN 3 replaces `dispEM` with native `error()`/
  `warning()` calls, most (not all) carrying real identifiers,
  predominantly `RAVEN:badInput`, plus a handful of specific ones
  (`RAVEN:modelError`, `RAVEN:badGrRule`, `RAVEN:sampling`, `RAVEN:infeasible`,
  `RAVEN:grRuleTooComplex`). Message text is largely unchanged (many messages
  are byte-identical to RAVEN 2's), so `try/catch` blocks that pattern-match on
  message text keep working; scripts can newly (optionally) match on
  `err.identifier` instead.
- **`getINITModel`/`runINIT` now emit a one-time "legacy" notice** pointing at
  `ftINIT`, silenceable with `warning('off','RAVEN:legacyMethod')`. This is
  explicitly *not* a deprecation; RAVEN's own documentation states these
  functions "remain supported" indefinitely, to reproduce previously published
  Human-GEM-derived models. See [§9](#ftinit).
- **`makeSomething`, `consumeSomething`, `canProduce`, `canConsume`** now live in
  a new `deprecated/` folder as thin wrappers around `findLeakMetabolite`/
  `canExchange`, and emit a one-time `RAVEN:deprecated` warning stating they
  "will be removed in the next major release." Unlike the legacy-notice
  functions above, these are on an actual removal track; migrate call sites
  before the next major release. See [§9](#ftinit).
- **`checkInstallation` is now `checkRaven`**, moved from `installation/` to the
  repository root, with an unchanged signature
  (`[currVer, installType] = checkRaven(developMode, checkBinaries)`). Existing
  calls do **not** break: `checkInstallation` survives as a forwarding wrapper
  that passes every argument and output straight through, after emitting a
  `RAVEN:deprecated` warning naming `checkRaven`. It is on the same removal
  track as the `deprecated/` functions above, so switch at the next opportunity.

### Environment / installation changes

KEGG HMM libraries and external command-line binaries (BLAST+, DIAMOND, HMMER,
cd-hit, MAFFT, WoLF PSORT) are no longer committed to the repository. RAVEN 3
fetches them on demand from the `raven-data` GitHub release the first time a
function needs one, which means **internet access is required on first use**,
not just at clone/install time. See [§11](#toolbox-deps) for what's needed for
an air-gapped install, and the full dependency comparison.

---

(removed-functionality)=
## 4. Removed functionality

Beyond the items already listed as backward-incompatible above, RAVEN 3 removed
a number of functions and whole subsystems as part of a deliberate "leaner
codebase" push. None of these have call sites left in RAVEN 3 itself.

| Removed | What it did | Replacement / notes |
|---|---|---|
| `pathway/*`, `plotting/*` (16 functions: `drawMap`, `drawPathway`, `colorPathway`, `colorSubsystem`, `markPathwayWithFluxes`, `markPathwayWithExpression`, `setOmicDataToRxns`, `plotAdditionalInfo`, etc.) | Metabolic map/pathway visualization | None in RAVEN core. Use COBRA Toolbox, Escher, or export flux/omics data for external plotting. |
| `external/metacyc/*` (7 functions: `getModelFromMetaCyc`, `getRxnsFromMetaCyc`, `getMetsFromMetaCyc`, `getEnzymesFromMetaCyc`, `addSpontaneousRxns`, `linkMetaCycKEGGRxns`, `combineMetaCycKEGGModels`) | MetaCyc-based draft reconstruction | None; KEGG- and homology-based reconstruction remain the supported paths. |
| `legacy/*` (CellDesigner import, `changeGeneAssoc`, the bundled `xml_toolbox`) | Pre-2.0 compatibility code | None; considered dead. |
| `io/importExcelModel.m`, `io/loadWorkbook.m`, `io/loadSheet.m`, `io/writeSheet.m`, `io/SBMLFromExcel.m`, `io/addJavaPaths.m`, `io/startup.m` | Apache-POI-based Excel model I/O | `io/writeExcel.m` (dependency-free OOXML writer) for export; `curation/curateModelFromTables.m` for tabular curation. No full Excel-template *import* path remains; see [§6](#excel-io). |
| `io/exportModelToSIF.m`, `io/exportToTabDelimited.m` | SIF graph export; tab-delimited model export | Dead/orphaned code with no callers; removed outright. |
| `io/getFullPath.m`, `io/getMD5Hash.m`, `io/getToolboxVersion.m` | Path canonicalization; file MD5 hashing; toolbox git-version lookup | Inlined where still needed (e.g. MD5 via Java's `MessageDigest` directly inside `getBlast`), or folded into `exportForGit`. |
| `core/dispEM.m` | Universal error/warning display | Native `warning()`/`error()` + new `utils/ravenList.m` for formatted item lists. See [§3](#backward-incompatible-changes). |
| `core/followFluxes.m`, `core/followChanged.m` | Flux-change reporting relative to a reference solution | `queries/printFluxes.m` covers the cutoff-filtering half; nothing replaces the reference-flux comparison directly. |
| `core/printModel.m` | Printed reactions to screen/file | `queries/printModelStats.m` / `queries/printFluxes.m` cover related summary/flux printing; no direct one-line-per-reaction dump remains. |
| `core/getMetsInComp.m` | Returned metabolite indices in a given compartment | Inline it as `model.metComps == compIndex`. |
| `core/mapCompartments.m` | Remapped compartment labels in a localization-score structure | Superseded by the new predictor-based localization workflow and `localization/defaultCompartmentMap.m`. |
| `core/getExpressionStructure.m` | Loaded an expression-experiment structure from an ad hoc Excel format | Superseded by `INIT/parseHPA.m`/`INIT/parseHPArna.m` for the supported expression-data workflow. |
| `core/checkRxn.m` | Per-reaction reactant/product synthesizability debugging | No direct successor; use `gapfilling/findLeakMetabolite.m`, `gapfilling/canExchange.m`, or `gapfilling/checkProduction.m`. |
| `core/parallelPoolRAVEN.m` | Parallel Computing Toolbox pool setup | Renamed/rewritten as `utils/parallelWorkersRAVEN.m`. |
| `external/getWoLFScores.m` | WoLF PSORT score parsing | None; see [§3](#backward-incompatible-changes). |
| `external/kegg/{getGenesFromKEGG,getMetsFromKEGG,getRxnsFromKEGG,constructMultiFasta,getWSLpath}.m`, `external/getBlastFromExcel.m` | Local-KEGG-FTP-dump parsing; per-KO multi-FASTA assembly; WSL path translation; Excel-based BLAST import | Superseded by the raven-data-artifact-based KEGG pipeline. See [§7](#kegg-reconstruction). |
| `solver/qMOMA.m`, `solver/solveQP.m` | MOMA-based analyses (quadratic programming) | Removed; no in-toolbox QP-based replacement. See [§3](#backward-incompatible-changes) for `findGeneDeletions` impact. |
| `testing/unit_tests/*.m` (script-based tests) | Ad hoc test scripts | `testing/function_tests/*.m`, a `matlab.unittest`-class-based suite. Contributor-facing only; `runRAVENtests` usage is unchanged for end users. |

---

(renamed-merged-and-consolidated-functions)=
## 5. Renamed, merged, and consolidated functions

RAVEN 3 introduces a formal **`deprecated/` folder convention**: functions that
were merged into a more general replacement stay callable under their old name,
as a thin wrapper that emits a one-time `RAVEN:deprecated` warning ("will be
removed in the next major release") and forwards to the new function.

| Old function(s) | New function | Notes |
|---|---|---|
| `makeSomething(model, ignoreMets, isNames, minNrFluxes, allowExcretion, params, ignoreIntBounds)` | `findLeakMetabolite(model, 'produce', ...)` | Argument order maps 1:1; the wrapper forwards `varargin` unchanged. |
| `consumeSomething(model, ignoreMets, isNames, minNrFluxes, params, ignoreIntBounds)` | `findLeakMetabolite(model, 'consume', ...)` | **Not** a verbatim forward: `consumeSomething`'s old positional order has no `allowExcretion` slot, so the wrapper explicitly remaps arguments by name to avoid corrupting `params`/`ignoreIntBounds`. |
| `canProduce(model, mets)` | `canExchange(model, 'produce', 'mets', mets)` | |
| `canConsume(model, mets)` | `canExchange(model, 'consume', 'mets', mets)` | |
| `compareRxnsGenesMetsComps` | folded into `comparison/compareMultipleModels.m` | Its rxn/gene/met/comp overlap output is now one part of `compareMultipleModels`'s output; no separate function remains. |
| `INIT/scoreComplexModel.m` | `INIT/scoreModel.m` | **Merged, not renamed.** RAVEN 2 had *both* `INIT/scoreComplexModel.m` and `hpa/scoreModel.m`; RAVEN 3 folded them into one `scoreModel`, called with different settings from tINIT than from ftINIT. A RAVEN 2 call to `scoreModel` is unaffected; a call to `scoreComplexModel` has to move to `scoreModel` *and* pass the settings that reproduce the old behaviour (a single operator for both `and`/`or`, `dataPrecedence` `'reaction'`). |
| `INIT/ftINITFillGapsMILP.m` | folded into `solver/getMinNrFluxes.m` | Exposed now via `getMinNrFluxes`'s `resolveTies`/`proveAbsGap` options. |
| `INIT/ftINITFillGapsForAllTasks.m` | folded into `gapfilling/ftINITFillGaps.m` and `fitTasks`'s `'preMerged'` gap-fill mode | |
| `getGenesFromKEGG`/`getMetsFromKEGG`/`getRxnsFromKEGG` | `reconstruction/kegg/readKEGGTable.m` + the raven-data KEGG artifacts | Not a direct signature-compatible rename: the whole data source changed; see [§7](#kegg-reconstruction). |
| `checkInstallation` | `checkRaven` | Moved from `installation/checkInstallation.m` to repo-root `checkRaven.m`; identical calling signature. `checkInstallation` remains as a deprecated forwarding wrapper, so old calls keep working with a `RAVEN:deprecated` warning. |

Separately, `getINITModel` and `runINIT` (now under `INIT/tINIT/`) are marked
**legacy but indefinitely supported** (not on the `deprecated/` removal track)
via `utils/legacyMethodNotice.m`, which fires a one-time, silenceable
`RAVEN:legacyMethod` warning pointing at `ftINIT`. Use `ftINIT` for new work;
keep `getINITModel`/`runINIT` only to reproduce models originally built with
them.

---

(file-formats-and-model-io)=
## 6. File formats and model I/O

(sbml-io)=
### SBML I/O

| | RAVEN 2 | RAVEN 3 |
|---|---|---|
| `exportModel` output format | SBML Level 3 Version 1, FBC v2 | unchanged |
| `importModel` accepted input | any SBML level/version; L2-style notes-based gene associations (`GENE_ASSOCIATION`/`PROTEIN_ASSOCIATION`) also read; FBC fields optional | only SBML **Level 3 Version 1, FBC v2**; anything else errors |
| MIRIAM prefixes read on import | `urn:miriam:`, `http://identifiers.org/`, `https://identifiers.org/` | unchanged |

Older SBML files must be converted first (e.g. re-exported from COBRApy/COBRA
Toolbox) before `importModel` will accept them.

(excel-io)=
### Excel I/O

| | RAVEN 2 | RAVEN 3 |
|---|---|---|
| Excel engine | Apache POI (Java), bundled | dependency-free OOXML writer (`io/writeExcel.m`) |
| Full-model `.xlsx` import | `importExcelModel.m` (`RXNS`/`METS`/`COMPS`/`GENES`/`MODEL` sheets → complete model) | removed, no equivalent importer |
| Nearest replacement for curation | no equivalent | `curation/curateModelFromTables.m`: curates/extends an *existing* model from separate `.tsv` files (mets by name+compartment, reactions by stoichiometry, genes by name), not a from-scratch importer |
| `exportToExcelFormat` on a bare path (no `.xlsx`) | fell back to tab-delimited text export | errors, `.xlsx` only |

If your pipeline depends on the old Excel curation template, either convert it
to the `.tsv` shape `curateModelFromTables` expects, or build the model via
`importModel`/YAML and use `curateModelFromTables` for incremental edits.

### YAML I/O

`readYAMLmodel`/`writeYAMLmodel` are pure-MATLAB in both branches; model YAML
I/O has no Python dependency in RAVEN 2 or RAVEN 3. (`io/parseYAML.m` is an
unrelated, new, pure-MATLAB generic YAML parser used only by
`conditions/applyCondition.m` to read condition files; it doesn't affect
model I/O.) Output format changes, visible as diffs in version-controlled
model files:

| | RAVEN 2 | RAVEN 3 |
|---|---|---|
| Quote style | single quotes | double quotes |
| Reaction EC codes | top-level `eccodes` field only | also written under `annotation: ec-code` |
| Gene-less model | `genes:` section omitted | `genes: []` written explicitly |
| Empty `gene_reaction_rule` | written as an empty string | omitted |
| `objective_coefficient` on import | ignored | honored |

(raven-cobra-interoperability)=
### RAVEN⇄COBRA interoperability

`conversion/ravenCobraWrapper.m` keeps its signature
(`newModel = ravenCobraWrapper(model)`) unchanged. Two correctness fixes change
output for affected models: a stale-variable bug that could reuse the wrong
MIRIAM data during gene-annotation conversion, and gene IDs containing regex
metacharacters (e.g. `ENSG00000141510.16`) that could be mis-matched during
annotation conversion; both fixed.

---

(kegg-reconstruction)=
## 7. Reconstruction: KEGG and homology pipelines

### KEGG-based reconstruction (`getModelFromKEGG`, `getKEGGModelForOrganism`)

| | RAVEN 2 | RAVEN 3 |
|---|---|---|
| Reaction/gene database source | local KEGG FTP dump (license required), parsed by `getGenesFromKEGG`/`getMetsFromKEGG`/`getRxnsFromKEGG` into a cached `keggModel.mat` | prebuilt artifacts (a gene-free reference model plus KO/reaction/organism tables) fetched on demand from the `raven-data` GitHub release, assembled by `buildGlobalKEGGModel`/`buildGlobalGPR`/`readKEGGTable` |
| `getModelFromKEGG`'s `keggPath` argument | required | removed, not needed |
| Ortholog HMM library | one `.hmm` file per KO (self-built via CD-HIT + MAFFT + `hmmbuild`, or downloaded); queried with one `hmmsearch` call per KO, via WSL on Windows | one concatenated per-domain library (`kegg118_eukaryotes.hmm` / `kegg118_prokaryotes.hmm`); one `hmmsearch` call against the whole proteome, no WSL |
| `dataDir` | arbitrary local folder | must be `kegg118_eukaryotes` or `kegg118_prokaryotes` |
| `nSequences`, `seqIdentity` (CD-HIT clustering controls) | configurable | removed, no local clustering step |
| `cutOff` default | `10^-50` | `10^-30` |
| `minScoreRatioG` default | `0.8` | `0.9` |
| Calling convention | positional | positional-or-named (`parseRAVENargs`); old positional order preserved |

### Homology-based reconstruction (`getModelFromHomology`)

| | RAVEN 2 | RAVEN 3 |
|---|---|---|
| `strictness` parameter | `1`/`2`/`3` | unchanged |
| Best-hit tie-break at `strictness=3` | E-value | bitscore by default (`"scoreBy","evalue"` restores the old criterion) |
| `minLen` default | `200` | `100` |
| GPR gene substitution when merging homology hits | regex/`strrep` substitution (could corrupt IDs that were substrings of one another, or contained regex metacharacters) | exact-token-based substitution |

### Shared infrastructure

External binaries (BLAST+, DIAMOND, HMMER) and the KEGG data artifacts
themselves are fetched on demand rather than bundled with the repository; see
[§11](#toolbox-deps).

**New:** `curation/downloadGenomeData.m`, `curation/getGeneData.m`, and
`curation/processProteinFastaFile.m` give a new on-ramp from a bare NCBI genome
accession (`GCF_`/`GCA_`) straight to a model-ready proteome and gene ID
mapping table.

---

(gpr-parsing)=
## 8. Gene-reaction-rule (GPR) parsing

RAVEN 3 adds a proper grRule tokenizer/parser: `utils/parseGrRule.m` builds a
parse tree (`type`: `'gene'|'and'|'or'`, with `children`); `utils/grRuleToDNF.m`
converts it to disjunctive normal form (RAVEN's canonical "OR of AND-clauses"
shape for enzyme-complex/isozyme structure); `utils/isDnfGrRule.m` checks
whether a rule is already in that form; `utils/grRuleToString.m` renders a tree
back to a canonical string. These are used internally by four functions,
they are **not** applied automatically to every loaded model; a grRule keeps
its original text unless one of these functions is called on it.

| Function | RAVEN 2 parsing | RAVEN 3 parsing |
|---|---|---|
| `removeGenes` | substring match on gene ID (`"10"` also matched `"100"`) | exact gene-token match |
| `expandModel` | naive split on `' or '` (could drop an `AND`-ed subunit inside a nested rule) | parse-tree-based isozyme expansion, preserves nested `AND`/`OR` |
| `findPotentialErrors` | string-pattern check for `") and ("` etc. (false positives on valid rules) | parse-tree-based non-DNF detection |
| `addRxns` (new gene IDs from a grRule) | split on the substrings "and"/"or" anywhere (could shred an ID like `"band1"`) | split only on space-bounded `' and '`/`' or '` tokens |
| `comparison/diffModels.m` | (function didn't exist) | grRules compared as logical DNF equality, not string equality |

The accepted grRule *syntax* itself is unchanged: `' and '`/`' or '`
(case-insensitive) still work exactly as before, and
`manipulation/standardizeGrRules.m` (which runs on import) uses the same
string-splitting logic it always did.

---

(ftinit)=
## 9. Gap-filling and context-specific model extraction

| | RAVEN 2 | RAVEN 3 |
|---|---|---|
| `fillGaps` algorithm | one built-in MILP connectivity-maximization strategy | same strategy is still the default; `algorithm` option adds `'fastLP'`/`'swiftLP'` (FASTCORE/SWIFTCORE-style LP relaxation), `'gapfillMILP'` (growth-floor MILP with directionality repair), `'topological'` (BFS producibility pre-screen, no model modification) |
| `fillGaps` positional arguments | `allowNetProduction, useModelConstraints, supressWarnings, rxnScores` | unchanged; new options are name-value-only |
| `ftINIT` tie-breaking | depends on solver seed | optional `resolveTies` pins degenerate MILP optima to a deterministic answer |
| `ftINIT` MILP optimality proof | escalating relative-gap search only | optional `proveAbsGap` proves each stage to a fixed absolute gap in one solve |
| `ftINIT` positional arguments | preserved | unchanged; `resolveTies`/`proveAbsGap` are name-value-only, default off |
| `getINITModel`/`runINIT` | supported, no runtime notice | supported, now under `INIT/tINIT/`; one-time "legacy, use `ftINIT`" notice (see [§5](#renamed-merged-and-consolidated-functions)) |
| `fitTasks` gap-fill mode | one behavior (equivalent to today's `'merge'`) | `gapFillMode`: `'merge'` (default, same as before) or `'preMerged'` (faster, ftINIT-style) |
| `fitTasks` outputs | `[outModel, addedRxns]` | `[outModel, addedRxns, failedTasks]` |
| Task requiring net production of a metabolite with no reactions | boundary constraint silently dropped before gap-filling; task could incorrectly report as passing | constraint preserved; task correctly reports failing if the reference model can't produce it |

---

(new-functionality)=
## 10. New functionality

All additive; none of this replaces or changes behavior of existing RAVEN 2
functions, except where noted.

| Area | New function(s) | What it adds |
|---|---|---|
| Flux sampling (`analysis/`) | `sampleACHR`, `sampleCHRR`, `sampleMaxVolEllipse`, `sampleChebyshevCenter`, `sampleWarmupPoints` | `randomSampling` becomes a dispatcher (`'method'` option) across RAVEN 2's original random-objective method (now `'randomObjective'`) plus two new near-uniform MCMC samplers: ACHR (hit-and-run) and CHRR (hit-and-run with rounding, better mixing on ill-conditioned polytopes) |
| Flux analysis / QC | `compareFluxes`, `getMinimalMedium`, `traceFluxPath`, `walkFluxes`, `modelSummary` | structured flux-vector diffing; MILP-based minimal-medium search; highest-flux-fraction path tracing between two reactions; interactive flux-neighborhood navigation; model/flux summary printing |
| Model comparison (`comparison/`) | `diffModels` | structured, ID-keyed diff between two models: stoichiometry, bounds, objective, grRule (as logical DNF equality), EC codes, metabolite properties; distinct from the existing overlap-style `compareMultipleModels` |
| Manipulation | `findDuplicateRxns`, `findPotentialErrors` | standalone duplicate-stoichiometry query; parse-tree-based non-DNF grRule detection (see [§8](#gpr-parsing)) |
| Genome-based curation (`curation/`, new folder) | `downloadGenomeData`, `getGeneData`, `processProteinFastaFile`, `renameModelGenes`, `curateModelFromTables` | pipeline from an NCBI genome accession to a gene ID mapping table to bulk gene renaming in a model; `curateModelFromTables` bulk-curates mets/rxns/genes from `.tsv` files against an existing model |
| Biomass composition (`biomass/`) | `getBiomassFractions`, `scaleBiomassFraction`, `scaleBiomassPseudoreaction`, `setGAM` | organism-agnostic biomass-composition and growth-associated-maintenance (GAM) calibration; `tutorial/tutorial7.m` demonstrates the workflow |
| Localization (`localization/`) | `assignCompartments`, `defaultCompartmentMap`, `getUniProtScores` | deterministic MILP compartment assignment (alternative to the heuristic `predictLocalization`); `parseScores` gains `'deeploc'`/`'cello'`/`'mulocdeep'`/`'compartments'`/`'uniprot'` predictors (replacing WoLF PSORT; see [§3](#backward-incompatible-changes)) |
| Annotation (`annotation/`) | `assignSBOterms`, `loadDeltaGCSV`/`saveDeltaGCSV` | organism-agnostic SBO term assignment; ΔG thermodynamic data CSV round-trip |
| Conditions (`conditions/`, new folder) | `applyCondition` | applies a data-driven growth/media condition (a YAML file, not code) to a model in a fixed sequence: exchange bounds, optional cofactor-pseudoreaction edits, optional biomass-stoichiometry deltas, per-reaction bound overrides |
| Internal infrastructure | `ravenModelFields` | central registry of every 1-D model field (entity type, default value), backing `permuteModel`/`removeReactions` internally |

---

(toolbox-deps)=
## 11. Toolbox dependencies and installation

| | RAVEN 2 | RAVEN 3 |
|---|---|---|
| MATLAB version | no pinned/documented minimum (guidance: avoid very new MATLAB syntax, to accommodate older installs) | CI is tested against **R2024b** |
| Statistics Toolbox | required (`combnk`) | not required (`nchoosek`, base MATLAB) |
| Bioinformatics Toolbox | required (`fastaread`/`fastawrite`) | not required (`io/readFasta.m`/`io/writeFasta.m`) |
| Optimization Toolbox | required for `qMOMA`/`solveQP` | not required (both removed) |
| Excel I/O | bundled Apache POI (Java) | dependency-free OOXML writer |
| LP/MILP solver | required (bundled `glpk`, or Gurobi/SCIP/COBRA) | unchanged, still required |
| External binaries (BLAST+, DIAMOND, HMMER, cd-hit, MAFFT) | committed to the repository, available offline immediately after clone | fetched on demand from the `raven-data` GitHub release on first use (per-platform ZIPs); an offline `*-full`/`*-binaries` release bundle is available for air-gapped installs |
| KEGG HMM libraries / reference data | manual download or local build required | fetched on demand from `raven-data`, cached locally after first use |
| Installation self-check | `installation/checkInstallation.m`; ran the full test suite to populate its pass/fail table | renamed `checkRaven`, moved to the repo root; does fast, targeted checks (a small import/export round-trip, a trivial LP per solver) instead of invoking the full test classes, and proactively offers to download missing binaries |

Net effect: a bare RAVEN 3 clone is far smaller and installs with fewer MATLAB
toolbox prerequisites, at the cost of needing network access the first time
KEGG- or homology-based reconstruction functions actually run.

---

## 12. Error and warning handling

RAVEN 2's `dispEM` always raised errors with an empty identifier, so no RAVEN 2
`try/catch` could have matched on `err.identifier`; RAVEN 3's move to native
`error()`/`warning()` with real (mostly `RAVEN:*`) identifiers is additive from
that angle, not breaking. Message text is preserved for most existing checks,
so text-matching `try/catch` blocks are unaffected either way. See
[§3](#backward-incompatible-changes) for the details and the new
`utils/ravenList.m` message-formatting helper.

One related, purely additive change: `queries/checkModelStruct.m`, called *with*
an output argument (`issues = checkModelStruct(model)`), now returns a
structured array of findings (`category`/`target`/`message`) instead of only
throwing or printing, useful for programmatic model QC. The no-output-argument
calling convention (throws/warns directly) is unchanged.
