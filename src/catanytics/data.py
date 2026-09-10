from enum import Enum, auto


class Resource(Enum):
    WOOL   = auto()
    GRAIN  = auto()
    LUMBER = auto()
    BRICK  = auto()
    ORE    = auto()

    @staticmethod
    def from_token(token : str) -> Resource:
        # Example tokens: 'w', 'W'
        match token.upper():
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

    @staticmethod
    def from_token(token : str) -> Data_Resource:
        # Example tokens: 'w', 'W'
        resource = Resource.from_token(token)
        if resource is None:
            return None
        data_resource = Data_Resource()
        data_resource[resource] = 1
        return data_resource


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

    @staticmethod
    def from_token(token : str) -> Data_Resource:
        # Example tokens: 'w3', 'W12'
        resource = Resource.from_token(token[0])
        if resource is None:
            return None
        dice = int(token[1:])
        if (dice not in Data_Resource.KEYS):
            return None
        data_player = Data_Player()
        data_player[dice][resource] = 1
        return data_player