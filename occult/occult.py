# Standard libs
import math

# Third party libs
import click
import numpy as np
from shapely.geometry import Polygon, MultiLineString
from shapely.ops import unary_union
from vpype import layer_processor, LineCollection, Length, as_vector
import pygeos


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

    line_arr = np.array(
        [pygeos.linestrings(list(zip(line.real, line.imag))) for line in lines]
    )

    for i, line in enumerate(line_arr):
        coords = pygeos.get_coordinates(line)

        if math.hypot(coords[-1, 0] - coords[0, 0], coords[-1, 1] - coords[0, 1]) < tolerance:
            p = pygeos.polygons(coords)
            line_arr[:i] = pygeos.set_operations.difference(line_arr[:i], p)

    new_lines = LineCollection()
    for geom in line_arr:
        for i in range(pygeos.get_num_geometries(geom)):
            coords = pygeos.get_coordinates(pygeos.get_geometry(geom, i))
            new_lines.append(coords[:, 0] + coords[:, 1] * 1j)

    return new_lines


occult.help_group = "Plugins"
