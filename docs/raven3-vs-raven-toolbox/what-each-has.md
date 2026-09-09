# What each has that the other doesn't

## What only raven-toolbox has

### Built on cobrapy

The largest difference is not a feature but a foundation: a raven-toolbox model
**is** a `cobra.Model`. Every cobrapy tool, and everything in the wider COBRA
Python ecosystem, works on it without conversion. RAVEN's own model is a MATLAB
struct, and `ravenCobraWrapper` converts between that and the COBRA Toolbox
format as an explicit step.

The practical consequence: FBA, FVA, knockouts, media handling and the rest come
from cobrapy rather than from raven-toolbox, which is why so many RAVEN
functions have a *cobrapy* row rather than a Python counterpart in the mapping
table.

### KEGG artefact generation

raven-toolbox can build the KEGG reference artefacts themselves, parsing a KEGG
release into reaction and compound tables, assembling the reference model,
building the per-KO FASTA sets and HMM libraries, and deriving the phylogenetic
distance matrix. RAVEN consumes pre-built artefacts; it does not produce them.

This is what keeps the KEGG route reproducible against a stated KEGG release
rather than against whichever artefact is currently distributed.

### Smaller additions

- **Growth conditions**: apply a named, versioned growth condition to a model.
- **Batch curation**: apply a table of curation edits to a model in one pass.
- **ΔG and SBO annotation**: load and save thermodynamic data through CSV, and
  assign SBO terms.
- **Biomass helpers**: sum a biomass composition, rescale a pseudoreaction, and
  scale a fraction to a measured value.
- **Checksummed provisioning**: both toolboxes now fetch BLAST+, DIAMOND,
  HMMER and the KEGG artefacts on demand rather than bundling them, from the
  same release. What is Python-only is the baked registry that pins a given
  release to the exact assets it was tested against; RAVEN resolves from the
  published release each time. See
  [Download data and binaries](../installation/data-and-binaries.md).

## What only RAVEN has

### tINIT

`getINITModel` and `runINIT` are the original tINIT implementation. RAVEN keeps
them for the models already built with them; raven-toolbox, a new
implementation with no such installed base, carries ftINIT alone. A tINIT model
has to be reproduced in MATLAB; see
[14. Context-specific models](../guide/init.md).

### COBRA Toolbox conversion

`ravenCobraWrapper` converts between the RAVEN and COBRA Toolbox model
structures. There is nothing to convert in Python: the model is already a
`cobra.Model`, so no equivalent exists or is needed.

### Dynamic FBA

`runDynamicFBA` has no Python counterpart, deliberately. Several maintained
Python packages already cover dynamic FBA well
([dfba](https://pypi.org/project/dfba/),
[reframed](https://pypi.org/project/reframed/),
[mewpy](https://pypi.org/project/mewpy/)), and reimplementing it would add a
second-rate version of something that already exists.

### MATLAB-specific plumbing

A large share of RAVEN's function count is MATLAB housekeeping with nothing to
map to: path management (`addRavenToUserPath`, `findRAVENroot`), argument
handling (`parseRAVENargs`, `convertCharArray`), progress and printing
(`setRavenProgress`, `printOrange`), and the solver abstraction
(`optimizeProb`, `setRavenSolver`), which in Python is cobrapy's solver
interface via optlang.
