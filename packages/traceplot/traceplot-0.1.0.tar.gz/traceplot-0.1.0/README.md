# Traceplot

_Traceplot_ is a library to generate static maps. You can download background maps from mapping services (Google Maps, Mapbox, OSM, ...) and plot your points on top. You can add markers, title, elevation graphs and more.

## Installation

_Traceplot_ is available on [Pypi](https://pypi.org/project/traceplot/):

```sh
# Using uv
uv add traceplot
# Using pip
pip install traceplot
```

## Usage

See more code in [examples](./examples) folder.

```python
from traceplot.BackgroundImage import BackgroundImage
from traceplot.Trace import Trace


t: Trace = Trace(points_geo=points_geo)
t.addBackgroundImage(
    background_img=BackgroundImage(
        bbox=(2.117, 48.704, 2.557, 48.994), image_path="out/background_paris.png"
    )
)
t.addMarker(
    points_geo[0],
    img_path="img/marker_start.png",
    label_text="Start",
    marker_scale=0.5,
    label_offset_x=0.05,
)
t.addElevationGraph(height_pct=0.17, backgroundColor="white", backgroundColorAlpha=0.6)
t.plotPoints()
t.addTitle("Around Paris", center_x=0.5, center_y=0.2, fontsize=30)
t.save("out/day_one.png")
t.show()
t.close()
```

## Maps providers

Current implemented maps providers are:

- [done] Google Maps Static API
- [todo] Mapbox
- [todo] OSM
- [todo] Geoapify

## Developpement

Here are some useful commands for developpement:

```sh
# Run tests
make test
# Run lint
make lint
# Format code
make format
# Type checking
make mypy
# Get coverage
make coverage
```

These commands are available in [Makefile](./Makefile).
