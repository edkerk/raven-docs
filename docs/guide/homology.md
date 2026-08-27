# 18. Reconstruction from homology

The oldest way to get a model for a new organism: take a model of a related one,
find out which of its genes have counterparts in your genome, and carry over the
reactions those genes are responsible for. Everything rests on the middle step —
what counts as a counterpart — so this page is mostly about the cut-offs.

### Functions on this page

| MATLAB | Python | |
|---|---|---|
| `getBlast` | `run_blast` | bidirectional BLASTP between two proteomes |
| `getDiamond` | `run_diamond` | the same, with DIAMOND — faster, less sensitive |
| `getModelFromHomology` | `get_model_from_homology` | carry reactions across on the hits |
| `makeFakeBlastStructure` | `make_ortholog_hits` | feed in orthologs you already have |

## Setup

Two proteomes and a template model. The template is `smallYeast.yml` — 53
reactions, 61 genes — and `sce-template.faa` holds the sequences of exactly those
61 *S. cerevisiae* genes. The organism being reconstructed is *Hansenula
polymorpha*, whose full 5177-protein proteome is in `hanpo.faa`.

The template model's id has to match the id used for the BLAST, because that is
how the hits are matched back to a model.

=== "MATLAB"

    ```matlab
    template = readYAMLmodel('smallYeast.yml');
    template.id = 'sce';
    fprintf('template: %d rxns, %d genes\n', numel(template.rxns), numel(template.genes));
    ```

    ```text title="Output"
    template: 53 rxns, 61 genes
    ```

=== "Python"

    ```python
    import cobra
    from raven_toolbox.io import read_yaml_model

    cobra.Configuration().processes = 1

    template = read_yaml_model("smallYeast.yml")
    template.id = "sce"
    print(f"template: {len(template.reactions)} rxns, {len(template.genes)} genes")
    ```

    ```text title="Output"
    template: 53 rxns, 61 genes
    ```

## 18.1 BLAST, in both directions

Both toolboxes run BLASTP twice — the new organism against the template, and the
template against the new organism. That second direction is what lets the next
step ask for *reciprocal* hits rather than merely good ones.

=== "MATLAB"

    ```matlab
    blastStructure = getBlast('hanpo', 'hanpo.faa', {'sce'}, {'sce-template.faa'});
    for i = 1:numel(blastStructure)
        fprintf('%s -> %s: %d hits\n', blastStructure(i).fromId, ...
            blastStructure(i).toId, numel(blastStructure(i).fromGenes));
    end
    ```

    ```text title="Output"
    BLASTing "sce" against "hanpo"..
    BLASTing "hanpo" against "sce"..
    sce -> hanpo: 159 hits
    hanpo -> sce: 178 hits
    ```

=== "Python"

    ```python
    from raven_toolbox.reconstruction.homology import run_blast

    hits = run_blast("hanpo", "hanpo.faa", ["sce"], ["sce-template.faa"])
    print(f"{len(hits)} hits total")
    print(hits.groupby(["from_id", "to_id"]).size().to_string())
    ```

    ```text title="Output"
    337 hits total
    from_id  to_id
    hanpo    sce      178
    sce      hanpo    159
    ```

Both are calling the same BLAST+ executables with the same parameters, so the
hit counts agree. RAVEN ships those binaries; raven-toolbox downloads them on
first use and caches them, or uses the ones on your `PATH` if you point
`RAVEN_PYTHON_BLASTP` at them.

`getDiamond` and `run_diamond` are drop-in alternatives. On a pair of full
proteomes DIAMOND is the difference between minutes and hours, at some cost in
sensitivity for distant homologs.

## 18.2 From hits to a draft

=== "MATLAB"

    ```matlab
    draft = getModelFromHomology({template}, blastStructure, 'hanpo');
    fprintf('draft: %d rxns, %d mets, %d genes\n', ...
        numel(draft.rxns), numel(draft.mets), numel(draft.genes));
    ```

    ```text title="Output"
    Standardizing grRules of template model with ID "sce" ... done
    draft: 37 rxns, 49 mets, 54 genes
    ```

=== "Python"

    ```python
    from raven_toolbox.reconstruction.homology import get_model_from_homology

    result = get_model_from_homology([template], hits, "hanpo")
    draft = result.model
    print(f"draft: {len(draft.reactions)} rxns, {len(draft.metabolites)} mets, "
          f"{len(draft.genes)} genes")
    ```

    ```text title="Output"
    draft: 37 rxns, 49 mets, 54 genes
    ```

