"""Utilities for packaging your data pack for use in a world"""
import os
import shutil
from os import PathLike
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Union

from . import PACK_FOLDER


def make_zip(destination_path: Optional[Union[str, PathLike]] = None):
    """Bundle up your pack folder as a data pack zip file

    Parameters
    ----------
    destination_path : path, optional
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

    destination_filebase = os.path.abspath(destination_path)

    with TemporaryDirectory() as tmpdir:
        shutil.copytree(
            PACK_FOLDER,
            os.path.join(tmpdir, PACK_FOLDER.name),
            ignore=shutil.ignore_patterns(".*"),
        )
        shutil.make_archive(
            destination_filebase, "zip", os.path.join(tmpdir, PACK_FOLDER.name)
        )
