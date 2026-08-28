<!-- run-examples: skip-file -->

# 19. Reconstruction from KEGG

[18. Reconstruction from homology](homology.md) needs a template model of a
related organism. KEGG needs none: its orthology groups (KOs) are already tied to
reactions, so annotating a genome with KOs gives you a draft directly. Which
route you take depends on one thing — whether your organism is already in KEGG.

!!! note "These examples are not run by the documentation build"
    Every other page in this guide is executed on each commit and its output
    checked. This one is not. A KEGG reconstruction downloads tens to hundreds of
    megabytes and takes minutes even once that is cached, which is too much for a
    per-commit check. The numbers below come from real runs and are quoted with
    their timings, measured on an ordinary laptop.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `getKEGGModelForOrganism` | `get_kegg_model_for_organism_from_artefacts` | draft from an organism's KEGG annotation |
| `getKEGGModelForOrganism` (with `fastaFile`) | `get_kegg_model_from_sequences` | draft from an HMM search of your proteins |
| `getModelFromKEGG` | `build_reference_model` | the global KEGG reaction model |
| `getPhylDist` | `PhylDist` | phylogenetic distance, used to weight the search |

## 19.1 When the organism is already in KEGG

If KEGG has your species — `sce` for *S. cerevisiae* — its gene-to-KO assignments
are already made, and no sequence search is needed. This is the fast route, and
the one to prefer when it applies.

=== "MATLAB"

    ```matlab
    model = getKEGGModelForOrganism('sce', ...
        'dataDir', fullfile(tempdir, 'kegg118_eukaryotes'));
    ```

    ```text title="Output"
    *** The model reconstruction from KEGG based on the annotation available for KEGG Species sce ***
    Downloading the HMM library file... COMPLETE
    Extracting the HMM library file... COMPLETE
    Error: keggModel.mat not found at <ravenRoot>/reconstruction/kegg/keggModel.mat.
    Generate it with the raven-toolbox Python package or download it via downloadRavenBinaries.
    ```

    **This does not currently work**, which is why the output above is an error
    rather than a model. `keggModel.mat` is not in the repository, and neither
    remedy the message names provides it: `downloadRavenBinaries` fetches only
    the BLAST+, DIAMOND and HMMER executables, and raven-toolbox has no reference
    to `keggModel` anywhere. Filed as
    [RAVEN#704](https://github.com/SysBioChalmers/RAVEN/issues/704). Note also
    that the 129 MB HMM library downloads first, although this route performs no
    homology search at all.

=== "Python"

    ```python
    from raven_toolbox.reconstruction.kegg import (
        get_kegg_model_for_organism_from_artefacts,
    )

    model = get_kegg_model_for_organism_from_artefacts("sce")
    print(f"{len(model.reactions)} rxns, {len(model.metabolites)} mets, "
          f"{len(model.genes)} genes")
    ```

    ```text title="Output"
    1357 rxns, 1502 mets, 838 genes
    ```

    The artefacts — a reference model and three tables, about 47 MB — are fetched
    from the `kegg118` raven-data release on first use and cached. Expect around
    five minutes for the first run and much the same afterwards: the download is
    not the slow part, assembling the draft from the tables is.

## 19.2 When it is not

For an organism KEGG has never seen, the KO assignments have to be made from
sequence. Both toolboxes search your proteins against a library of profile HMMs,
one per KO, trained on either prokaryotic or eukaryotic sequences.

=== "MATLAB"

    ```matlab
    model = getKEGGModelForOrganism('hpo', ...
        'fastaFile', 'hanpo.faa', ...
        'dataDir', fullfile(tempdir, 'kegg118_eukaryotes'), ...
        'outDir', fullfile(tempdir, 'hanpo_hmm'));
    ```

=== "Python"

    ```python
    from raven_toolbox.reconstruction.kegg import get_kegg_model_from_sequences

    model = get_kegg_model_from_sequences("hanpo.faa", domain="eukaryotes")
    ```

This is the expensive route. The eukaryotic HMM library alone is **129 MB
compressed**, and `hmmsearch` against every KO takes tens of minutes to hours for
a full proteome — which is why `outDir` exists in the MATLAB version: results are
kept per-KO so an interrupted run can resume rather than start again.

The organism id still matters even here. It sets the phylogenetic distance used
to weight the KO assignments, so pick the closest relative KEGG does have.

## 19.3 What a KEGG draft is

Genome-scale in size and quite unlike a working model in every other respect.

```text title="the sce draft, measured"
reactions:     1357
metabolites:   1502
genes:          838
compartments:  1 — everything is in 's'
exchange rxns:   0
objective:       none
```

**There are no compartments.** KEGG describes reactions, not cell biology, so
every metabolite lands in one undifferentiated space. A KEGG draft cannot
distinguish mitochondrial from cytosolic anything until you localise it —
see [16. Combining and simplifying](combining.md) for the reverse operation, and
what is lost by it.

The flags decide how inclusive the draft is. `keepIncomplete` /
`keep_incomplete` keeps reactions whose KO assignment is only partial;
`keepUndefinedStoich` / `keep_undefined_stoich` keeps reactions with `n` or `x`
in their stoichiometry, which cannot be balanced as written. Turning both off:

```text title="keep_incomplete=False, keep_undefined_stoich=False"
1348 rxns, 827 genes   (from 1357 and 838)
```

A change of nine reactions — smaller than it sounds, and worth checking on your
own organism rather than assuming. `keepGeneral` / `keep_general` is off by
default for a better reason: general reactions are placeholders like "an alcohol
+ NAD+", and admitting them produces a network that appears to do far more than
it can.

!!! warning "What can go wrong"
    - **Expecting a model.** No biomass reaction, no exchanges, no compartments,
      no medium. What you have is a reaction inventory with gene associations.
    - **Trusting the KO assignment.** A KO is an orthology group, not a
      demonstrated activity in your organism, and a partial HMM hit is weaker
      still.
    - **Undefined stoichiometry.** Reactions with `n` or `x` coefficients cannot
      be mass-balanced. They are kept by default because dropping them loses real
      chemistry, but they will trip up
      [9. Quality control](quality-control.md) later.
    - **Version drift.** The artefacts are built from a specific KEGG release —
      `kegg118` here. Rebuilding a year later with a different release gives a
      different model, so record which one you used.

## See also

- [18. Reconstruction from homology](homology.md) — the same goal from a template
  model instead of an orthology database.
- [13. Gap-filling](gap-filling.md) — what to do with 1357 reactions that cannot
  yet carry flux.
- [Legacy tutorial 5](../tutorials/tutorial5.md) — the original KEGG
  reconstruction exercise from the RAVEN paper.
