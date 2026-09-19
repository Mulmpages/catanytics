import json
from enum import Enum, auto

from catanytics import data, language


class Catan_Error(Exception): ...


class State(Enum):
    SELECTION = auto()
    SETUP = auto()
    ACTIVE = auto()
    FINISHED = auto()

    def __repr__(self) -> str:
        return self.name

    __str__ = __repr__


class Catan:
    def __init__(self):
        # Turn -1  :    Player Selection
        # Turn  0  :    No dice throw; Initial Settlement Placement
        # Turn  1+ :    Dice Throw; Resource Distribution
        self.turn: int = -1
        self.players: list[str] = []
        self.winner: str = None
        self.dice: list[int] = []
        self.settlements: list[dict[str, data.Player]] = []
        self.robber: list[dict[str, data.Player]] = []

    def repr_dict(self) -> dict:
        return {
            "lang": language.get(),
            "turn": self.turn,
            "players": self.players,
            "winner": self.winner,
            "dice": self.dice,
            "settlements": [
                {p: repr(d) for p, d in s.items()} for s in self.settlements
            ],
            "robber": [{p: repr(d) for p, d in s.items()} for s in self.robber],
        }

    def __repr__(self) -> str:
        return repr(self.repr_dict())

    @staticmethod
    def read(string: str) -> Catan:
        loaded = json.loads(string)
        catan = Catan()
        language.set(loaded["lang"])
        catan.turn = loaded["turn"]
        catan.players = loaded["players"]
        catan.winner = loaded["winner"]
        catan.dice = loaded["dice"]
        catan.settlements = [
            {p: data.Player.read(s) for p, s in t.items()}
            for t in loaded["settlements"]
        ]
        catan.robber = [
            {p: data.Player.read(s) for p, s in t.items()} for t in loaded["robber"]
        ]

    # Access Game Information
    def get_turn(self) -> int:
        return self.turn

    def get_players(self) -> list[str]:
        return self.players

    def get_player(self) -> str:
        if self.turn < 1:
            return None
        else:
            players = self.get_players()
            index = (self.turn - 1) % len(players)
            return players[index]

    def get_state(self) -> State:
        if self.get_turn() == -1:
            return State.SELECTION
        if self.get_turn() == 0:
            return State.SETUP
        if self.winner != None:
            return State.FINISHED
        return State.ACTIVE

    # Access Game Information for Analysis
    def get_dice(self, turn: int | None = None) -> int:
        if turn == None:
            turn = self.get_turn()
        if turn < 1:
            return None
        return self.dice[turn]

    def get_settlements(
        self,
        player: str,
        turn: int | None = None,
        dice: int | None = None,
        resource: data.Resource | None = None,
    ) -> int:
        if turn == None:
            turn = self.get_turn()
        if turn < 0:
            return 0
        if dice == None and resource == None:
            return int(self.settlements[turn][player])
        if dice == None:
            data_player = self.settlements[turn][player]
            return sum([data_dice[resource] for data_dice in data_player.values()])
        if resource == None:
            return int(self.settlements[turn][player][dice])
        return self.settlements[turn][player][dice][resource]

    def get_robber(
        self,
        player: str,
        turn: int | None = None,
        dice: int | None = None,
        resource: data.Resource | None = None,
    ) -> int:
        if turn == None:
            turn = self.get_turn()
        if turn < 0:
            return 0
        if dice == None and resource == None:
            return int(self.robber[turn][player])
        if dice == None:
            data_player = self.robber[turn][player]
            return sum([data_dice[resource] for data_dice in data_player.values()])
        if resource == None:
            return int(self.robber[turn][player][dice])
        return self.robber[turn][player][dice][resource]

    def get_production(
        self,
        player: str,
        turn: int | None = None,
        dice: int | None = None,
        resource: data.Resource | None = None,
    ) -> int:
        settlements = self.get_settlements(player, turn, dice, resource)
        robber = self.get_robber(player, turn, dice, resource)
        return settlements - robber

    # Change Game Information
    def set_dice(self, dice: int) -> None:
        self.check("Game is not ACTIVE", State.ACTIVE)
        self.dice[self.get_turn()] = dice

    def add_settlement(self, player: str, resources: data.Player) -> None:
        self.check("Game is not SETUP/ACTIVE", State.SETUP, State.ACTIVE)
        self.settlements[self.get_turn()][player] += resources

    def add_robber(self, player: str, resources: data.Player) -> None:
        self.check("Game is not SETUP/ACTIVE", State.SETUP, State.ACTIVE)
        self.robber[self.get_turn()][player] += resources

    def remove_robber(self) -> None:
        self.check("Game is not SETUP/ACTIVE", State.SETUP, State.ACTIVE)
        self.robber[self.get_turn()] = self.empty_data_player()

    # Turn -1: Player Selection
    def add_player(self, player: str) -> None:
        self.check("Game is not SELECTION", State.SELECTION)
        self.players.append(player)

    def remove_player(self, player: str) -> None:
        self.check("Game is not SELECTION", State.SELECTION)
        index = self.players.index(player)
        del self.players[index]

    # Transition to Turn 0: No Dice Throw; Initial Settlement Placement
    def start(self) -> None:
        self.check("Game is not SELECTION", State.SELECTION)
        self.dice.append(None)
        self.settlements.append(self.empty_data_player())
        self.robber.append(self.empty_data_player())
        self.turn = 0

    # Transition to Turn 1+: Dice Throw; Resource Distribution
    def next_turn(self) -> None:
        self.check("Game is not SETUP/ACTIVE", State.SETUP, State.ACTIVE)
        self.dice.append(None)
        self.settlements.append(self.settlements[self.turn])
        self.robber.append(self.robber[self.turn])
        self.turn += 1

    # Transition to Finished: Winner is known, Game ends
    def finish(self, winner: str) -> None:
        self.check("Game is not ACTIVE", State.ACTIVE)
        self.winner = winner

    # Utility
    def empty_data_player(self) -> dict[str, data.Player]:
        return {p: data.Player() for p in self.get_players()}

    def check(self, message: str, *states: tuple[State]) -> None:
        for state in states:
            if self.get_state() == state:
                return
        raise Catan_Error(message)

    def save(self, path: str) -> None:
        with open(path, "w") as file:
            json.dump(self.repr_dict(), file, indent=2)

    @staticmethod
    def load(path: str) -> Catan:
        with open(path, "r") as file:
            return Catan.read(file.read())

    def undo(self) -> None:
        raise Catan_Error("Undo is not implemented")
