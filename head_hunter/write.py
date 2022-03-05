"""Utilities for writing / updating datapack files"""

import datetime as dt
from os import PathLike
from pathlib import Path
from typing import Optional, Union

from . import PACK_FOLDER


def write_mcmeta(
    template_path: Optional[Union[str, bytes, PathLike]] = None,
    version: Optional[str] = None,
):
    """Write a pack.mcmeta, using the template in the templates folder
    (or one you brought yourself)

    Parameters
    ----------
    template_path : path-like, optional
        The path to a template pack.mcmeta file. If None is provided,
        the file in the templates folder will be used.
    version : str, optional
        The version to give to the pack. If None is provided, one will
        be generated based on the current date (calver).

    Returns
    -------
    None

    Raises
    ------
    FileNotFoundError
        If the specified template file doesn't exist, or if the pack
        folder doesn't exist (meaning you haven't downloaded the base datapack)
    PermissionError
        If you don't have the ability to open the template file
    """
    if template_path is None:
        template_path = Path(__file__).parent / "templates" / "pack.mcmeta"

    if version is None:
        version = dt.date.today().strftime("v%Y.%m.%d")

    with open(template_path) as template_file:
        template = template_file.read()

    mcmeta = template.replace("VERSION", version)

    with open(PACK_FOLDER / "pack.mcmeta", "w") as pack_file:
        pack_file.write(mcmeta)
