from typing import TYPE_CHECKING

from magicgui import magic_factory
from magicgui.widgets import Label, Container, Button, create_widget
from qtpy.QtCore import Qt
import skimage.filters.thresholding as st
from napari.layers import Image, Labels
import napari.types


if TYPE_CHECKING:
    import napari

"""
For thresholding, a single widget is defined that can be used for all thresholding methods. No options are available.
Manual thresholding is handled via a Container class definition. The main reason for this is that the threshold value
needs to be updated based on the image and more options (e.g. multi-threshold) can be added in the future.
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


class ManualThresholdWidget(Container):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self._viewer = viewer
        # use create_widget to generate widgets from type annotations
        self._image_layer_combo = create_widget(
            label="Image", annotation="napari.layers.Image"
        )

        self.threshold = create_widget(
            label="Threshold value", annotation=float,
            options={'value': 0, 'min': 0, 'max': 255, 'step': 1}
        )

        self.btn_apply = Button(text="Apply Thresholding")
        self.btn_apply.clicked.connect(self.apply_threshold)

        # append into/extend the container with your widgets
        self.extend(
            [
                self._image_layer_combo,
                self.threshold,
                self.btn_apply,
            ]
        )

        self._image_layer_combo.changed.connect(self._on_update_threshold_limits)
        self._on_update_threshold_limits(self)

    def _on_update_threshold_limits(self, event=None):
        image_layer = self._image_layer_combo.value
        if image_layer is None:
            return
        if (self.threshold.value > image_layer.data.max()) or (self.threshold.value < image_layer.data.min()):
            self.threshold.value = image_layer.data.min()
        # setting the minimum creates the following problem. If the mimimum
        # is set to 7 and one wants to input 100, starting to type 1 turns it
        # automatically to 7. Leaving at 0 for the moment
        # self.threshold.min = image_layer.data.min()
        self.threshold.max = image_layer.data.max()
        self.threshold.step = (self.threshold.max - self.threshold.min) / 100

    def apply_threshold(self, event=None):
        image_layer = self._image_layer_combo.value
        if image_layer is None:
            return
        mask = image_layer.data > self.threshold.value
        self._viewer.add_labels(
            mask,
            name=f"{image_layer.name}_threshold_manual",
        )