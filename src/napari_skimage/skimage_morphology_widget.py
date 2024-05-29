from typing import TYPE_CHECKING

from magicgui import magic_factory
import skimage.morphology as sm
from napari.layers import Image, Labels
import napari.types


if TYPE_CHECKING:
    import napari

@magic_factory(
    label_layer={'label': 'Labels'},
    call_button="Find connected components"
 )
def connected_components_widget(
    label_layer: Labels) -> napari.types.LayerDataTuple:
    return (
        sm.label(label_layer.data),
        {'name': f'{label_layer.name}_labels'},
        'labels')
 
@magic_factory(
    label_layer={'label': 'Labels'},
    method={'choices': ['erosion', 'dilation', 'opening', 'closing']},
    footprint={'label': 'Footprint', 'choices': ['disk', 'square', 'diamond', 'star', 'octagon']},
    footprint_size={'label': 'Footprint size', 'max': 100, 'min': 1, 'step': 1},
    # to add for skimage 0.23
    #mode = {'choices': ['min', 'max', 'ignore']},
    call_button="Apply operation"
)
def binary_morphology_widget(
    label_layer: Labels,
    method = "erosion",
    footprint = "disk",
    footprint_size = 3,
    #mode = "ignore"
) -> napari.types.LayerDataTuple:
    fun = getattr(sm, f'binary_{method}')
    fun_footprint = getattr(sm, footprint)
    selem = fun_footprint(footprint_size)
    mask = fun(label_layer.data, selem)#, mode=mode)
    return (
        mask,
        {'name': f'{label_layer.name}_{method}'},
        'labels')

@magic_factory(
    label_layer={'label': 'Image'},
    method={'choices': ['erosion', 'dilation', 'opening', 'closing',
                        'white_tophat', 'black_tophat']},
    footprint={'label': 'Footprint', 'choices': ['disk', 'square', 'diamond', 'star', 'octagon']},
    footprint_size={'label': 'Footprint size', 'max': 100, 'min': 1, 'step': 1},
    # to add for skimage 0.23
    # mode = {'choices': ['reflect', 'constant', 'nearest0', 'mirror', 'wrap', 'max', 'min', 'ignore']},
    call_button="Apply operation"
)
def morphology_widget(
    label_layer: Image,
    method = "erosion",
    footprint = "disk",
    footprint_size = 3,
    #mode = "ignore"
) -> napari.types.LayerDataTuple:
    fun = getattr(sm, f'{method}')
    fun_footprint = getattr(sm, footprint)
    selem = fun_footprint(footprint_size)
    mask = fun(label_layer.data, selem)#, mode=mode)
    return (
        mask,
        {'name': f'{label_layer.name}_{method}'},
        'image')
