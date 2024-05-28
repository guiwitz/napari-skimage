from typing import TYPE_CHECKING

import numpy as np
from magicgui import magic_factory
from magicgui.widgets import CheckBox, Container, create_widget
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget
from skimage.util import img_as_float
import skimage.filters as sf
import skimage.morphology as sm
from napari.layers import Image
import napari.types


if TYPE_CHECKING:
    import napari

@magic_factory(
        image_layer={'label': 'Image'},
        mode={'choices': ['reflect', 'constant', 'nearest', 'mirror', 'wrap']},
        call_button="Apply Farid filter"
        )
def farid_filter_widget(
    image_layer: Image, mode='reflect') -> napari.types.LayerDataTuple:
    return (
        sf.farid(image_layer.data, mode=mode),
        {'name': f'{image_layer.name}_farid'},
        'image')

@magic_factory(
        image_layer={'label': 'Image'},
        mode={'choices': ['reflect', 'constant', 'nearest', 'mirror', 'wrap']},
        call_button="Apply Prewitt filter"
        )
def prewitt_filter_widget(
    image_layer: Image, mode='reflect') -> napari.types.LayerDataTuple:
    return (
        sf.prewitt(image_layer.data, mode=mode),
        {'name': f'{image_layer.name}_prewitt'},
        'image')

@magic_factory(
        image_layer={'label': 'Image'},
        call_button="Apply Laplace filter"
        )
def laplace_filter_widget(
    image_layer: Image,
    ksize: int = 3.0) -> napari.types.LayerDataTuple:
    return (
        sf.laplace(image_layer.data, ksize=ksize),
        {'name': f'{image_layer.name}_laplace'},
        'image')
    
@magic_factory(
        img_layer={'label': 'Image'},
        mode={'choices': ['reflect', 'constant', 'nearest', 'mirror', 'wrap']},
        call_button="Apply Gaussian Filter"
        )
def gaussian_filter_widget(
    img_layer: Image,
    sigma: float = 1.0,
    preserve_range: bool = False,
    mode = "reflect",
) -> napari.types.LayerDataTuple:
    return (
        sf.gaussian(img_layer.data, sigma=sigma, preserve_range=preserve_range, mode=mode),
        {'name': f'{img_layer.name}_gaussian_σ={sigma}'},
        'image')

@magic_factory(
        img_layer={'label': 'Image'},
        mode={'choices': ['reflect', 'constant', 'nearest', 'mirror', 'wrap']},
        call_button="Apply Frangi Filter"
        )
def frangi_filter_widget(
    img_layer: Image,
    scale_start: float = 1.0,
    scale_end: float = 10.0,
    scale_step: float = 2.0,
    mode = "reflect",
    black_ridges: bool = True,
) -> napari.types.LayerDataTuple:
    return (
        sf.frangi(img_layer.data, sigmas=np.arange(scale_start, scale_end, scale_step),
                  black_ridges=black_ridges, mode=mode),
        {'name': f'{img_layer.name}_frangi'},
        'image')

@magic_factory(
    img_layer={'label': 'Image'},
    mode={'choices': {'reflect', 'constant', 'nearest', 'mirror', 'wrap'}},
    footprint={'label': 'Footprint', 'choices': ['disk', 'square', 'diamond', 'star', 'octagon']},
    footprint_size={'label': 'Footprint size', 'max': 100, 'min': 1, 'step': 1},
    call_button="Apply operation"
)
def median_filter_widget(
    img_layer: Image,
    footprint = "disk",
    footprint_size = 3,
    mode = "nearest"
) -> napari.types.LayerDataTuple:
    fun_footprint = getattr(sm, footprint)
    selem = fun_footprint(footprint_size)
    img_filtered = sf.median(img_layer.data, footprint=selem, mode=mode)
    return (
        img_filtered,
        {'name': f'{img_layer.name}_median'},
        'image')