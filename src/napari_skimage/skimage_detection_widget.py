from typing import TYPE_CHECKING
import numpy as np
from magicgui import magic_factory
from qtpy.QtCore import Qt
from magicgui.widgets import Label
from skimage.feature import peak_local_max
from skimage.measure import marching_cubes
from napari.layers import Image, Labels
import napari.types

if TYPE_CHECKING:
    import napari


def _on_init_peak_local_max(widget):
    label_widget = Label(value='')
    func_name = '_'.join(widget.label.split(' ')[:-1])
    label_widget.value = f'<a href=\"https://scikit-image.org/docs/stable/api/skimage.feature.html#skimage.feature.{func_name}\">skimage.feature.{func_name}</a>'
    label_widget.native.setTextFormat(Qt.RichText)
    label_widget.native.setTextInteractionFlags(Qt.TextBrowserInteraction)
    label_widget.native.setOpenExternalLinks(True)
    widget.extend([label_widget])


def _on_init_marching_cubes(widget):
    label_widget = Label(value='')
    label_widget.value = '<a href=\"https://scikit-image.org/docs/stable/api/skimage.measure.html#skimage.measure.marching_cubes\">skimage.measure.marching_cubes</a>'
    label_widget.native.setTextFormat(Qt.RichText)
    label_widget.native.setTextInteractionFlags(Qt.TextBrowserInteraction)
    label_widget.native.setOpenExternalLinks(True)
    widget.extend([label_widget])


@magic_factory(
    image_layer={'label': 'Image'},
    min_distance={'label': 'Minimum Distance'},
    threshold_absolute={'label': 'Threshold Absolute', 'min': 0.0, 'max': 65535},
    threshold_relative={'label': 'Threshold Relative', 'min': 0.0, 'max': 1.0},
    call_button="Detect Local Maxima",
    widget_init=_on_init_peak_local_max
)
def peak_local_max_widget(
    image_layer: Image,
    min_distance: int = 10,
    threshold_absolute: float = 0,
    threshold_relative: float = 0.0,
    exclude_border: bool = True,
) -> napari.types.LayerDataTuple:
    coordinates = peak_local_max(image_layer.data,
                                 min_distance=min_distance,
                                 threshold_abs=threshold_absolute,
                                 threshold_rel=threshold_relative,
                                 exclude_border=exclude_border)
    return (
        coordinates,
        {'name': f'{image_layer.name}_local_maxima'},
        'points'
    )


@magic_factory(
    image_layer={'label': 'Image'},
    level={'label': 'Level', 'min': 0.0, 'max': 65535},
    call_button="Apply Marching Cubes",
    widget_init=_on_init_marching_cubes
)
def marching_cubes_widget(
    image_layer: Image,
    level: float = 0.5,
) -> napari.types.LayerDataTuple:

    verts, faces, _, _ = marching_cubes(image_layer.data, level=level, spacing=image_layer.scale)
    return (
        (verts, faces.astype(int)),
        {'name': f'{image_layer.name}_surface'},
        'surface'
    )


@magic_factory(
    labels_layer={'label': 'Labels'},
    call_button='Apply Marching Cubes',
    widget_init=_on_init_marching_cubes
)
def marching_cubes_labels_widget(
    labels_layer: Labels,
) -> napari.types.LayerDataTuple:

    verts, faces, _, _ = marching_cubes(labels_layer.data > 0, level=0.5)
    return (
        (verts, faces.astype(int)),
        {'name': f'{labels_layer.name}_surface'},
        'surface'
    )
