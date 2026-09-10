from enum import Enum, auto


class Resource(Enum):
    WOOL =   auto()
    GRAIN =  auto()
    LUMBER = auto()
    BRICK =  auto()
    ORE =    auto()

class Data_Resource(dict):
    KEYS = Resource

    def __init__(self):
        super().__init__()
        for key in Data_Resource.KEYS:
            self[key] = 0

    def __eq__(self, other):
        for key in Data_Resource.KEYS:
            if self[key] != other[key]:
                return False
        return True

    def __int__(self):
        return sum(self.values())

    def __add__(self, other):
        result = Data_Resource()
        for key in Data_Resource.KEYS:
            result[key] = self[key] + other[key]
        return result
    
    __radd__ = __add__

    def __sub__(self, other):
        result = Data_Resource()
        for key in Data_Resource.KEYS:
            result[key] = self[key] - other[key]
        return result


class Data_Player(dict):
    KEYS = range(2, 13)

    def __init__(self):
        super().__init__()
        for key in Data_Player.KEYS:
            self[key] = Data_Resource()

    def __eq__(self, other):
        for key in Data_Player.KEYS:
            if self[key] != other[key]:
                return False
        return True

    def __abs__(self):
        return sum(int(self.values()))

    def __add__(self, other):
        result = Data_Player()
        for key in Data_Player.KEYS:
            result[key] = self[key] + other[key]
        return result
    
    __radd__ = __add__

    def __sub__(self, other):
        result = Data_Player()
        for key in Data_Player.KEYS:
            result[key] = self[key] - other[key]
        return result
