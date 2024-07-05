"""Utilities for parsing an existing trade list"""

import json
import re
from os import PathLike
from pathlib import Path
from typing import IO

from . import HEAD_TRADE_FILENAME
from ._legacy import LegacyHeadSpec
from .extract import file_from_data_pack


def _function_dirs(parent_dir: Path) -> tuple[Path, ...]:
    """Given a data pack namespace folder, which should be the parent of a
    "function(s)" folder, return all possible functions folders

    Parameters
    ----------
    parent_dir : Path
        The directory that should contain a function(s) folder

    Returns
    -------
    tuple of Paths
        The possible function folders, with priority given to the one recognized
        by the most recent Minecraft versions
    """
    return parent_dir / "function", parent_dir / "functions"


def parse_wandering_trades(
    trade_path: str | PathLike | None = None,
) -> tuple[list[LegacyHeadSpec], list[str]]:
    """Parse an existing trade list

    Parameters
    ----------
    trade_path : path, optional
        The trade list you want to parse. If None is specified,
        this method will look for a "wandering trades" pack in the packs folder
        and attempt to parse `add_trade.mcfunction`  from there.

    Returns
    -------
    list of NamedTuples
        list of player-head specifications such that calling
        ```
        /give @s minecraft:player_head{head.spec}
        ```
        would give you the specified head
    list of str
        list of block trade commands, with the trade index replaced by the
        placeholder "IDX"

    Raises
    ------
    FileNotFoundError
        If the specified trade file doesn't exist
    PermissionError
        If you don't have the ability to open the trade file
    RuntimeError
        If a command in the file could not be parsed

    Notes
    -----
    This function is not smart enough to detect if the full spec doesn't
    actually match the "skull owner"
    """
    if trade_path is None:
        with file_from_data_pack(
            "wandering trades hermit edition",
            (
                function_folder / HEAD_TRADE_FILENAME
                for function_folder in _function_dirs(Path("data") / "wandering_trades")
            ),
        ) as trade_file:
            return _parse_wandering_trades(trade_file)
    else:
        with open(trade_path) as trade_file:
            return _parse_wandering_trades(trade_file)


def _parse_wandering_trades(trade_file: IO) -> tuple[list[LegacyHeadSpec], list[str]]:
    player_head_trades: list[LegacyHeadSpec] = []
    block_trades: list[str] = []
    for line_num, line in enumerate(trade_file.readlines()):
        if isinstance(line, bytes):
            line = line.decode("utf-8")

        # just being prepared for failure
        parse_fail_message = f"Could not parse line {line_num}:\n\n{line}"

        command = line.strip()
        if not command or command.startswith("#"):
            # blank line or comment
            continue

        if not re.search(r'sell:{id:"?minecraft:player_head"?', command):
            # not selling a player head, so ignore
            continue

        if 'buyB:{id:"minecraft:air"' not in command:
            # then it's a block trade
            match = re.search(r"(?:wt_tradeIndex matches ([0-9]*) run)", command)
            if not match:
                raise RuntimeError(parse_fail_message)
            span = match.span(1)
            block_trades.append(command[: span[0]] + "IDX" + command[span[1] :])
            continue

        # this is brittle generally, but depth matching is probably YAGNI
        match = re.search(r"tag:{.*}}}", command)
        if not match:
            raise RuntimeError(parse_fail_message)
        player_head_spec = match.group(0)[5:-3]

        match = re.search(r"Name:.*?,", player_head_spec)
        if not match:
            # try legacy spec
            if re.match(r"^SkullOwner:\w*$", player_head_spec):
                player_name = player_head_spec.split(":")[1]
                player_head_trades.append(LegacyHeadSpec.from_username(player_name))
                continue
            raise RuntimeError(parse_fail_message)
        player_name = match.group(0)[5:-1]
        skull_spec = player_head_spec[match.span()[1] :]

        match = re.search(r'(?:\\"text\\":(?:\\"|)(.*?)(?:\\"|)}")', player_name)
        if match:
            player_name = match.group(1)

        player_head_trades.append(LegacyHeadSpec(player_name, skull_spec))

    return player_head_trades, block_trades


def parse_mob_heads(mob: str | PathLike) -> list[LegacyHeadSpec]:
    """Extract head specs from a "More Mob Heads" data pack loot table.

    Parameters
    ----------
    mob: str or path
        Either the name of the mob whose head (or heads) you're looking
        to parse (in which case this method will attempt to extract the mob
        head from a "more mob heads" data pack stored in the "packs" folder)

        _or_

        the path of the particular loot table JSON you're wanting to parse

    Returns
    -------
    List of NamedTuples
        list of player-head specifications such that calling
        ```
        /give @s minecraft:player_head{head.spec}
        ```
        would give you the specified head

    Raises
    ------
    FileNotFoundError
        If the specified file doesn't exist or can't be found
    PermissionError
        If you don't have the ability to open the file
    JSONDecodeError
        If the specified file is not valid JSON
    """
    # first check if it's a file
    try:
        with open(mob) as mob_file:
            return _parse_mob_heads(mob_file)
    except (FileNotFoundError, PermissionError, json.JSONDecodeError) as oops:
        # maybe it's a relative path inside a pack?
        try:
            with file_from_data_pack("more mob heads", mob) as mob_file:
                return _parse_mob_heads(mob_file)
        except (KeyError, json.JSONDecodeError, PermissionError):
            pass
        if not isinstance(mob, str):
            raise oops

    # now check if it's the mob name
    with file_from_data_pack(
        "more mob heads",
        Path("data") / "minecraft" / "loot_tables" / "entities" / f"{mob}.json",
    ) as mob_file:
        return _parse_mob_heads(mob_file)


def _parse_mob_heads(mob_file: IO) -> list[LegacyHeadSpec]:
    loot_table = json.load(mob_file)
    head_drops: list[dict] = []
    for pool in loot_table["pools"]:
        for entry in pool["entries"]:
            if "children" in entry:
                for drop in entry["children"]:
                    if drop["name"] == "minecraft:player_head":
                        head_drops.append(drop)
            if entry.get("name", "") == "minecraft:player_head":
                head_drops.append(entry)

    head_specs: list[LegacyHeadSpec] = []
    for drop in head_drops:
        for head_function in drop["functions"]:
            head_spec = head_function["tag"]
            match = re.search(r'(?:Name:"(.*?)")', head_spec)
            if not match:
                parse_fail_message = f"Could not parse:\n {drop}"
                raise RuntimeError(parse_fail_message)
            else:
                name = match.group(1)
            head_specs.append(LegacyHeadSpec(name, head_spec[1:-1]))

    return head_specs


def parse_give_command(command: str, name: str) -> LegacyHeadSpec:
    """Parse a /give command (such as you'd find from a skin lookup site) to
    extract just the relevant specification that needs to go into the head-list

    Parameters
    ----------
    command : str
        The full `/give` command
    name : str
        The name (with any fancy formatting) to give to the head

    Returns
    -------
    NamedTuple
        The tokenized head specification

    Raises
    ------
    ValueError
        If the command could not be parsed
    """
    match = re.search(r"(?:(SkullOwner:.*?)(?:,display:|}$))", command.strip())
    if not match:
        raise ValueError("Could not parse command")
    return LegacyHeadSpec(
        name, r'display:{Name:"{\"text\":\"' + name + r'\"}"},' + match.group(1)
    )
