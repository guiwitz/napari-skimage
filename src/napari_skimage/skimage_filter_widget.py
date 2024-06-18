from typing import TYPE_CHECKING

import numpy as np
from magicgui import magic_factory
from magicgui.widgets import Button, Container, create_widget, Label
from qtpy.QtCore import Qt
import skimage.filters as sf
import skimage.morphology as sm
from napari.layers import Image
import napari.types


if TYPE_CHECKING:
    import napari

"""For filters a widget is defined for each filter. The _on_init function is used to add a hyperlink to the
documentation of the function that the widget is calling. For this to work properly, the widget function needs
to be named "<skimage function name>_filter_widget".

RankFilterWidget is a class that defines a widget for rank filters. The widget can be used for all rank filters.
"""

def _on_init(widget):
    label_widget = Label(value='')
    func_name = widget.label.split(' ')[0]
    label_widget.value = f'<a href=\"https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.{func_name}\">skimage.filters.{func_name}</a>'
    label_widget.native.setTextFormat(Qt.RichText)
    label_widget.native.setTextInteractionFlags(Qt.TextBrowserInteraction)
    label_widget.native.setOpenExternalLinks(True)
    widget.extend([label_widget])

@magic_factory(
        image_layer={'label': 'Image'},
        mode={'choices': ['reflect', 'constant', 'nearest', 'mirror', 'wrap']},
        call_button="Apply Farid filter",
        widget_init=_on_init
        )
def farid_filter_widget(
    image_layer: Image, mode='reflect') -> napari.types.LayerDataTuple:
    return (
        sf.farid(image_layer.data, mode=mode),
        {'name': f'{image_layer.name}_farid'},
        'image')

@magic_factory(
        image_layer={'label': 'Image'},
        mode={'choices': ['reflect', 'constant', 'nearest', 'mirror', 'wrap']},
        call_button="Apply Prewitt filter",
        widget_init=_on_init
        )
def prewitt_filter_widget(
    image_layer: Image, mode='reflect') -> napari.types.LayerDataTuple:
    return (
        sf.prewitt(image_layer.data, mode=mode),
        {'name': f'{image_layer.name}_prewitt'},
        'image')

@magic_factory(
        image_layer={'label': 'Image'},
        call_button="Apply Laplace filter",
        widget_init=_on_init
        )
def laplace_filter_widget(
    image_layer: Image,
    ksize: int = 3.0) -> napari.types.LayerDataTuple:
    return (
        sf.laplace(image_layer.data, ksize=ksize),
        {'name': f'{image_layer.name}_laplace'},
        'image')

@magic_factory(
        img_layer={'label': 'Image'},
        mode={'choices': ['reflect', 'constant', 'nearest', 'mirror', 'wrap']},
        call_button="Apply Gaussian Filter",
        widget_init=_on_init
        )
def gaussian_filter_widget(
    img_layer: Image,
    sigma: float = 1.0,
    preserve_range: bool = False,
    mode = "reflect",
) -> napari.types.LayerDataTuple:
    return (
        sf.gaussian(img_layer.data, sigma=sigma, preserve_range=preserve_range, mode=mode),
        {'name': f'{img_layer.name}_gaussian_σ={sigma}'},
        'image')

@magic_factory(
        img_layer={'label': 'Image'},
        mode={'choices': ['reflect', 'constant', 'nearest', 'mirror', 'wrap']},
        call_button="Apply Frangi Filter",
        widget_init=_on_init
        )
def frangi_filter_widget(
    img_layer: Image,
    scale_start: float = 1.0,
    scale_end: float = 10.0,
    scale_step: float = 2.0,
    mode = "reflect",
    black_ridges: bool = True,
) -> napari.types.LayerDataTuple:
    return (
        sf.frangi(img_layer.data, sigmas=np.arange(scale_start, scale_end, scale_step),
                  black_ridges=black_ridges, mode=mode),
        {'name': f'{img_layer.name}_frangi'},
        'image')

@magic_factory(
    img_layer={'label': 'Image'},
    mode={'choices': {'reflect', 'constant', 'nearest', 'mirror', 'wrap'}},
    footprint={'label': 'Footprint', 'choices': ['disk', 'square', 'diamond', 'star', 'octagon']},
    footprint_size={'label': 'Footprint size', 'max': 100, 'min': 1, 'step': 1},
    call_button="Apply operation",
    widget_init=_on_init
)
def median_filter_widget(
    img_layer: Image,
    footprint = "disk",
    footprint_size = 3,
    mode = "nearest"
) -> napari.types.LayerDataTuple:
    fun_footprint = getattr(sm, footprint)
    selem = fun_footprint(footprint_size)
    img_filtered = sf.median(img_layer.data, footprint=selem, mode=mode)
    return (
        img_filtered,
        {'name': f'{img_layer.name}_median'},
        'image')

