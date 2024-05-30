from typing import TYPE_CHECKING

from magicgui import magic_factory
from magicgui.widgets import Label
from qtpy.QtCore import Qt
import skimage.morphology as sm
from napari.layers import Image, Labels
import napari.types


if TYPE_CHECKING:
    import napari

"""For morphological operations, two widgets are defined: one for binary images and one for grey scale 
images. Options are provided to define the footprint shape and size. Links to skimage documentation are
provided via the _on_init function which first checks if the widget is for binary or grey scale images
and then creates the appropriate link.
"""

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

def _on_init(widget):
    label_widget = Label(value='')   

    def get_func_name(w): 
        if w.label.split(' ')[0] == 'binary':
            func_name = f'binary_{w.method.value}'
        else:
            func_name = w.method.value
        return func_name     
    
    func_name = get_func_name(widget)
    label_widget.value = f'<a href=\"https://scikit-image.org/docs/stable/api/skimage.morphology.html#skimage.morphology.{func_name}\">skimage.morphology.{func_name}</a>'
    label_widget.native.setTextFormat(Qt.RichText)
    label_widget.native.setTextInteractionFlags(Qt.TextBrowserInteraction)
    label_widget.native.setOpenExternalLinks(True)
    widget.extend([label_widget])

    widget.method.changed.connect(lambda x: setattr(label_widget, 'value', f'<a href=\"https://scikit-image.org/docs/stable/api/skimage.morphology.html#skimage.morphology.{get_func_name(widget)}\">skimage.morphology.{get_func_name(widget)}</a>'))
 
@magic_factory(
    label_layer={'label': 'Labels'},
    method={'choices': ['erosion', 'dilation', 'opening', 'closing']},
    footprint={'label': 'Footprint', 'choices': ['disk', 'square', 'diamond', 'star', 'octagon']},
    footprint_size={'label': 'Footprint size', 'max': 100, 'min': 1, 'step': 1},
    # to add for skimage 0.23
    #mode = {'choices': ['min', 'max', 'ignore']},
    call_button="Apply operation",
    widget_init=_on_init
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
    call_button="Apply operation",
    widget_init=_on_init
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
