from typing import TYPE_CHECKING, Union

from magicgui import magic_factory
from magicgui.widgets import Label
from qtpy.QtCore import Qt
import skimage.morphology as sm
from napari.layers import Image, Labels
from napari.utils._magicgui import find_viewer_ancestor
import napari.types


if TYPE_CHECKING:
    import napari

"""For morphological operations, two widgets are defined: one for binary images and one for grey scale 
images. Options are provided to define the footprint shape and size. Links to skimage documentation are
provided via the _on_init function which first checks if the widget is for binary or grey scale images
and then creates the appropriate link.
"""

def _image_or_labels_choices(widget):
    viewer = find_viewer_ancestor(widget.native)
    if viewer is None:
        return []
    return [layer for layer in viewer.layers if isinstance(layer, (Image, Labels))]


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

def _on_init_morphology(widget):
    _on_init(widget)
    def update_properties_choices(event: object) -> None:
        if widget.label_layer.value is None:
            widget.footprint._default_choices = []
        elif widget.label_layer.value.data.ndim == 2:
            widget.footprint._default_choices = ['disk', 'square', 'diamond', 'star', 'octagon']
        elif widget.label_layer.value.data.ndim == 3:
            widget.footprint._default_choices = ['ball', 'cube']
        else:
            widget.footprint._default_choices = []
        widget.footprint.reset_choices()

    widget.label_layer.changed.connect(update_properties_choices)
    update_properties_choices(widget)


@magic_factory(
    label_layer={'label': 'Labels'},
    method={'choices': ['erosion', 'dilation', 'opening', 'closing']},
    footprint={'label': 'Footprint', 'choices': ['disk', 'square',
                                                 'diamond', 'star', 'octagon', 'ball', 'cube']},
    footprint_size={'label': 'Footprint size', 'max': 100, 'min': 1, 'step': 1},
    # to add for skimage 0.23
    #mode = {'choices': ['min', 'max', 'ignore']},
    call_button="Apply operation",
    widget_init=_on_init_morphology
)
def binary_morphology_widget(
    label_layer: Labels,
    method = "erosion",
    footprint = "disk",
    footprint_size = 3,
    #mode = "ignore"
) -> napari.types.LayerDataTuple:
    fun = getattr(sm, f'binary_{method}')
    if footprint == 'cube':
        selem = sm.footprint_rectangle((footprint_size, footprint_size, footprint_size))
    else:
        fun_footprint = getattr(sm, footprint)
        selem = fun_footprint(footprint_size)

    if (label_layer.data.ndim == 3) and (selem.ndim == 2):
        raise ValueError("For 3D data, selem needs to be 'ball")
    if (label_layer.data.ndim == 2) and (selem.ndim == 3):
        raise ValueError("For 2D data, selem cannot be 'ball'")

    mask = fun(label_layer.data, selem)#, mode=mode)
    return (
        mask,
        {'name': f'{label_layer.name}_{method}',
         'scale': label_layer.scale,
         'translate': label_layer.translate,
         'rotate': label_layer.rotate,
         'affine': label_layer.affine,
        },
        'labels')

@magic_factory(
    label_layer={'label': 'Image or Labels', 'choices': _image_or_labels_choices},
    method={'choices': ['erosion', 'dilation', 'opening', 'closing',
                        'white_tophat', 'black_tophat']},
    footprint={'label': 'Footprint', 'choices': ['disk', 'square', 
                                                 'diamond', 'star', 'octagon', 'ball', 'cube']},
    footprint_size={'label': 'Footprint size', 'max': 100, 'min': 1, 'step': 1},
    # to add for skimage 0.23
    # mode = {'choices': ['reflect', 'constant', 'nearest0', 'mirror', 'wrap', 'max', 'min', 'ignore']},
    call_button="Apply operation",
    widget_init=_on_init_morphology
)
def morphology_widget(
    label_layer: Union[Image, Labels],
    method = "erosion",
    footprint = "disk",
    footprint_size = 3,
    #mode = "ignore"
) -> napari.types.LayerDataTuple:
    fun = getattr(sm, f'{method}')
    if footprint == 'cube':
        selem = sm.footprint_rectangle((footprint_size, footprint_size, footprint_size))
    else:
        fun_footprint = getattr(sm, footprint)
        selem = fun_footprint(footprint_size)

    if (label_layer.data.ndim == 3) and (selem.ndim == 2):
        raise ValueError("For 3D data, selem needs to be 'ball")
    if (label_layer.data.ndim == 2) and (selem.ndim == 3):
        raise ValueError("For 2D data, selem cannot be 'ball'")
    
    mask = fun(label_layer.data, selem)#, mode=mode)
    return (
        mask,
        {'name': f'{label_layer.name}_{method}',
         'scale': label_layer.scale,
         'translate': label_layer.translate,
         'rotate': label_layer.rotate,
         'affine': label_layer.affine,
        },
        'image' if isinstance(label_layer, Image) else 'labels'
    )


def _on_init2(widget):
    label_widget = Label(value='')
    func_name = widget.label.split(' ')[0]
    label_widget.value = f'<a href=\"https://scikit-image.org/docs/stable/api/skimage.morphology.html#skimage.morphology.{func_name}\">skimage.morphology.{func_name}</a>'
    label_widget.native.setTextFormat(Qt.RichText)
    label_widget.native.setTextInteractionFlags(Qt.TextBrowserInteraction)
    label_widget.native.setOpenExternalLinks(True)
    widget.extend([label_widget])

@magic_factory(
    label_layer={'label': 'Labels'},
    max_size={'label': 'max_size', 'value': 64, 'min': 0, 'max': 2_147_483_647},
    connectivity={'label': 'connectivity', 'max': 3, 'min': 1, 'step': 1},
    call_button="Apply operation",
    widget_init=_on_init2
)
def remove_small_objects_widget(
    label_layer: Labels,
    max_size = 64,
    connectivity = 1,
) -> napari.types.LayerDataTuple:
    """Remove small objects from a labeled image.

    Parameters
    ----------
    label_layer : napari.layers.Labels
        The labeled image from which to remove small objects.
    max_size : int, optional
        The maximum size of objects to keep, by default 64.
    connectivity : int, optional
        The connectivity defining the neighborhood of a pixel, by default 1.

    Returns
    -------
    napari.types.LayerDataTuple
        The labeled image with small objects removed.
    """
    
    mask = sm.remove_small_objects(label_layer.data, max_size=max_size, connectivity=connectivity)
    return (
        mask,
        {'name': f'{label_layer.name}_remove_small_objects',
         'scale': label_layer.scale,
         'translate': label_layer.translate,
         'rotate': label_layer.rotate,
         'affine': label_layer.affine,
        },
        'labels')