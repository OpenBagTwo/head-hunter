"""Utilities for parsing an existing trade list"""
import json
import re
from os import PathLike
from pathlib import Path
from typing import IO, Dict, List, Optional, Union

from .extract import file_from_data_pack


def parse_wandering_trades(
    trade_path: Optional[Union[str, PathLike]] = None
) -> List[Union[str, Dict[str, str]]]:
    """Parse an existing trade list

    Parameters
    ----------
    trade_path : path, optional
        The trade list you want to parse. If None is specified,
        this method will look for a "wandering trades" pack in the packs folder
        and attempt to parse `add_trade.mcfunction`  from there.

    Returns
    -------
    list of dicts and strings
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
    This function is not smart enough to detect if the full spec doesn't actually match the "skull owner"
    """
    if trade_path is None:
        with file_from_data_pack(
            "wandering trades hermit edition",
            Path("data") / "wandering_trades" / "functions" / "add_trade.mcfunction",
        ) as trade_file:
            return _parse_wandering_trades(trade_file)
    else:
        with open(trade_path) as trade_file:
            return _parse_wandering_trades(trade_file)


def _parse_wandering_trades(trade_file: IO) -> List[Union[str, Dict[str, str]]]:
    player_head_trades = []  # type: List[Union[str, Dict[str, str]]]
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
            # then it's a mini-block
            continue

        # this is brittle gererally, but depth matching is probably YAGNI
        match = re.search(r"tag:{.*}}}", command)
        if not match:
            raise RuntimeError(parse_fail_message)
        player_head_spec = match.group(0)[5:-3]

        if re.match(r"^SkullOwner:\w*$", player_head_spec):
            # using simple spec
            player_head_trades.append(player_head_spec.split(":")[1])
        else:
            match = re.search(r"Name:.*?,", player_head_spec)
            if not match:
                raise RuntimeError(parse_fail_message)
            player_name = match.group(0)[5:-1]

            match = re.search(r'\\"text\\":.*}"', player_name)
            if match:
                player_name = match.group(0)[9:-2]

            player_name = re.sub(r'\\?"|\xA7.|}', "", player_name)
            player_head_trades.append({player_name: player_head_spec})
    return player_head_trades


def parse_mob_heads(mob: Union[str, PathLike]) -> List[Dict[str, str]]:
    """Extract head specs from a "More Mob Heads" datapack loot table.
    For`more mob heads v2.9.4.zip` these loot tables are found at:
    `/data/minecraft/loot_tables/entities/`

    Parameters
    ----------
    mob: str or path
        Either the name of the mob whose head (or heads) you're looking
        to parse (in which case this method will attempt to extract the mob
        head from a "more mob heads" datapack stored in the "packs" folder)

        _or_

        the path of the particular loot table JSON you're wanting to parse

    Returns
    -------
    List of 1-item dicts
        list of player-head specifications, in the form
        {mob_name: full_spec} such that calling
        ```
        /give @s minecraft:player_head{full_spec}
        ```
        would give you that head

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


def _parse_mob_heads(mob_file: IO) -> List[Dict[str, str]]:
    loot_table = json.load(mob_file)
    head_drops = []
    for pool in loot_table["pools"]:
        for entry in pool["entries"]:
            if "children" in entry:
                for drop in entry["children"]:
                    if drop["name"] == "minecraft:player_head":
                        head_drops.append(drop)
            if entry.get("name", "") == "minecraft:player_head":
                head_drops.append(entry)

    head_specs = []
    for drop in head_drops:
        for head_function in drop["functions"]:
            head_spec = head_function["tag"]
            match = re.search(r'Name:".*?"', head_spec)
            if not match:
                name = "???"
                # name isn't actually used for anything anyway
            else:
                name = match.group(0)[6:-1]
            head_specs.append({name: head_spec[1:-1]})

    return head_specs


def parse_give_command(command: str) -> str:
    """Parse a /give command (such as you'd find from a skin lookup site) to
    extract just the relevant specification that needs to go into the head-list

    Parameters
    ----------
    command : str
        The full `/give` command

    Returns
    -------
    str
        the relevant head specification

    Raises
    ------
    ValueError
        If the command could not be parsed
    """

    match = re.search(r"SkullOwner.*,display:", command.strip())
    if not match:
        raise ValueError("Could not parse command")
    return match.group(0)[: -len(",display:")]
