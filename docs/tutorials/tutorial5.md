# Tutorial 5 — Reconstruct a GEM from KEGG

This exercise creates a draft model *de novo* from protein sequences in a FASTA
file, using **KEGG** as the reaction database, and runs some functionality
checks on the result. The example organism is *Saccharomyces cerevisiae*.

Unlike Tutorials 1–4, this is a **showcase**: its main purpose is to serve as a
scaffold you can adapt to reconstruct a GEM for any organism.

## What the script does

1. **Download trained HMMs.** KEGG Orthology groups are matched with profile
   Hidden Markov Models. The archive `euk90_kegg105` (for eukaryotes) is fetched
   automatically; see the RAVEN Wiki for how these archives are prepared.
2. **Reconstruct from KEGG** with `getKEGGModelForOrganism`, supplying the
   organism's whole-proteome FASTA (`sce.fa`). This searches the sequences
   against the HMMs and assembles a draft model from the matching KEGG reactions.
3. **Inspect and check** the draft model — number of reactions, metabolites and
   genes, and basic connectivity/quality checks.

The key reconstruction call looks like:

```matlab
model = getKEGGModelForOrganism('sce', 'sce.fa', 'euk90_kegg105', 'output', ...
    false, false, false, false, 10^-30, 0.8, 0.3, -1);
```

!!! note "Runtime"
    *De novo* reconstruction performs sequence searches against large HMM
    databases and can take a long time on a full proteome. The downloaded
    archives are also large.

## Full script

```matlab
--8<-- "RAVEN/tutorial/tutorial5.m"
```

For the complete, narrated description see *Tutorial 5* in the
[`RAVEN tutorials.docx`](https://github.com/SysBioChalmers/RAVEN/blob/main/tutorial/RAVEN%20tutorials.docx)
that ships in the `tutorial/` folder.
