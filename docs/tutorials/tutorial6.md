# Tutorial 6 — Reconstruct a GEM from MetaCyc + KEGG

This exercise demonstrates how to reconstruct a **combined** draft GEM from both
the **KEGG** and **MetaCyc** pathway databases, giving more comprehensive
pathway coverage than either approach alone. The combined draft is then used to
refine an existing high-quality model and generate a new version of it.

The input is a FASTA file with whole-proteome sequences. The example showcases
features released in RAVEN 2.0, applied to *Streptomyces coelicolor* A3(2). Like
Tutorial 5, it is a **showcase** you can use as a template for your own organism.

## What the script does

1. **Draft from KEGG** — `getKEGGModelForOrganism` builds a KEGG-based draft
   from the proteome FASTA.
2. **Draft from MetaCyc** — `getMetaCycModelForOrganism` builds a MetaCyc-based
   draft from the same sequences.
3. **Combine** the two drafts into a single model with broader pathway coverage
   (`combineMetaCycKEGGModels` / `mergeModels`).
4. **Refine an existing GEM** — the combined draft is used to extend and curate
   a published high-quality model, producing a new version.

!!! note
    *De novo* reconstruction from two databases is computationally heavy and
    involves matching metabolites across namespaces, which is the main challenge
    when merging models from different sources. The
    [GEM reconstruction protocol](../protocol/index.md) discusses this trade-off
    in the context of homology-based reconstruction.

## Full script

```matlab
--8<-- "RAVEN/tutorial/tutorial6.m"
```

For the complete, narrated description see *Tutorial 6* in the
[`RAVEN tutorials.docx`](https://github.com/SysBioChalmers/RAVEN/blob/main/tutorial/RAVEN%20tutorials.docx)
that ships in the `tutorial/` folder.
