"""Utilities for parsing an existing trade list"""
import re
from os import PathLike
from typing import Dict, List, Optional, Union

from . import PACK_FOLDER


def parse_trades(
    trade_file_path: Optional[Union[str, bytes, PathLike]] = None
) -> List[Union[str, Dict[str, str]]]:
    """Parse an existing trade list

    Parameters
    ----------
    trade_file_path: path-like, optional
        The path to the trade list you want to parse. If None is specified,
        this method will load add_trade.mcfunction from the appropriate spot
        in the pack folder.

    Returns
    -------
    list of dicts and strings
        list of player-head specifications, either in the form of player names,
        such that calling
        ```
        /give @s minecraft:player_head{SkullOwner:player_name}
        ```
        would give you the specified head, or a dict {player_name: full_spec}
        such that calling
        ```
        /give @s minecraft:player_head{full_spec}
        ```
        would give you that head

    Raises
    ------
    FileNotFoundError
        If the specified trade file doesn't exist, or if the pack
        folder doesn't exist (meaning you haven't downloaded the base datapack)
    PermissionError
        If you don't have the ability to open the trade file
    RuntimeError
        If a command in the file could not be parsed

    Notes
    -----
    This function is not smart enough to detect if the full spec doesn't actually match the "skull owner"
    """
    if trade_file_path is None:
        trade_file_path = (
            PACK_FOLDER
            / "data"
            / "wandering_trades"
            / "functions"
            / "add_trade.mcfunction"
        )
    with open(trade_file_path) as trade_file:
        file_lines = trade_file.readlines()

    player_head_trades = []  # type: List[Union[str, Dict[str, str]]]
    for line_num, line in enumerate(file_lines):

        # just being prepared for failure
        parse_fail_message = f"Could not parse line {line_num}:\n\n{line}"

        command = line.strip()
        if not command or command.startswith("#"):
            # blank line or comment
            continue

        if not re.search(r'sell:{id:"?minecraft:player_head"?', command):
            # not selling a player head, so ignore
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
            match = re.search(r"Name:.*?},", player_head_spec)
            if not match:
                raise RuntimeError(parse_fail_message)
            player_name = match.group(0)[5:-2]

            match = re.search(r'\\"text\\":.*}"', player_name)
            if match:
                player_name = match.group(0)[9:-2]

            player_name = re.sub(r'\\"|\xA7.', "", player_name)
            player_head_trades.append({player_name: player_head_spec})
    return player_head_trades