`get_model_from_homology` returns a `HomologyResult` rather than a model:
`.model` is the draft, `.gene_map` records which template gene each new gene came
from, and `.candidates` — with `review_identity=` — collects the reactions that
just missed the identity threshold, so a curator can accept or reject them
deliberately instead of never seeing them. RAVEN returns the draft and its hit
genes as two outputs.

The draft is smaller than the template: reactions whose genes have no acceptable
counterpart are not carried over. That is the whole point, and also the whole
risk — a missing hit is indistinguishable from a gene the organism does not have.

## 18.3 The cut-offs decide the model

Defaults are a judgement, not a fact. Two matter most: `maxE` (`1e-30`) and
`minLen` (`100`, an alignment length). Tightening either shrinks the draft.

=== "MATLAB"

    ```matlab
    strict = getModelFromHomology({template}, blastStructure, 'hanpo', ...
        'maxE', 1e-100, 'minLen', 250);
    fprintf('strict draft: %d rxns, %d genes\n', numel(strict.rxns), numel(strict.genes));
    ```

    ```text title="Output"
    Standardizing grRules of template model with ID "sce" ... done
    strict draft: 32 rxns, 46 genes
    ```

=== "Python"

    ```python
    strict = get_model_from_homology([template], hits, "hanpo",
                                     max_evalue=1e-100, min_align_len=250).model
    print(f"strict draft: {len(strict.reactions)} rxns, {len(strict.genes)} genes")
    ```

    ```text title="Output"
    strict draft: 32 rxns, 46 genes
    ```

!!! warning "`minLen` changed recently"
    Its default was **200** and is now **100**. The value was measured against
    KEGG and OMA orthology across four organisms: anything at or below 150
    performed the same, while 200 was discarding real orthologs. If you are
    reproducing an older reconstruction, set it explicitly — otherwise the same
    script gives you a different model than it did before.

## 18.4 A draft is not a model

What comes out of this step has reactions and genes, and nothing else. There is
no biomass reaction unless a template reaction happened to carry one, no
exchange reactions, and no guarantee that anything can carry flux.

=== "MATLAB"

    ```matlab
    exchangeRxns = getExchangeRxns(draft);
    fprintf('objective set: %d\n', any(draft.c ~= 0));
    fprintf('exchange reactions: %d\n', numel(exchangeRxns));
    fprintf('reactions that can carry flux: %d of %d\n', ...
        sum(haveFlux(draft)), numel(draft.rxns));
    ```

    ```text title="Output"
    objective set: 0
    exchange reactions: 0
    reactions that can carry flux: 0 of 37
    ```

=== "Python"

    ```python
    from cobra.flux_analysis import find_blocked_reactions

    blocked = find_blocked_reactions(draft)
    print(f"objective set: {str(draft.objective.expression) != '0'}")
    print(f"exchange reactions: {len(draft.boundary)}")
    print(f"reactions that can carry flux: {len(draft.reactions) - len(blocked)} "
          f"of {len(draft.reactions)}")
    ```

    ```text title="Output"
    objective set: False
    exchange reactions: 0
    reactions that can carry flux: 0 of 37
    ```

Not one of the 37 reactions can carry flux, and there is no objective and no way
in or out. That is the normal, expected state of a homology draft: it is a set of
claims about which reactions the organism probably has, and nothing more.

From here the work is the rest of this guide: give it a medium
([5. Growth media and conditions](media.md)), close the holes
([13. Gap-filling](gap-filling.md)), check it against what the organism is known
to do ([12. Metabolic tasks](tasks.md)). The
[GEM reconstruction protocol](../protocol/index.md) follows exactly that path for
*H. polymorpha*, at full scale.

!!! warning "What can go wrong"
    - **Identifiers that do not match.** The FASTA headers must carry the same
      gene ids as the template model's `genes`. A mismatch produces a draft with
      no reactions and no error worth the name.
    - **One template, one organism's biases.** Every reaction in the draft comes
      from the template, so anything the template lacks the draft cannot have.
      Several templates, with `preferredOrder`, spread that risk.
    - **Reading absence as evidence.** A reaction left out means no acceptable
      hit was found — not that the organism lacks the capability. Sequencing
      gaps, divergent sequences and short proteins all look the same here.
    - **Full proteomes are slow.** The example on this page finishes in seconds
      because the template proteome is 61 sequences. Two complete proteomes take
      minutes to hours with BLASTP; that is what `getDiamond` and `run_diamond`
      are for.

## See also

- [13. Gap-filling](gap-filling.md) — the usual next step, and the one that
  decides what the draft is missing.
- [10. Context-specific models](init.md) — cutting a model down by evidence
  instead of building one up from homology.
- [17. Comparing models](comparing.md) — checking a draft against a curated
  model of the same organism.
