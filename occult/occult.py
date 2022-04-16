# Standard libs
import math
from typing import Dict, List, Optional, Tuple, Union

# Third party libs
import click
import numpy as np
import vpype as vp
import vpype_cli
from shapely.geometry import LineString, MultiLineString, Polygon
from shapely.strtree import STRtree


def add_to_linecollection(lc, line):
    """Helper function to add a LineString or a MultiLineString to a LineCollection"""
    if isinstance(line, LineString) and len(line.coords) != 0:
        lc.append(line)
    elif isinstance(line, MultiLineString):
        lc.extend(line)

    return None


def _occult_layer(
    layers: Dict[int, vp.LineCollection], tolerance: float, keep_occulted: bool = False
) -> Tuple[Dict[int, vp.LineCollection], vp.LineCollection]:
    """
    Perform occlusion on all provided layers. Optionally returns occulted lines
    in a separate LineCollection.

    Args:
        layers: dictionary of LineCollections to perform occlusion on, keyed by layer ID
        tolerance: Max distance between start and end point to consider a path closed
        keep_occulted: if True, save removed lines in removed_lines LineCollection.
        Otherwise, removed_lines is an empty LineCollection.

    Returns:
        a tuple with two items:
        - new_lines, a dictionary of LineCollections for each layer ID received
        - removed_lines, a LineCollection of removed lines
    """
    removed_lines = vp.LineCollection()
    new_lines = {l_id: vp.LineCollection() for l_id in layers}

    line_arr = []
    line_arr_lines = []
    for l_id, lines in layers.items():
        line_arr.extend([[l_id, line] for line in lines.as_mls().geoms])
        line_arr_lines.extend([line for line in lines.as_mls().geoms])

    # Build R-tree from previous geometries
    tree = STRtree(line_arr_lines)
    index_by_id = dict((id(pt), i) for i, pt in enumerate(line_arr_lines))

    for i, (l_id, line) in enumerate(line_arr):
        coords = np.array(line.coords)

        if not (
            len(coords) > 3
            and math.hypot(coords[-1, 0] - coords[0, 0], coords[-1, 1] - coords[0, 1])
            < tolerance
        ):
            continue

        p = Polygon(coords)

        if not p.is_valid:
            continue

        geom_idx = [index_by_id[id(g)] for g in tree.query(p)]
        geom_idx = [idx for idx in geom_idx if idx < i]

        for gi in geom_idx:
            # Aggregate removed lines
            if keep_occulted:
                rl = p.intersection(line_arr_lines[gi])
                add_to_linecollection(removed_lines, rl)

            # Update previous geometries
            line_arr[gi][1] = line_arr[gi][1].difference(p)

    for (l_id, line) in line_arr:
        add_to_linecollection(new_lines[l_id], line)

    return new_lines, removed_lines


@click.command()
@click.option(
    "-t",
    "--tolerance",
    type=vpype_cli.LengthType(),
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
    type=vpype_cli.LayerType(accept_multiple=True),
    default="all",
    help="Target layer(s).",
)
@click.option(
    "-i",
    "--ignore-layers",
    is_flag=True,
    default=False,
    help="Ignore layers when performing occlusion",
)
@click.option(
    "-r",
    "--reverse",
    is_flag=True,
    default=False,
    help="Reverse geometry order",
)
@vpype_cli.global_processor
def occult(
    document: vp.Document,
    tolerance: float,
    layer: Optional[Union[int, List[int]]],
    keep_occulted: bool = False,
    ignore_layers: bool = False,
    reverse: bool = False,
) -> vp.Document:
    """
    Remove lines occulted by polygons.
    The 'keep_occulted' option (-k, --keep-occulted) saves removed geometries in a new layer.
    The order of the geometries in 'lines' matters, see basic example below.
    Occlusion is performed layer by layer. This means that if one geometry is occulting another,
    and these geometries are not in the same layer, occult won't remove occulted paths.
    With the 'ignore_layers' option, occlusion is performed on all geometry regardless
    of layers, with higher-numbered layers occluding lower-numbered layers.

    Args:
        document: the vpype.Document to work on.
        tolerance: controls the distance tolerance between the first and last points
        of a geometry to consider it closed.
        layer: specify which layer(s) to work on. Default: all.
        keep_occulted: If set, this flag allows to save removed lines in a separate layer.
        ignore_layers: If set, this flag causes occult to treat all geometries as if they
        exist on the same layer. However, all geometries in the final result
        remain on their original layer.

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
    new_document = document.empty_copy(keep_layers=True)
    layer_ids = vpype_cli.multiple_to_layer_ids(layer, document)
    removed_layer_id = document.free_id()

    if ignore_layers:
        layers = [{l_id: list(document.layers_from_ids([l_id]))[0] for l_id in layer_ids}]
    else:
        layers = [{l_id: list(document.layers_from_ids([l_id]))[0]} for l_id in layer_ids]

    if reverse:
        for layer in layers:
            for key in layer:
                layer[key].reverse()

    for layer in layers:
        lines, removed_lines = _occult_layer(layer, tolerance, keep_occulted)

        for l_id, occulted_lines in lines.items():
            new_document.add(occulted_lines, layer_id=l_id)

        if keep_occulted and not removed_lines.is_empty():
            new_document.add(removed_lines, layer_id=removed_layer_id)

    return new_document


occult.help_group = "Plugins"
