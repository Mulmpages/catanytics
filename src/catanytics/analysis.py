from catanytics.catan import Catan
import matplotlib.pyplot as plt 

class Analysis:
    def __init__(self, catan: Catan):
        self.catan = catan

    def __repr__(self) -> str:
        return f"Analysis of\n{self.catan}"

    @staticmethod
    def P(dice):
        if dice < 8:
            prob = (dice - 1) / 36
        else:
            prob = (13 - dice) / 36
        return prob
    
    def E(self, func, player, turn, resource):
        exp = 0
        for dice in range(2, 13):
            prob = Analysis.P(dice)
            exp += prob * func(player, turn, dice, resource)
        return exp

    def C(self, func, player, turn, resource):
        total = 0
        for x in range(1, turn + 1):
            dice = self.catan.get_dice(x)
            total += func(player, x, dice, resource)
        return total

    def EC(self, func, player, turn, resource):
        exp_total = 0
        for x in range(1, turn + 1):
            dice = self.catan.get_dice(x)
            prob = Analysis.P(dice)
            exp_total += prob * func(player, x, dice, resource)
        return exp_total

    def settlements_C(self, player, turn, resource):
        return self.C(self.catan.get_settlements, player, turn, resource)
        
    def robber_C(self, player, turn, resource):
        return self.C(self.catan.get_robber, player, turn, resource)

    def production_C(self, player, turn, resource):
        return self.C(self.catan.get_production, player, turn, resource)

    def settlements_E(self, player, turn, resource):
        return self.E(self.catan.get_settlements, player, turn, resource)

    def robber_E(self, player, turn, resource):
        return self.E(self.catan.get_robber, player, turn, resource)

    def production_E(self, player, turn, resource):
        return self.E(self.catan.get_production, player, turn, resource)

    def settlements_EC(self, player, turn, resource):
        return self.EC(self.catan.get_settlements, player, turn, resource)

    def robber_EC(self, player, turn, resource):
        return self.EC(self.catan.get_robber, player, turn, resource)

    def production_EC(self, player, turn, resource):
        return self.EC(self.catan.get_production, player, turn, resource)

    # Plotting
    def get_data_plot(self, func, player, turn):
        data = []
        for x in range(1, turn):
            data.append(func, player, x)

        return data

    def plot_C_vs_EC(self, objective : str, turn):
        # objective can be "settlements", "robber" or "production"
        func_C = None
        func_EC = None
        match objective:
            case "settlements":
                func_C = self.settlements_C
                func_EC = self.settlements_EC
            case "robber":
                func_C = self.robber_C
                func_EC = self.robber_EC
            case "production":
                func_C = self.production_C
                func_EC = self.production_EC

        dataset_C = {}
        for player in self.catan.players:
            C_data = self.get_data_plot(func_C, player, turn)
            dataset_C[player] = C_data

        dataset_EC = {}
        for player in self.catan.players:
            EC_data = self.get_data_plot(func_EC, player, turn)
            dataset_EC[player] = EC_data

        turns = list(range(1, turn + 1))

        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

        fig, ax = plt.subplots()

        for i, y in enumerate(dataset_C):
            color_player = colors[i % len(colors)]
            x = turns
            ax.plot(x, y, marker="o", linestyle="-", color=color_player, label=f"{i} cumulative")

        for i, y in enumerate(dataset_EC):
            color_player = colors[i % len(colors)]
            x = turns
            ax.plot(x, y, marker="o", linestyle="--", color=color_player, label=f"{i} expected cumulative")

        ax.legend()
        plt.show()
