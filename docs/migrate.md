---
icon: material/folder-open
---

# Migrate

Four ways of moving between versions or languages, each answering a
different question.

| | |
|---|---|
| [RAVEN 2 → RAVEN 3 (MATLAB)](raven3-migration.md) | Upgrading an existing MATLAB codebase: what was renamed, removed outright, or changed between RAVEN 2 and RAVEN 3. |
| [RAVEN 3 → raven-toolbox](raven3-vs-raven-toolbox.md) | Choosing between the two current implementations, or porting a MATLAB workflow to Python: what each toolbox has, and where they answer the same question differently. |
| [MATLAB vs Python function mapping](matlab-vs-python.md) | The full name table pairing every function that exists in both, generated at build time from both toolboxes' sources. |
| [Model file format (YAML)](yaml-format.md) | The YAML model format cobrapy, raven-toolbox and RAVEN MATLAB all read and write, for moving a model file between any of them or into version control. |

```{toctree}
:hidden:

raven3-migration
raven3-vs-raven-toolbox
matlab-vs-python
yaml-format
```
