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
    """

    line_arr = np.array(
        [pygeos.linestrings(list(zip(line.real, line.imag))) for line in lines]
    )

    for i, line in enumerate(line_arr):
        coords = pygeos.get_coordinates(line)

        if math.hypot(coords[-1, 0] - coords[0, 0], coords[-1, 1] - coords[0, 1]) < tolerance:
            p = pygeos.polygons(coords)
            idx = pygeos.intersects(line_arr[:i], p)
            line_arr[:i][idx] = pygeos.set_operations.difference(line_arr[:i][idx], p)

    new_lines = LineCollection()
    for geom in line_arr:
        for i in range(pygeos.get_num_geometries(geom)):
            coords = pygeos.get_coordinates(pygeos.get_geometry(geom, i))
            new_lines.append(coords[:, 0] + coords[:, 1] * 1j)

    return new_lines


occult.help_group = "Plugins"
