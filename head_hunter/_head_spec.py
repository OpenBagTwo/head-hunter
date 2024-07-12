"""Functionality for abstracting and serializing player heads"""

import re
from typing import Iterable, NamedTuple

_RARITY_COLORS = (
    ("common", "white"),
    ("uncommon", "yellow"),
    ("rare", "aqua"),
    ("epic", "magenta"),
)


class HeadSpec(NamedTuple):
    """Specification of a player head

    Attributes
    ----------
    name : str
        The display name for the head
    player_name : str, optional
        The name of the skull's owner
    texture : str, optional
        The player's skin, encoded in base64. This will effectively overwrite
        any value that would have been set via the player name.
    note_block_sound : str, optional
        If set, when placed above a note block on a modern version of the game
        (1.20 and above), the note block will play the sound event
        specified by this string.
    rarity : str, optional
        Can be used for color-coding the item's name in modern versions of
        the game.
        See: https://minecraft.wiki/w/Rarity#Tiers
    color : str, optionsl
        The color to code the item's name. This will override any color set by
        rarity.
        See: https://minecraft.wiki/w/Formatting_codes
    italic : bool, optional
        Whether the item's name should be italicized. Default is False.
    bold : bool, optional
        Whether the item's name should be bolded. Default is False.
    underlined : bool, optional
        Whether the item's name should be bolded. Default is False.
    strikethrough : bool, optional
        Whether the item's name should be bolded. Default is False.
    obfuscated : bool, optional
        Whether the item's name should be bolded. Default is False.
        See: https://minecraft.wiki/w/Formatting_codes
    comment : str, optional
        An optional annotation on the head spec (that will only be used
        internally) for referencing, for example, a particular head variant


    Notes
    -----
    This spec does not currently support lore.
    """

    name: str
    player_name: str | None = None
    texture: str | None = None
    note_block_sound: str | None = None
    rarity: str | None = None
    color: str | None = None
    italic: bool = False
    bold: bool = False
    underlined: bool = False
    strikethrough: bool = False
    obfuscated: bool = False
    comment: str | None = None

    @classmethod
    def from_username(cls, name: str) -> "HeadSpec":
        """Construct a HeadSpec from a player's name alone (this will yield
        the head from the player's current skin)

        Parameters
        ----------
        name : str
            The player's username

        Returns
        -------
        LegacyHeadSpec
            The corresponding head spec
        """
        if not re.match(r"^[A-Za-z0-9_]{3,16}$", name):
            raise ValueError(f"{repr(name)} is not a valid Minecraft username")
        return cls(name, name)

    def __str__(self):
        return self.to_player_head()

    def __repr__(self):
        representation = f"HeadSpec({repr(self.player_name or self.name)}"
        if self.player_name and self.player_name != self.name:
            representation += f",name={repr(self.name)}"
        if self.comment:
            representation += f",comment={repr(self.comment)}"
        return representation + ")"

    def dumps(self) -> str:
        """Reference serialization method. Feel free to write your own.

        Returns
        -------
        str
            1-3 lines specifying the head spec in a concise and standard format
        """
        if self.comment:
            header: str = self.comment
        else:
            header = self.name
        writeme: list[str] = [header]
        if header != self.name:
            writeme.append(self.name)
        spec = ", ".join(
            (
                f"{key}={repr(value)}"
                for key, value in self._asdict().items()
                if key not in ("name", "comment") and value
            )
        )
        if spec:
            writeme.append(spec)
        return "\n".join(writeme)

    def to_player_head(self, pack_format: int = 48) -> str:
        """Generate the player head specification for use in commands and

        Parameters
        ----------
        pack_format : int, optional
            The data pack version
            (see: https://minecraft.wiki/w/Data_pack#Pack_format).
            Default is 48 for Minecraft 1.21

        Returns
        -------
        str
            The properly composited head specification, such that the command
            `/give @s minecraft:player_head[head_spec]` (where `head_spec` is the
            string returned by this method) should give you the desired head
            in modern versions of the game (see note)

        Notes
        -----
        - The proper `/give` command syntax for Minecraft versions before 1.20.5
          (`pack_format < 41`) is `/give @s minecraft_player_head{head_spec}`
          (where `head_spec` is the string returned by this method when using the
          corresponding `pack_format`)
        - This head specification should work in data packs as well for
          `pack_format < 41`, but for modern versions of the game,
          `HeadSpec.to_component_dict()` is the method to generate the
          specification for use in a trade list.
        """
        if pack_format >= 41:
            return self._to_v41()
        if pack_format >= 15:
            return self._to_v15()
        if pack_format >= 4:
            return self._to_v4()
        raise NotImplementedError(f"Data pack version {pack_format} is not supported.")

    def to_component_dict(self) -> str:
        """Generate the player head specification for use in trade lists for
        modern versions of the game (Minecraft 1.21 and above)

        Returns
        -------
        str
            The properly composited head specification suitable for including
            in the `components` field of a data pack trade list

        Notes
        -----
        This method is only meant for modern versions of the game (pack format
        41 and above). For older datapacks, use
        `HeadSpec.to_player_head(pack_format=desired_pack_format)`
        """
        head_spec = self.to_player_head()
        for component in (
            "item_name",
            "profile",
            "properties",
            "rarity",
            "note_block_sound",
        ):
            head_spec = head_spec.replace(
                f"minecraft:{component}=", f'"minecraft:{component}":'
            )
        return head_spec

    def _to_v41(self) -> str:
        components: list[str] = [
            "minecraft:item_name='"
            + _format_text(
                self.name,
                color=self.color,
                italic=self.italic,
                bold=self.bold,
                underlined=self.underlined,
                strikethrough=self.strikethrough,
                obfuscated=self.obfuscated,
            ).replace("'", r"\'")
            + "'"
        ]
        if profile_spec := _format_profile_v41(self.player_name, self.texture):
            components.append(f"minecraft:profile={profile_spec}")
        if self.rarity:
            components.append(f'minecraft:rarity="{self.rarity}"')
        if self.note_block_sound:
            components.append(f'minecraft:note_block_sound="{self.note_block_sound}"')

        # TODO
        # if self.lore:
        #     components.append(
        #         "minecraft:lore=[{lore}]".format(
        #             lore=", ".join(
        #                 (_format_text(**lore_line) for lore_line in self.lore)
        #             )
        #         )
        #     )
        return ", ".join(components)

    def _to_v15(self) -> str:
        head_str = self._to_v4()
        if self.note_block_sound:
            head_str += (
                ', BlockEntityTag:{note_block_sound:"' + self.note_block_sound + '"}'
            )
        return head_str

    def _to_v4(self) -> str:
        if self.rarity and not self.color:
            try:
                color: str | None = dict(_RARITY_COLORS)[self.rarity]
            except KeyError as no_such_rarity:
                raise ValueError(
                    f"HeadSpec has invalid rarity: {self.rarity}"
                ) from no_such_rarity
        else:
            color = self.color

        components: list[str] = [
            (
                'display:{Name:"'
                + _format_text(
                    self.name,
                    color=color,
                    italic=self.italic,
                    bold=self.bold,
                    underlined=self.underlined,
                    strikethrough=self.strikethrough,
                    obfuscated=self.obfuscated,
                ).replace('"', r"\"")
                + '"}'
            )
        ]
        if profile_spec := _format_profile_v4(self.player_name, self.texture):
            components.append(f"SkullOwner:{profile_spec}")

        return ", ".join(components)


