from typing import TYPE_CHECKING

import warnings
import numpy as np
from magicgui import magic_factory
import skimage.util
from napari.layers import Image, Labels, Layer, Shapes
import napari.types


if TYPE_CHECKING:
    import napari

@magic_factory(
        image_layer={'label': 'Image'},
        operation={'choices': ['square', 'sqrt', 'log', 'log10', 'exp']},
        call_button="Apply operation"
        )
def simple_maths_widget(
    image_layer: Image, operation='sqrt'
) -> napari.types.LayerDataTuple:
    if operation == 'square':
        fun = lambda x: x.astype(np.float32)**2
    else:
        fun = getattr(np, f'{operation}')
    out = fun(image_layer.data)
    return (
        out,
        {'name': f'{image_layer.name}_{operation}'},
        'image')

@magic_factory(
        data_layer={'label': 'Image'},
        data_layer2={'label': 'Image 2'},
        operation={'choices': ['add', 'subtract', 'multiply', 'divide']},
        call_button="Apply operation"
        )
def maths_image_pairs_widget(
    data_layer: Layer,
    data_layer2: Layer,
    operation='add'
) -> napari.types.LayerDataTuple:
    if not isinstance(data_layer, (Labels, Image)) or not isinstance(data_layer2, (Labels, Image)):
        raise ValueError("Both layers must be Image or Labels layers")
    if operation == 'add':
        out = data_layer.data + data_layer2.data
    elif operation == 'subtract':
        out = data_layer.data - data_layer2.data
    elif operation == 'multiply':
        out = data_layer.data * data_layer2.data
    elif operation == 'divide':
        out = data_layer.data / data_layer2.data
    return (
        out,
        {'name': f'Result_{operation}'},
        'image')

@magic_factory(
        image_layer={'label': 'Image'},
        mode={'choices': ['uint8', 'uint16', 'float32', 'float64']},
        call_button="Apply operation"
        )
def conversion_widget(
    image_layer: Image, mode='uint8',
) -> napari.types.LayerDataTuple:
    if mode == 'uint8':
        out = skimage.util.img_as_ubyte(image_layer.data)
    if mode == 'uint16':
        out = skimage.util.img_as_uint(image_layer.data)
    elif mode == 'float32':
        out = skimage.util.img_as_float32(image_layer.data)
    elif mode == 'float64':
        out = skimage.util.img_as_float64(image_layer.data)
    return (
        out,
        {'name': f'{image_layer.name}_{mode}'},
        'image')

"""
The code for the maths_crop_widget has been directly adapated from the napari-crop
plugin (https://github.com/BiAPoL/napari-crop/). The original code is licensed under
the BSD 3-Clause License reproduced below:

Copyright (c) 2021, Robert Haase, Tim Morello, Marcelo Zoccoler, DFG Cluster of Excellence "Physics of Life", TU Dresden
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of napari-manual-split-and-merge-labels nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

@magic_factory(
        image_layer={'label': 'Image'},
        shapes_layer={'label': 'Image 2'},
        call_button="Crop rectangle"
        )
def maths_crop_widget(
    viewer: 'napari.viewer.Viewer',
    image_layer: Image,
    shapes_layer: Shapes,
) -> napari.types.LayerDataTuple:
    
    if not isinstance(image_layer, (Image)) or not isinstance(shapes_layer, (Shapes)):
        raise ValueError("You need an image and a shapes layer.")
    
    shape_data, shape_props, shape_type = shapes_layer.as_layer_data_tuple()
    if len(shape_data) != 1:
        warnings.warn("Only the first rectangle will be used for cropping.")

    layer_data, layer_props, layer_type = image_layer.as_layer_data_tuple()

    try:
        rgb = layer_props["rgb"]
    except KeyError:
        rgb = False

    shape_types = shapes_layer.shape_type
    shapes = shapes_layer.data
    cropped_list = []
    new_layer_index = 0
    names_list = []
    if viewer is not None:
        # Get existing layer names in viewer
        names_list = [layer.name for layer in viewer.layers]
    
    #for shape_count, [shape, shape_type] in enumerate(zip(shapes,
    #                                                      shape_types)):

    shape = shapes[0]
    shape_type = shape_types[0]
    # move shape vertices to within image coordinate limits
    layer_shape = np.array(layer_data.shape)
    if rgb:
        layer_shape = layer_shape[:-1]
    # find min and max for each dimension
    start = np.rint(np.min(shape, axis=0))
    stop = np.rint(np.max(shape, axis=0))
    # create slicing indices
    slices = tuple(
        slice(first, last + 1) if first != last else slice(0, None)
        for first, last in np.stack([start.clip(0),
                                        stop.clip(0)]).astype(int).T
    )
    cropped_data = layer_data[slices].copy()

    # Update start and stop values for bbox
    start = [slc.start for slc in slices if slc is not None]
    stop = []
    for slc in slices:
        if slc is not None:
            if slc.stop is None:
                stop.append(layer_shape[slices.index(slc)])
            else:
                stop.append(slc.stop)
    # stop = [slc.stop for slc in slices if slc is not None]
    # Add cropped coordinates as metadata
    # bounding box: ([min_z,] min_row, min_col, [max_z,] max_row, max_col)
    # Pixels belonging to the bounding box are in the half-open interval [min_row; max_row) and [min_col; max_col).
    
    new_layer_props = layer_props.copy()
    new_layer_props = dict(layer_props)
    new_layer_props['metadata'] = {'bbox': tuple(start + stop)}
    # apply layer translation scaled by layer scaling factor
    new_layer_props['translate'] = tuple(np.asarray(tuple(start)) * np.asarray(layer_props['scale']))
    
    # If layer name is in viewer or is about to be added,
    # increment layer name until it has a different name
    while True:
        new_name = layer_props["name"] \
            + f" cropped [{new_layer_index}]"
        if new_name not in names_list:
            break
        else:
            new_layer_index += 1
    new_layer_props["name"] = new_name
    names_list.append(new_name)
    
    return (
        cropped_data,
        new_layer_props,
        layer_type)
