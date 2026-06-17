# RAVEN

**RAVEN** (*Reconstruction, Analysis and Visualization of Metabolic Networks*)
is a toolbox for the semi-automated reconstruction, curation, simulation and
analysis of genome-scale metabolic models (GEMs). It supports *de novo*
reconstruction from the KEGG and MetaCyc databases, homology-based
reconstruction from template models, gap-filling, simulation through flux
balance analysis, omics-data integration and network visualization.

RAVEN comes in two implementations that expose the **same** functionality:

<div class="grid cards" markdown>

-   :custom-matlab: **RAVEN (MATLAB)**

    The original toolbox, built on the COBRA Toolbox and `libSBML`.
    Functions use `camelCase` names (e.g. `getModelFromHomology`).

    [:octicons-arrow-right-24: Source on GitHub](https://github.com/SysBioChalmers/RAVEN)

-   :material-language-python: **raven-toolbox**

    The Python port, built on [cobrapy](https://opencobra.github.io/cobrapy/).
    Functions use `snake_case` names (e.g. `get_model_from_homology`).

    [:octicons-arrow-right-24: Source on GitHub](https://github.com/SysBioChalmers/raven-toolbox)

</div>

This site documents both side by side. The API reference extracts the function
help directly from each project's source on its `main` branch, so what you read
here always matches the code.

## Where to start

<div class="grid cards" markdown>

-   :material-download: **[Installation](installation.md)**

    Install RAVEN (MATLAB) and raven-toolbox, with solver setup.

-   :material-school: **[Tutorials](tutorials/index.md)**

    Six hands-on exercises: from running FBA on an existing GEM to
    reconstructing a model from KEGG and MetaCyc.

-   :material-flask: **[GEM reconstruction protocol](protocol/index.md)**

    A complete, worked homology-based reconstruction of a genome-scale model
    for the yeast *Hansenula polymorpha* (`hanpo-GEM`).

-   :material-api: **[API reference](api/index.md)**

    Every documented function, MATLAB and Python, organised by category.

</div>

## Citing RAVEN

If you use RAVEN in your research, please cite:

> Wang H, Marcišauskas S, Sánchez BJ, Domenzain I, Hermansson D, Agren R,
> Nielsen J, Kerkhoven EJ (2018). **RAVEN 2.0: A versatile toolbox for
> metabolic network reconstruction and a case study on *Streptomyces
> coelicolor*.** *PLoS Computational Biology* 14(10): e1006541.
> <https://doi.org/10.1371/journal.pcbi.1006541>

See [References](references.md) for the full citation list, including the
*Hansenula polymorpha* reconstruction protocol.
