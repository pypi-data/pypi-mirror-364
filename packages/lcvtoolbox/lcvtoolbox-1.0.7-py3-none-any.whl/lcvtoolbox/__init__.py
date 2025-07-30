"""Computer vision toolbox for road infrastructure analysis."""

__version__ = "1.0.4"
__author__ = "Logiroad"
__email__ = "thibaut.deveraux@logiroad-center.com"

# Import main modules for easier access
from . import cli, core, data, integrations, vision

__all__ = [
    "__version__",
    "cli",
    "core",
    "data",
    "integrations",
    "vision",
]
