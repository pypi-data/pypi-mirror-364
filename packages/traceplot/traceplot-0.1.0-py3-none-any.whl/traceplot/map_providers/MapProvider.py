from abc import ABC, abstractmethod
from traceplot.types import PointGeo
from traceplot.BackgroundImage import BackgroundImage


class MapProvider(ABC):
    providerConfig: object
    providerName: str

    def __init__(self, providerConfig: object, name: str):
        self.providerConfig = providerConfig
        self.providerName = name
        pass

    @abstractmethod
    def downloadEnclosingMap(
        self,
        points_geo: list[PointGeo],
        out_filename: str,
        w_px: int = 640,
        h_px: int = 640,
    ) -> BackgroundImage:
        pass
