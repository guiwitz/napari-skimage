from typing import TYPE_CHECKING

import numpy as np
from magicgui.widgets import Button, Container, create_widget, Label
from qtpy.QtCore import Qt
from napari.layers import Image
import napari.types
from typing import Union



if TYPE_CHECKING:
    import napari
    
class AxisWidget(Container):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        
        self._viewer = viewer

        self._image_layer_combo = create_widget(
            label="Image", annotation="napari.layers.Layer"
        )
        self.operation = create_widget(
            label="Operation type", annotation=str, widget_type="ComboBox",
            options={'choices':['flip', 'swapaxes', 'squeeze', 'moveaxis', 'expand_dims']}
        )

        self.axis1 = create_widget(
            label="Axis 1", annotation=int, widget_type="SpinBox",
            options={'min': 0, 'max': 1}
        )

        self.axis2 = create_widget(
            label="Axis 2", annotation=int, widget_type="SpinBox",
            options={'min': 0, 'max': 1}
        )

        self.image_shape = create_widget(
            label="Image shape", annotation=tuple, widget_type="Label"
        )

        self.btn_apply = Button(text="Apply operation")
        self.btn_apply.clicked.connect(self._apply_operation)

        self.link_label = Label(value='')
        self.link_label.native.setTextFormat(Qt.RichText)
        self.link_label.native.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.link_label.native.setOpenExternalLinks(True)

        # append into/extend the container with your widgets
        self.extend(
            [
                self._image_layer_combo,
                self.operation,
                self.axis1,
                self.axis2,
                self.btn_apply,
                self.image_shape,
                self.link_label
            ]
        )

        self._image_layer_combo.changed.connect(self._on_update_axis)
        self.operation.changed.connect(self._on_update_axis)
        self._on_update_axis()

    def _on_update_axis(self, event=None):

        if self._image_layer_combo.value is not None:
            self.axis1.min = 0
            self.axis1.max = len(self._image_layer_combo.value.data.shape) - 1
            self.axis2.min = 0
            self.axis2.max = len(self._image_layer_combo.value.data.shape) - 1

            self.image_shape.value = self._image_layer_combo.value.data.shape

        self.link_label.value = f'<a href=\"https://numpy.org/doc/stable/reference/generated/numpy.{self.operation.value}.html\">numpy.{self.operation.value}</a>'

    def _apply_operation(self):

        if not isinstance(self._image_layer_combo.value, napari.layers.Image) and not isinstance(self._image_layer_combo.value, napari.layers.Labels):
            return
        
        if self.operation.value == 'flip':
            image_modif = np.flip(self._image_layer_combo.value.data, axis=self.axis1.value)
        elif self.operation.value == 'swapaxes':
            image_modif = np.swapaxes(self._image_layer_combo.value.data, self.axis1.value, self.axis2.value)
        elif self.operation.value == 'squeeze':
            image_modif = np.squeeze(self._image_layer_combo.value.data)
        elif self.operation.value == 'moveaxis':
            image_modif = np.moveaxis(self._image_layer_combo.value.data, self.axis1.value, self.axis2.value)
        elif self.operation.value == 'expand_dims':
            image_modif = np.expand_dims(self._image_layer_combo.value.data, axis=self.axis1.value)

        if isinstance(self._image_layer_combo.value, napari.layers.Image):
            self._viewer.add_image(
                image_modif,
                name=f"{self._image_layer_combo.value.name}_{self.operation.value}",
                colormap=self._image_layer_combo.value.colormap,
            )
        elif isinstance(self._image_layer_combo.value, napari.layers.Labels):
            self._viewer.add_labels(
                image_modif,
                name=f"{self._image_layer_combo.value.name}_{self.operation.value}",
            )
