from traceplot.types import Point, PointGeo, Segment, BoundingBox
import numpy as np
from pyproj import Geod


def getSquareDistance(p1: Point, p2: Point) -> float:
    """
    Square distance between two points
    """
    dx = p1[1] - p2[1]
    dy = p1[0] - p2[0]

    return dx * dx + dy * dy


def getSquareSegmentDistance(p: Segment, p1: Point, p2: Point) -> float:
    """
    Square distance between point and a segment
    """
    x = p1[1]
    y = p1[0]

    dx = p2[1] - x
    dy = p2[0] - y

    if dx != 0 or dy != 0:
        t = ((p[1] - x) * dx + (p[0] - y) * dy) / (dx * dx + dy * dy)

        if t > 1:
            x = p2[1]
            y = p2[0]
        elif t > 0:
            x += dx * t
            y += dy * t

    dx = p[1] - x
    dy = p[0] - y

    return dx * dx + dy * dy


def _simplifyRadialDistance(points: list[Point], tolerance: float) -> list[Point]:
    length = len(points)
    prev_point = points[0]
    new_points = [prev_point]

    for i in range(length):
        point = points[i]

        if getSquareDistance(point, prev_point) > tolerance:
            new_points.append(point)
            prev_point = point

    if prev_point != point:
        new_points.append(point)

    return new_points


def _simplifyDouglasPeucker(points: list[Point], tolerance: float) -> list[Point]:
    length = len(points)
    markers = [0] * length  # Maybe not the most efficent way?

    first = 0
    last = length - 1

    first_stack = []
    last_stack = []

    new_points = []

    markers[first] = 1
    markers[last] = 1

    while last:
        max_sqdist = 0.0

        for i in range(first, last):
            sqdist = getSquareSegmentDistance(points[i], points[first], points[last])

            if sqdist > max_sqdist:
                index = i
                max_sqdist = sqdist

        if max_sqdist > tolerance:
            markers[index] = 1

            first_stack.append(first)
            last_stack.append(index)

            first_stack.append(index)
            last_stack.append(last)

        # Can pop an empty array in Javascript, but not Python, so check
        # the length of the list first
        if len(first_stack) == 0:
            first = None
        else:
            first = first_stack.pop()

        if len(last_stack) == 0:
            last = None
        else:
            last = last_stack.pop()

    for i in range(length):
        if markers[i]:
            new_points.append(points[i])

    return new_points


def simplify(
    points: list[Point], tolerance: float = 0.1, highestQuality: bool = True
) -> list[Point]:
    sqtolerance = tolerance * tolerance

    if not highestQuality:
        points = _simplifyRadialDistance(points, sqtolerance)

    points = _simplifyDouglasPeucker(points, sqtolerance)

    return points


# TODO test this
def pointGeoToPoint(
    p_geo: PointGeo, minx: float, miny: float, maxx: float, maxy: float
) -> Point:
    return (p_geo.lng - minx) / (maxx - minx), (p_geo.lat - miny) / (maxy - miny)


# TODO test this
def getBoundingBox(p_geo: list[PointGeo]) -> BoundingBox:
    "return a bounding box which contains all waypoints"
    lat = [p.lat for p in p_geo]
    lon = [p.lng for p in p_geo]
    return (min(lon), min(lat), max(lon), max(lat))


def addMarginToBbox(
    bbox: BoundingBox,
    margin_top_pct: float = 0,
    margin_bottom_pct: float = 0,
    margin_left_pct: float = 0,
    margin_right_pct: float = 0,
) -> BoundingBox:
    """
    Add margins to bounding box
    """
    bbox_lon = bbox[2] - bbox[0]
    bbox_lat = bbox[3] - bbox[1]

    return (
        bbox[0] - bbox_lon * margin_left,
        bbox[1] - bbox_lat * margin_bottom,
        bbox[2] + bbox_lon * margin_right,
        # TODO fix margin_top not working
        bbox[3] + bbox_lat * margin_top,
    )


# TODO test this
def getCenterOfBoundingBox(bbox: BoundingBox) -> PointGeo:
    return PointGeo(
        lat=(bbox[1] + bbox[3]) / 2, lng=(bbox[0] + bbox[2]) / 2, elevation=0
    )


def getDistanceDeg(p1: PointGeo, p2: PointGeo) -> float:
    return np.linalg.norm(np.array([p1.lng, p1.lat]) - np.array([p2.lng, p2.lat]))


def degree_to_meter_at_lat(lat: float) -> float:
    """
    Converts one degree to meters for given latitude
    """
    geod = Geod(ellps="WGS84")
    lon = 0
    lat1 = lat - 0.5
    lat2 = lat + 0.5
    _, _, distance_m = geod.inv(lon, lat1, lon, lat2)
    return float(distance_m)
