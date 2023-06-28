import json
import sys
from enum import Enum
from typing import Any, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from route import Route


class MouseCrashedError(Exception):
    pass


class PythonActionType(Enum):
    SET_VELOCITIES = 0
    SET_EXPLORED = 1
    SET_CELL_VALUE = 2
    DEBUG = 3
    TERMINATE = 4
    DISPLAY_ROUTE = 5

class PythonAction:
    def __init__(self, actionType : PythonActionType, jsonBody : str) -> None:
        self.actionType = actionType.value
        self.jsonBody = jsonBody

class Actions:
    def __init__(self) -> None:
        self.actions: list[PythonAction] = []

    def _addToActions(
        self, actionType: PythonActionType, body: dict[str, Any] = {}
    ) -> None:
        
        self.actions.append(
            PythonAction(actionType, json.dumps(body))
        )

    def _addToActionsStr(self, actionType: PythonActionType, body: str) -> None:
        self.actions.append(PythonAction(actionType, body))

    def setVelocities(self, left: int, right: int) -> None:
        self._addToActions(
            PythonActionType.SET_VELOCITIES, {"left": left, "right": right}
        )

    def setCellValue(self, x: int, y: int, value: int) -> None:
        self._addToActions(
            PythonActionType.SET_CELL_VALUE, {"x": x, "y": y, "value": value}
        )

    def setExplored(self, x: int, y: int, explored: bool) -> None:
        self._addToActions(
            PythonActionType.SET_EXPLORED, {"x": x, "y": y, "explored": explored}
        )

    def debugPrint(self, message: str) -> None:
        self._addToActions(PythonActionType.DEBUG, {"message": message})

    def terminate(self) -> None:
        self._addToActions(PythonActionType.TERMINATE)

    def displayRoute(self, route: "Route") -> None:
        self._addToActionsStr(PythonActionType.DISPLAY_ROUTE, route.to_json())


    def send(self) -> None:
        actionsToSend = [json.dumps(action.__dict__) for action in self.actions]
        sys.stdout.write(json.dumps({"actions": actionsToSend}) + "\n")
        sys.stdout.flush()

def log(message: str) -> None:
    sys.stdout.write(message + "\n")
    sys.stdout.flush()

class InputData:
    @staticmethod
    def get_from_unity() -> "InputData":
        inputObj = json.loads(input())

        inputData = InputData(
            inputObj["leftDistance"],
            inputObj["left45Distance"],
            inputObj["forwardDistance"],
            inputObj["right45Distance"],
            inputObj["rightDistance"],
            inputObj["directionRad"],
            inputObj["actualPositionX"] / 18.0,
            inputObj["actualPositionY"] / 18.0,
            inputObj["actualDirectionRad"],
        )

        return inputData

    def __init__(
        self,
        leftDistance: float,
        left45Distance: float,
        forwardDistance: float,
        right45Distance: float,
        rightDistance: float,
        directionRad: float,
        actualPositionX : float,
        actualPositionY : float,
        actualDirectionRad : float,
    ) -> None:
        self.leftDistance = leftDistance
        self.left45Distance = left45Distance
        self.forwardDistance = forwardDistance
        self.right45Distance = right45Distance
        self.rightDistance = rightDistance
        self.directionRad = directionRad
        self.actualPositionX = actualPositionX
        self.actualPositionY = actualPositionY
        self.actualDirectionRad = actualDirectionRad
