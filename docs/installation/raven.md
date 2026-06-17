# RAVEN (MATLAB)

The RAVEN Toolbox runs in MATLAB and works completely independently (it does not
require the COBRA Toolbox, although it can interoperate with it). This page
covers installing, verifying, upgrading and removing it. The canonical reference
is the [RAVEN installation wiki](https://github.com/SysBioChalmers/RAVEN/wiki/Installation).

## Requirements

- **MATLAB** R2016b or later. No additional MathWorks toolboxes are required.
- A **linear-programming solver** — [Gurobi](https://www.gurobi.com/) (free
  academic license, recommended) or the **GLPK** solver bundled with the
  [COBRA Toolbox](https://github.com/opencobra/cobratoolbox). See
  [Choosing a solver](index.md#choosing-a-solver).
- RAVEN **bundles** the `libSBML` MATLAB API (for SBML import/export) and the
  `BLAST+`, `DIAMOND` and `HMMER` binaries (for sequence-based reconstruction)
  for Windows, macOS and Linux — no separate installation needed.

## Install

There are three ways to install RAVEN. The first is the easiest; the third is
best if you want the very latest development version.

### Option 1 — MATLAB Add-Ons manager (easiest)

1. In MATLAB, open the **Home** tab and click **Add-Ons → Get Add-Ons**.
2. Search the Add-On Explorer for **RAVEN Toolbox** and click **Add → Add to
   MATLAB**.
3. When it finishes, [verify the installation](#verify-the-installation).

### Option 2 — Download a release

1. Download the latest release ZIP from the
   [RAVEN releases page](https://github.com/SysBioChalmers/RAVEN/releases).
2. Extract it to a location of your choice.
3. In MATLAB, add the RAVEN folder to the path (run `checkInstallation` from the
   RAVEN root, or use `pathtool`), then
   [verify the installation](#verify-the-installation).

### Option 3 — Clone with git (latest)

With [git](https://git-scm.com/) installed, from your target directory run:

```bash
git clone --depth=1 https://github.com/SysBioChalmers/RAVEN.git
```

Then add the folder to the MATLAB path and
[verify the installation](#verify-the-installation). Using `git` makes
[upgrading](#upgrading) a one-line command.

## Verify the installation

From the MATLAB command window, run:

```matlab
checkInstallation
```

This adds RAVEN to the path, tests general functioning, reports whether SBML and
Excel models can be parsed and which solver is active, sets a default solver
(Gurobi if available, otherwise GLPK), and checks the bundled binaries. Its
output is the first thing to check when troubleshooting.

!!! warning "Excel parsing conflict"
    MATLAB's **Text Analytics Toolbox** (R2017b and later) can conflict with
    RAVEN's Excel parser. If `checkInstallation` reports *"Checking if it is
    possible to parse a model in Microsoft Excel format... FAILED"*, uninstall
    the Text Analytics Toolbox. See
    [RAVEN issue #55](https://github.com/SysBioChalmers/RAVEN/issues/55).

## Upgrading

The way you upgrade depends on how you installed RAVEN:

- **Add-Ons manager (Option 1):** in MATLAB, go to **Help → Check for Updates**,
  click **Update** for RAVEN, then run `checkInstallation` again.
- **Release download (Option 2):** close MATLAB, delete the old RAVEN folder,
  optionally clean the path with `pathtool`, then download and extract the new
  release and run `checkInstallation`.
- **git clone (Option 3):** pull the latest `main` branch and run
  `checkInstallation`:

    ```bash
    git pull origin main
    ```

## Removing RAVEN

- **Add-Ons manager:** remove RAVEN through the **Add-Ons → Manage Add-Ons**
  list.
- **Release download or git clone:** in MATLAB, locate and clear the path
  entries, then delete the folder:

    ```matlab
    which removeRavenFromPath   % locate the installation
    removeRavenFromPath         % clear RAVEN from the MATLAB path
    ```

    Then delete the RAVEN folder from disk.

## Getting help

For installation problems, consult the
[RAVEN wiki](https://github.com/SysBioChalmers/RAVEN/wiki/Installation) or open
an issue on the [RAVEN GitHub repository](https://github.com/SysBioChalmers/RAVEN/issues).
