import unittest
from cell import Direction, MouseDirection, Cell

class TestCellFunctions(unittest.TestCase):
    def test_relative_directions(self) -> None:
        self.assertEqual(Direction.fromMouseDirection(Direction.NORTH, MouseDirection.LEFT), Direction.WEST)
        self.assertEqual(Direction.fromMouseDirection(Direction.NORTH, MouseDirection.FORWARD), Direction.NORTH)
        self.assertEqual(Direction.fromMouseDirection(Direction.NORTH, MouseDirection.RIGHT), Direction.EAST)
        self.assertEqual(Direction.fromMouseDirection(Direction.NORTH, MouseDirection.BACKWARD), Direction.SOUTH)
        self.assertEqual(Direction.fromMouseDirection(Direction.WEST, MouseDirection.LEFT), Direction.SOUTH)
        self.assertEqual(Direction.fromMouseDirection(Direction.WEST, MouseDirection.FORWARD), Direction.WEST)
        self.assertEqual(Direction.fromMouseDirection(Direction.WEST, MouseDirection.RIGHT), Direction.NORTH)
        self.assertEqual(Direction.fromMouseDirection(Direction.WEST, MouseDirection.BACKWARD), Direction.EAST)
        self.assertEqual(Direction.fromMouseDirection(Direction.EAST, MouseDirection.LEFT), Direction.NORTH)
        self.assertEqual(Direction.fromMouseDirection(Direction.EAST, MouseDirection.FORWARD), Direction.EAST)
        self.assertEqual(Direction.fromMouseDirection(Direction.EAST, MouseDirection.RIGHT), Direction.SOUTH)
        self.assertEqual(Direction.fromMouseDirection(Direction.EAST, MouseDirection.BACKWARD), Direction.WEST)
        self.assertEqual(Direction.fromMouseDirection(Direction.SOUTH, MouseDirection.LEFT), Direction.EAST)
        self.assertEqual(Direction.fromMouseDirection(Direction.SOUTH, MouseDirection.FORWARD), Direction.SOUTH) 
        self.assertEqual(Direction.fromMouseDirection(Direction.SOUTH, MouseDirection.RIGHT), Direction.WEST)
        self.assertEqual(Direction.fromMouseDirection(Direction.SOUTH, MouseDirection.BACKWARD), Direction.NORTH)

    def test_add_to_existing_cell(self) -> None:
        # Small subset of all possible cases
        self.assertEqual(Cell.addWall(0, Direction.NORTH), 8)
        self.assertEqual(Cell.addWall(1, Direction.NORTH), 9)
        self.assertEqual(Cell.addWall(2, Direction.NORTH), 10)
        self.assertEqual(Cell.addWall(10, Direction.NORTH), 10)
        self.assertEqual(Cell.addWall(0, Direction.WEST), 4)
        self.assertEqual(Cell.addWall(8, Direction.WEST), 12)
        self.assertEqual(Cell.addWall(11, Direction.WEST), 15)

    def test_get_clear_directions(self) -> None:
        self.assertEqual(Cell.getClearDirections(0), [Direction.NORTH, Direction.WEST, Direction.EAST, Direction.SOUTH])
        self.assertEqual(Cell.getClearDirections(1), [Direction.NORTH, Direction.WEST, Direction.EAST])
        self.assertEqual(Cell.getClearDirections(2), [Direction.NORTH, Direction.WEST, Direction.SOUTH])
        self.assertEqual(Cell.getClearDirections(3), [Direction.NORTH, Direction.WEST])
        self.assertEqual(Cell.getClearDirections(4), [Direction.NORTH, Direction.EAST, Direction.SOUTH])
        self.assertEqual(Cell.getClearDirections(5), [Direction.NORTH, Direction.EAST])
        self.assertEqual(Cell.getClearDirections(6), [Direction.NORTH, Direction.SOUTH])
        self.assertEqual(Cell.getClearDirections(7), [Direction.NORTH])
        self.assertEqual(Cell.getClearDirections(8), [Direction.WEST, Direction.EAST, Direction.SOUTH])
        self.assertEqual(Cell.getClearDirections(9), [Direction.WEST, Direction.EAST])
        self.assertEqual(Cell.getClearDirections(10), [Direction.WEST, Direction.SOUTH])
        self.assertEqual(Cell.getClearDirections(11), [Direction.WEST])
        self.assertEqual(Cell.getClearDirections(12), [Direction.EAST, Direction.SOUTH])
        self.assertEqual(Cell.getClearDirections(13), [Direction.EAST])
        self.assertEqual(Cell.getClearDirections(14), [Direction.SOUTH])
        self.assertEqual(Cell.getClearDirections(15), [])

if __name__ == '__main__':
    unittest.main()