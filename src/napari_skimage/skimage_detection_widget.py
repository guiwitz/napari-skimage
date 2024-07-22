from typing import TYPE_CHECKING
import numpy as np
from magicgui import magic_factory
from skimage.feature import peak_local_max
from skimage.measure import marching_cubes
from napari.layers import Image, Labels
import napari.types

if TYPE_CHECKING:
    import napari

@magic_factory(
    image_layer={'label': 'Image'},
    min_distance={'label': 'Minimum Distance'},
    threshold_absolute={'label': 'Threshold Absolute'},
    threshold_relative={'label': 'Threshold Relative', 'min': 0.0, 'max': 1.0},
    call_button="Detect Local Maxima"
)
def peak_local_max_widget(
    image_layer: Image,
    min_distance: int = 10,
    threshold_absolute: float = 0,
    threshold_relative: float = 0.0
) -> napari.types.LayerDataTuple:
    coordinates = peak_local_max(image_layer.data,
                                 min_distance=min_distance,
                                 threshold_abs=threshold_absolute,
                                 threshold_rel=threshold_relative)
    return (
        coordinates,
        {'name': f'{image_layer.name}_local_maxima'},
        'points'
    )

@magic_factory(
    label_layer={'label': 'Labels'},
    label={'label': 'Label'},
    binarize={'label': 'Binarize'},
    call_button="Apply Marching Cubes"
)
def marching_cubes_widget(
    label_layer: Labels,
    label: int = 1,
    binarize: bool = False
) -> napari.types.LayerDataTuple:
    if binarize:
        data = (label_layer.data > 0).astype(int)
    else:
        data = (label_layer.data == label).astype(int)
    verts, faces, _, _ = marching_cubes(data, level=0.5)
    return (
        (verts, faces.astype(int)),
        {'name': f'{label_layer.name}_surface'},
        'surface'
    )
