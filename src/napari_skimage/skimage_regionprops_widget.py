from typing import TYPE_CHECKING
from magicgui import magic_factory
from magicgui.widgets import Table, Label
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QAbstractItemView
from skimage.measure import regionprops_table
from skimage.measure._regionprops import PROPS
import pandas as pd
from napari.layers import Image, Labels
import napari
import napari.types
from napari.utils.notifications import show_warning

if TYPE_CHECKING:
    from magicgui.widgets import Widget

# Get the list of available properties for RegionProperties
available_properties = set(PROPS.values())

# Hard-code the properties that are only valid for 2D images
only_2d_properties = {
    "eccentricity",
    "moments_hu",
    "orientation",
    "perimeter",
    "perimeter_crofton",
    "moments_weighted_hu",
}

valid_properties_3d = available_properties - only_2d_properties


def _on_init(widget: "Widget"):
    """Initialize the widget, add a hyperlink, and set up connections."""
    # Add a hyperlink to the documentation
    label_widget = Label(value="")
    label_widget.value = '<a href="https://scikit-image.org/docs/stable/api/skimage.measure.html#skimage.measure.regionprops_table">skimage.measure.regionprops_table</a>'
    label_widget.native.setTextFormat(Qt.RichText)
    label_widget.native.setTextInteractionFlags(Qt.TextBrowserInteraction)
    label_widget.native.setOpenExternalLinks(True)
    widget.extend([label_widget])

    # Define a function to get valid properties dynamically
    def get_valid_properties(widget: "Widget"):
        labels_layer = widget.labels_layer.value
        if labels_layer:
            is_2d = labels_layer.data.ndim == 2
            return sorted(available_properties) if is_2d else sorted(valid_properties_3d)
        else:
            return []

    # Update the properties choices dynamically
    def update_properties_choices(event: object):
        widget.properties.choices = []
        widget.properties.reset_choices()

    # Enable or disable the Analyze button based on input validation
    def update_analyze_button_state(event: object):
        labels_layer = widget.labels_layer.value
        image_layer = widget.image_layer.value

        if labels_layer and image_layer:
            shapes_match = labels_layer.data.shape == image_layer.data.shape
            if not shapes_match:
                show_warning(
                    "Shape mismatch: Labels Layer and Intensity Image must have the same shape."
                )
            widget.call_button.enabled = shapes_match
        else:
            widget.call_button.enabled = False

    # Connect the signals to the update functions
    widget.labels_layer.changed.connect(update_properties_choices)
    widget.image_layer.changed.connect(update_properties_choices)
    widget.labels_layer.changed.connect(update_analyze_button_state)
    widget.image_layer.changed.connect(update_analyze_button_state)

    # initialize Select widget and button state
    widget.properties._default_choices = lambda _: get_valid_properties(widget)
    update_properties_choices(widget)
    update_analyze_button_state(widget)

@magic_factory(
    image_layer={"label": "Intensity Image Layer"},
    labels_layer={"label": "Labels Layer"},
    properties={
        "label": "Properties",
        "widget_type": "Select",
        "allow_multiple": True,
    },
    call_button="Analyze",
    widget_init=_on_init,
)
def regionprops_widget(
    image_layer: Image, labels_layer: Labels, properties: list[str]
) -> napari.types.LayerDataTuple:
    """Widget to compute regionprops_table and display results."""
    if labels_layer.data.shape != image_layer.data.shape:
        show_warning("Labels Layer and Intensity Image must have the same shape.")
        return

    # Compute regionprops_table
    props = regionprops_table(
        label_image=labels_layer.data,
        intensity_image=image_layer.data,
        properties=properties,
        spacing=image_layer.scale,
    )

    # Convert to DataFrame
    results_df = pd.DataFrame(props)

    viewer =  napari.current_viewer()
     # Check if the dock widget exists and is still valid
    if (
        not hasattr(regionprops_widget, "_results_dock_widget")
        or regionprops_widget._results_dock_widget.widget is None
    ):
        regionprops_widget.results_table = Table(value=results_df, name="Results Table")
        regionprops_widget.results_table.read_only = True

        regionprops_widget._results_dock_widget = viewer.window.add_dock_widget(
            regionprops_widget.results_table, area="bottom", name="Results Table"
        )
    else:
        try:
            regionprops_widget.results_table.value = results_df
            regionprops_widget.results_table.read_only = True

            regionprops_widget._results_dock_widget.show()
        except RuntimeError:
            regionprops_widget.results_table = Table(
                value=results_df, name="Results Table"
            )
            regionprops_widget.results_table.read_only = True

            regionprops_widget._results_dock_widget = viewer.window.add_dock_widget(
                regionprops_widget.results_table, area="bottom", name="Results Table"
            )
    