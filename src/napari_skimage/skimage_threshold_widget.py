from typing import TYPE_CHECKING

from magicgui import magic_factory
import skimage.filters.thresholding as st
from napari.layers import Image, Labels
import napari.types


if TYPE_CHECKING:
    import napari

    
@magic_factory(
        img_layer={'label': 'Image'},
        method={'choices': ['otsu', 'li', 'mean', 'yen', 'sauvola']},
        call_button="Apply Thresholding"
        )
def threshold_widget(
    img_layer: Image,
    method = "otsu",
) -> napari.types.LayerDataTuple:
    fun = getattr(st, f'threshold_{method}')
    th = fun(img_layer.data)
    mask = img_layer.data > th
    return (
        mask,
        {'name': f'{img_layer.name}_threshold_{method}'},
        'labels')