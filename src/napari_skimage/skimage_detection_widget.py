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
    threshold_abs={'label': 'Threshold Absolute'},
    call_button="Detect Local Maxima"
)
def peak_local_max_widget(
    image_layer: Image,
    min_distance: int = 1,
    threshold_abs: float = 0
) -> napari.types.LayerDataTuple:
    coordinates = peak_local_max(image_layer.data, min_distance=min_distance, threshold_abs=threshold_abs)
    return (
        coordinates,
        {'name': f'{image_layer.name}_local_maxima'},
        'points'
    )

@magic_factory(
    label_layer={'label': 'Labels'},
    level={'label': 'Level'},
    call_button="Apply Marching Cubes"
)
def marching_cubes_widget(
    label_layer: Labels,
    level: float = 0.0
) -> napari.types.LayerDataTuple:
    verts, faces, _, _ = marching_cubes(label_layer.data, level=level)
    return (
        (verts, faces.astype(int)),
        {'name': f'{label_layer.name}_surface'},
        'surface'
    )