@magic_factory(
    img_layer={'label': 'Image'},
    call_button="Apply operation",
    widget_init=_on_init
)
def butterworth_filter_widget(
    img_layer: Image,
    cuttoff_frequency_ratio: float = 0.005,
    high_pass: bool = True,
    order: int = 2,
    squared_butterworth: bool = True,
    npad: int = 0,
) -> napari.types.LayerDataTuple:
    img_filtered = sf.butterworth(
        img_layer.data, cutoff_frequency_ratio=cuttoff_frequency_ratio,
        high_pass=high_pass, order=order, squared_butterworth=squared_butterworth,
        npad=npad)
    return (
        img_filtered,
        {'name': f'{img_layer.name}_butterworth'},
        'image')

class RankFilterWidget(Container):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        
        self._viewer = viewer

        self._image_layer_combo = create_widget(
            label="Image", annotation="napari.layers.Image"
        )
        self.stat = create_widget(
            label="Filter type", annotation=str, widget_type="ComboBox",
            options={'choices':['mean', 'median', 'minimum', 'maximum', 'sum',
                                'entropy', 'otsu', 'subtract_mean', 'windowed_histogram',
                                'gradient', 'geometric_mean','equalize', 'entropy',
                                'enhance_contrast', 'autolevel',
                                'mean_percentile', 'subtract_mean_percentile', 'sum_percentile',
                                'gradient_percentile', 'enhance_contrast_percentile', 
                                'autolevel_percentile']}
        )

        self.footprint = create_widget(
            label="Footprint", annotation=str, widget_type="ComboBox",
            options={'choices':['disk', 'square', 'diamond', 'star', 'octagon']}
        )

        self.footprint_size = create_widget(
            label="Footprint size", annotation=int, options={'value': 3})

        self.percentile =create_widget(
            label="Percentile", widget_type='FloatRangeSlider',
            options={'value':[0.1, 0.99], 'min': 0, 'max': 1, 'step': 0.01})

        self.btn_apply = Button(text="Apply operation")
        self.btn_apply.clicked.connect(self._rank_filter_im)

        self.link_label = Label(value='')
        self.link_label.native.setTextFormat(Qt.RichText)
        self.link_label.native.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.link_label.native.setOpenExternalLinks(True)

        # append into/extend the container with your widgets
        self.extend(
            [
                self._image_layer_combo,
                self.stat,
                self.footprint,
                self.footprint_size,
                self.btn_apply,
                self.link_label
            ]
        )

        self.stat.changed.connect(self._on_choose_stat)
        self._on_choose_stat()

    def _on_choose_stat(self, event=None):
        if self.stat.value in ['mean_percentile', 'subtract_mean_percentile', 'sum_percentile',
                                'gradient_percentile', 'enhance_contrast_percentile', 'autolevel_percentile']:
            if self.percentile not in self:
                self.extend([self.percentile])
        else:
            if self.percentile in self:
                self.remove(self.percentile)

        self.link_label.value = f'<a href=\"https://scikit-image.org/docs/stable/api/skimage.filters.rank.html#skimage.filters.rank.{self.stat.value}\">skimage.filters.rank.{self.stat.value}</a>'
        

    def _rank_filter_im(self):
        image_layer = self._image_layer_combo.value
        if image_layer is None:
            return

        kwargs = {}
        if self.stat.value in ['mean_percentile', 'subtract_mean_percentile', 'sum_percentile',
                                'gradient_percentile', 'enhance_contrast_percentile', 'autolevel_percentile']:
            kwargs = {'p0': self.percentile.value[0], 'p1': self.percentile.value[1]}          

        fun = getattr(sf.rank, self.stat.value)
        fun_footprint = getattr(sm, self.footprint.value)
        selem = fun_footprint(self.footprint_size.value)
        img_filtered = fun(image_layer.data, footprint=selem, **kwargs)
        self._viewer.add_image(
            img_filtered,
            name=f"{image_layer.name}_{self.stat.value}",
            colormap="gray",
        )
