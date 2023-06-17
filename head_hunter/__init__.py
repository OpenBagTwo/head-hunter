"""The Head Hunter package"""
import re
from pathlib import Path
from typing import NamedTuple, Optional

PACK_FOLDER = Path("Head Hunter")


class HeadSpec(NamedTuple):
    """Standard specification of a player head

    Attributes
    ----------
    name : str
        The display name of the head, including any formatting characters
    skull_owner : str
        The skull owner specification (which can be tied to a specific texture)
    spec : str
        The full head spec such that calling
        ```
        /give @s minecraft:player_head{spec}
        ```
        will give you that head
    comment : str or None
        An optional annotation on the head spec (that will only be used
        internally) for referencing, for example, a particular head variant
    """

    name: str
    skull_owner: str

    @property
    def spec(self):
        return r'display:{Name:"{\"text\":\"' + self.name + r'\"}"},' + self.skull_owner

    comment: Optional[str] = None

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
        HeadSpec
            The corresponding head spec
        """
        return cls(name, name)

    def __str__(self):
        return self.spec

    def __repr__(self):
        sans_formatting = re.sub(r'\\?"|\xA7.|}', "", self.name)
        representation = f"HeadSpec({sans_formatting}"
        if self.comment:
            representation += f",comment={self.comment}"
        return representation + ")"
