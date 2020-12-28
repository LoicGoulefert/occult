# Standard libs
import math

# Third party libs
import click
import numpy as np
import pygeos
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
        $ vpype line 0 0 5 5 rect 2 2 1 1 occult show  # line is occulted by rect

        $ vpype rect 2 2 1 1 line 0 0 5 5 occult show  # line is NOT occulted by rect,
        as the line is drawn after the rectangle.
    """

    line_arr = np.array(
        [pygeos.linestrings(list(zip(line.real, line.imag))) for line in lines]
    )

    for i, line in enumerate(line_arr):
        coords = pygeos.get_coordinates(line)

        if math.hypot(coords[-1, 0] - coords[0, 0], coords[-1, 1] - coords[0, 1]) < tolerance:
            tree = pygeos.STRtree(line_arr[:i])
            p = pygeos.polygons(coords)
            geom_idx = tree.query(p, predicate="intersects")
            line_arr[geom_idx] = pygeos.set_operations.difference(line_arr[geom_idx], p)

    new_lines = LineCollection()
    for geom in line_arr:
        for i in range(pygeos.get_num_geometries(geom)):
            coords = pygeos.get_coordinates(pygeos.get_geometry(geom, i))
            new_lines.append(coords[:, 0] + coords[:, 1] * 1j)

    return new_lines


occult.help_group = "Plugins"
