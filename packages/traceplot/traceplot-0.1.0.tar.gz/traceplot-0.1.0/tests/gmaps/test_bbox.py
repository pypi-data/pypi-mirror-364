from traceplot.helpers.gmaps import get_bbox


def test_bbox_paris_z12() -> None:
    assert get_bbox(
        center_lat=48.8589385,
        center_lon=2.2646338,
        zoom=12,
        width_px=640,
        height_px=640,
    ) == (2.1547704730131003, 48.786584670849734, 2.3744971269868995, 48.93129232915027)
