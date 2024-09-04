from ._version import version as __version__
try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"
from .skimage_filter_widget import (farid_filter_widget, prewitt_filter_widget,
                                    laplace_filter_widget, gaussian_filter_widget,
                                    frangi_filter_widget, median_filter_widget,
                                    butterworth_filter_widget, RankFilterWidget)
from .skimage_threshold_widget import threshold_widget, ManualThresholdWidget
from .skimage_morphology_widget import (connected_components_widget,
                                        binary_morphology_widget, morphology_widget)
from .skimage_restoration_widget import (rolling_ball_restoration_widget,
                                         denoise_nl_means_restoration_widget)
from. mathsops import (simple_maths_widget, maths_image_pairs_widget,
                       maths_crop_widget, conversion_widget)
from .skimage_detection_widget import (peak_local_max_widget,
                                       marching_cubes_widget,
                                       marching_cubes_labels_widget)

__all__ = (
    "farid_filter_widget",
    "prewitt_filter_widget",
    "laplace_filter_widget",
    "gaussian_filter_widget",
    "frangi_filter_widget",
    "median_filter_widget",
    "butterworth_filter_widget",
    "RankFilterWidget",
    "threshold_widget",
    "ManualThresholdWidget",
    "connected_components_widget",
    "binary_morphology_widget",
    "morphology_widget",
    "rolling_ball_restoration_widget",
    "denoise_nl_means_restoration_widget",
    "simple_maths_widget",
    "maths_image_pairs_widget",
    "maths_crop_widget",
    "conversion_widget",
    "peak_local_max_widget",
    "marching_cubes_widget",
    "marching_cubes_labels_widget",
)
