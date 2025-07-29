from traceplot.types import BoundingBox


class BackgroundImage:
    bbox: BoundingBox
    image_path: str

    def __init__(self, bbox: BoundingBox, image_path: str):
        self.bbox = bbox
        self.image_path = image_path
