<div class="rh-hero">
  <p class="rh-tag">MATLAB &amp; Python</p>
  <h1>Reconstruction, Analysis and Visualization<br>of Metabolic Networks</h1>
  <p class="rh-tagline">A toolkit for building, curating, and simulating genome-scale metabolic models — available as a MATLAB toolbox and a Python package built on cobrapy.</p>
  <div class="rh-badges">
    <span class="rh-badge">MIT license</span>
    <span class="rh-badge">Python ≥ 3.11</span>
    <span class="rh-badge">MATLAB R2016b+</span>
    <span class="rh-badge">cobrapy</span>
    <span class="rh-badge">SBML</span>
    <span class="rh-badge">Gurobi · GLPK</span>
    <span class="rh-badge">Windows · macOS · Linux</span>
    <span class="rh-badge">DOI 10.1371/journal.pcbi.1006541</span>
  </div>
</div>

<div class="rh-install">
  <div class="rh-install-tabs">
    <button class="rh-itab active" data-cmd="pip install raven-toolbox">Python (pip)</button>
    <button class="rh-itab" data-cmd="Home &rarr; Add-Ons &rarr; Get Add-Ons &rarr; search RAVEN Toolbox" data-plain>MATLAB (Add-Ons)</button>
    <button class="rh-itab" data-cmd="git clone https://github.com/SysBioChalmers/raven-toolbox.git&#10;pip install -e raven-toolbox/">Python (git)</button>
    <button class="rh-itab" data-cmd="git clone --depth=1 https://github.com/SysBioChalmers/RAVEN.git">MATLAB (git)</button>
  </div>
  <div class="rh-code-row">
    <code id="rh-cmd">pip install raven-toolbox</code>
    <button class="rh-copy" onclick="navigator.clipboard.writeText(document.getElementById('rh-cmd').innerText)" title="Copy to clipboard" aria-label="Copy">:octicons-copy-16:</button>
  </div>
</div>

<p class="rh-section-label">Key features</p>

<div class="grid cards rh-features" markdown>

-   :material-dna:{ .rh-feat-icon }

    **Homology reconstruction**

    Build draft models by transferring reactions from template models using BLAST+, DIAMOND, or HMMER.

-   :material-database:{ .rh-feat-icon }

    **KEGG-based reconstruction**

    Reconstruct metabolic networks directly from KEGG organism annotations and pathway databases.

-   :material-chart-line:{ .rh-feat-icon }

    **Flux analysis**

    FBA, FVA, gene knockouts, MOMA, and sampling with Gurobi or GLPK solvers.

-   :material-layers:{ .rh-feat-icon }

    **ftINIT**

    Fast task-and-data-driven INIT for extracting context-specific models from transcriptomics data.

-   :material-transit-connection:{ .rh-feat-icon }

    **Gap-filling**

    Identify and fill stoichiometric gaps by LP to restore connectivity or enable predicted growth.

-   :material-clipboard-check:{ .rh-feat-icon }

    **Model curation**

    Check mass and charge balance, dead-end metabolites, and metabolic task fulfilment.

</div>

<hr class="rh-divider">

<p class="rh-section-label">Quick start</p>

=== "Python"

    ```python
    import cobra

    # load yeast-GEM -- standard formats come from cobrapy;
    # RAVEN YAML models use raven_toolbox.io.read_yaml_model
    model = cobra.io.read_sbml_model("yeast-GEM.xml")

    # set growth as the objective
    model.objective = "r_2111"

    # constrain glucose uptake to 1 mmol/gDW/h
    model.reactions.get_by_id("r_1714").lower_bound = -1.0

    # run FBA
    sol = model.optimize()
    print(f"Growth rate: {sol.objective_value:.4f} h⁻¹")
    ```

=== "MATLAB"

    ```matlab
    % load yeast-GEM
    model = importModel('yeast-GEM.xml');

    % set growth as the objective
    model = setParam(model, 'obj', 'r_2111', 1);

    % constrain glucose uptake to 1 mmol/gDW/h
    model = setParam(model, 'ub', 'r_1714', 1);

    % run FBA
    sol = solveLP(model);
    fprintf('Growth rate: %.4f h-1\n', -sol.f);
    ```

<hr class="rh-divider">

<p class="rh-section-label">Documentation</p>

<div class="grid cards rh-docs" markdown>

-   :material-download:

    **[Installation](installation/index.md)**

    Set up RAVEN in MATLAB or raven-toolbox in Python with a solver.

-   :material-flask:

    **[Guides](protocol/index.md)**

    End-to-end GEM reconstruction protocol and legacy tutorials.

-   :material-api:

    **[API reference](api/index.md)**

    Complete function reference for both MATLAB and Python.

</div>

---

## Citing RAVEN

If you use RAVEN in your research, please cite:

> Wang H, Marcišauskas S, Sánchez BJ, Domenzain I, Hermansson D, Agren R,
> Nielsen J, Kerkhoven EJ (2018). **RAVEN 2.0: A versatile toolbox for
> metabolic network reconstruction and a case study on *Streptomyces
> coelicolor*.** *PLoS Computational Biology* 14(10): e1006541.
> <https://doi.org/10.1371/journal.pcbi.1006541>

> Agren R, Liu L, Shoaie S, Vongsangnak W, Nookaew I, Nielsen J (2013).
> **The RAVEN toolbox and its use for generating a genome-scale metabolic model
> for *Penicillium chrysogenum*.** *PLoS Computational Biology* 9(3): e1002980.
> <https://doi.org/10.1371/journal.pcbi.1002980>

If you use the GEM reconstruction protocol, also cite:

> Zorrilla F, Kerkhoven EJ (2022). **Reconstruction of Genome-Scale Metabolic
> Model for *Hansenula polymorpha* Using RAVEN.** In: Mapelli V, Bettiga M
> (eds), *Yeast Metabolic Engineering: Methods and Protocols*, Methods in
> Molecular Biology, vol. 2513. Humana, New York, NY, pp. 271–290.
> <https://doi.org/10.1007/978-1-0716-2399-2_16>

See [References](references.md) for the full list including methods cited in the protocol.

<script>
(function () {
  var tabs = document.querySelectorAll('.rh-itab');
  var cmd  = document.getElementById('rh-cmd');
  tabs.forEach(function (btn) {
    btn.addEventListener('click', function () {
      tabs.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      cmd.innerHTML = btn.dataset.cmd;
    });
  });
})();
</script>
