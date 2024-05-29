from typing import TYPE_CHECKING

import numpy as np
from magicgui import magic_factory
import skimage.util
from napari.layers import Image
import napari.types


if TYPE_CHECKING:
    import napari

@magic_factory(
        image_layer={'label': 'Image'},
        operation={'choices': ['square', 'sqrt', 'log', 'log10', 'exp']},
        call_button="Apply operation"
        )
def simple_maths_widget(
    image_layer: Image, operation='sqrt'
) -> napari.types.LayerDataTuple:
    if operation == 'square':
        fun = lambda x: x.astype(np.float32)**2
    else:
        fun = getattr(np, f'{operation}')
    out = fun(image_layer.data)
    return (
        out,
        {'name': f'{image_layer.name}_{operation}'},
        'image')

@magic_factory(
        image_layer={'label': 'Image'},
        image_layer2={'label': 'Image 2'},
        operation={'choices': ['add', 'subtract', 'multiply', 'divide']},
        call_button="Apply operation"
        )
def maths_image_pairs_widget(
    image_layer: Image, image_layer2: Image, operation='add'
) -> napari.types.LayerDataTuple:
    if operation == 'add':
        out = image_layer.data + image_layer2.data
    elif operation == 'subtract':
        out = image_layer.data - image_layer2.data
    elif operation == 'multiply':
        out = image_layer.data * image_layer2.data
    elif operation == 'divide':
        out = image_layer.data / image_layer2.data
    return (
        out,
        {'name': f'Result_{operation}'},
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
