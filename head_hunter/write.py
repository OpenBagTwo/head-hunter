"""Utilities for writing / updating datapack files"""

import datetime as dt
from os import PathLike
from pathlib import Path
from typing import Iterable, List, Mapping, Optional, Tuple, Union

from . import PACK_FOLDER

META_FILES = (
    "pack.mcmeta",
    "data/vanillatweaks/advancements/wandering_trades.json",
)

START_AT = 2


def write_meta_files(
    *template_paths: Union[str, PathLike],
    version: Optional[str] = None,
) -> None:
    """Write a metadata file (or files), using the template in the templates
    folder (or one(s) you brought yourself)

    Parameters
    ----------
    template_paths : path-like, optional
        The paths to template files. If None is provided, the files in the
        templates folder will be used.
    version : str, optional
        The version to give to the pack. If None is provided, one will
        be generated based on the current date (calver).

    Returns
    -------
    None

    Notes
    -----
    The list of supported metadata files is hard-coded in this module as
    `META_FILES`.

    Raises
    ------
    ValueError
        If the template file is not recognized (filename should match the file
        name of the metadata file).
    FileNotFoundError
        If the specified template file doesn't exist
    PermissionError
        If you don't have the ability to open the template file or write to the
        pack folder
    """
    if version is None:
        version = dt.date.today().strftime("v%Y.%m.%d")

    if not template_paths:
        # TODO: replace this with some proper importlib resources
        template_paths = (
            Path(__file__).parent / "templates" / "pack.mcmeta",
            Path(__file__).parent / "templates" / "wandering_trades.json",
        )

    for file in template_paths:
        _write_meta_file(Path(file), version)


def _write_meta_file(template_file: Path, version: str) -> None:
    template = template_file.read_text()

    mcmeta = template.replace("VERSION", version)

    for file in META_FILES:
        if file.split("/")[-1] == template_file.name:
            destination = Path(file)
            break
    else:
        raise ValueError(f"Unrecognized template {template_file.name}")

    with open(PACK_FOLDER / destination, "w") as pack_file:
        pack_file.write(mcmeta)


def write_trades(
    trades: Iterable[Union[str, Mapping[str, str]]],
    price: Optional[Tuple[str, int]] = None,
    purchase_limit: int = 3,
    xp_bonus: int = 0,
) -> Tuple[int, int]:
    """Render the add_trade.mcfunction file that will give the Wandering Trader
    a specified list of head trades

    Parameters
    ----------
    trades: list-like of dicts and strings
        list of player-head specifications, either in the form of player names,
        such that calling
        ```
        /give @s minecraft:player_head{SkullOwner:player_name}
        ```
        would give you the specified head, or single-item dicts
        {player_name: full_spec} such that calling
        ```
        /give @s minecraft:player_head{full_spec}
        ```
        would give you that head
    price: tuple of (str, int), optional
        The price of a head, structured in the form (item, quantity).
        Default price is one emerald.
    purchase_limit: int, optional
        The number of each head you can buy per trader. Default is 3.
    xp_bonus: int, optional
        The amount of XP you get from buying a player head. Default behavior
        is that buying player heads does not award experience.

    Returns
    -------
    (int, int) tuple
        The lower and upper bounds of the trade indices corresponding to the
        written trades (the lower bound is hard-coded as `START_AT` but still...)

    Notes
    -----
    If the return values are such that the upper bound is less than the lower
    bound, that means that no trades were actually written.

    Raises
    ------
    FileNotFoundError
        If the pack folder or functions subdirectory doesn't exist
        (meaning you haven't downloaded the base datapack or that the file
        structure is corrupted
    PermissionError
        If you don't have the ability to write to the pack folder
    """
    if price is None:
        price = ('"minecraft:emerald"', 1)

    template_path = Path(__file__).parent / "templates" / "add_trade.mcfunction"

    with open(template_path) as template_file:
        template = template_file.readlines()

    header = template[:-2]

    command_template = "".join(template[-2:])

    commands = []
    for placeholder, value in (
        ("XP_BONUS", str(xp_bonus)),
        ("PURCHASE_LIMIT", str(purchase_limit)),
        ("COST_ITEM", price[0]),
        ("COST_QTY", str(price[1])),
    ):
        command_template = command_template.replace(placeholder, value)

    # the trick here is that we want the bounds to be inclusive,
    # so STARTS_AT should be the first written value, and trade_index
    # should be the last
    trade_index = START_AT - 1

    for i, head in enumerate(trades):
        if isinstance(head, str):
            head_spec = f"SkullOwner:{head}"
        else:
            head_spec = list(head.values())[0]

        command = command_template.replace(
            "IDX", str(trade_index := trade_index + 1)  # ++trade_index
        ).replace("HEAD_SPEC", head_spec)
        commands.append(command)

    trade_file_path = (
        PACK_FOLDER / "data" / "wandering_trades" / "functions" / "add_trade.mcfunction"
    )

    trade_file_path.write_text("".join([*header, *commands]))
    return START_AT, trade_index


def update_trade_count(
    lower_bound: int,
    upper_bound: int,
    trade_provider_file: Optional[Union[str, PathLike]] = None,
) -> None:
    """Update the "provide trades" function file to generate a random number
    from the specified bounds

    Parameters
    ----------
    lower_bound : int
        The number of the first trade (inclusive)
    upper_bound : int
        The number of the last trade (inclusive)
    trade_provider_file : path, optional
        The file to update (in case you renamed it). If None is provided, this
        method will look for "provide_hermit_trades.mcfunction" within the
        default pack folder.

    Raises
    ------
    FileNotFoundError
        If the destination trade provider file doesn't exist
    PermissionError
        If you don't have the ability to write to the trade file
    ValueError
        If the trade provider file could not be properly munged
    """
    if trade_provider_file is None:
        trade_provider_file = (
            PACK_FOLDER
            / "data"
            / "wandering_trades"
            / "functions"
            / "provide_hermit_trades.mcfunction"
        )

    commands = Path(trade_provider_file).read_text().splitlines()

    bound_idx = 0
    bounds = (lower_bound, upper_bound)
    write_me: List[str] = []
    for command in commands:
        if command.startswith(f"scoreboard players set @s math_input{bound_idx + 1}"):
            try:
                write_me.append(
                    f"scoreboard players set @s math_input{bound_idx + 1} {bounds[bound_idx]}"
                )
            except IndexError:
                raise ValueError(f"Too many math_input variables found:\n {command}")

            bound_idx += 1
        else:
            write_me.append(command)
    if bound_idx < 2:
        raise ValueError(
            "Was not able to replace all of the bounds!"
            f"\n Number of bounds replaced: {bound_idx}"
        )

    if write_me[-1] != "":
        write_me.append("")  # always good to end with a newline

    Path(trade_provider_file).write_text("\n".join(write_me))
