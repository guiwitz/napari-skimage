import numpy as np
import pandas as pd

from napari_skimage.skimage_regionprops_widget import (
    only_2d_properties,
    regionprops_widget,
)


def test_regionprops_widget(make_napari_viewer):
    # Create a napari viewer
    viewer = make_napari_viewer()

    # Test data
    intensity_image = np.array(
        [
            [0, 0, 0, 0],
            [0, 6, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 7, 0],
            [0, 0, 0, 0],
        ]
    )
    labels_image = np.array(
        [
            [0, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 2, 0],
            [0, 0, 0, 0],
        ]
    )

    # Add the test data to the viewer
    intensity_layer = viewer.add_image(intensity_image, name="Intensity Image")
    labels_layer = viewer.add_labels(labels_image, name="Labels Layer")

    # Create the regionprops widget
    widget = regionprops_widget()

    # Select properties to compute
    widget.properties.value = ["area", "label", "intensity_mean"]

    # Call the widget with the test layers
    widget(
        image_layer=intensity_layer,
        labels_layer=labels_layer,
        properties=widget.properties.value,
    )

    # Check that the results table is created
    assert hasattr(widget, "results_table")

    # Check the contents of the results table
    results_df = widget.results_table.to_dataframe()
    expected_df = pd.DataFrame(
        {
            "area": [1.0, 1.0],
            "intensity_mean": [6.0, 7.0],
            "label": [1.0, 2.0],
        }
    )
    pd.testing.assert_frame_equal(results_df, expected_df)

    # Check that the dock widget is added to the viewer
    assert hasattr(widget, "_results_dock_widget")
    assert widget._results_dock_widget.widget is not None


def test_2d_vs_3d_properties(make_napari_viewer):
    # Create a napari viewer
    viewer = make_napari_viewer()

    # Test 2D data
    labels_2d = np.array(
        [
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 0],
        ]
    )
    labels_layer_2d = viewer.add_labels(labels_2d, name="2D Labels")

    # Test 3D data
    labels_3d = np.array(
        [
            [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            [[0, 0, 0], [0, 2, 0], [0, 0, 0]],
        ]
    )
    labels_layer_3d = viewer.add_labels(labels_3d, name="3D Labels")

    # Create the regionprops widget
    widget = regionprops_widget()

    # Check properties for 2D input
    widget.labels_layer.value = labels_layer_2d
    widget.properties.reset_choices()
    properties_2d = widget.properties.choices
    for prop in only_2d_properties:
        assert prop in properties_2d, (
            f"Property '{prop}' should be available for 2D input."
        )

    # Check properties for 3D input
    widget.labels_layer.value = labels_layer_3d
    widget.properties.reset_choices()
    properties_3d = widget.properties.choices
    for prop in only_2d_properties:
        assert prop not in properties_3d, (
            f"Property '{prop}' should not be available for 3D input."
        )


def test_analyze_button_state(make_napari_viewer):
    # Create a napari viewer
    viewer = make_napari_viewer()

    # Test data
    intensity_image = np.array(
        [
            [0, 0, 0],
            [0, 6, 0],
            [0, 0, 0],
        ]
    )
    labels_image = np.array(
        [
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 0],
        ]
    )
    mismatched_image = np.array(
        [
            [0, 0],
            [0, 6],
        ]
    )

    # Add the test data to the viewer
    intensity_layer = viewer.add_image(intensity_image, name="Intensity Image")

    # Create the regionprops widget
    widget = regionprops_widget()

    # Only image layer -> button disabled
    assert len(viewer.layers) == 1
    widget.image_layer.value = intensity_layer
    assert not widget.call_button.enabled

    # Add labels layer and mismatched image
    labels_layer = viewer.add_labels(labels_image, name="Labels Layer")
    mismatched_layer = viewer.add_image(
        mismatched_image, name="Mismatched Image"
    )
    widget.image_layer.reset_choices()
    widget.labels_layer.reset_choices()

    # Both layers selected with matching shapes -> button enabled
    assert widget.image_layer.value == intensity_layer
    widget.labels_layer.value = labels_layer
    assert widget.call_button.enabled

    # CBoth layers selected with mismatched shapes -> button disabled
    widget.labels_layer.value = labels_layer
    widget.image_layer.value = mismatched_layer
    assert not widget.call_button.enabled
