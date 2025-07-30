

class BaseMarker:
    """Base class for all markers"""
    def __init__(self, key: str, label: str, position:dict):
        self.key = key
        self.label = label
        self.position = position

    @staticmethod
    def _from_response(response: tuple):
        raise NotImplementedError

