from traceplot.helpers.geo import getSquareDistance, getSquareSegmentDistance
from traceplot.types import Point, Segment


def test_d0() -> None:
    p1: Point = (0.0, 0.4)
    p2: Point = (0.0, 0.4)
    assert getSquareDistance(p1, p2) == 0.0


def test_d1() -> None:
    p1: Point = (0.0, 0.0)
    p2: Point = (0.0, 1.0)
    assert getSquareDistance(p1, p2) == 1.0


def test_d0_segment() -> None:
    p1: Point = (0.0, 0.0)
    p2: Point = (0.0, 0.0)
    seg1: Segment = (0.0, 0.0)
    assert getSquareSegmentDistance(seg1, p1, p2) == 0.0
