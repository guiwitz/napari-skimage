from typing import TYPE_CHECKING

import numpy as np
from magicgui import magic_factory
from magicgui.widgets import CheckBox, Container, create_widget
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget
import skimage.util
import skimage.filters as sf
from napari.layers import Image
import napari.types


if TYPE_CHECKING:
    import napari

@magic_factory(
        image_layer={'label': 'Image'},
        image_layer2={'label': 'Image 2'},
        mode={'choices': ['add', 'subtract', 'multiply', 'divide']},
        call_button="Apply operation"
        )
def simple_maths_widget(
    image_layer: Image, image_layer2: Image, mode='add'
) -> napari.types.LayerDataTuple:
    if mode == 'add':
        out = image_layer.data + image_layer2.data
    elif mode == 'subtract':
        out = image_layer.data - image_layer2.data
    elif mode == 'multiply':
        out = image_layer.data * image_layer2.data
    elif mode == 'divide':
        out = image_layer.data / image_layer2.data
    return (
        out,
        {'name': f'Result_{mode}'},
        'image')

@magic_factory(
        image_layer={'label': 'Image'},
        mode={'choices': ['uint8', 'uint16', 'float32', 'float64']},
        call_button="Apply operation"
        )
def conversion_widget(
    image_layer: Image, mode='uint8',
) -> napari.types.LayerDataTuple:
    if mode == 'uint8':
        out = skimage.util.img_as_ubyte(image_layer.data)
    if mode == 'uint16':
        out = skimage.util.img_as_uint(image_layer.data)
    elif mode == 'float32':
        out = skimage.util.img_as_float32(image_layer.data)
    elif mode == 'float64':
        out = skimage.util.img_as_float64(image_layer.data)
    return (
        out,
        {'name': f'{image_layer.name}_{mode}'},
        'image')
