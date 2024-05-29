from typing import TYPE_CHECKING

import numpy as np
from magicgui import magic_factory
import skimage.restoration as sr
from napari.layers import Image
import napari.types


if TYPE_CHECKING:
    import napari

@magic_factory(
        image_layer={'label': 'Image'},
        call_button="Apply rolling ball"
        )
def rolling_ball_restoration_widget(
    image_layer: Image, 
    radius: int = 100) -> napari.types.LayerDataTuple:
    return (
        sr.rolling_ball(image_layer.data, radius=radius),
        {'name': f'{image_layer.name}_rolling_ball'},
        'image')

@magic_factory(
        image_layer={'label': 'Image'},
        call_button="Apply denoise nl means"
        )
def denoise_nl_means_restoration_widget(
    image_layer: Image, 
    patch_distance: int = 11,
    h: float = 0.1,
    fast_mode: bool = True,
    sigma: float = 0.0,
    preserve_range : bool = False) -> napari.types.LayerDataTuple:
    return (
        sr.denoise_nl_means(image_layer.data, patch_distance=patch_distance,
                        h=h, fast_mode=fast_mode, sigma=sigma,
                        preserve_range=preserve_range),
        {'name': f'{image_layer.name}_denoise_nl_means'},
        'image')