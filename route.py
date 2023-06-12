from copy import copy
from cell import Direction
import API

class Route(list[tuple[int, int]]):
    def __init__(self, args : list[tuple[int, int]] | None = None) -> None:
        if (args is not None):
            super().__init__(args)
        else:
            super().__init__()

    def copy(self) -> "Route":
        return copy(self)
    
    
    def __hash__(self) -> int: # type: ignore
        hash = ""
        for i in range(len(self) - 1):
            vector = (self[i + 1][0] - self[i][0], self[i + 1][1] - self[i][1])
            hash += str(Direction.fromVector(vector).value)
        return hash.__hash__()
    
    def getNumberOfTurns(self) -> int:
        turns = 0
        for i in range(len(self) - 2):
            vector1 = (self[i + 1][0] - self[i][0], self[i + 1][1] - self[i][1])
            vector2 = (self[i + 2][0] - self[i + 1][0], self[i + 2][1] - self[i + 1][1])
            if (Direction.fromVector(vector1) != Direction.fromVector(vector2)):
                turns += 1
                API.setColor(self[i + 1][0], self[i + 1][1], "y")
        return turns