# Standard libs
import math

# Third party libs
import click
import numpy as np
from shapely.geometry import LineString, Polygon
from shapely.geometry.multilinestring import MultiLineString
from shapely.strtree import STRtree
from vpype import layer_processor, LineCollection, LengthType


@click.command()
@click.option(
    "-t",
    "--tolerance",
    type=LengthType(),
    default="0.01mm",
    help="Max distance between start and end point to consider a path closed"
    "(default: 0.01mm)",
)
@layer_processor
def occult(lines: LineCollection, tolerance: float) -> LineCollection:
    """
    Remove occulted lines.

    The order of the geometries in 'lines' matters, see example below.

    'tolerance' controls the distance tolerance between the first and last points
    of a geometry to consider it closed.

    Examples:
        $ vpype line 0 0 5 5 rect 2 2 1 1 occult show  # line is occulted by rect
        $ vpype rect 2 2 1 1 line 0 0 5 5 occult show  # line is NOT occulted by rect,
        as the line is drawn after the rectangle.
    """

    line_arr = [line for line in lines.as_mls()]

    for i, line in enumerate(line_arr):
        coords = np.array(line.coords)

        if math.hypot(coords[-1, 0] - coords[0, 0], coords[-1, 1] - coords[0, 1]) < tolerance:
            # Build R-tree from previous geometries
            tree = STRtree(line_arr[:i])
            p = Polygon(coords)
            geom_idx = [line_arr.index(g) for g in tree.query(p)]

            # Update previous geometries
            for gi in geom_idx:
                line_arr[gi] = line_arr[gi].difference(p)

    new_lines = LineCollection()
    for line in line_arr:
        if isinstance(line, LineString):
            new_lines.append(line)
        elif isinstance(line, MultiLineString):
            new_lines.extend(line)

    return new_lines


occult.help_group = "Plugins"
