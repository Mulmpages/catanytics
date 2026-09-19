from enum import Enum, auto
from typing import ClassVar

from catanytics import language


class Resource(Enum):
    WOOL = auto()
    GRAIN = auto()
    LUMBER = auto()
    BRICK = auto()
    ORE = auto()

    def long_name(self) -> str:
        # Example Output: 'Wood'
        if language.get() == "en":
            match self:
                case Resource.WOOL:
                    return "Wool"
                case Resource.GRAIN:
                    return "Grain"
                case Resource.LUMBER:
                    return "Lumber"
                case Resource.BRICK:
                    return "Brick"
                case Resource.ORE:
                    return "Ore"
        # Example Output: 'Holz'
        if language.get() == "de":
            match self:
                case Resource.WOOL:
                    return "Schaf"
                case Resource.GRAIN:
                    return "Weizen"
                case Resource.LUMBER:
                    return "Holz"
                case Resource.BRICK:
                    return "Lehm"
                case Resource.ORE:
                    return "Erz"

    def __repr__(self) -> str:
        # Example Output: 'W'
        # Example Output: 'H'
        return self.long_name()[0]

    __str__ = __repr__

    @staticmethod
    def read(string: str) -> Resource:
        # Example Input: 'W'
        string = string.strip()
        if language.get() == "en":
            match string.upper():
                case "W":
                    return Resource.WOOL
                case "G":
                    return Resource.GRAIN
                case "L":
                    return Resource.LUMBER
                case "B":
                    return Resource.BRICK
                case "O":
                    return Resource.ORE
        # Example Input: 'H'
        if language.get() == "de":
            match string.upper():
                case "S":
                    return Resource.WOOL
                case "W":
                    return Resource.GRAIN
                case "H":
                    return Resource.LUMBER
                case "L":
                    return Resource.BRICK
                case "E":
                    return Resource.ORE


class Resources(dict):
    KEYS: ClassVar = Resource

    def __init__(self):
        super().__init__()
        for key in Resources.KEYS:
            self[key] = 0

    def __eq__(self, other):
        for key in Resources.KEYS:
            if self[key] != other[key]:
                return False
        return True

    def __int__(self) -> int:
        return sum(self.values())

    def __add__(self, other):
        result = Resources()
        for key in Resources.KEYS:
            result[key] = self[key] + other[key]
        return result

    __radd__ = __add__

    def __sub__(self, other):
        result = Resources()
        for key in Resources.KEYS:
            result[key] = self[key] - other[key]
        return result

    def __repr__(self) -> str:
        # Example Output: 'WWL'
        string = ""
        for k, num in self.items():
            for _ in range(num):
                string += f"{k}"
        return string

    @staticmethod
    def read(string: str) -> Resources:
        # Example Input: 'WWL'
        if string is None or string == "":
            return Resources()
        string = string.strip()
        obj = Resources()
        for token in string:
            resource = Resource.read(token)
            obj[resource] += 1
        return obj


class Player(dict):
    KEYS: ClassVar = range(2, 13)

    def __init__(self):
        super().__init__()
        for key in Player.KEYS:
            self[key] = Resources()

    def __eq__(self, other):
        for key in Player.KEYS:
            if self[key] != other[key]:
                return False
        return True

    def __int__(self) -> int:
        return sum([int(d) for d in self.values()])

    def __add__(self, other):
        result = Player()
        for key in Player.KEYS:
            result[key] = self[key] + other[key]
        return result

    __radd__ = __add__

    def __sub__(self, other):
        result = Player()
        for key in Player.KEYS:
            result[key] = self[key] - other[key]
        return result

    def __repr__(self):
        # Example Output: '2WWL 5L 12B'
        string = ""
        for dice in Player.KEYS:
            resources = self[dice]
            if int(resources) != 0:
                string += f"{dice}{resources} "
        return string.strip()

    @staticmethod
    def read(string: str) -> Player:
        # Example Input: '2WWL 5L 12B'
        if string is None or string == "":
            return Player()
        string = string.strip()
        tokens = string.split(" ")
        obj = Player()
        for t in tokens:
            dice, resources = None, None
            for k in reversed(Player.KEYS):
                if str(k) in t:
                    dice = k
                    resources = Resources.read(t.removeprefix(str(k)))
                    break
            obj[dice] += resources
        return obj
