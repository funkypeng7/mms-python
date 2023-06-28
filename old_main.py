import copy
import src.api as api
from enum import Enum
from src.cell import Direction, MouseDirection, Cell
from src.route import Route
from typing import Final
import time
import json


class MouseState(Enum):
    EXPLORING = 0

REACH_FINISH_GOAL = [(7,7), (7,8), (8,7), (8,8)]
REACH_START_GOAL = [(0,0)]
 

class Mouse:
    ORDER_TO_CHECK : Final[list[MouseDirection]] = [MouseDirection.FORWARD, MouseDirection.LEFT, MouseDirection.RIGHT, MouseDirection.BACKWARD]

    def __init__(self) -> None:
        self.maze = Maze()
        self.x = 0
        self.y = 0
        self.direction = Direction.NORTH
        self.state = MouseState.EXPLORING

    def run(self) -> None:
        while (True):
            match self.state:
                case MouseState.EXPLORING:
                    complete = self.exploringMove(REACH_FINISH_GOAL, False, MouseState.RETURNING)
                    if (complete):
                        self.markOutCenter()

    def exploringMove(self, goal : list[tuple[int, int]], shouldEnterGoal : bool, nextState : MouseState) -> bool:
        if (shouldEnterGoal and (self.x, self.y) in goal):
            log("Entered goal")
            self.state = nextState
            return True
        
        self.addMouseWalls()
        self.maze.setExplored(self.x, self.y)

        self.maze.recalculate(goal)
        self.drawRoute()

        bestDirection = self.FindBestDirection()

        # Check if mouse will complete maze
        dx, dy = bestDirection.vector
        if not shouldEnterGoal and (self.x + dx, self.y + dy) in REACH_FINISH_GOAL:
            log("Can enter goal")
            self.state = nextState
            return True
        
        self.TurnMouse(bestDirection)
        self.MoveForward()

        return False

    def addMouseWalls(self) -> None:
        left, front, right = self.getSensors()
        log(f"Sensors detected at ({self.x}, {self.y}). Facing {self.direction.name}. left: {left}, front {front}, right {right}")
        
        # Add walls to maze
        if left:
            self.maze.addWall(self.x, self.y, Direction.fromMouseDirection(self.direction, MouseDirection.LEFT))
        if front:
            self.maze.addWall(self.x, self.y, Direction.fromMouseDirection(self.direction, MouseDirection.FORWARD))
        if right:
            self.maze.addWall(self.x, self.y, Direction.fromMouseDirection(self.direction, MouseDirection.RIGHT))

    def FindBestDirection(self) -> Direction:
        # Get next direction
        currentCell = self.maze.cells[self.x][self.y]
        clearDirectionsAbsolute = Cell.getClearDirections(currentCell)
        
        # Convert to relative directions, to prioritize front over left over right over back
        clearDirections = []

        forwardAbsolute = Direction.fromMouseDirection(self.direction, MouseDirection.FORWARD)
        leftAbsolute = Direction.fromMouseDirection(self.direction, MouseDirection.LEFT)
        rightAbsolute = Direction.fromMouseDirection(self.direction, MouseDirection.RIGHT)
        backwardAbsolute = Direction.fromMouseDirection(self.direction, MouseDirection.BACKWARD)

        if forwardAbsolute in clearDirectionsAbsolute:
            clearDirections.append(forwardAbsolute)
        if leftAbsolute in clearDirectionsAbsolute:
            clearDirections.append(leftAbsolute)
        if rightAbsolute in clearDirectionsAbsolute:
            clearDirections.append(rightAbsolute)
        if backwardAbsolute in clearDirectionsAbsolute:
            clearDirections.append(backwardAbsolute)

        log(f"Clear directions at ({self.x}, {self.y}): {clearDirections}")

        bestDirection = clearDirections[0]
        bestDirectionValue = 999999
        for direction in clearDirections:
            # Get vector
            dx, dy = direction.vector

            # Get new position
            nx = self.x + dx
            ny = self.y + dy

            # Check if in bounds
            if nx < 0 or nx >= 16 or ny < 0 or ny >= 16:
                raise Exception("Clear direction detected in out of bounds")
                        
            shortestPrediction = self.maze.flood[nx][ny] < bestDirectionValue

            # Check if better than current best, enforces dfs
            # if notExploredButBestDirectionHas or (not exploredButBestDirectionHasnt and shortestPrediction):
            if shortestPrediction:
                bestDirection = direction
                bestDirectionValue = self.maze.flood[nx][ny]

        log(f"Best direction calculated: {bestDirection.name}")
        return bestDirection

    def TurnMouse(self, newDirection : Direction) -> None:
        for turn in self.direction.turnsTo(newDirection):
            match turn:
                case MouseDirection.LEFT:
                    api.turnLeft()
                case MouseDirection.RIGHT:
                    api.turnRight()
                case _:
                    raise Exception("Invalid turn")
        
        self.direction = newDirection

    def MoveForward(self) -> None:
        api.moveForward()

        # Update position
        dx, dy = self.direction.vector
        self.x += dx
        self.y += dy
            

    def getSensors(self) -> tuple[bool, bool, bool]:
        return (api.wallLeft(), api.wallFront(), api.wallRight())


    def drawRoute(self) -> None:
        api.clearAllColor()

        x, y = self.x, self.y
        direction = self.direction
        currentValue = self.maze.flood[x][y]
        while (True):
            api.setColor(x, y, "g")
            if (currentValue == 0):
                break

            clearDirections = Cell.getClearDirections(self.maze.cells[x][y])
            for directionToCheck in Mouse.ORDER_TO_CHECK:
                possibleNewDirection = Direction.fromMouseDirection(direction, directionToCheck)
                if possibleNewDirection not in clearDirections:
                    continue

                dx, dy = possibleNewDirection.vector
                nx = x + dx
                ny = y + dy
                if (nx < 0 or nx >= 16 or ny < 0 or ny >= 16):
                    continue

                if (self.maze.flood[nx][ny] == currentValue - 1):
                    x, y = nx, ny
                    direction = possibleNewDirection
                    currentValue -= 1
                    break
        
    def markOutCenter(self) -> None:
        # Mark out center square
        directionToCenter = self.FindBestDirection()
        dx, dy = directionToCenter.vector
        centerWithEntrance = (self.x + dx, self.y + dy)
        if centerWithEntrance != (7,7):
            self.maze.addWall(7,7, Direction.WEST)
            self.maze.addWall(7,7, Direction.SOUTH)
        if centerWithEntrance != (7,8):
            self.maze.addWall(7,8, Direction.WEST)
            self.maze.addWall(7,8, Direction.NORTH)
        if centerWithEntrance != (8,7):
            self.maze.addWall(8,7, Direction.EAST)
            self.maze.addWall(8,7, Direction.SOUTH)
        if centerWithEntrance != (8,8):
            self.maze.addWall(8,8, Direction.EAST)
            self.maze.addWall(8,8, Direction.NORTH)

        # Add center square without entrance
        possibleWallToAdd = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
        if (dx == 1):
            possibleWallToAdd.remove(Direction.WEST)
        elif (dx == -1):
            possibleWallToAdd.remove(Direction.EAST)
        elif (dy == 1):
            possibleWallToAdd.remove(Direction.SOUTH)
        elif (dy == -1):
            possibleWallToAdd.remove(Direction.NORTH)
        
        if centerWithEntrance[0] == 7:
            possibleWallToAdd.remove(Direction.EAST)
        elif centerWithEntrance[0] == 8:
            possibleWallToAdd.remove(Direction.WEST)

        if centerWithEntrance[1] == 7:
            possibleWallToAdd.remove(Direction.NORTH)
        elif centerWithEntrance[1] == 8:
            possibleWallToAdd.remove(Direction.SOUTH)

        assert len(possibleWallToAdd) == 1

        self.maze.addWall(centerWithEntrance[0], centerWithEntrance[1], possibleWallToAdd.pop())

        self.maze.setExplored(7, 7)
        self.maze.setExplored(7, 8)
        self.maze.setExplored(8, 7)
        self.maze.setExplored(8, 8)

    def loadMaze(self, filename : str) -> None:
        with open(filename, "r") as f:
            maze = json.loads(f.read())
            self.maze = Maze()
            self.maze.cells = maze["cells"]
            self.maze.explored = maze["explored"]
            self.maze.recalculate(REACH_FINISH_GOAL)
            api.clearAllColor()
            
