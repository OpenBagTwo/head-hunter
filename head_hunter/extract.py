"""Utilities for loading a particular file from inside a zipped data pack"""
import fnmatch
import os
import shutil
import warnings
from contextlib import contextmanager
from os import PathLike
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import IO, Generator, List, Optional, Union
from zipfile import BadZipFile, ZipFile

from . import PACK_FOLDER
from .write import patch_tick_function


def list_available_packs(
    pack_directory: Optional[Union[str, PathLike]] = None
) -> List[Path]:
    """Return a list of all data packs (zipped or not) in the specified pack
    directory

    Parameters
    ----------
    pack_directory : path, optional
        The pack directory to search. If None is given, this method will look
        for a "packs" folder inside the current working directory.

    Returns
    -------
    list of paths
        The available data packs, sorted lexically (alphabetically)

    Notes
    -----
    If the pack directory doesn't exist, this method will return an empty list
    rather than raising an error
    """
    if pack_directory is None:
        pack_directory = Path("packs")
    if not isinstance(pack_directory, Path):
        pack_directory = Path(pack_directory)

    return sorted(
        [file for file in pack_directory.iterdir() if _is_valid_data_pack(file)]
    )


def get_data_pack(
    pack_name: str, pack_directory: Optional[Union[str, PathLike]] = None
) -> Path:
    """Get a specific data pack

    Parameters
    ----------
    pack_name : str
        Which data pack you want (not case-sensitive, and after normalizing
        for spaces, underscores and dashes)
    pack_directory : path, optional
        The pack directory to search. If None is given, this method will look
        for a "packs" folder inside the current working directory.

    Returns
    -------
    Path
        The path to that data pack. If there are multiple paths matching the
        given description, the one returned should hopefully be the _most
        recent_ one (it'll be the last one sorted lexically).


    Raises
    ------
    KeyError
        If no matching packs can be found
    RuntimeWarning
        If there are multiple packs matching the given specification
    """
    pack_pattern = _normalize_file_name(pack_name) + "*"
    matches: List[Path] = [
        file
        for file in list_available_packs(pack_directory)
        if fnmatch.fnmatchcase(_normalize_file_name(file.name), pack_pattern)
    ]

    if len(matches) == 0:
        raise KeyError(f"Could not find a pack matching {pack_pattern}")
    if len(matches) > 1:
        message = f"Multiple packs match {pack_pattern}:"
        for pack in matches:
            message += f"\n - {pack}"
        warnings.warn(message, RuntimeWarning)

    return matches[-1]


@contextmanager
def file_from_data_pack(
    pack_name: str,
    resource: Union[str, PathLike],
    pack_directory: Optional[Union[str, PathLike]] = None,
) -> Generator[IO, None, None]:
    """Extract a specific file from a data pack

    Parameters
    ----------
    pack_name : str
        Which data pack you want (not case-sensitive, and after normalizing
        for spaces, underscores and dashes)
    resource : Path
        The specific resource you want to extract, specified as a Path relative
        to the pack root
    pack_directory : path, optional
        The pack directory to search. If None is given, this method will look
        for a "packs" folder inside the current working directory.

    Yields
    -------
    file
        file pointer open to the requested file from the requested pack

    Raises
    ------
    KeyError
        If the pack or pack file cannot be found
    """
    pack_root = get_data_pack(pack_name, pack_directory)
    if pack_root.is_dir():
        try:
            with (pack_root / resource).open() as pack_file:
                yield pack_file
        except FileNotFoundError as not_here:
            raise KeyError(not_here)
    else:
        with ZipFile(pack_root).open(str(resource)) as pack_file:
            yield pack_file


def copy_data_from_existing_pack(
    pack_path: Optional[Union[str, PathLike]] = None,
    keep_block_trades: Optional[bool] = False,
) -> None:
    """Copy the "data" folder from an existing pack into the default pack folder,
    overwriting any existing data directory

    Parameters
    ----------
    pack_path : path, optional
        The pack to copy from. If None is provided, this method will look
        for a "wandering trades" data pack in the "packs" folder ("hermit edition"
        packs should be given priority).
    keep_block_trades: bool, optional
        Since this package completely overwrites the trade list, the mini-block
        trades that are in the standard pack will be removed, and
        `provide_block_trades.mcfunction` will break when it tries to load them.
        Thus, by default, this method *does not* copy `keep_block_trades` and
        removes any reference to it from `tick.mcfunction`. If you plan on
        adding back the block trades yourself manually, pass in
        `keep_block_trades=True`.

    Raises
    ------
    KeyError
        If the specified pack path does not exist or has no data folder
    """
    if pack_path is None:
        return copy_data_from_existing_pack(get_data_pack("wandering trades"))

    donor_root = Path(pack_path).resolve()
    if not donor_root.exists():
        raise KeyError(f"{donor_root} does not exist")

    with TemporaryDirectory() as tmpdir:
        try:
            shutil.move(str(PACK_FOLDER / "data"), os.path.join(tmpdir, "data"))
            move_back = True
        except FileNotFoundError:
            move_back = False
        try:
            if donor_root.is_dir():
                shutil.copytree(
                    donor_root / "data",
                    PACK_FOLDER / "data",
                    ignore=shutil.ignore_patterns("provide_block_trades.mcfunction"),
                )
            else:
                zipped = ZipFile(donor_root)
                zipped.extractall(
                    PACK_FOLDER,
                    [
                        file
                        for file in zipped.namelist()
                        if file.startswith(f"data{os.sep}")
                        and (
                            not file.endswith("provide_block_trades.mcfunction")
                            or keep_block_trades
                        )
                    ],
                )
            if not keep_block_trades:
                patch_tick_function()

        except Exception as fail:
            if move_back:
                shutil.rmtree(PACK_FOLDER / "data", ignore_errors=True)
                shutil.move(os.path.join(tmpdir, "data"), PACK_FOLDER / "data")
            raise fail


def _is_valid_data_pack(pack_path: Path) -> bool:
    """Determine if a given path represents a valid data pack

    Parameters
    ----------
    pack_path : Path
        The path to check

    Returns
    -------
    bool
        Returns True if the path is a folder or a directory containing a
        `pack.mcmeta` file in its root. Otherwise returns False.
    """
    if pack_path.is_symlink():
        return _is_valid_data_pack(pack_path.resolve())
    if pack_path.is_dir():
        return (pack_path / "pack.mcmeta").exists()
    try:
        return "pack.mcmeta" in ZipFile(pack_path).namelist()
    except (BadZipFile, FileNotFoundError):
        return False


def _normalize_file_name(name: str) -> str:
    """Normalize a file name for easy matching

    Parameters
    ----------
    name: str
        The raw name

    Returns
    -------
    str
        The normalized version of that name (lowercase, removing spaces,
         dashes and underscores)
    """
    return name.replace(" ", "").replace("_", "").replace("-", "").lower()
