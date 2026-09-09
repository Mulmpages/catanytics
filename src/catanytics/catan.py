from catanytics.data import Data_Player, Resource


class Catan:
    def __init__(self, path : str | None = None):
        # Turn -1  :    Player Selection
        # Turn  0  :    No dice throw; Initial Settlement Placement
        # Turn  1+ :    Dice Throw; Resource Distribution
        self.turn : int = -1

        self.players : list[str] = []
        self.winner : str = None
        # self.history = []

        self.dice        : list[int]                    = []
        self.settlements : list[dict[str, Data_Player]] = []
        self.robber      : list[dict[str, Data_Player]] = []

        # DANGER: Only temporary use, vulnerable to ACE
        if path is not None:
            with open(path, "r") as file:
                lines = file.readlines()
                self.turn        = eval(lines[0])
                self.players     = eval(lines[1])
                self.winner      = eval(lines[2])
                self.dice        = eval(lines[3])
                self.settlements = eval(lines[4])
                self.robber      = eval(lines[5])

    def __repr__(self) -> str:
        return f"{self.turn}\n{self.players}\n{self.winner}\n{self.dice}\n{self.settlements}\n{self.robber}"

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

    def player(self) -> str:
        return self.players[(self.turn - 1) % len(self.players)]

    # Access Game Information for Analysis
    def get_dice(self, turn : int) -> int:
        return self.dice[turn]

    def get_settlements(self, player : str, turn : int, dice : int, resource : Resource) -> int:
        return self.settlements[turn][player][dice][resource]

    def get_robber(self, player : str, turn : int, dice : int, resource : Resource) -> int:
        return self.robber[turn][player][dice][resource]

    def get_production(self, player : str, turn : int, dice : int, resource : Resource) -> int:
        return self.production[turn][player][dice][resource]

    # Change Game Information
    def set_dice(self, dice : int) -> None:
        self.dice[self.turn] = dice

    def add_settlement(self, player : str, resources : Data_Player) -> None:
        for dice in resources:
            for resource in resources[dice]:
                self.settlements[self.turn][player][dice][resource] += resources[dice][resource]

    def set_robber(self, robber : dict[str, Data_Player]) -> None:
        self.robber[self.turn] = robber

    # Turn -1: Player Selection
    def add_player(self, player : str) -> None:
        self.players.append(player)

    def remove_player(self, player : str) -> None:
        del self.players[player]

    # Transition to Turn 0: No Dice Throw; Initial Settlement Placement
    def start(self) -> None:
        self.dice.append(None)
        data_player_empty = {p: Data_Player() for p in self.players}
        self.settlements.append(data_player_empty)
        self.robber.append(data_player_empty)
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
    def save(self, path : str) -> None:
        with open(path, "w") as file:
            file.write(repr(self))

    def undo(self) -> None:
        pass