def dumps(heads: Iterable[HeadSpec]) -> str:
    """Serialize a list of HeadSpecs so they can be written to file

    Parameters
    ----------
    heads : list of LegacyHeadSpec
        The heads to serialize

    Returns
    -------
    str
        A series of 1-3-line sections, separated by blank lines, that specify
        each head in a concise and standard format
    """
    return "\n\n".join([head.dumps() for head in heads])


def loads(head_list: str | bytes) -> list[HeadSpec]:
    """Deserialize a list of HeadSpecs written by `dumps()`

    Parameters
    ----------
    head_list : str
        The serialized head specs, consisting of a series of 1-3-line sections,
        delimited by blank lines, as generated by `dumps()`

    Returns
    -------
    list of HeadSpec
        The deserialized head specs
    """
    if isinstance(head_list, bytes):
        head_list = head_list.decode("utf-8")
    heads: list[HeadSpec] = []
    for head in head_list.split("\n\n"):
        lines = head.splitlines()
        if len(lines) == 1:
            heads.append(HeadSpec.from_username(lines[0]))
        else:
            to_eval = f"name={repr(lines[-2])}, {lines[-1]}"
            if len(lines) == 3:
                to_eval += f", comment={repr(lines[0])}"
            heads.append(HeadSpec(**eval(f"dict({to_eval})")))
    return heads


def _format_text(text: str, **formatters) -> str:
    text_spec = ""
    for formatter, value in formatters.items():
        if not value:
            continue
        text_spec += '"{fmt}": {val}, '.format(
            fmt=formatter, val="true" if value is True else f'"{value}"'
        )
    if not text_spec:
        return f'"{text}"'
    return '{"text":"' + text + '", ' + text_spec[:-2] + "}"


def _format_profile_v41(player_name: str | None, texture: str | None) -> str:
    # note: there's really probably not much sense in including both components,
    # but since it works, why not?
    profile_spec_components: list[str] = []
    if player_name:
        profile_spec_components.append(f'"name":"{player_name}"')
    if texture:
        profile_spec_components.append(
            '"properties":[{"name":"textures", "value":"' + texture + '"}]'
        )
    if not profile_spec_components:
        return ""
    return "{" + ", ".join(profile_spec_components) + "}"


def _format_profile_v4(player_name: str | None, texture: str | None) -> str:
    if texture:
        return '{Properties:{textures:[{Value:"' + texture + '"}]}'
    if player_name:
        return player_name
    return ""