# Class for storing and displaying maze data
# As well as calculating the shortest path
# And active updating based on cells detected
class Maze:
    # Cell states
    def __init__(self) -> None:
        self.cells = [[0 for _ in range (16)] for _ in range(16)]

        # Add edges of maze
        for x in range(16):
            self.addWall(x, 0, Direction.SOUTH)
            self.addWall(x, 15, Direction.NORTH)

        for y in range(16):
            self.addWall(0, y, Direction.WEST)
            self.addWall(15, y, Direction.EAST)

        self.flood = [[-1 for _ in range (16)] for _ in range(16)]

        self.explored = [[False for _ in range (16)] for _ in range(16)]
        self.explored[0][0] = True

    def recalculate(self, goal : list[tuple[int, int]], updateDisplay : bool = True) -> None:
        # Flood fill
        self.flood = [[-1 for _ in range (16)] for _ in range(16)]

        for point in goal:
            self.flood[point[0]][point[1]] = 0

        # Set initial search points
        search = goal.copy()
        while (True):
            # Get next search point
            if len(search) == 0:
                break
            x, y = search.pop(0)

            # Get current distance
            distance = self.flood[x][y]

            # Check in free directions
            for direction in Cell.getClearDirections(self.cells[x][y]):
                # Get vector
                dx, dy = direction.vector

                # Get new position
                nx = x + dx
                ny = y + dy

                # Check if in bounds
                if nx < 0 or nx >= 16 or ny < 0 or ny >= 16:
                    continue

                # Check if already visited
                if self.flood[nx][ny] != -1:
                    continue

                # Set distance
                self.flood[nx][ny] = distance + 1

                # Add to search
                search.append((nx, ny))

        if updateDisplay:
            self.updateDisplay()

    def blockUnexplored(self) -> None:
        for x in range(16):
            for y in range(16):
                if not self.explored[x][y]:
                    # Check if all cells around it are explored
                    allNeighboursExplored = True
                    for direction in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + direction[0], y + direction[1]
                        if nx < 0 or nx >= 16 or ny < 0 or ny >= 16:
                            continue

                        if not self.getExplored(nx, ny):
                            allNeighboursExplored = False
                    
                    if not allNeighboursExplored:
                        self.cells[x][y] = 15

                    self.setExplored(x, y)
        self.updateDisplay()

    def calculateBestRoutes(self, start : tuple[int, int], startDirection : Direction, goal : list[tuple[int, int]], tryCalcuateAlternatives : bool = False) -> list[Route]:
        self.recalculate(goal, updateDisplay=False)
        
        bestRoutes = []
        stack = [(start, startDirection, Route([start]))]

        while stack:
            current, currentDirection, route = stack.pop()

            if current in goal:
                bestRoutes.append(route)
                continue

            x, y = current
            # time.sleep(0.1)
            api.clearAllColor()
            api.setColor(x, y, "g")

            mustCopyRoute = False
            clearDirections = Cell.getClearDirections(self.cells[x][y])
            for directionToCheck in Mouse.ORDER_TO_CHECK:
                possibleNewDirection = Direction.fromMouseDirection(currentDirection, directionToCheck)
                if possibleNewDirection not in clearDirections:
                    continue

                dx, dy = possibleNewDirection.vector
                nx = x + dx
                ny = y + dy
                if (nx < 0 or nx >= 16 or ny < 0 or ny >= 16):
                    continue

                if not self.getExplored(nx, ny):
                    # Check if all cells around it are explored
                    allNeighboursExplored = True
                    for direction in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        if not self.getExplored(nx + direction[0], ny + direction[1]):
                            allNeighboursExplored = False
                    
                    if not allNeighboursExplored:
                        continue

                    self.setExplored(nx, ny)

                api.setColor(nx, ny, "y")
                if (self.flood[nx][ny] == self.flood[x][y] - 1):
                    if mustCopyRoute:
                        route = route.copy()
                    mustCopyRoute = True
                    route.append((nx, ny))
                    stack.append(((nx, ny), possibleNewDirection, route))
                    api.setColor(nx, ny, "g")

                    break
        
        # Save maze cells to bring back after
        if tryCalcuateAlternatives:
            for route in bestRoutes[:]:
                for index in range(len(route) - 1):
                    testingMaze = Maze()
                    testingMaze.cells = copy.deepcopy(self.cells)
                    testingMaze.explored = copy.deepcopy(self.explored)
                    
                    x, y = route[index]
                    dx, dy = route[index + 1][0] - x, route[index + 1][1] - y

                    testingMaze.addWall(x, y, Direction.fromVector((dx, dy)))
                    try:
                        otherBestRoutes = testingMaze.calculateBestRoutes(start, startDirection, goal, False)
                        bestRoutes.extend(otherBestRoutes)
                    except:
                        continue
            
            log(f"Had len(bestRoutes) = {len(bestRoutes)}")
            bestRoutes = list(set(bestRoutes))
            log(f"Now len(bestRoutes) = {len(bestRoutes)}")




        return bestRoutes



        # Find best route, when reaches a branch find both route from there, using depth first search approach


    def setExplored(self, x : int, y : int) -> None:
        self.explored[x][y] = True

    def getExplored(self, x : int, y : int) -> bool:
        return self.explored[x][y]

    def addWall(self, x : int, y : int, direction : Direction) -> None:
        # Get cell
        cell = self.cells[x][y]
        # Edit cell
        cell = Cell.addWall(cell, direction)
        self.cells[x][y] = cell


        # Edit neighbor
        dx, dy = direction.vector
        nx = x + dx
        ny = y + dy
        if nx < 0 or nx >= 16 or ny < 0 or ny >= 16:
            # Neighbour not in bounds
            return

        neighbor = self.cells[nx][ny]
        neighbor = Cell.addWall(neighbor, direction.opposite)
        self.cells[nx][ny] = neighbor


    def updateDisplay(self) -> None:
        # Draw maze
        for x in range(16):
            for y in range(16):
                # Get distance
                distance = self.flood[x][y]

                # Check if visited
                if distance == -1:
                    api.setText(x, y, "X")
                    raise Exception("Flood fill algorithm did not complete maze")
                else:
                    api.setText(x, y, str(distance))

        for x in range(16):
            for y in range(16):
                # Get cell
                cell = self.cells[x][y]

                # Check if visited
                clearDirections = Cell.getClearDirections(cell)
                if Direction.NORTH not in clearDirections:
                    api.setWall(x, y, "n")
                if Direction.EAST not in clearDirections:
                    api.setWall(x, y, "e")
                if Direction.SOUTH not in clearDirections:
                    api.setWall(x, y, "s")
                if Direction.WEST not in clearDirections:
                    api.setWall(x, y, "w")

                if not self.explored[x][y]:
                    api.setColor(x, y, "r")
        
def main() -> None:
    mouse = Mouse()
    # mouse.loadMaze("maze.json")
    # mouse.state = MouseState.CALCULATING_ROUTE
    mouse.run()
        



if __name__ == "__main__":
    main()
