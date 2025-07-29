#!/usr/bin/env python
"""
Package stub.
"""

import importlib

from .package import Package

# Convert to a loop later if other packages are added.
importlib.import_module(".python.package", __name__)


__all__ = ["Package"]
