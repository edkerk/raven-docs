# RAVEN (MATLAB)

The RAVEN Toolbox runs in MATLAB and works completely independently; it does
not require the COBRA Toolbox, although it can interoperate with it. The
canonical reference is the
[RAVEN installation wiki](https://github.com/SysBioChalmers/RAVEN/wiki/Installation).

## Requirements

- **MATLAB** R2016b or later, which is the oldest release the code still guards
  for. Continuous integration tests R2024b only, so a recent release is the
  better-covered choice. No additional MathWorks toolboxes required.
- A **linear-programming solver**: [Gurobi](https://www.gurobi.com/) (free
  academic license, recommended) or **GLPK** (bundled with the
  [COBRA Toolbox](https://github.com/opencobra/cobratoolbox)).
  See [Choosing a solver](index.md#choosing-a-solver).
- RAVEN **bundles** `libSBML` and the GLPK mex files for Windows, macOS and
  Linux. `BLAST+`, `DIAMOND` and `HMMER` are **not** bundled: RAVEN fetches the
  build for your platform on first use, so the reconstruction functions need
  internet access the first time they run. `downloadRavenBinaries` fetches them
  ahead of time. See
  [Downloaded data and binaries](data-and-binaries.md) for the full set, where
  it is cached, and how to prepare an offline machine.

---

## Install

=== ":material-puzzle: Add-Ons manager"

    Installs from within MATLAB, with no separate download.

    1. Open the **Home** tab and click **Add-Ons → Get Add-Ons**.
    2. Search for **RAVEN Toolbox** and click **Add → Add to MATLAB**.
    3. [Verify the installation](#verify).

=== ":material-file-download: Release download"

    Good for offline or managed environments.

    1. Download the latest ZIP from the
       [RAVEN releases page](https://github.com/SysBioChalmers/RAVEN/releases).
    2. Extract it to a location of your choice.
    3. In MATLAB, add the RAVEN folder to the path (`pathtool`), then
       [verify](#verify).

=== ":octicons-git-branch-16: Clone with git"

    Tracks the development branch, and upgrades with a single command.

    ```bash
    git clone --depth=1 https://github.com/SysBioChalmers/RAVEN.git
    ```

    Add the folder to the MATLAB path and [verify](#verify).

---

## Verify { #verify }

From the MATLAB command window:

```matlab
checkInstallation
```

A successful run looks like:

```text
*** THE RAVEN TOOLBOX ***

Checking if RAVEN is on the MATLAB path...                                  OK
Checking if it is possible to parse a model in Microsoft Excel format...    OK
Checking if it is possible to import an SBML model using libSBML...         OK
Solver found in preferences... gurobi
Checking if it is possible to solve an LP problem using gurobi...           OK
Checking essential binary executables:
    BLAST+... OK
    DIAMOND... OK
    HMMER... OK
*** checkInstallation complete ***
```

---

## Upgrade

=== ":material-puzzle: Add-Ons manager"

    In MATLAB go to **Help → Check for Updates**, click **Update** for RAVEN,
    then run `checkInstallation` again.

=== ":material-file-download: Release download"

    Close MATLAB, delete the old RAVEN folder, download and extract the new
    release, and run `checkInstallation`.

=== ":octicons-git-branch-16: Clone with git"

    ```bash
    git pull origin main
    ```

    Then run `checkInstallation`.

---

## Remove

=== ":material-puzzle: Add-Ons manager"

    Go to **Add-Ons → Manage Add-Ons** and remove RAVEN from the list.

=== ":material-file-download: Release download"

    ```matlab
    which removeRavenFromPath   % locate the installation
    removeRavenFromPath         % clear RAVEN from the MATLAB path
    ```

    Then delete the RAVEN folder from disk.

=== ":octicons-git-branch-16: Clone with git"

    ```matlab
    which removeRavenFromPath   % locate the installation
    removeRavenFromPath         % clear RAVEN from the MATLAB path
    ```

    Then delete the cloned RAVEN folder from disk.

---

## Getting help

For installation problems, consult the
[RAVEN wiki](https://github.com/SysBioChalmers/RAVEN/wiki/Installation) or
open an issue on [GitHub](https://github.com/SysBioChalmers/RAVEN/issues).
