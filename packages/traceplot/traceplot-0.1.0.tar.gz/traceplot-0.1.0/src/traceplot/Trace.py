from traceplot.types import BoundingBox, PointGeo, Point
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
from traceplot.helpers.geo import pointGeoToPoint, getBoundingBox, addMarginToBbox
from traceplot.helpers.graph import getTicksInt
from traceplot.BackgroundImage import BackgroundImage
from matplotlib.patches import Rectangle
from numpy import linspace


class Trace:
    background_bbox: BoundingBox
    fig: Figure
    ax: Axes
    points_px: list[Point]
    points_geo: list[PointGeo]
    elevation: list[float]

    def __init__(
        self,
        points_geo: list[PointGeo],
    ):
        FIGSIZE = (10, 10)
        self.points_geo = points_geo

        # TODO set bounding box enclosing points (+ margins)
        self._setBoundingBoxBackground(getBoundingBox(points_geo))

        self.elevation = self._extractElevation(points_geo)

        self.fig, self.ax = plt.subplots(figsize=FIGSIZE)
        self.fig.subplots_adjust(top=1, bottom=0, left=0, right=1, wspace=0)

    def _convertPointGeotoPx(self, points_geo: list[PointGeo]) -> list[Point]:
        [minx, miny, maxx, maxy] = self.background_bbox
        return [pointGeoToPoint(p, minx, miny, maxx, maxy) for p in points_geo]

    def _extractElevation(self, points_geo: list[PointGeo]) -> list[float]:
        return [p.ele for p in points_geo]

    def addMarker(
        self,
        point: PointGeo,
        img_path: str,
        label_text: str,
        marker_scale: float = 1.0,
        label_fontsize: int = 20,
        label_offset_x: float = 0,
        label_offset_y: float = 0,
    ) -> None:
        minx, miny, maxx, maxy = self.background_bbox
        point_xy = pointGeoToPoint(point, minx, miny, maxx, maxy)
        imagebox_marker = OffsetImage(Image.open(img_path), zoom=marker_scale)
        # add marker
        self.ax.add_artist(
            AnnotationBbox(
                imagebox_marker,
                point_xy,
                xycoords="data",
                frameon=False,
                box_alignment=(0.5, 0),
            )
        )
        # add label
        self.ax.text(
            point_xy[0] + label_offset_x,
            point_xy[1] + label_offset_y,
            label_text,
            fontsize=label_fontsize,
            bbox=dict(
                boxstyle="round",
                ec=(1.0, 0.5, 0.5),
                fc=(1.0, 0.8, 0.8),
            ),
        )
        pass

    def addBackgroundImage(self, background_img: BackgroundImage) -> None:
        # Set bounding box
        self._setBoundingBoxBackground(background_img.bbox)

        # Load backgroud image
        self.ax.imshow(Image.open(background_img.image_path), extent=(0, 1, 0, 1))

        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.set_aspect("equal")
        self.ax.axis("off")

    def _setBoundingBoxBackground(self, bbox: BoundingBox) -> None:
        self.background_bbox = bbox
        # recompute point px positions
        self.points_px: list[Point] = self._convertPointGeotoPx(self.points_geo)

    def resizeBbox(
        self,
        margin_top: float = 0,
        margin_bottom: float = 0,
        margin_left: float = 0,
        margin_right: float = 0,
    ) -> None:
        self._setBoundingBoxBackground(
            addMarginToBbox(
                self.background_bbox,
                margin_top,
                margin_bottom,
                margin_left,
                margin_right,
            )
        )

    def addElevationGraph(
        self,
        height_pct: float,
        backgroundColor: str,
        backgroundColorAlpha: float,
        ticks_space_meters: int = 200,
        margin_top: float = 0.02,
        margin_bottom: float = 0.02,
        margin_left: float = 0.1,
        margin_right: float = 0.05,
    ) -> None:
        PICTURE_HEIGHT = 1
        height_px = height_pct * PICTURE_HEIGHT

        # Add rectangle
        self.ax.add_patch(
            Rectangle(
                xy=(0, 0),
                width=1,
                height=height_px,
                facecolor=backgroundColor,
                alpha=backgroundColorAlpha,
            )
        )
        ELE_GRAPH_MARGIN_TOP = margin_top
        ELE_GRAPH_MARGIN_BOTTOM = margin_bottom
        ELE_GRAPH_MARGIN_LEFT = margin_left
        ELE_GRAPH_MARGIN_RIGHT = margin_right

        ELE_GRAPH_TOP = height_px - ELE_GRAPH_MARGIN_TOP
        ELE_GRAPH_RIGHT = 1 - ELE_GRAPH_MARGIN_RIGHT

        min_elev, max_elev = min(self.elevation), max(self.elevation)

        elevation_norm_x = linspace(
            ELE_GRAPH_MARGIN_LEFT, ELE_GRAPH_RIGHT, len(self.elevation)
        ).tolist()
        elevation_norm_y = [
            (elev - min_elev)
            / (max_elev - min_elev)
            * (ELE_GRAPH_TOP - ELE_GRAPH_MARGIN_BOTTOM)
            + ELE_GRAPH_MARGIN_BOTTOM
            for elev in self.elevation
        ]

        self.ax.plot(elevation_norm_x, elevation_norm_y, "b-")

        elevation_legend_x = [ELE_GRAPH_MARGIN_LEFT, ELE_GRAPH_MARGIN_LEFT]
        elevation_legend_y = [ELE_GRAPH_MARGIN_BOTTOM, ELE_GRAPH_TOP]
        self.ax.plot(
            elevation_legend_x, elevation_legend_y, color="grey", linestyle="-"
        )

        ## SCALE: Ticks
        TICKS_LENGTH = 0.005
        TICKS_COLOR = "grey"

        scale_ticks_meters = getTicksInt(
            min_elev, max_elev, ticks_space_meters, include_min_max=True
        )
        scale_ticks_y = list(
            map(
                lambda x: ELE_GRAPH_MARGIN_BOTTOM
                + (x - min_elev)
                / (max_elev - min_elev)
                * (ELE_GRAPH_TOP - ELE_GRAPH_MARGIN_BOTTOM),
                scale_ticks_meters,
            )
        )
        for y_tick in scale_ticks_y:
            self.ax.plot(
                [ELE_GRAPH_MARGIN_LEFT - TICKS_LENGTH, ELE_GRAPH_MARGIN_LEFT],
                [y_tick, y_tick],
                color=TICKS_COLOR,
                linestyle="-",
            )

        # SCALE: legend min/max ticks
        SCALE_LEGEND_OFFSET_X = -0.01
        SCALE_LEGEND_FONTSIZE = 10
        SCALE_LEGEND_COLOR = "grey"

        self.ax.text(
            ELE_GRAPH_MARGIN_LEFT + SCALE_LEGEND_OFFSET_X,
            ELE_GRAPH_TOP,
            f"{round(max_elev)}m",
            verticalalignment="center",
            horizontalalignment="right",
            transform=self.ax.transAxes,
            fontsize=SCALE_LEGEND_FONTSIZE,
            color=SCALE_LEGEND_COLOR,
        )
        self.ax.text(
            ELE_GRAPH_MARGIN_LEFT + SCALE_LEGEND_OFFSET_X,
            ELE_GRAPH_MARGIN_BOTTOM,
            f"{round(min_elev)}m",
            verticalalignment="center",
            horizontalalignment="right",
            transform=self.ax.transAxes,
            fontsize=SCALE_LEGEND_FONTSIZE,
            color=SCALE_LEGEND_COLOR,
        )

    def addTitle(
        self, title: str, center_x: float, center_y: float, fontsize: int
    ) -> None:
        self.ax.text(
            center_x,
            center_y,
            title,
            verticalalignment="center",
            horizontalalignment="center",
            transform=self.ax.transAxes,
            fontsize=fontsize,
        )

    def plotPoints(self) -> None:
        self.ax.plot([p[0] for p in self.points_px], [p[1] for p in self.points_px])

    def save(self, outfile_img_path: str) -> None:
        plt.savefig(
            outfile_img_path,
            dpi=600,
            pad_inches=0.01,
        )

    def close(self) -> None:
        plt.close()

    def show(self) -> None:
        plt.show()
