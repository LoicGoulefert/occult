# Third party libs
import click
import numpy as np
from shapely.geometry import Polygon, MultiLineString
from shapely.ops import unary_union
from vpype import layer_processor, LineCollection, Length, as_vector


@click.command()
@click.option(
    "-t",
    "--tolerance",
    type=Length(),
    default="0.01mm",
    help="Max distance between start and end point to consider a path closed "
    "(default: 0.01mm)",
)
@layer_processor
def occult(lines: LineCollection, tolerance: float) -> LineCollection:
    """
    Remove occulted lines.
    """
    new_lines = LineCollection()
    polys = []

    # Convert from LineCollection to Polygons
    for line in lines:
        if np.abs(line[0] - line[-1]) <= tolerance:
            polys.append(Polygon([(pt.real, pt.imag) for pt in line]))

    # Remove occulted segments
    for i, poly in enumerate(polys):
        for j, other in enumerate(polys[:i]):
            if not other.difference(poly).is_empty:
                polys[j] = other.difference(poly)

    # Convert Polygons to LineCollection
    for poly in polys:
        bounds = poly.boundary
        if bounds.type == "MultiLineString":
            new_lines.extend(bounds)
        else:
            new_lines.append(bounds)

    return new_lines


occult.help_group = "Plugins"
