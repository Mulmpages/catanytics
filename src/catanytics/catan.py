"""Data model for recording a game of Catan and querying its production."""

import json
from copy import deepcopy
from enum import Enum, auto
from typing import ClassVar


class Catan_Error(Exception):
    """Raised for invalid input or actions that the current game state forbids."""


class Lang(Enum):
    """Language used for resource names and abbreviations."""

    EN = auto()
    DE = auto()

    def __repr__(self) -> str:
        return self.name

    __str__ = __repr__

    @staticmethod
    def read(string: str) -> Lang:
        """Parse a language code such as "EN" or "de" (case-insensitive).

        Raises:
            Catan_Error: If the code is unknown.
        """
        if string is None or string == "":
            raise Catan_Error("Name unknown")
        string = string.strip()
        for lang in Lang:
            if string.casefold() == lang.name.casefold():
                return lang
        raise Catan_Error("Name unknown")


class State(Enum):
    """Phase of a game, as returned by `Catan.get_state()`.

    - SELECTION: Players are being added; the game has not started.
    - ACTIVE: The game is running; settlements, robber and dice can be entered.
    - FINISHED: A winner has been declared; the game can no longer change.
    """

    SELECTION = auto()
    ACTIVE = auto()
    FINISHED = auto()

    def __repr__(self) -> str:
        return self.name

    __str__ = __repr__


class Stat(Enum):
    """Statistic to query with `Catan.get_stats()`."""

    SETTLEMENTS = auto()
    ROBBER = auto()
    PRODUCTION = auto()

    def __repr__(self) -> str:
        return self.name

    __str__ = __repr__


class Resource(Enum):
    """One of the five resource types."""

    WOOL = auto()
    GRAIN = auto()
    LUMBER = auto()
    BRICK = auto()
    ORE = auto()

    @staticmethod
    def _names() -> dict[Lang, dict[Resource, str]]:
        return {
            Lang.EN: {
                Resource.WOOL: "Wool",
                Resource.GRAIN: "Grain",
                Resource.LUMBER: "Lumber",
                Resource.BRICK: "Brick",
                Resource.ORE: "Ore",
            },
            Lang.DE: {
                Resource.WOOL: "Schaf",
                Resource.GRAIN: "Weizen",
                Resource.LUMBER: "Holz",
                Resource.BRICK: "Lehm",
                Resource.ORE: "Erz",
            },
        }

    def repr_long(self, lang: Lang = Lang.EN) -> str:
        """Return the full name, e.g. "Wool" (EN) or "Schaf" (DE) for WOOL."""
        if lang in Resource._names():
            return Resource._names()[lang][self]
        raise Catan_Error("Language unknown")

    def repr(self, lang: Lang = Lang.EN) -> str:
        """Return the one-letter abbreviation, e.g. "W" (EN) or "S" (DE) for WOOL."""
        return self.repr_long(lang)[0]

    def __repr__(self) -> str:
        return self.repr()

    __str__ = __repr__

    @staticmethod
    def read(string: str, lang: Lang = Lang.EN) -> Resource:
        """Parse a full name or one-letter abbreviation (case-insensitive).

        Example for WOOL: "Wool" or "W" in EN, "Schaf" or "S" in DE.

        Raises:
            Catan_Error: If the name is unknown in `lang`.
        """
        if string is None or string == "":
            raise Catan_Error("Name unknown")
        string = string.strip()
        if lang in Resource._names():
            for k, v in Resource._names()[lang].items():
                if string.casefold() == v.casefold():
                    return Resource(k)
                if len(string) == 1 and string.casefold()[0] == v.casefold()[0]:
                    return Resource(k)
            raise Catan_Error("Name unknown")
        raise Catan_Error("Language unknown")


