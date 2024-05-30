from typing import TYPE_CHECKING

import numpy as np
from magicgui import magic_factory
from magicgui.widgets import Label
from qtpy.QtCore import Qt
import skimage.restoration as sr
from napari.layers import Image
import napari.types


if TYPE_CHECKING:
    import napari

'''
In this module, widgets for restoration methods are defined one by one. The _on_init function that can be used
with the widget_init argument of @magic_factory adds a hyperlink to the documentation of the function that the
widget is calling. For this to work properly, the widget function needs to be named
"<skimage function name>_restoration_widget".
'''

def _on_init(widget):
    label_widget = Label(value='')   
    
    func_name = '_'.join(widget.label.split(' ')[0:-2])
    label_widget.value = f'<a href=\"https://scikit-image.org/docs/stable/api/skimage.restoration.html#skimage.restoration.{func_name}\">skimage.restoration.{func_name}</a>'
    label_widget.native.setTextFormat(Qt.RichText)
    label_widget.native.setTextInteractionFlags(Qt.TextBrowserInteraction)
    label_widget.native.setOpenExternalLinks(True)
    widget.extend([label_widget])

@magic_factory(
        image_layer={'label': 'Image'},
        call_button="Apply rolling ball",
        widget_init=_on_init
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
        call_button="Apply denoise nl means",
        widget_init=_on_init
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