from catanytics.catan import Catan


class Analysis:
    def __init__(self, catan: Catan):
        self.catan = catan

    def __repr__(self) -> str:
        return f"Analysis of\n{self.catan}"



    def settlements_C(self, player, resource, turn):
        production_total = 0
        for x in range(1, turn + 1):
            dice = self.catan.get_dice(x)
            production_total += self.catan.get_settlements(player, x, dice, resource)
        return production_total
        
    def robber_C(self, player, resource, turn):
        robber_total = 0
        for x in range(1, turn + 1):
            dice = self.catan.get_dice(x)
            robber_total += self.catan.get_robber(player, x, dice, resource)    
        return robber_total

    def production_C(self, player, resource, turn):
        prod_total = 0
        for x in range(1, turn + 1):
            dice = self.catan.get_dice(x)
            prod_total += self.catan.get_production(player, x, dice, resource)
        return prod_total
