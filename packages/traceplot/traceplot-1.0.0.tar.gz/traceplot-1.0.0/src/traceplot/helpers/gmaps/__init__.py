from math import cos, radians, log2, sqrt
from traceplot.types import ZoomLevel, BoundingBox
from traceplot.helpers.geo import degree_to_meter_at_lat


def get_zoom_level_from_radius(
    latitude: float, radius_meters: float, width_px: int
) -> ZoomLevel:
    meters_per_pixel_at_zoom_0 = 156543.03392
    target_meters_per_pixel = (2 * radius_meters * sqrt(2)) / width_px
    adjusted_mpp = target_meters_per_pixel / cos(radians(latitude))
    zoom_level_float = log2(meters_per_pixel_at_zoom_0 / adjusted_mpp)
    zoom_level_int = int(round(zoom_level_float))

    return zoom_level_int


def get_bbox(
    center_lat: float, center_lon: float, zoom: ZoomLevel, width_px: int, height_px: int
) -> BoundingBox:
    scale = 156543.03392 * cos(radians(center_lat)) / (2**zoom)

    # Image dimensions
    image_width_m = width_px * scale
    image_height_m = height_px * scale

    # Conversion from meters in degrees
    lat_deg_per_m = 1 / degree_to_meter_at_lat(center_lat)
    lon_deg_per_m = 360 / (40075000 * cos(radians(center_lat)))

    delta_lat = (image_height_m * lat_deg_per_m) / 2
    delta_lon = (image_width_m * lon_deg_per_m) / 2

    minx = center_lon - delta_lon
    maxx = center_lon + delta_lon
    miny = center_lat - delta_lat
    maxy = center_lat + delta_lat

    return minx, miny, maxx, maxy
