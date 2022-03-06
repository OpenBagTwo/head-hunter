"""Utilities for packaging your datapack for use in a world"""
import shutil
from os import PathLike
from os.path import abspath
from pathlib import Path
from typing import Optional, Union

from . import PACK_FOLDER


def make_zip(destination_path: Optional[Union[str, bytes, PathLike]] = None):
    """Bundle up your pack folder as a datapack zip file

    Parameters
    ----------
    destination_path : path-like, optional
        The file path where you'd like to save the zip file.
        DO NOT include the ".zip" extension.
        If None is specified, the file will be saved as
        "Head Hunter.zip" in the current working directory.

    Returns
    -------
    None

    Raises
    ------
    FileNotFoundError
        If the specified template file doesn't exist or if the
        pack folder doesn't exist
    PermissionError
        If you don't have the ability to open the pack folder
        or write to the destination path
    """
    if destination_path is None:
        destination_path = Path("Head Hunter")

    destination_filebase = str(abspath(destination_path))
    pack_root = str(abspath(PACK_FOLDER))

    shutil.make_archive(destination_filebase, "zip", pack_root)
