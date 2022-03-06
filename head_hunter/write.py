"""Utilities for writing / updating datapack files"""

import datetime as dt
from os import PathLike
from pathlib import Path
from typing import Iterable, Mapping, Optional, Tuple, Union

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
        If you don't have the ability to open the template file or write to the pack folder
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


def write_trades(
    trades: Iterable[Union[str, Mapping[str, str]]],
    price: Optional[Tuple[str, int]] = None,
    purchase_limit: int = 3,
    xp_bonus: int = 0,
):
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

    for i, head in enumerate(trades):
        if isinstance(head, str):
            head_spec = f"SkullOwner:{head}"
        else:
            head_spec = list(head.values())[0]
        command = command_template.replace("IDX", str(i + 2)).replace(
            "HEAD_SPEC", head_spec
        )

        commands.append(command)

    trade_file_path = (
        PACK_FOLDER / "data" / "wandering_trades" / "functions" / "add_trade.mcfunction"
    )

    with open(trade_file_path, "w") as trade_file:
        trade_file.write("".join([*header, *commands]))
