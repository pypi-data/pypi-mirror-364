# spotisyaspy/__init__.py

from .spotisyaspy import SIAP_Factory, AttrDict

try:
    from ._version import version as __version__
except ImportError:
    # Fallback for when the package is not installed or setuptools_scm hasn't run yet
    __version__ = "unknown"

__author__ = "Pethő Gergely"
__email__ = "pagstudium@gmail.com"