class Resources(dict[Resource, int]):
    """Count per resource type; every resource is always present as a key.

    Supports `+` and `-` element-wise; `-` raises Catan_Error if a count would
    become negative. `int(resources)` is the total count.
    """

    _KEYS: ClassVar = Resource

    def __init__(self):
        super().__init__()
        for key in Resources._KEYS:
            self[key] = 0

    def __eq__(self, other):
        for key in Resources._KEYS:
            if self[key] != other[key]:
                return False
        return True

    def __int__(self) -> int:
        return sum(self.values())

    def __add__(self, other):
        result = Resources()
        for key in Resources._KEYS:
            result[key] = self[key] + other[key]
        return result

    def __sub__(self, other):
        result = Resources()
        for key in Resources._KEYS:
            result[key] = self[key] - other[key]
            if result[key] < 0:
                raise Catan_Error("Values may not be negative")
        return result

    def repr(self, lang: Lang = Lang.EN) -> str:
        """Return the counts as abbreviations, e.g. "WWL" for 2 wool and 1 lumber."""
        string = ""
        for k, num in self.items():
            for _ in range(num):
                string += f"{k.repr(lang)}"
        return string

    def __repr__(self) -> str:
        return self.repr()

    __str__ = __repr__

    @staticmethod
    def read(string: str, lang: Lang = Lang.EN) -> Resources:
        """Parse abbreviations such as "WWL"; an empty string gives no resources.

        Raises:
            Catan_Error: If a letter is not a resource in `lang`.
        """
        if string is None or string == "":
            return Resources()
        string = string.strip()
        obj = Resources()
        for token in string:
            resource = Resource.read(token, lang)
            obj[resource] += 1
        return obj


class Player(dict[int, Resources]):
    """Resources one player receives per dice number (2-12).

    Used both for a player's settlements and for what the robber blocks.
    Supports `+` and `-` per dice number; `int(player)` is the total count.
    """

    _KEYS: ClassVar = range(2, 13)

    def __init__(self):
        super().__init__()
        for key in Player._KEYS:
            self[key] = Resources()

    def __eq__(self, other):
        for key in Player._KEYS:
            if self[key] != other[key]:
                return False
        return True

    def __int__(self) -> int:
        return sum([int(d) for d in self.values()])

    def __add__(self, other):
        result = Player()
        for key in Player._KEYS:
            result[key] = self[key] + other[key]
        return result

    def __sub__(self, other):
        result = Player()
        for key in Player._KEYS:
            result[key] = self[key] - other[key]
        return result

    def repr(self, lang: Lang = Lang.EN):
        """Return e.g. "2WWL 5L 12B": dice number followed by its resources."""
        string = ""
        for dice in Player._KEYS:
            resources = self[dice]
            if int(resources) != 0:
                string += f"{dice}{resources.repr(lang)} "
        return string.strip()

    def __repr__(self) -> str:
        return self.repr()

    __str__ = __repr__

    @staticmethod
    def read(string: str, lang: Lang) -> Player:
        """Parse the format of `repr()`, e.g. "2WWL 5L 12B".

        A dice number may appear more than once; its resources are added up.

        Raises:
            Catan_Error: If a token does not start with 2-12 or contains an
                unknown resource letter.
        """
        if string is None or string == "":
            return Player()
        string = string.strip()
        tokens = string.split()
        obj = Player()
        for t in tokens:
            dice, resources = None, None
            for k in reversed(Player._KEYS):
                if t.startswith(str(k)):
                    dice = k
                    remainder = t.removeprefix(str(k))
                    resources = Resources.read(remainder, lang)
                    break
            else:
                raise Catan_Error("Dice rolls must be in range 2-12")
            obj[dice] += resources
        return obj


