from catanytics.catan import Catan


class Analysis:
    def __init__(self, catan: Catan):
        self.catan = catan

    def settlements_C(self, player, dice, resource):
        turn = self.catan.turn
        expProd = 0
        for x in range(1, turn + 1):
            expProd += self.catan.get_settlements(player, x, dice, resource)

        return expProd
