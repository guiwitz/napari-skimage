from typing import TYPE_CHECKING

from magicgui import magic_factory
from magicgui.widgets import Label
from qtpy.QtCore import Qt
import skimage.filters.thresholding as st
from napari.layers import Image, Labels
import napari.types


if TYPE_CHECKING:
    import napari

"""
For thresholding, a single widget is defined that can be used for all thresholding methods. No options are available.
"""

def _on_init(widget):
    label_widget = Label(value='')   
    
    func_name = widget.method.value
    label_widget.value = f'<a href=\"https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_{func_name}\">skimage.filters.threshold_{func_name}</a>'
    label_widget.native.setTextFormat(Qt.RichText)
    label_widget.native.setTextInteractionFlags(Qt.TextBrowserInteraction)
    label_widget.native.setOpenExternalLinks(True)
    widget.extend([label_widget])

    widget.method.changed.connect(lambda x: setattr(label_widget, 'value', f'<a href=\"https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_{x}\">skimage.filters.threshold_{x}</a>'))
    
@magic_factory(
        img_layer={'label': 'Image'},
        method={'choices': ['otsu', 'li', 'mean', 'yen', 'sauvola']},
        call_button="Apply Thresholding",
        widget_init=_on_init
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