class Catan:
    """One recorded game of Catan.

    The game is divided into turns by the dice rolls. Turn i covers everything
    that happens before roll i, so turn 0 is the initial settlement placement.
    `get_dice(i)` and the board queries with `turn=i` therefore belong
    together: roll i produced `get_production(player, i, get_dice(i))`.
    The current turn has no roll yet. Before `start()`, the turn is -1.
    """

    def __init__(self, lang: Lang = Lang.EN):
        """Create an empty game in state SELECTION."""
        self._lang: Lang = lang
        self._turn: int = -1
        self._players: list[str] = []
        self._winner: str = None
        self._dice: list[int] = []
        self._settlements: list[dict[str, Player]] = []
        self._robber: list[dict[str, Player]] = []

    def _repr_dict(self) -> dict:
        return {
            "lang": repr(self._lang),
            "turn": self._turn,
            "players": self._players,
            "winner": self._winner,
            "dice": self._dice,
            "settlements": [
                {p: d.repr(self._lang) for p, d in s.items()}
                for s in self._settlements
            ],
            "robber": [
                {p: d.repr(self._lang) for p, d in s.items()} for s in self._robber
            ],
        }

    def __repr__(self) -> str:
        return repr(self._repr_dict())

    __str__ = __repr__

    @staticmethod
    def read(string: str) -> Catan:
        """Create a game from the JSON text written by `save()`."""
        loaded = json.loads(string)
        catan = Catan()
        lang = Lang.read(loaded["lang"])
        catan._lang = lang
        catan._turn = loaded["turn"]
        catan._players = loaded["players"]
        catan._winner = loaded["winner"]
        catan._dice = loaded["dice"]
        catan._settlements = [
            {p: Player.read(s, lang) for p, s in t.items()}
            for t in loaded["settlements"]
        ]
        catan._robber = [
            {p: Player.read(s, lang) for p, s in t.items()} for t in loaded["robber"]
        ]
        return catan

    # Access Game Information
    def get_lang(self) -> Lang:
        """Return the language used for input and saving."""
        return self._lang

    def get_turn(self) -> int:
        """Return the current turn: -1 before `start()`, then the number of rolls so far."""
        return self._turn

    def get_players(self) -> list[str]:
        """Return the player names in seating order."""
        return self._players

    def get_player(self) -> str:
        """Return the player who rolled last, or None before the first roll."""
        if self.get_turn() < 1:
            return None
        else:
            index = (self.get_turn() - 1) % len(self.get_players())
            return self.get_players()[index]

    def get_winner(self) -> str:
        """Return the winner, or None while the game is not finished."""
        return self._winner

    def get_state(self) -> State:
        """Return the current phase of the game."""
        if self.get_turn() == -1:
            return State.SELECTION
        if self.get_winner() != None:
            return State.FINISHED
        return State.ACTIVE

    # Access Game Information for Analysis
    def get_dice(self, turn: int | None = None) -> int:
        """Return the roll that ended `turn`.

        Args:
            turn: Defaults to the last turn with a roll, not the current one.

        Returns:
            The rolled number, or None if that turn has no roll yet.
        """
        if turn == None:
            turn = self.get_turn() - 1
        if turn < 0:
            return None
        return self._dice[turn]

    def get_settlements(
        self,
        player: str,
        turn: int | None = None,
        dice: int | None = None,
        resource: Resource | None = None,
    ) -> int:
        """Count the resources a player's settlements and cities produce.

        Args:
            player: Name of the player.
            turn: Board at the moment of roll `turn`. Defaults to the current turn.
            dice: Only count tiles with this number. Defaults to all numbers.
            resource: Only count this resource. Defaults to all resources.

        Returns:
            The count, or 0 before the game has started.
        """
        if turn == None:
            turn = self.get_turn()
        if turn < 0:
            return 0
        if dice == None and resource == None:
            return int(self._settlements[turn][player])
        elif dice == None:
            data_player = self._settlements[turn][player]
            return sum([data_dice[resource] for data_dice in data_player.values()])
        elif resource == None:
            return int(self._settlements[turn][player][dice])
        else:
            return self._settlements[turn][player][dice][resource]

    def get_robber(
        self,
        player: str,
        turn: int | None = None,
        dice: int | None = None,
        resource: Resource | None = None,
    ) -> int:
        """Count the resources the robber blocks for a player.

        Takes the same arguments as `get_settlements()`.
        """
        if turn == None:
            turn = self.get_turn()
        if turn < 0:
            return 0
        if dice == None and resource == None:
            return int(self._robber[turn][player])
        elif dice == None:
            data_player = self._robber[turn][player]
            return sum([data_dice[resource] for data_dice in data_player.values()])
        elif resource == None:
            return int(self._robber[turn][player][dice])
        else:
            return self._robber[turn][player][dice][resource]

    def get_production(
        self,
        player: str,
        turn: int | None = None,
        dice: int | None = None,
        resource: Resource | None = None,
    ) -> int:
        """Count what a player actually receives: settlements minus robber.

        Takes the same arguments as `get_settlements()`.
        """
        settlements = self.get_settlements(player, turn, dice, resource)
        robber = self.get_robber(player, turn, dice, resource)
        return settlements - robber

    def get_stats(
        self,
        stat: Stat,
        player: str,
        turn: int | None = None,
        dice: int | None = None,
        resource: Resource | None = None,
    ) -> int:
        """Call `get_settlements()`, `get_robber()` or `get_production()`, chosen by `stat`."""
        match stat:
            case Stat.SETTLEMENTS:
                return self.get_settlements(player, turn, dice, resource)
            case Stat.ROBBER:
                return self.get_robber(player, turn, dice, resource)
            case Stat.PRODUCTION:
                return self.get_production(player, turn, dice, resource)
            case _:
                raise Catan_Error("Statistic unknown")

    # Change Game Information
    def set_lang(self, lang: Lang) -> None:
        """Change the language used for input and saving."""
        self._lang = lang

    def add_settlement(self, player: str, resources: Player) -> None:
        """Add a settlement's resources to a player in the current turn.

        For a city, add the same resources a second time.

        Raises:
            Catan_Error: If the game is not ACTIVE or the player is unknown.
        """
        self._check("Game state is not ACTIVE", State.ACTIVE)
        if player not in self.get_players():
            raise Catan_Error("Player unknown")
        self._settlements[self.get_turn()][player] += resources

    def add_robber(self, player: str, resources: Player) -> None:
        """Add resources the robber blocks for a player in the current turn.

        Raises:
            Catan_Error: If the game is not ACTIVE or the player is unknown.
        """
        self._check("Game state is not ACTIVE", State.ACTIVE)
        if player not in self.get_players():
            raise Catan_Error("Player unknown")
        self._robber[self.get_turn()][player] += resources

    def remove_robber(self) -> None:
        """Clear the blocked resources of all players in the current turn.

        Raises:
            Catan_Error: If the game is not ACTIVE.
        """
        self._check("Game state is not ACTIVE", State.ACTIVE)
        self._robber[self.get_turn()] = self._empty_data()

    def add_player(self, player: str) -> None:
        """Add a player; add them in seating order, starting with the first to roll.

        Raises:
            Catan_Error: If the game has started or the name is taken.
        """
        self._check("Game state is not SELECTION", State.SELECTION)
        if player in self.get_players():
            raise Catan_Error("Player exists already")
        self._players.append(player)

    def remove_player(self, player: str) -> None:
        """Remove a player.

        Raises:
            Catan_Error: If the game has started.
        """
        self._check("Game state is not SELECTION", State.SELECTION)
        if player not in self.get_players():
            return
        index = self._players.index(player)
        del self._players[index]

    def start(self) -> None:
        """Start the game with turn 0, the initial settlement placement.

        Raises:
            Catan_Error: If the game has already started or has no players.
        """
        self._check("Game state is not SELECTION", State.SELECTION)
        if len(self.get_players()) == 0:
            raise Catan_Error("At least one player is needed to start the game")
        self._dice.append(None)
        self._settlements.append(self._empty_data())
        self._robber.append(self._empty_data())
        self._turn = 0

    def next_turn(self, dice: int) -> None:
        """Record a dice roll; it ends the current turn and starts the next one.

        The new turn starts with a copy of the current board.

        Raises:
            Catan_Error: If the game is not ACTIVE.
        """
        self._check("Game state is not ACTIVE", State.ACTIVE)
        if dice not in range(2, 13):
            raise Catan_Error("Dice rolls must be in range 2-12")
        self._dice[self.get_turn()] = dice
        self._dice.append(None)
        settlements_copy = deepcopy(self._settlements[self.get_turn()])
        self._settlements.append(settlements_copy)
        robber_copy = deepcopy(self._robber[self.get_turn()])
        self._robber.append(robber_copy)
        self._turn += 1

    def finish(self, winner: str) -> None:
        """Declare the winner and end the game.

        Raises:
            Catan_Error: If the game is not ACTIVE or the player is unknown.
        """
        self._check("Game state is not ACTIVE", State.ACTIVE)
        if winner not in self.get_players():
            raise Catan_Error("Player unknown")
        self._winner = winner

    # Utility
    def _empty_data(self) -> dict[str, Player]:
        return {p: Player() for p in self.get_players()}

    def _check(self, message: str, *states: tuple[State]) -> None:
        for state in states:
            if self.get_state() == state:
                return
        raise Catan_Error(message)

    def save(self, path: str = "catan.json") -> None:
        """Write the game as JSON to `path`.

        Raises:
            FileExistsError: If `path` already exists; files are never overwritten.
        """
        with open(path, "x") as file:
            json.dump(self._repr_dict(), file, indent=2)

    @staticmethod
    def load(path: str = "catan.json") -> Catan:
        """Read a game from a JSON file written by `save()`."""
        with open(path, "r") as file:
            return Catan.read(file.read())

    def undo(self) -> None:
        """Not implemented yet; always raises Catan_Error."""
        raise Catan_Error("Undo is not implemented")
