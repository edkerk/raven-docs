# Example data

The models the [user guide](../guide/index.md) pages load. They are copied here,
rather than read from the `RAVEN` submodule, so that every snippet can use a
short, stable path (`smallYeast.yml`) that works the same way for a reader who
downloads the file and for the example runner in CI.

| File | Size | Source | Used by |
|---|---|---|---|
| `smallYeast.yml` | 45 kB | `RAVEN/tutorial/smallYeast.yml` | the default example model for most guide pages |
| `smallYeastBad.yml` | 45 kB | `RAVEN/tutorial/smallYeastBad.yml` | the quality-control and gap-filling pages, which need a model with known errors |
| `yeast-GEM.yml` | 3.6 MB | yeast-GEM **v9.1.0**, `model/yeast-GEM.yml` | pages that need a genome-scale model — sampling, deletions, ftINIT, gap-filling |
| `yeast-GEM.xml` | 11.6 MB | yeast-GEM **v9.1.0**, `model/yeast-GEM.xml` | the same model as SBML, for the pages about SBML I/O and annotations |

The two small yeast models are part of the RAVEN Toolbox (MIT licence).
yeast-GEM is the consensus genome-scale model of *Saccharomyces cerevisiae*
([SysBioChalmers/yeast-GEM](https://github.com/SysBioChalmers/yeast-GEM),
CC-BY-4.0), pinned here at release **v9.1.0** so the numbers printed in the guide
stay reproducible while the model keeps developing.

The `.yml` files are RAVEN YAML, read by `readYAMLmodel` in MATLAB and
`read_yaml_model` in Python; `yeast-GEM.xml` is SBML, read by `importModel` and
cobrapy's `read_sbml_model`.

## Refreshing them

The two RAVEN tutorial copies are deliberate duplicates, so they do not follow the
`RAVEN` submodule automatically. After a submodule bump that changes either
model, refresh them and re-run the examples:

```bash
cp "RAVEN/tutorial/smallYeast.yml" docs/data/smallYeast.yml
cp "RAVEN/tutorial/smallYeastBad.yml" docs/data/smallYeastBad.yml
python scripts/run_examples.py
```

Moving to a newer yeast-GEM is a deliberate act, not a routine one: every number
the guide prints from it changes, so bump the tag, re-download both files, and
re-generate the affected output blocks in one commit.

```bash
YEAST_GEM=v9.1.0   # the release the guide currently documents
curl -sSL -o docs/data/yeast-GEM.yml "https://raw.githubusercontent.com/SysBioChalmers/yeast-GEM/${YEAST_GEM}/model/yeast-GEM.yml"
curl -sSL -o docs/data/yeast-GEM.xml "https://raw.githubusercontent.com/SysBioChalmers/yeast-GEM/${YEAST_GEM}/model/yeast-GEM.xml"
python scripts/run_examples.py --update
```

Do not edit the files in place: any change here silently makes the guide's
numbers unreproducible for a reader who takes the model from RAVEN instead.
