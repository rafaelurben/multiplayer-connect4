"""Player model"""

import typing
import re


class Player:
    everyone: typing.Dict[int, "Player"] = {}

    def __init__(self, name: str, plid: int, hidden: bool = False) -> None:
        self.name: str = name
        self.playerid: int = plid
        self.gameid: int | None = None
        self.is_ready: bool = False

        if not hidden:
            Player.everyone[self.playerid] = self

    @property
    def id(self):
        return self.playerid

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "id": self.playerid,
        }

    def delete(self):
        del Player.everyone[self.playerid]

    @classmethod
    def get(cls, pid: int) -> "Player":
        return cls.everyone.get(pid, invalid)

    @classmethod
    def is_valid_name(cls, name: str) -> bool:
        """Check if a name is valid"""

        # Check for duplicate names
        for player in Player.everyone.values():
            if player.name == name:
                return False

        # Validate name
        if not re.match(r'^[a-zA-Z0-9_\- ]{3,20}$', name):
            return False

        return True


# Special player used when there's a tie
tie = Player("Unentschieden", 0)
# Special player used when a player was not found
invalid = Player("Invalid", 0)

Player.everyone.pop(0)
