
from ._version import version as __version__
try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"
from .skimage_widget import farid_filter_widget, gaussian_filter_widget

__all__ = (
    "farid_filter_widget",
    "gaussian_filter_widget",
)