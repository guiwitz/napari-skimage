import numpy as np

from napari_skimage.skimage_morphology_widget import (
    binary_morphology_widget,
    connected_components_widget,
    morphology_widget
)
from napari_skimage.skimage_threshold_widget import threshold_widget, ManualThresholdWidget
import napari_skimage.skimage_filter_widget as sfw
import napari_skimage.mathsops as nsm

# single fun test
def test_farid_filter_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    random_image = np.random.random((100, 100))
    layer = viewer.add_image(random_image)

    # our widget will be a MagicFactory or FunctionGui instance
    my_widget = sfw.farid_filter_widget()

    filtered, _, _ = my_widget(viewer.layers[0])
    assert filtered.shape == random_image.shape

# multifun
def test_filters(make_napari_viewer):

    filter_list = ["farid_filter_widget",
                   "prewitt_filter_widget",
                   "laplace_filter_widget",
                   "gaussian_filter_widget",
                   "frangi_filter_widget",
                   "median_filter_widget",
                   "butterworth_filter_widget"]
    
    viewer = make_napari_viewer()
    random_image = np.random.random((100, 100))
    viewer.add_image(random_image)
    
    for filt in filter_list:

        filt = getattr(sfw, filt)
        my_widget = filt()
        filtered, _, _ = my_widget(viewer.layers[0])
        assert filtered.shape == random_image.shape, f"Filter {filt} failed"

def test_rank_filter_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    random_image = np.random.randint(0, 100, (100, 100), dtype=np.uint8)
    layer = viewer.add_image(random_image)

    # our widget will be a MagicFactory or FunctionGui instance
    my_widget = sfw.RankFilterWidget(viewer=viewer)

    for choice in my_widget.stat.choices:
        my_widget.stat.native.setCurrentText(choice)

        my_widget._rank_filter_im()
        filtered = viewer.layers[1]
        assert filtered.data.shape == random_image.shape

def test_binary_morphology_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    random_image = np.random.randint(0, 2, (100, 100), dtype=np.uint8)
    layer = viewer.add_labels(random_image)

    # our widget will be a MagicFactory or FunctionGui instance
    my_widget = binary_morphology_widget()

    for choice in my_widget.method.choices:
        my_widget.method.native.setCurrentText(choice)

        filtered, _, _ = my_widget(viewer.layers[0])
        assert filtered.data.shape == random_image.shape

def test_morphology_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    random_image = np.random.randint(0, 10, (100, 100), dtype=np.uint8)
    layer = viewer.add_image(random_image)

    # our widget will be a MagicFactory or FunctionGui instance
    my_widget = morphology_widget()
    
    for choice in my_widget.method.choices:
        my_widget.method.native.setCurrentText(choice)

        filtered, _, _ = my_widget(viewer.layers[0])
        assert filtered.data.shape == random_image.shape

def test_connected_components_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    random_image = np.random.randint(0, 10, (100, 100), dtype=np.uint8)
    layer = viewer.add_labels(random_image)

    # our widget will be a MagicFactory or FunctionGui instance
    my_widget = connected_components_widget()

    filtered, _, _ = my_widget(viewer.layers[0])
    assert filtered.data.shape == random_image.shape

def test_thresholding_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    random_image = np.random.random((100, 100))
    layer = viewer.add_image(random_image, name='random_image')

    # our widget will be a MagicFactory or FunctionGui instance
    my_widget = threshold_widget()
    
    for choice in my_widget.method.choices:
        my_widget.method.native.setCurrentText(choice)
        my_widget()
        assert viewer.layers[f'random_image_threshold_{choice}'].data.shape == random_image.shape

def test_manual_thresholding_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    random_image = np.random.random((100, 100))
    layer = viewer.add_image(random_image)

    # our widget will be a MagicFactory or FunctionGui instance
    my_widget = ManualThresholdWidget(viewer=viewer)
    
    my_widget.threshold.native.setValue(50)
    my_widget.apply_threshold()
    assert viewer.layers[1].data.shape == random_image.shape

def test_simple_maths_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    random_image = np.random.random((100, 100))
    layer = viewer.add_image(random_image)

    # our widget will be a MagicFactory or FunctionGui instance
    my_widget = nsm.simple_maths_widget()
    
    for choice in my_widget.operation.choices:
        my_widget.operation.native.setCurrentText(choice)

        filtered, _, _ = my_widget(viewer.layers[0])
        assert filtered.data.shape == random_image.shape

def test_maths_image_pairs_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    random_image = np.random.random((100, 100))
    random_image2 = np.random.random((100, 100))
    layer = viewer.add_image(random_image)
    layer2 = viewer.add_image(random_image2)

    # our widget will be a MagicFactory or FunctionGui instance
    my_widget = nsm.maths_image_pairs_widget()
    
    for choice in my_widget.operation.choices:
        my_widget.operation.native.setCurrentText(choice)

        filtered, _, _ = my_widget(viewer.layers[0], viewer.layers[1])
        assert filtered.data.shape == random_image.shape

def test_math_crop_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    random_image = np.random.random((100, 100))
    layer = viewer.add_image(random_image)
    layer_shapes = viewer.add_shapes([[0, 0],
                                  [0,10],
                                  [10,10],
                                  [10,0]])

    my_widget = nsm.maths_crop_widget()

    croped, _, _ = my_widget(viewer, viewer.layers[0], viewer.layers[1])
    assert croped.shape == (11,11)

def test_conversion_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    random_image = np.random.random((100, 100))
    layer = viewer.add_image(random_image)

    # our widget will be a MagicFactory or FunctionGui instance
    my_widget = nsm.conversion_widget()
    
    for choice in my_widget.mode.choices:
        my_widget.mode.native.setCurrentText(choice)

        filtered, _, _ = my_widget(viewer.layers[0])
        assert filtered.data.shape == random_image.shape