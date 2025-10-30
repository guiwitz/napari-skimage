from typing import TYPE_CHECKING, Optional

import napari
import napari.types
import numpy as np
import pandas as pd
from qtpy.QtWidgets import QFileDialog
from magicgui import magic_factory
from magicgui.widgets import Label, Table, Button, CheckBox, ComboBox
from napari.layers import Image, Labels
from napari.utils.notifications import show_info, show_warning
from qtpy.QtCore import Qt
from skimage.measure import regionprops_table
from skimage.measure._regionprops import PROPS, _require_intensity_image

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


def _on_init(widget: "Widget") -> None:
    """Initialize the widget, add a hyperlink, and set up connections."""
    # Controls for per-slice analysis
    widget.per_slice = CheckBox(text="Per-slice (frame) analysis", value=False)
    widget.slice_axis = ComboBox(label="Axis", choices=[0], value=0, enabled=False)
    widget.extend([widget.per_slice, widget.slice_axis])

    # Save button
    widget.save_button = Button(enabled=False, text='Save Results')
    widget.extend([widget.save_button])

    # Add a hyperlink to the documentation
    label_widget = Label(value="")
    label_widget.value = '<a href="https://scikit-image.org/docs/stable/api/skimage.measure.html#skimage.measure.regionprops_table">skimage.measure.regionprops_table</a>'
    label_widget.native.setTextFormat(Qt.RichText)
    label_widget.native.setTextInteractionFlags(Qt.TextBrowserInteraction)
    label_widget.native.setOpenExternalLinks(True)
    widget.extend([label_widget])

    # Define a function to get valid properties dynamically
    def get_valid_properties(widget: "Widget") -> Optional[list]:
        labels_layer = widget.labels_layer.value
        if labels_layer:
            # Treat as 2D when per-slice is enabled on >=3D labels
            is_2d = (labels_layer.data.ndim == 2) or (
                widget.per_slice.value and labels_layer.data.ndim >= 3
            )
            valid_props = set(available_properties if is_2d else valid_properties_3d)
            if not widget.image_layer.value:
                valid_props = valid_props - set(_require_intensity_image)
            return sorted(valid_props)
        else:
            return []

    # Update the properties choices dynamically
    def update_properties_choices(event: object) -> None:
        if hasattr(widget, "properties"):
            widget.properties._default_choices = lambda _: get_valid_properties(widget)
            widget.properties.reset_choices()

    # Enable or disable the Analyze button based on input validation
    def update_analyze_button_state(event: object) -> None:
        labels_layer = widget.labels_layer.value
        image_layer = widget.image_layer.value

        if labels_layer and image_layer:
            shapes_match = labels_layer.data.shape == image_layer.data.shape
            if not shapes_match:
                show_warning(
                    "Shape mismatch: Labels Layer and Intensity Image must have the same shape."
                )
            widget.call_button.enabled = shapes_match
        elif labels_layer:
            widget.call_button.enabled = True
        else:
            widget.call_button.enabled = False

    # Update axis selector enablement/choices
    def update_axis_controls(event: object) -> None:
        labels_layer = widget.labels_layer.value
        enable_axis = (
            widget.per_slice.value and labels_layer and labels_layer.data.ndim >= 3
        )
        widget.slice_axis.enabled = bool(enable_axis)
        if enable_axis:
            ndim = labels_layer.data.ndim
            choices = list(range(ndim))
            widget.slice_axis.choices = choices
            if widget.slice_axis.value not in choices:
                widget.slice_axis.value = 0

    def clicked_table(event: object):
        row = widget.results_table.native.currentRow()
        if "label" in widget.results_table.column_headers:
            label = int(widget.results_table["label"][row])
        else:
            # If the label column is not present, use the row index
            # plus one to account for zero-based indexing
            label = np.unique(widget.labels_layer.value.data)[row + 1]
        show_info(f"Table clicked, set label: {label}")
        widget.labels_layer.value.selected_label = label

        # If a frame column exists, set the viewer to that frame along selected axis
        if "frame" in widget.results_table.column_headers and widget.per_slice.value:
            try:
                frame = int(widget.results_table["frame"][row])
                axis = int(widget.slice_axis.value)
                viewer = napari.current_viewer()
                if viewer is not None and 0 <= axis < viewer.dims.ndim:
                    viewer.dims.set_current_step(axis, frame)
            except Exception:
                # Avoid breaking on click if dims setting fails
                pass

    def save_table(event: object):
        # get file path from user
        file_path = QFileDialog.getSaveFileName(
                widget.native,
                "Save Results",
                ".",
                "CSV Files (*.csv);;All Files (*)",
            )[0]

        # if the user cancels the dialog, file_path will be None, so we return
        if not file_path:
            return

        widget.results_table.to_dataframe().to_csv(
                file_path,
                index=False,
            )

    # initialize table
    widget.results_table = Table(name="Results Table")

    # Connect the signals to the update functions
    widget.labels_layer.changed.connect(update_properties_choices)
    widget.image_layer.changed.connect(update_properties_choices)
    widget.labels_layer.changed.connect(update_analyze_button_state)
    widget.image_layer.changed.connect(update_analyze_button_state)
    widget.labels_layer.changed.connect(update_axis_controls)
    widget.per_slice.changed.connect(update_axis_controls)
    widget.per_slice.changed.connect(update_properties_choices)

    widget.results_table.native.clicked.connect(clicked_table)
    widget.save_button.clicked.connect(save_table)

    # initialize Select widget and button state
    widget.properties._default_choices = lambda _: get_valid_properties(widget)
    update_axis_controls(widget)
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
    labels_layer: Labels, image_layer: Optional[Image], properties: list[str]
) -> napari.types.LayerDataTuple:
    """Widget to compute regionprops_table and display results."""

    # if both image and labels layers are provided, they need to match shape
    if image_layer and labels_layer and labels_layer.data.shape != image_layer.data.shape:
        show_warning(
            "Labels Layer and Intensity Image must have the same shape."
        )
        return

    # Check for an image layer. If it's absent,
    if image_layer:
        image_layer_data = image_layer.data
        spacing = image_layer.scale
    else:
        image_layer_data = None
        spacing = None

    # Compute regionprops_table with optional per-slice (frame) analysis
    per_slice = getattr(regionprops_widget, "per_slice", None)
    slice_axis_widget = getattr(regionprops_widget, "slice_axis", None)
    do_per_slice = False
    axis = 0
    try:
        do_per_slice = bool(per_slice.value) if per_slice is not None else False
        axis = int(slice_axis_widget.value) if slice_axis_widget is not None else 0
    except Exception:
        do_per_slice = False
        axis = 0

    if do_per_slice and labels_layer.data.ndim >= 3:
        n_slices = labels_layer.data.shape[axis]
        dfs = []
        for i in range(n_slices):
            labels_slice = np.take(labels_layer.data, i, axis=axis)
            if image_layer_data is not None:
                intensity_slice = np.take(image_layer_data, i, axis=axis)
            else:
                intensity_slice = None

            # Derive 2D spacing per slice when possible
            if spacing is not None and len(spacing) == labels_layer.data.ndim:
                spacing_slice = tuple(
                    spacing[j] for j in range(len(spacing)) if j != axis
                )
                if len(spacing_slice) != labels_slice.ndim:
                    spacing_slice = None
            else:
                spacing_slice = None

            props = regionprops_table(
                label_image=labels_slice,
                intensity_image=intensity_slice,
                properties=properties,
                spacing=spacing_slice,
            )
            df = pd.DataFrame(props)
            df.insert(0, "frame", i)
            dfs.append(df)

        results_df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    else:
        props = regionprops_table(
            label_image=labels_layer.data,
            intensity_image=image_layer_data,
            properties=properties,
            spacing=spacing,
        )
        results_df = pd.DataFrame(props)

    # Enable save button
    regionprops_widget.save_button.enabled = True

    viewer = napari.current_viewer()
    # Check if the dock widget exists and is still valid
    if (
        not hasattr(regionprops_widget, "_results_dock_widget")
        or regionprops_widget._results_dock_widget is None
        or regionprops_widget._results_dock_widget.widget is None
    ):
        regionprops_widget.results_table.value = results_df
        regionprops_widget.results_table.read_only = True

        regionprops_widget._results_dock_widget = (
            viewer.window.add_dock_widget(
                regionprops_widget.results_table,
                area="bottom",
                name="Results Table",
            )
        )
    else:
        try:
            regionprops_widget.results_table.value = results_df
            regionprops_widget.results_table.read_only = True

            regionprops_widget._results_dock_widget.show()
        except RuntimeError:
            regionprops_widget.results_table.value = results_df
            regionprops_widget.results_table.read_only = True

            regionprops_widget._results_dock_widget = (
                viewer.window.add_dock_widget(
                    regionprops_widget.results_table,
                    area="bottom",
                    name="Results Table",
                )
            )