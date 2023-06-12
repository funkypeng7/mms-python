from enum import Enum
from tools import log

class MouseDirection(Enum):
    LEFT = -1
    FORWARD = 0
    RIGHT = 1
    BACKWARD = 2

class Direction(Enum):
    WEST = 0
    NORTH = 1
    EAST = 2
    SOUTH = 3

    @staticmethod
    def fromMouseDirection(mouseDirection : "Direction", relativeDirection : "MouseDirection") -> "Direction":
        return Direction((mouseDirection.value + relativeDirection.value) % 4)

    @staticmethod
    def fromVector(vector : tuple[int, int]) -> "Direction":
        match (vector):
            case (-1, 0):
                return Direction.WEST
            case (0, 1):
                return Direction.NORTH
            case (1, 0):
                return Direction.EAST
            case (0, -1):
                return Direction.SOUTH
            case _:
                raise Exception("Invalid vector")
        
    
    def turnsTo(self, turnTo : "Direction") -> list["MouseDirection"]:
        if (self.value != turnTo.value):
            log(f"Turning from {self.name} to {turnTo.name}")

        match (turnTo.value - self.value):
            case 0:
                return []
            case -1 | 3:
                return [MouseDirection.LEFT]
            case -2 | 2:
                return [MouseDirection.LEFT, MouseDirection.LEFT]
            case -3 | 1:
                return [MouseDirection.RIGHT]
            case _:
                raise Exception("Invalid turnTo")
            
    

    @property
    def vector(self) -> tuple[int, int]:
        match (self.value):
            case Direction.WEST.value:
                return (-1, 0)
            case Direction.NORTH.value:
                return (0, 1)
            case Direction.EAST.value:
                return (1, 0)
            case Direction.SOUTH.value:
                return (0, -1)
            case _:
                return (0,0) 
            
    @property
    def opposite(self) -> "Direction":
        match (self.value):
            case Direction.WEST.value:
                return Direction.EAST
            case Direction.NORTH.value:
                return Direction.SOUTH
            case Direction.EAST.value:
                return Direction.WEST
            case Direction.SOUTH.value:
                return Direction.NORTH
            case _:
                return Direction.NORTH

# Cell Calculation
# ULRD
# 0000 = 0 = no walls
# 0001 = 1 = wall down
# 0010 = 2 = wall right
# 0011 = 3 = wall right and down
# 0100 = 4 = wall left
# 0101 = 5 = wall left and down
# 0110 = 6 = wall left and down
# 0111 = 7 = wall left, right and down
# 1000 = 8 = wall up
# 1001 = 9 = wall up and down
# 1010 = 10 = wall up and right
# 1011 = 11 = wall up, right and down
# 1100 = 12 = wall up and left
# 1101 = 13 = wall up, left and down
# 1110 = 14 = wall up, left and right
# 1111 = 15 = wall up, left, right and down

def set_bit(value : int, bit : int) -> int:
    return value | (1 << bit)

def clear_bit(value : int, bit : int) -> int:
    return value & ~(1 << bit)

class Cell:
    @staticmethod
    def addWall(cellValue : int, directionOfWall : "Direction") -> int:
        match directionOfWall:
            case Direction.NORTH:
                return set_bit(cellValue, 3)
            case Direction.WEST:
                return set_bit(cellValue, 2)
            case Direction.EAST:
                return set_bit(cellValue, 1)
            case Direction.SOUTH:
                return set_bit(cellValue, 0)
            
    @staticmethod
    def getClearDirections(cellValue : int) -> list[Direction]:
        directions = []
        if cellValue & (1 << 3) == 0:
            directions.append(Direction.NORTH)
        if cellValue & (1 << 2) == 0:
            directions.append(Direction.WEST)
        if cellValue & (1 << 1) == 0:
            directions.append(Direction.EAST)
        if cellValue & (1 << 0) == 0:
            directions.append(Direction.SOUTH)
        return directions