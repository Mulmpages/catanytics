from ressources import Ressources


class Catan:
    def __init__(self):
        # Turn -1  :    Player Selection 
        # Turn  0  :    No dice throw; Initial Settlement Placement
        # Turn  1+ :    Dice Throw; Ressource Distribution
        self.turn = -1

        self.players = []
        self.winner = None
        # self.history = []
        
        # Dice Throws are stored as ___[turn] -> int
        # Settlements, Robbers and Production are stored as ___[turn][player][ressource] -> int
        self.dice = []
        self.settlements = []
        self.robber = []
        self.production = []
    
    # Access Game Information
    def is_player_selection(self):
        return self.turn is -1

    def is_initial_placement(self):
        return self.turn is 0

    def is_finished(self):
        return self.winner is not None

    def is_active(self):
        return (
            (not self.is_player_selection()) and
            (not self.is_initial_placement()) and
            (not self.is_finished())
        )

    def get_dice(self, turn):
        return self.dice[turn]

    def get_settlements(self, turn, player, ressource):
        return self.settlements[turn][player][ressource]

    def get_robber(self, turn, player, ressource):
        return self.robber[turn][player][ressource]

    def get_production(self, turn, player, ressource):
        return self.production[turn][player][ressource]

    # Change Game Information
    def set_dice(self, dice):
        self.dice[self.turn] = dice

    def add_settlement(self, player, ressources):
        for r in ressources:
            self.settlements[self.turn][player][r] += ressources[r] # Can maybe remove the [r]?
        self.calc_production()

    def set_robber(self, robber):
        self.robber[self.turn] = robber
        self.calc_production()

    def calc_production(self):
        production = self.empty_turn()
        for p in self.players:
            for r in Ressources:
                production[p][r] = (
                    self.get_settlements(self.turn, p, r)
                    - self.get_robber(self.turn, p, r)
                )
        self.production[self.turn] = production

    # Turn -1: Player Selection
    def add_player(self, player):
        self.players.append(player)

    def remove_player(self, player):
        del self.players[player]

    # Turn 0: No dice throw; Initial Settlement Placement
    def start(self):
        self.dice.append(None)
        self.settlements.append(self.empty_turn())
        self.robber.append(self.empty_turn())
        self.production.append(self.empty_turn())
        self.started = True

    # Turn 1+: Dice Throw; Ressource Distribution
    def next_turn(self):
        self.dice.append(None)
        self.settlements.append(self.settlements[self.turn])
        self.robber.append(self.robber[self.turn])
        self.production.append(self.production[self.turn])
        self.turn += 1

    # Finished: Winner is known
    def finish(self, winner):
        self.winner = winner

    # Utility
    def empty_turn(self):
        return {p: Ressources.empty() for p in self.players}

    def undo(self):
        pass