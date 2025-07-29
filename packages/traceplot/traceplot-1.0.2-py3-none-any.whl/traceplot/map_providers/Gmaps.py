from typing import TypedDict
import requests
from traceplot.map_providers import MapProvider
from traceplot.BackgroundImage import BackgroundImage
from traceplot.helpers.gmaps import (
    get_zoom_level_from_radius,
    get_bbox,
)
from traceplot.helpers.geo import (
    getDistanceDeg,
    degree_to_meter_at_lat,
    getCenterOfBoundingBox,
    getBoundingBox,
)
from traceplot.types import PointGeo


GmapsConfig = TypedDict(
    "GmapsConfig",
    {
        "maptype": str,
        "gmaps_api_key": str,
    },
)


class Gmaps(MapProvider):
    def __init__(self, providerConfig: GmapsConfig):
        super().__init__(providerConfig, name="Google Maps")

    def downloadEnclosingMap(
        self,
        points_geo: list[PointGeo],
        out_filename: str,
        w_px: int = 640,
        h_px: int = 640,
    ) -> BackgroundImage:
        """
        Download map background containing all points
        """
        gpx_bbox = getBoundingBox(points_geo)
        gpx_bbox_center = getCenterOfBoundingBox(gpx_bbox)

        radius_deg = getDistanceDeg(
            PointGeo(lng=gpx_bbox[2], lat=gpx_bbox[3], elevation=0), gpx_bbox_center
        )
        radius_m = radius_deg * degree_to_meter_at_lat(gpx_bbox_center.lat)

        STATIC_MAPS_BASE_API = "https://maps.googleapis.com/maps/api/staticmap"

        zoom = get_zoom_level_from_radius(gpx_bbox_center.lat, radius_m, w_px)
        size = str(w_px) + "x" + str(h_px)

        url: str = "".join(
            [
                STATIC_MAPS_BASE_API,
                f"?center={gpx_bbox_center.lat},{gpx_bbox_center.lng}",
                f"&zoom={zoom}",
                f"&size={size}",
                f"&maptype={self.providerConfig.get('maptype')}",
                "&scale=2",
                f"&key={self.providerConfig.get('gmaps_api_key')}",
            ]
        )

        response = requests.get(url)
        if response.status_code == 200:
            with open(out_filename, "wb") as f:
                f.write(response.content)
                print(
                    f"PNG centered on {round(gpx_bbox_center.lat, 4)}, {round(gpx_bbox_center.lng, 4)} with a {radius_m}m radius exported"
                )
        else:
            print("Erreur :", response.status_code, response.text)

        return BackgroundImage(
            bbox=get_bbox(gpx_bbox_center.lat, gpx_bbox_center.lng, zoom, w_px, h_px),
            image_path=out_filename,
        )
