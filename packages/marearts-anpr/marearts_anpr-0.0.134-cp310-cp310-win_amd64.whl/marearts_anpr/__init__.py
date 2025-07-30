# Import version information
from ._version import __version__

# Import the Python module first
from .marearts_anpr import marearts_anpr_from_pil, marearts_anpr_from_image_file, marearts_anpr_from_cv2

# Now import the Cython-compiled modules
try:
    from . import marearts_anpr_d
    ma_anpr_detector = marearts_anpr_d.ma_anpr_detector
except ImportError as e:
    print(f"Error importing ma_anpr_detector: {e}")
    ma_anpr_detector = None

try:
    from . import marearts_anpr_r
    ma_anpr_ocr = marearts_anpr_r.ma_anpr_ocr
except ImportError as e:
    print(f"Error importing ma_anpr_ocr: {e}")
    ma_anpr_ocr = None

__all__ = [
    "__version__",
    "marearts_anpr_from_pil",
    "marearts_anpr_from_image_file",
    "marearts_anpr_from_cv2",
    "ma_anpr_detector",
    "ma_anpr_ocr"
]