# RAVEN documentation — design & content guide

> **This is a living document, and it is the source of intent.** It describes how
> the RAVEN documentation site *should* be designed and what it *should*
> contain — it is a set of instructions, not a description of whatever happens to
> be on `main` at the moment. When the site and this document disagree, treat
> this document as the target and bring the site in line (not the other way
> round). Keep it updated as decisions are made; record new decisions in the
> decisions log and move resolved items out of "open questions".

> **⚠️ Before doing any work in this repo, pull all remotes first** — the
> superproject *and* every submodule. The submodules are updated frequently
> (including automatically), so local state goes stale quickly; never build on a
> stale checkout:
>
> ```bash
> git fetch --all --prune
> git checkout main && git pull --ff-only
> git submodule sync --recursive
> git submodule update --init --recursive
> ```

## 1. Purpose

A single, dual-language documentation site for **RAVEN** that serves both the
**MATLAB** toolbox and the **Python** package (**raven-toolbox**) from one place,
so a user can learn a concept once and apply it in either language. The site is
built with [MkDocs](https://www.mkdocs.org/) +
[Material](https://squidfunk.github.io/mkdocs-material/) and published on Read
the Docs.

## 2. Guiding principles

- **Dual-language parity.** MATLAB and Python are presented side by side
  throughout: paired API entries, and code blocks with MATLAB/Python tabs.
- **Single source of truth.** API documentation is extracted directly from the
  function help in each toolbox's source (via `mkdocstrings`), so it never
  drifts from the code. The source repos are tracked as **git submodules**.
- **Source of truth follows the active branch.** The RAVEN submodule tracks
  **`develop3`** and raven-toolbox tracks **`develop`**. develop3's modular
  folder layout (`reconstruction`, `manipulation`, `analysis`, …) mirrors
  raven-toolbox's package structure, so the two line up by category.
- **Don't reinvent cobrapy.** Where the Python version intentionally relies on
  [cobrapy](https://cobrapy.readthedocs.io/) instead of providing its own
  function, the site links to the cobrapy equivalent rather than duplicating it.
- **Low maintenance.** Pages that can be generated (the API reference) are
  generated at build time; prose pages are hand-written and kept short.
- **Living, curated content.** Protocols and tutorials are a growing, curated
  set — quality over quantity.

## 3. Technical foundation

- MkDocs + Material theme; Read the Docs build (`.readthedocs.yaml`).
- `mkdocstrings` with two handlers, both collecting statically from submodule
  source (no MATLAB runtime, no installed package required):
  - Python handler (griffe) over the raven-toolbox source, NumPy docstring style.
  - MATLAB handler (`mkdocstrings-matlab`, tree-sitter) over the RAVEN modular
    directories, NumPy docstring style.
- Function help in both toolboxes uses **NumPy-style docstrings** so it renders
  as structured argument/return tables.
- The API reference is **generated at build time** (`mkdocs-gen-files` +
  `mkdocs-literate-nav`): a cobrapy-style autoapi, one page per category, with
  MATLAB and Python paired by name.
- Submodules: `RAVEN` (branch `develop3`), **raven-toolbox** (branch
  `develop`), `hanpo-GEM` (branch `main`).

## 4. Site structure

### 4.1 Home (first page)

- **(a)** A very brief introduction to RAVEN: what it is (reconstruction,
  analysis and visualization of genome-scale metabolic models) and what it is
  for.
- **(b)** Make clear that **both a MATLAB and a Python version exist**, and that
  this site documents both.
- **(c)** Links to the key articles:
  - RAVEN 2.0 — Wang et al. (2018), *PLoS Comput Biol* 14(10):e1006541.
  - RAVEN (1.0) — Agren et al. (2013), *PLoS Comput Biol* 9(3):e1002980.
  - (Add the raven-toolbox reference once published.)

### 4.2 Installation

Separate instructions for each version:

- **MATLAB.** Summarize requirements (MATLAB, libSBML, a solver) and link to the
  canonical instructions on the wiki:
  <https://github.com/SysBioChalmers/RAVEN/wiki/Installation#installation>.
- **Python (raven-toolbox).** `pip install raven-toolbox`, plus Python version,
  solver (GLPK/Gurobi) and the cobrapy dependency.

### 4.3 MATLAB vs Python versions

Explain the relationship between the two implementations:

- They have **large overlap**, but there are differences.
- The **MATLAB** version works **completely independently** — including
  independently of the COBRA Toolbox — although `ravenCobraWrapper` can translate
  between the RAVEN and COBRA model formats.
- The **Python** version (raven-toolbox) is built **on top of cobrapy**.
- As a result there are **MATLAB-only functions**, many of which are not ported
  because cobrapy already covers that functionality.

Then a **mapping table**: MATLAB function name (left) ↔ Python function name
(right). Conventions:

- Each function name links to its entry in the [API reference](#46-api-reference).
- Where no raven-toolbox function exists because cobrapy provides the
  equivalent, link to the **cobrapy** function instead and mark it with a small
  **cobrapy** indicator (icon/badge) to show it is an external cobrapy function.
  cobrapy API index: <https://cobrapy.readthedocs.io/en/latest/autoapi/cobra/index.html>.
- **Maintenance:** the RAVEN ↔ raven-toolbox pairs are **auto-generated** from
  the API data (by normalised name); the **cobrapy-alternative rows are
  hand-curated** (a maintained list of MATLAB-only functions → cobrapy links).

| MATLAB (RAVEN) | Python (raven-toolbox) |
|---|---|
| `importModel` | `import_model` |
| `solveLP` | `solve_lp` |
| … | … (cobrapy) :material-link-variant: |

### 4.4 Protocols

A curated, growing collection of worked protocols. Each is available in **both
MATLAB and Python**, and **every code block has two tabs** (MATLAB / Python) so
the reader can switch language quickly.

- **Default tab: MATLAB.** Tabs are **persistent/linked** (Material linked
  content tabs), so selecting a language applies across the whole page and is
  remembered site-wide — effectively the "open all MATLAB / all Python" switch.

Protocols to include:

- **GEM reconstruction** — homology-based reconstruction of a model for
  *Hansenula polymorpha* (`hanpo-GEM`).
- **GEM extraction** — from
  <https://sysbiochalmers.github.io/Human-GEM-guide/gem_extraction/>.
- **GEM comparison** — from
  <https://sysbiochalmers.github.io/Human-GEM-guide/gem_comparison/>.

### 4.5 Legacy tutorials

Include **tutorials 1–5** only. State that these were part of the **RAVEN 1
paper** (Agren et al., 2013); the code has been updated to run with current
RAVEN, but **no further changes** have been made to the exercises.

> Tutorial 6 (de novo reconstruction of *Streptomyces coelicolor* from
> MetaCyc + KEGG) is **not** included — it is a RAVEN 2.0 showcase, not a RAVEN 1
> legacy tutorial.

### 4.6 API reference

Generated from source, organised so each function is shown for both languages.

- **Python (raven-toolbox)** — should look and feel like cobrapy's autoapi, e.g.
  <https://cobrapy.readthedocs.io/en/latest/autoapi/cobra/index.html> and a
  function page like
  <https://cobrapy.readthedocs.io/en/latest/autoapi/cobra/flux_analysis/parsimonious/index.html#cobra.flux_analysis.parsimonious.pfba>.
- **MATLAB** — functions organised **by subfolder** (the `develop3` modular
  categories: `reconstruction`, `manipulation`, `analysis`, …).

## 5. Conventions

- **Code tabs.** Material content tabs labelled "MATLAB" / "Python", **linked
  and persistent**, defaulting to **MATLAB**.
- **cobrapy indicator.** Functions that resolve to cobrapy (not RAVEN) are
  marked with a consistent icon/badge and link out to the cobrapy docs.
- **Naming.** MATLAB `camelCase` ↔ Python `snake_case`; the two are paired by
  normalised name in the API generator. The Python package is **raven-toolbox**.
- **Citations / attribution.** Neutral; no AI-authorship attribution anywhere.

## 6. Open questions

*(To be resolved with the maintainer; record answers here and fold the decisions
into the relevant section above.)*

1. **Theme / branding** — colour scheme, logo, and default light/dark mode.
2. **Hosting** — Read the Docs project name / custom domain; versioned docs
   (per release) vs always-latest from the tracked dev branches.

## 7. Decisions log

*(Append decisions here as they are made.)*

- Build stack: MkDocs + Material + `mkdocstrings` (Python + MATLAB handlers).
- Source via git submodules: RAVEN tracks `develop3`, **raven-toolbox tracks
  `develop`**, hanpo-GEM tracks `main`.
- The Python package is named **raven-toolbox**.
- Function help reformatted to NumPy-style docstrings (renders as tables).
- API reference is cobrapy-style, generated from source, paired by name.
- **Tutorial 6 is excluded**; legacy tutorials are 1–5 (RAVEN 1 paper).
- **Code tabs default to MATLAB and are persistent/linked** across the site.
- **MATLAB↔Python mapping table:** auto-generated pairs + hand-curated cobrapy
  alternatives.
- **Always pull all remotes (superproject + submodules) before starting work.**
