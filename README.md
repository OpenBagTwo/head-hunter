# Wandering Head Hunter

Utilities for creating customized datapacks that provide the wandering trader
with player head trades

**The entire credit for the datapack itself** goes to the [**Vanilla Tweaks**](https://vanillatweaks.net)
team and their Wandering Trades datapack upon which this is based.

## Installation and Setup

The scripts in this repo require python 3.8 or newer and requires no other dependencies to run.

Thus, all you need to do to run these scripts is to download this repo and run the commands below from the
project's root folder.

You'll also need to grab yourself a copy of the Wandering Trader datapack.
1. Go to the Vanilla Tweaks [datapacks page](https://vanillatweaks.net/picker/datapacks/)
1. Under "Hermitcraft," select "More Mob Heads" and "Wandering Trades (Hermit Edition)"
1. Download the zip archive and extract the "UNZIP_ME" parent zip file into the "packs" folder.

## Usage

This package contains four modules:
1. `extract`, which extracts files from existing datapacks
1. `parse`, which parses head configurations from data pack functions and `/give` commands
1. `write`, which write the various datapack files
1. `release`, which bundles everything up into a handy zip file

You can grab information about the methods in each module using the
[`help()`](https://docs.python.org/3/library/functions.html#help)
function, or you can browse the docstrings in GitHub (HTML docs are coming).

There's also a handy [end-to-end tutorial](Tutorial.ipynb) that you can even run interactively
in Jupyter.

## Contributing

A development environment is provided in the form of a
[conda `environment.yml` file](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).
I highly recommend the [mambaforge](https://github.com/conda-forge/miniforge#mambaforge)
distribution of conda.

For ease of style-guide enforcement, a [pre-commit](https://pre-commit.com/) configuration has been
provided.

## License

The `head_hunter` package and its contents are licensed under [the GNU Public License v3](LICENSE). Any data packs produced
by this package must be licensed under [Vanilla Tweaks' terms of use](Head Hunter/LICENSE.txt).
