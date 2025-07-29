Point = tuple[float, float]


class PointGeo:
    lng: float
    lat: float
    ele: float

    def __init__(self, lng: float, lat: float, elevation: float) -> None:
        self.lng = lng
        self.lat = lat
        self.ele = elevation

    def __str__(self) -> str:
        return f"PointGeo (lng={self.lng},lat={self.lat},ele={self.ele})"


## todo fix
Segment = tuple[float, float]
ZoomLevel = int

BoundingBox = tuple[float, float, float, float]
