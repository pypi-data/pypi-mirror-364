# SPDX-License-Identifier: LGPL-2.1-or-later
# Copyright (c) 2025 Daniel Wefer
"""
Public API for ceilfeat.
"""

from __future__ import annotations

# Try to expose the installed version
try:
    from importlib.metadata import version as _version, PackageNotFoundError
    try:
        __version__ = _version("ceilfeat")
    except PackageNotFoundError:  # pragma: no cover
        __version__ = "0.0.0"
except Exception:  # pragma: no cover
    __version__ = "0.0.0"

from .io import create_file
from .layers import get_layers, get_clouds_and_precip
from .precip import get_precip, get_precip_flags
from .clouds import get_clouds, get_cloud_base_height
from .flags import get_cloud_flags, get_fog_flags, get_clear_air_flag, get_flags

__all__ = [
    "create_file",
    "get_layers",
    "get_clouds_and_precip",
    "get_precip",
    "get_precip_flags",
    "get_clouds",
    "get_cloud_base_height",
    "get_cloud_flags",
    "get_fog_flags",
    "get_clear_air_flag",
    "get_flags",
    "__version__",
]
