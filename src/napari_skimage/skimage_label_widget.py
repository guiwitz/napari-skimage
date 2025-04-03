from typing import TYPE_CHECKING

import napari.types
from magicgui import magic_factory
from magicgui.widgets import Label
from napari.layers import Labels
from napari.utils.notifications import show_info
from qtpy.QtCore import Qt
from skimage.measure import label

if TYPE_CHECKING:
    import napari
    from magicgui.widgets import Widget


def _on_init_label(widget: "Widget") -> None:
    label_widget = Label(value="")
    label_widget.value = '<a href="https://scikit-image.org/docs/stable/api/skimage.measure.html#skimage.measure.label">skimage.measure.label</a>'
    label_widget.native.setTextFormat(Qt.RichText)
    label_widget.native.setTextInteractionFlags(Qt.TextBrowserInteraction)
    label_widget.native.setOpenExternalLinks(True)
    widget.extend([label_widget])

    # Dynamically update the max value of connectivity based on labels_layer.ndim
    @widget.labels_layer.changed.connect
    def update_connectivity_range(event: object) -> None:
        """Update the max value of connectivity based on labels_layer.ndim
        
        Also ensures that the default value of connectivity is set to the
        ndim, which matches the skimage default behavior."""
        if widget.labels_layer.value is not None:
            widget.connectivity.value = widget.labels_layer.value.data.ndim
            widget.connectivity.max = widget.labels_layer.value.data.ndim


    update_connectivity_range(None)  # Initialize the range


@magic_factory(
    labels_layer={"label": "Labels Layer"},
    connectivity={"label": "Connectivity", "min": 1, "step": 1},
    call_button="Label connected components",
    widget_init=_on_init_label,
)
def label_widget(
    labels_layer: Labels,
    connectivity: int = 1,
    background: int = 0,
) -> napari.types.LayerDataTuple:
    labeled_array, number = label(
        labels_layer.data,
        connectivity=connectivity,
        background=background,
        return_num=True,
    )
    show_info(f"Labeled {number} regions")
    return (
        (labeled_array,),
        {"name": f"{labels_layer.name}_labeled"},
        "labels",
    )
