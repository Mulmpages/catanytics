from catanytics.catan import Catan


class Analysis:
    def __init__(self, catan: Catan):
        self.catan = catan

    def __repr__(self) -> str:
        return f"Analysis of\n{self.catan}"


        
    def settlements_C(self, player, dice, resource, turn):
        expProd = 0
        for x in range(1, turn + 1):
            expProd += self.catan.get_settlements(player, x, dice, resource)
        return expProd

    def robber_C(self, player, dice, resource, turn):
        robber_total = 0
        for x in range(1, turn + 1):
            robber_total += self.catan.get_robber(player, x, dice, resource)    
        return robber_total

    def production_C(self, player, dice, resource, turn):
        prod_total = 0
        for x in range(1, turn + 1):
            prod_total += self.catan.get_production(player, x, dice, resource)
    
        return prod_total
