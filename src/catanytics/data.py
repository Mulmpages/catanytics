from enum import Enum, auto


class Resource(Enum):
    WOOL   = auto()
    GRAIN  = auto()
    LUMBER = auto()
    BRICK  = auto()
    ORE    = auto()

    def __repr__(self) -> str:
        # Example Output: 'W'
        match self:
            case Resource.WOOL:     return "W"
            case Resource.GRAIN:    return "G"
            case Resource.LUMBER:   return "L"
            case Resource.BRICK:    return "B"
            case Resource.ORE:      return "O"

    __str__ = __repr__

    @staticmethod
    def read(string : str) -> Resource:
        # Example Input: 'W'
        string = string.strip()
        match string.upper():
            case "W": return Resource.WOOL
            case "G": return Resource.GRAIN
            case "L": return Resource.LUMBER
            case "B": return Resource.BRICK
            case "O": return Resource.ORE
            case _: return None


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

    def __repr__(self) -> str:
        # Example Output: 'W W L'
        string = ""
        for (k, num) in self.items():
            for i in range(num):
                string += f"{k} "
        return string.strip()

    @staticmethod
    def read(string : str) -> Data_Resource:
        # Example Input: 'w W L'
        string = string.strip()
        if string is None or string == "":
            return Data_Resource()
        obj = Data_Resource()
        tokens = string.split(" ")
        for t in tokens:
            resource = Resource.read(t)
            obj[resource] += 1
        return obj


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

    def __repr__(self):
        # Example Output: 'W2 W5 L12'
        string = ""
        for dice in Data_Player.KEYS:
            for resource in Data_Resource.KEYS:
                if self[dice][resource] != 0:
                    string += f"{resource}{dice} "
        return string.strip()

    @staticmethod
    def read(string : str) -> Data_Player:
        # Example Input: 'W2 W5 L12'
        string = string.strip()
        if string is None or string == "":
            return Data_Player()
        tokens = string.split(" ")
        obj = Data_Player()
        for t in tokens:
            resource = Data_Resource.read(t[0])
            dice = int(t[1:])
            obj[dice] += resource
        return obj
