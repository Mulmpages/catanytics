import json

from catanytics.data import Data_Player, Resource


class Catan:
    def __init__(self, path: str | None = None):
        if path is not None:
            with open(path, "r") as file:
                data = json.loads(file.read())
                self.turn        = data["turn"]
                self.players     = data["players"]
                self.winner      = data["winner"]
                self.dice        = data["dice"]
                self.settlements = [{p: Data_Player.read(s) for p, s in t.items()} for t in data["settlements"]]
                self.robber      = [{p: Data_Player.read(s) for p, s in t.items()} for t in data["robber"]]
            return

        # Turn -1  :    Player Selection
        # Turn  0  :    No dice throw; Initial Settlement Placement
        # Turn  1+ :    Dice Throw; Resource Distribution
        self.turn: int = -1

        self.players: list[str] = []
        self.winner: str = None
        # self.history = []

        self.dice: list[int] = []
        self.settlements: list[dict[str, Data_Player]] = []
        self.robber: list[dict[str, Data_Player]] = []

    def repr_dict(self) -> dict:
        return {
            "turn":        self.turn,
            "players":     self.players,
            "winner":      self.winner,
            "dice":        self.dice,
            "settlements": [{p: repr(d) for p, d in s.items()} for s in self.settlements],
            "robber":      [{p: repr(d) for p, d in s.items()} for s in self.robber],
        }

    def __repr__(self) -> str:
        return repr(self.repr_dict())
        # return f"{self.turn}\n{self.players}\n{self.winner}\n{self.dice}\n{self.settlements}\n{self.robber}"

    # Access Game Information
    def is_player_selection(self) -> bool:
        return self.turn == -1

    def is_initial_placement(self) -> bool:
        return self.turn == 0

    def is_finished(self) -> bool:
        return self.winner is not None

    def is_active(self) -> bool:
        return (
            (not self.is_player_selection())
            and (not self.is_initial_placement())
            and (not self.is_finished())
        )

    def get_turn(self) -> int:
        return self.turn

    def player(self) -> str:
        return self.players[(self.turn - 1) % len(self.players)]

    # Access Game Information for Analysis
    def get_dice(self, turn: int) -> int:
        return self.dice[turn]

    def get_settlements(
        self, player: str, turn: int, dice: int, resource: Resource | None = None
    ) -> int:
        if resource is None:
            return int(self.settlements[turn][player][dice])
        else:
            return self.settlements[turn][player][dice][resource]

    def get_robber(
        self, player: str, turn: int, dice: int, resource: Resource | None = None
    ) -> int:
        if resource is None:
            return int(self.robber[turn][player][dice])
        else:
            return self.robber[turn][player][dice][resource]

    def get_production(
        self, player: str, turn: int, dice: int, resource: Resource | None = None
    ) -> int:
        if resource is None:
            settlements = int(self.get_settlements(player, turn, dice, resource))
            robber = int(self.get_robber(player, turn, dice, resource))
            return settlements - robber
        else:
            settlements = self.get_settlements(player, turn, dice, resource)
            robber = self.get_robber(player, turn, dice, resource)
            return settlements - robber

    # Change Game Information
    def set_dice(self, dice: int) -> None:
        self.dice[self.turn] = dice

    def add_settlement(self, player: str, resources: Data_Player) -> None:
        for dice in resources:
            for resource in resources[dice]:
                self.settlements[self.turn][player][dice][resource] += resources[dice][
                    resource
                ]

    def remove_robber(self) -> None:
        self.robber[self.turn] = self.empty_data_player()

    def set_robber(self, player: str, resources: Data_Player) -> None:
        self.robber[self.turn][player] = resources

    # Turn -1: Player Selection
    def add_player(self, player: str) -> None:
        self.players.append(player)

    def remove_player(self, player: str) -> None:
        del self.players[player]

    # Transition to Turn 0: No Dice Throw; Initial Settlement Placement
    def start(self) -> None:
        self.dice.append(None)
        self.settlements.append(self.empty_data_player())
        self.robber.append(self.empty_data_player())
        self.turn = 0

    # Transition to Turn 1+: Dice Throw; Resource Distribution
    def next_turn(self) -> None:
        self.dice.append(None)
        self.settlements.append(self.settlements[self.turn])
        self.robber.append(self.robber[self.turn])
        self.turn += 1

    # Transition to Finished: Winner is known, Game ends
    def finish(self, winner: str) -> None:
        self.winner = winner

    # Utility
    def empty_data_player(self) -> dict[str, Data_Player]:
        return {p: Data_Player() for p in self.players}

    def save(self, path: str) -> None:
        with open(path, "w") as file:
            json.dump(self.repr_dict(), file, indent=2)

    def undo(self) -> None:
        pass
