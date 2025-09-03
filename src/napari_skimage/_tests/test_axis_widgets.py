import pytest
import numpy as np

from napari_skimage.axis_ops import (
    AxisWidget
)

# single fun test
def test_swap_move_axis_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    random_image = np.random.random((100, 100, 3))
    layer = viewer.add_image(random_image)

    # our widget will be a MagicFactory or FunctionGui instance
    my_widget = AxisWidget(viewer=viewer)
    my_widget.operation.native.setCurrentText('swapaxes')
    my_widget.axis1.native.setValue(0)
    my_widget.axis2.native.setValue(2)
    my_widget._apply_operation()

    assert len(viewer.layers) == 2, "Expected 2 layers in viewer"
    assert viewer.layers[1].data.shape == (3, 100, 100), f"Expected shape (3, 100, 100) for swapped layer but got {viewer.layers[1].data.shape}"

    viewer.layers.remove(viewer.layers[1])
    
    my_widget.operation.native.setCurrentText('moveaxis')
    my_widget.axis1.native.setValue(0)
    my_widget.axis2.native.setValue(2)
    my_widget._apply_operation()

    assert len(viewer.layers) == 2, "Expected 2 layers in viewer"
    assert viewer.layers[0].data.shape == (100, 100, 3), f"Expected shape (100, 100, 3) for moved layer but got {viewer.layers[0].data.shape}"
    assert viewer.layers[1].data.shape == (100, 3, 100), f"Expected shape (100, 3, 100) for moved layer but got {viewer.layers[1].data.shape}"

def test_flip_widget(make_napari_viewer):
    viewer = make_napari_viewer()

    image = np.zeros((10, 10))
    image[0, 0] = 1
    viewer.add_image(image, name='test_image')

    my_widget = AxisWidget(viewer=viewer)
    my_widget.operation.native.setCurrentText('flip')

    my_widget.axis1.native.setValue(0)
    my_widget.axis2.native.setValue(1)
    my_widget._apply_operation()

    assert len(viewer.layers) == 2, "Expected 2 layers in viewer"
    assert viewer.layers[1].data.shape == (10, 10), f"Expected shape (10, 10) but got {viewer.layers[1].data.shape}"
    assert viewer.layers[1].data[-1, 0].item() == 1, "Expected flipped image top-down but bottom-left pixel is not 1"

def test_squeeze_widget(make_napari_viewer):
    viewer = make_napari_viewer()

    image = np.zeros((10, 1, 10))
    viewer.add_image(image, name='test_image')

    my_widget = AxisWidget(viewer=viewer)
    my_widget.operation.native.setCurrentText('squeeze')

    my_widget.axis1.native.setValue(0)
    my_widget.axis2.native.setValue(1)
    my_widget._apply_operation()

    assert len(viewer.layers) == 2, "Expected 2 layers in viewer"
    assert viewer.layers[1].data.shape == (10, 10), f"Expected shape (10, 10) but got {viewer.layers[1].data.shape}"

def test_expand_dims_widget(make_napari_viewer):
    viewer = make_napari_viewer()

    image = np.zeros((10, 10))
    viewer.add_image(image, name='test_image')

    my_widget = AxisWidget(viewer=viewer)
    my_widget.operation.native.setCurrentText('expand_dims')

    my_widget.axis1.native.setValue(1)
    my_widget._apply_operation()

    assert len(viewer.layers) == 2, "Expected 2 layers in viewer"
    assert viewer.layers[1].data.shape == (10, 1, 10), f"Expected shape (10, 1, 10) but got {viewer.layers[1].data.shape}"