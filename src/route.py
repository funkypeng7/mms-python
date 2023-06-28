import json
import sys
import numpy as np
from typing import Tuple, List
from scipy.spatial.distance import cdist

from api import Actions, InputData, log

class Route:
    def __init__(self) -> None :
        self.curve_list: List[Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]] = []

    def add_curve(self, points: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]) -> None:
        self.curve_list.append(points)

    def calculate_bezier_point(self, t: float, p0: Tuple[float, float], p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple:
        u = 1 - t
        tt = t * t
        uu = u * u
        p = np.array(p0) * uu
        p += 2 * u * t * np.array(p1)
        p += tt * np.array(p2)
        return tuple(p)

    def calculate_errors(self, current_position: Tuple[float, float], current_direction: float) -> Tuple:
        tangential_offset = None
        rotational_offset = None
        closest_curve = None
        closest_point = None

        for curve in self.curve_list:
            # Calculate distance from current position to each point on the curve
            curve_points = np.array([self.calculate_bezier_point(t, *curve) for t in np.linspace(0, 1, 100, endpoint=True)])
            distances = cdist([current_position], curve_points)
            closest_point_index = np.argmin(distances)

            # Calculate tangential offset (minimum distance to the curve)
            if tangential_offset is None or distances[0, closest_point_index] < tangential_offset:
                tangential_offset = distances[0, closest_point_index]
                closest_point = curve_points[closest_point_index]

                # Calculate the tangent at the closest point on the curve
                t = closest_point_index / 100  # Because np.linspace(0, 1, 100) was used
                p0, p1, p2 = curve
                closest_curve = curve
                # tangent = 2 * (1 - t) * np.array(p1) - 2 * t * np.array(p0) + 2 * t * np.array(p2)
                tangent = -2 * (1 - t) * np.array(p0) + (2 - 4 * t) * np.array(p1) + 2 * t * np.array(p2)

                # Calculate the direction that the mouse should be in
                rotational_offset = current_direction - np.arctan2(tangent[1], tangent[0]) 
                # Normalize the direction to be between -pi and pi
                if rotational_offset > np.pi:
                    rotational_offset -= 2 * np.pi
                elif rotational_offset < -np.pi:
                    rotational_offset += 2 * np.pi

        return tangential_offset, rotational_offset, closest_point, closest_curve



    def to_json(self) -> str:
        return json.dumps({"curveList" : self.curve_list})


if __name__ == "__main__":
    sys.stdout.write('Ready\n')
    sys.stdout.flush()

    route = Route()
    route.add_curve(((0, 0), (0, 1), (0, 2.5)))
    route.add_curve(((0, 2.5), (0, 3), (0.5, 3)))
    route.add_curve(((0.5, 3), (1, 3), (1, 3.5)))
    route.add_curve(((1, 3.5), (1, 4), (0.5, 4)))
    route.add_curve(((0.5, 4), (0, 4), (0, 4.5)))
    route.add_curve(((0, 4.5), (0, 5), (0.5, 5)))
    route.add_curve(((0.5, 5), (1, 5), (1, 5.5)))
    route.add_curve(((1, 5.5), (1, 6), (0.5, 6)))
    route.add_curve(((0.5, 6), (0, 6), (0, 6.5)))
    route.add_curve(((0, 6.5), (0, 7), (0.5, 7)))
    route.add_curve(((0.5, 7), (1, 7), (1, 7.5)))

    first_time = True

    while(True):
        inputData = InputData.get_from_unity()
        
        actions = Actions()
        if first_time:
            actions.displayRoute(route)
            first_time = False
        
        tangentialError, directionError, closestPoint, closestCurve = route.calculate_errors((inputData.actualPositionX, inputData.actualPositionY), inputData.actualDirectionRad)
        actions.debugPrint(f"Tagential error: {tangentialError}, Direction error: {directionError * 180 / np.pi}, Direction of Mouse: {inputData.actualDirectionRad * 180 / np.pi}")
        
        SPEED = 0.1, 0.1

        # Adjust speed based on tangentail error error
        

        actions.send()




