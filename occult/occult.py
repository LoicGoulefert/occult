# Standard libs
import math
from typing import Union, List, Optional

# Third party libs
import click
import numpy as np
from shapely.geometry import LineString, Polygon
from shapely.geometry.multilinestring import MultiLineString
from shapely.strtree import STRtree
from vpype import global_processor, LineCollection, LengthType, multiple_to_layer_ids
import vpype


def add_to_linecollection(lc, line):
    """Helper function to add a LineString or a MultiLineString to a LineCollection"""
    if isinstance(line, LineString) and len(line.coords) != 0:
        lc.append(line)
    elif isinstance(line, MultiLineString):
        lc.extend(line)

    return None


def _occult_layer(
    lines: LineCollection, tolerance: float, keep_occulted: bool = False
) -> LineCollection:
    """
    Perform per-layer occlusion. Optionally returns occulted lines
    in a separate LineCollection.

    Args:
        lines: LineCollection to perform occlusion on
        tolerance: Max distance between start and end point to consider a path closed
        keep_occulted: if True, save removed lines in removed_lines LineCollection.
        Otherwise, removed_lines is an empty LineCollection.

    Returns:
        a tuple of LineCollections, (new_lines, removed_lines)
    """
    removed_lines = LineCollection()
    line_arr = [line for line in lines.as_mls()]

    for i, line in enumerate(line_arr):
        coords = np.array(line.coords)

        if (
            len(coords) > 3
            and math.hypot(coords[-1, 0] - coords[0, 0], coords[-1, 1] - coords[0, 1])
            < tolerance
        ):
            # Build R-tree from previous geometries
            tree = STRtree(line_arr[:i])
            p = Polygon(coords)
            geom_idx = [line_arr.index(g) for g in tree.query(p)]

            for gi in geom_idx:
                # Aggregate removed lines
                if keep_occulted:
                    rl = p.intersection(line_arr[gi])
                    add_to_linecollection(removed_lines, rl)

                # Update previous geometries
                line_arr[gi] = line_arr[gi].difference(p)

    new_lines = LineCollection()
    for line in line_arr:
        add_to_linecollection(new_lines, line)

    return new_lines, removed_lines


@click.command()
@click.option(
    "-t",
    "--tolerance",
    type=LengthType(),
    default="0.01mm",
    help="Max distance between start and end point to consider a path closed"
    "(default: 0.01mm)",
)
@click.option(
    "-k",
    "--keep-occulted",
    is_flag=True,
    default=False,
    help="Save the occulted lines on a different layer",
)
@click.option(
    "-l",
    "--layer",
    type=vpype.LayerType(accept_multiple=True),
    default="all",
    help="Target layer(s).",
)
@global_processor
def occult(
    document: vpype.Document,
    tolerance: float,
    layer: Optional[Union[int, List[int]]],
    keep_occulted: bool = False,
) -> vpype.Document:
    """
    Remove lines occulted by polygons.
    The 'keep_occulted' option (-k, --keep-occulted) saves removed geometries in a new layer.
    The order of the geometries in 'lines' matters, see basic example below.
    Occlusion is performed layer by layer. This means that if one geometry is occulting another,
    and these geometries are not in the same layer, occult won't remove occulted paths.

    Args:
        document: the vpype.Document to work on.
        tolerance: controls the distance tolerance between the first and last points
        of a geometry to consider it closed.
        layer: specify which layer(s) to work on. Default: all.
        keep_occulted: If set, this flag allows to save removed lines in a separate layer.

    Examples:

        - Basic usage:
            $ vpype line 0 0 5cm 5cm rect 2cm 2cm 1cm 1cm occult show  # line is occulted by rect
            $ vpype rect 2cm 2cm 1cm 1cm line 0 0 5cm 5cm occult show  # line is NOT occulted by rect,
            as the line is drawn after the rectangle.

        - Keep occulted lines in a separate layer:
            $ vpype line -- -3cm 0 8cm 0  circle 0 0 3cm  circle -l 2 5cm 0 3cm occult -k show
            # 'occult -k' will remove the path inside the first circle, and put it in a third layer.
            # both the first circle and the line are not affected by the second circle, as it is
            # in a different layer.
    """

    new_document = document.empty_copy()
    layer_ids = multiple_to_layer_ids(layer, document)
    removed_layer_id = document.free_id()

    for lines, l_id in zip(document.layers_from_ids(layer_ids), layer_ids):
        lines, removed_lines = _occult_layer(lines, tolerance, keep_occulted)
        new_document.add(lines, layer_id=l_id)

        if keep_occulted and not removed_lines.is_empty():
            new_document.add(removed_lines, layer_id=removed_layer_id)

    return new_document


occult.help_group = "Plugins"
