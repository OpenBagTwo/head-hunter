# [Head Hunter](https://github.com/OpenBagTwo/head-hunter)

A package for customizing [**Vanilla Tweaks'**](https://vanillatweaks.net)
[Wandering Trades data pack](https://www.youtube.com/watch?v=L3En7cuOdHY) to stock
[everyone's favorite](https://www.youtube.com/shorts/tbkQ-IXRdbs) [ex-nitwit](https://www.youtube.com/watch?v=tVA8eNh7VWs)
with your own personalized list of custom player heads.

## Installation and Setup

To get started, it's recommended that you clone this repo to your computer:

```bash
git clone https://github.com/OpenBagTwo/head-hunter -–depth 1
```

You'll also need to grab yourself a copies of the Vanilla Tweaks data packs.

1. Go to the Vanilla Tweaks [data packs page](https://vanillatweaks.net/picker/datapacks/)
1. Under "Hermitcraft," select "More Mob Heads" and "Wandering Trades (Hermit Edition)"
1. Download the zip archive and extract the "UNZIP_ME" parent zip file into the "packs" folder.

## Usage

This package is compatible with Python 3.8 or newer and consists of four modules:

1. `extract`, which extracts files from existing data packs
1. `parse`, which parses head configurations from data pack functions and `/give` commands
1. `write`, which write the various data pack files
1. `release`, which bundles everything up into a handy zip file

You can grab information about the methods in each module using the
[`help()`](https://docs.python.org/3/library/functions.html#help)
function, or you can browse [the API documentation online](https://openbagtwo.github.io/head-hunter/reference/head_hunter/).

There's also a handy [end-to-end tutorial](Tutorial.ipynb) that you can even run interactively
in [Jupyter](https://jupyter.org/).

## Contributing

A development environment is provided in the form of a
[conda `environment.yml` file](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).
I highly recommend the [mambaforge](https://github.com/conda-forge/miniforge#mambaforge)
distribution of conda.

For ease of style-guide enforcement, a [pre-commit](https://pre-commit.com/) configuration has been
provided.

Documentation is automatically built on every push to the `main` branch. To preview them locally, run `mkdocs serve`
from the repo root.

## License

The `head_hunter` package and its contents are licensed under [the GNU Public License v3](https://github.com/OpenBagTwo/head-hunter/blob/main/LICENSE). Any data packs produced
by this package must be licensed under [Vanilla Tweaks' terms of use](https://github.com/OpenBagTwo/head-hunter/blob/main/Head%20Hunter/credits.txt).
