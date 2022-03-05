# Wandering Head Hunter

Utilities for creating customized datapacks that provide the wandering trader
with player head trades

**The entire credit for the datapack itself** goes to the [**Vanilla Tweaks**](https://vanillatweaks.net)
team and their Wandering Trades datapack upon which this is based.

## Installation and Setup

This scripts in this repo require python 3.6 or newer and requires no other dependencies to run.

Thus, all you need to do to run these scripts is to download this repo and run the commands below from the
project's root folder.

You'll also need to grab yourself a copy of the Wandering Trader datapack.
1. Go to the Vanilla Tweaks [datapacks page](https://vanillatweaks.net/picker/datapacks/)
1. Under "Hermitcraft," select "Wandering Trades (Hermit Edition)"
1. Download the zip archive and extract the "UNZIP_ME" parent zip file
1. Extract the contents of the "wandering trades hermit edition" zip file to a folder named
   `Head Hunter` located in the project root folder (or your current working directory if you
   installed this package via pip)

You should now have a folder named `Head Hunter` whose top-level contents are:
* a `data` directory
* a file named `pack.mcmeta`
* an icon named `pack.png`

## Usage

(TBD)


## Contributing

A development environment is provided in the form of a
[conda `environment.yml` file](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).
I highly recommend the [mambaforge](https://github.com/conda-forge/miniforge#mambaforge)
distribution of conda.

For ease of style-guide enforcement, a [pre-commit](https://pre-commit.com/) configuration has been
provided. 
