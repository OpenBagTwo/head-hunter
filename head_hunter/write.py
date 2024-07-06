"""Utilities for writing / updating data pack files"""

import datetime as dt
from os import PathLike
from pathlib import Path
from typing import Iterable

from . import BLOCK_TRADE_FILENAME, HEAD_TRADE_FILENAME, PACK_FOLDER
from ._legacy import LegacyHeadSpec

META_FILES = (
    "pack.mcmeta",
    "data/vanillatweaks/advancements/wandering_trades.json",
)

START_AT = 2


def write_meta_files(
    *template_paths: str | PathLike,
    version: str | None = None,
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


def write_head_trades(
    trades: Iterable[LegacyHeadSpec],
    price: tuple[str, int] | None = None,
    purchase_limit: int = 3,
    xp_bonus: int = 0,
) -> tuple[int, int]:
    """Render the `add_trade.mcfunction` file that will give the
    Wandering Trader a specified list of head trades

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
        The (inclusive) lower and upper bounds of the trade indices corresponding
        to the written trades (the lower bound is hard-coded as
        `START_AT` but still...)

    Notes
    -----
    If the return values are such that the upper bound is less than the lower
    bound, that means that no trades were actually written.

    Raises
    ------
    FileNotFoundError
        If the pack folder or functions subdirectory doesn't exist
        (meaning you haven't downloaded the base data pack or that the file
        structure is corrupted
    PermissionError
        If you don't have the ability to write to the pack folder
    """
    if price is None:
        price = ('"minecraft:emerald"', 1)

    template_path = Path(__file__).parent / "templates" / "add_trade.mcfunction"

    with open(template_path) as template_file:
        template = template_file.readlines()

    header = (
        "".join(template[:-2])
        .replace("TRADE_TYPE", "head")
        .replace("PROVIDER", "provide_hermit_trades.mcfunction")
    )

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

    for head in trades:
        command = command_template.replace(
            "IDX", str(trade_index := trade_index + 1)  # ++trade_index
        ).replace("HEAD_SPEC", head.spec)
        commands.append(command)

    trade_file_path = (
        PACK_FOLDER / "data" / "wandering_trades" / "functions" / HEAD_TRADE_FILENAME
    )

    trade_file_path.write_text("".join([*header, *commands]))
    return START_AT, trade_index


def write_block_trades(
    commands: Iterable[str], start_at: int = 1002
) -> tuple[int, int]:
    """Render the file `add_block_trade.mcfunction` that will separately specify
    the list of block trades to provide the Wandering Trader

    Parameters
    ----------
    commands: list-like of str
        The commands extracted from the original `add_trade.mcfunction` file
        (though I suppose you could provide your own)
    start_at: int, optional
        The starting value for the trade index. Default is 1000.

    Returns
    -------
    (int, int) tuple
        The lower and upper bounds of the trade indices corresponding to the
        written trades (note that if start_at is negative, then the start_at
        value will be the *upper bound*)

    Notes
    -----
    If the return values are such that the upper bound is less than the lower
    bound, that means that no trades were actually written.

    Raises
    ------
    FileNotFoundError
        If the pack folder or functions subdirectory doesn't exist
        (meaning you haven't downloaded the base data pack or that the file
        structure is corrupted
    PermissionError
        If you don't have the ability to write to the pack folder
    """
    template_path = Path(__file__).parent / "templates" / "add_trade.mcfunction"

    with open(template_path) as template_file:
        template = template_file.readlines()

    header = (
        "".join(template[:-2])
        .replace("TRADE_TYPE", "block")
        .replace("PROVIDER", "provide_block_trades.mcfunction")
    )

    trade_file_path = (
        PACK_FOLDER / "data" / "wandering_trades" / "functions" / BLOCK_TRADE_FILENAME
    )

    # see comment in write_head_trades about why we do this
    trade_index = start_at - 1

    with trade_file_path.open("w") as trade_file:
        trade_file.write(header)
        for command in commands:
            trade_file.write(
                command.replace("IDX", str(trade_index := trade_index + 1)) + "\n\n"
            )

    return start_at, trade_index


def update_trade_count(
    lower_bound: int,
    upper_bound: int,
    trade_provider: str | PathLike,
) -> None:
    """Update the "provide trades" function file to generate a random number
    from the specified bounds

    Parameters
    ----------
    lower_bound : int
        The number of the first trade (inclusive)
    upper_bound : int
        The number of the last trade (inclusive)
    trade_provider : str or path
        Which trade provider to update. Should either be "head", "block" or
        the path to the actual `mcfunction` file (in case you have something
        custom going on).

    Raises
    ------
    FileNotFoundError
        If the destination trade provider file doesn't exist
    PermissionError
        If you don't have the ability to write to the trade file
    ValueError
        If the trade provider file could not be properly munged
    """
    if trade_provider in ("head", "heads", "hermit", "hermits"):
        trade_provider_file = (
            PACK_FOLDER
            / "data"
            / "wandering_trades"
            / "functions"
            / "provide_hermit_trades.mcfunction"
        )
    elif trade_provider in ("block", "blocks"):
        trade_provider_file = (
            PACK_FOLDER
            / "data"
            / "wandering_trades"
            / "functions"
            / "provide_block_trades.mcfunction"
        )
    else:
        trade_provider_file = Path(trade_provider)

    commands = trade_provider_file.read_text().splitlines()

    bound_idx = 0
    bounds = (lower_bound, upper_bound)
    write_me: list[str] = []
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


def patch_block_trades_out_of_tick_function(
    tick_function_path: str | PathLike | None = None,
) -> None:
    """If you're not looking to keep the block trades, then this method removes
    all reference to them from `tick.mcfunction`

    Parameters
    ----------
    tick_function_path : path, optional
        The file to update (in case it's in a weird place). If None is provided,
        this method will look for "tick.mcfunction" within the default pack
        folder.
    """
    if tick_function_path is None:
        tick_function_path = (
            PACK_FOLDER / "data" / "wandering_trades" / "functions" / "tick.mcfunction"
        )

    commands = Path(tick_function_path).read_text().splitlines()

    write_me: list[str] = []
    for command in commands:
        if (
            "!has_new_block_trades" in command
            or command.strip() == "# Amount of block trades"
        ):
            continue
        if command.strip().endswith(
            "run function wandering_trades:provide_hermit_trades"
        ):
            write_me.append(
                "execute as"
                " @e[type=minecraft:wandering_trader,tag=!has_new_hermit_trades]"
                " at @s run function wandering_trades:provide_hermit_trades"
            )
        else:
            write_me.append(command)

    if write_me[-1] != "":
        write_me.append("")  # always good to end with a newline

    Path(tick_function_path).write_text("\n".join(write_me))


def patch_block_trade_provider_function(
    provider_function_path: str | PathLike | None = None,
) -> None:
    """If you're looking to keep the block trades, then update the block
    trade provider so that it knows where to find them

    Parameters
    ----------
    provider_function_path : path, optional
        The file to update (in case it's in a weird place). If None is provided,
        this method will look for "provide_block_trades.mcfunction" within
        the default pack folder.
    """
    if provider_function_path is None:
        provider_function_path = (
            PACK_FOLDER
            / "data"
            / "wandering_trades"
            / "functions"
            / "provide_block_trades.mcfunction"
        )

    provider = Path(provider_function_path).read_text()
    Path(provider_function_path).write_text(
        provider.replace(
            "wandering_trades:add_trade",
            "wandering_trades:" + BLOCK_TRADE_FILENAME.split(".")[0],
        )
    )
