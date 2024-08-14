import numpy as np
from napari_skimage.skimage_detection_widget import (peak_local_max_widget,
                                                     marching_cubes_widget,
                                                     marching_cubes_labels_widget)
from napari.layers import Image, Labels

def test_peak_local_max_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    random_image = np.random.random((100, 100))
    layer = viewer.add_image(random_image)

    my_widget = peak_local_max_widget()

    points, _, _ = my_widget(viewer.layers[0])
    assert points.shape[1] == 2  # Ensure points are 2D
    assert points.shape[0] > 0  # Ensure some points are detected

def test_marching_cubes_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    label_image = np.zeros((100, 100, 100), dtype=int)
    label_image[25:75, 25:75, 25:75] = 1
    layer = viewer.add_image(label_image)

    my_widget = marching_cubes_widget()

    surface, _, _ = my_widget(layer)
    vertices, faces = surface
    assert vertices.shape[1] == 3  # Ensure vertices are 3D
    assert faces.shape[1] == 3  # Ensure faces are triangles
    assert (faces.dtype == np.int32) | (faces.dtype == np.int64)  # Ensure faces are integer type

    layer = viewer.add_labels(label_image)
    my_widget = marching_cubes_labels_widget()

    surface, _, _ = my_widget(layer)
    vertices, faces = surface
    assert vertices.shape[1] == 3  # Ensure vertices are 3D
    assert faces.shape[1] == 3  # Ensure faces are triangles
    assert (faces.dtype == np.int32) | (faces.dtype == np.int64)  # Ensure faces are integer type
