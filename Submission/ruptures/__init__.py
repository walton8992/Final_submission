"""Offline change point detection for Python."""

from .datasets import pw_constant, pw_linear, pw_normal, pw_wavy
from .detection import Binseg, BottomUp, Dynp, KernelCPD, Pelt, Window,WindowEnsemble,BinsegEnsemble
from .exceptions import NotEnoughPoints
from .show import display
# Convenient access to the version number
from .version import version as __version__
