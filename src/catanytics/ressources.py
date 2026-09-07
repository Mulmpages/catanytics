from enum import Enum


class Ressources(Enum):
    WOOL = 1
    GRAIN = 2
    LUMBER = 3
    BRICK = 4
    ORE = 5

    @staticmethod
    def empty():
        return {r: 0 for r in Ressources}
