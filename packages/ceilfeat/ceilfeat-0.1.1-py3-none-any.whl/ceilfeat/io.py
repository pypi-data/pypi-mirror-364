# SPDX-License-Identifier: LGPL-2.1-or-later
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Mapping
import numpy as np
import xarray as xr
from xarray.backends.api import to_netcdf as _to_netcdf

__all__ = ["read_netcdf", "write_netcdf", "create_file"]

def read_netcdf(path: str | Path, *, chunks: Mapping[str, int] | None = None,
                engine: str | None = None, decode_cf: bool = True) -> xr.Dataset:
    return xr.open_dataset(Path(path), chunks=chunks, engine=engine, decode_cf=decode_cf)

def write_netcdf(ds: xr.Dataset, path: str | Path, *, overwrite: bool = False,
                 engine: str | None = None, encoding: dict[str, Any] | None = None,
                 mode: str = "w") -> Path:
    path = Path(path)
    if path.exists() and not overwrite and mode == "w":
        raise FileExistsError(f"{path} exists (set overwrite=True or use mode='a').")
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp"); os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        _to_netcdf(ds, tmp_path, mode=mode, engine=engine, encoding=encoding)
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            try: tmp_path.unlink()
            except OSError: pass
    return path

def create_file(
    ds,
    row_wt,
    col_wt,
    remnant,
    clouds,
    precip,
    fog_flags,
    precip_flags,
    cloud_flags,
    clear_air_flag,
    cleaned_thresh,
    layers,
    overlap_function,
    output_path: str | Path,
    *,
    overwrite: bool = False,
    max_height: int = 5000,
) -> Path:
    """
    Same as your original create_file, but writes to `output_path`.
    """

    clouds = xr.DataArray(
        clouds.astype(np.uint8),
        dims=('range', 'time'),
        coords={'range': ds['range'], 'time': ds['time']},
        attrs={'long_name': 'detected cloud regions'},
    )

    precip = xr.DataArray(
        precip.astype(np.uint8),
        dims=('range', 'time'),
        coords={'range': ds['range'], 'time': ds['time']},
        attrs={'long_name': 'detected precipitation regions',
               'comment': 'detected/not-detected (1/0)'}
    )

    fog_flags = xr.DataArray(
        fog_flags, dims=('time',), coords={'time': ds['time']},
        attrs={'long_name': 'detected fog times', 'comment': 'detected/not-detected (1/0)'}
    )

    precip_flags = xr.DataArray(
        precip_flags, dims=('time',), coords={'time': ds['time']},
        attrs={'long_name': 'detected precipitation times', 'comment': 'detected/not-detected (1/0)'}
    )

    cloud_flags = xr.DataArray(
        cloud_flags, dims=('time',), coords={'time': ds['time']},
        attrs={'long_name': 'detected fog times', 'comment': 'detected/not-detected (1/0)'}
    )

    clear_air_flag = xr.DataArray(
        clear_air_flag, dims=('time',), coords={'time': ds['time']},
        attrs={'long_name': 'detected fog/clouds/precipitation', 'comment': 'clear air/unclear air (0/1)'}
    )

    layers = xr.DataArray(
        layers,
        dims=('time', 'detected_layer'),
        coords={'time': ds['time'], 'detected_layer': np.arange(layers.shape[1])},
        attrs={'long_name': 'Detected Layers', 'units': 'meters'}
    )

    ds['col_wt']          = col_wt
    ds['row_wt']          = row_wt
    ds['remnant']         = remnant
    ds['clouds']          = clouds
    ds['precip']          = precip
    ds['fog_flags']       = fog_flags
    ds['precip_flags']    = precip_flags
    ds['cloud_flags']     = cloud_flags
    ds['clear_air_flag']  = clear_air_flag
    ds['threshold_3hr']   = cleaned_thresh
    ds['layers']          = layers
    ds['overlap_function']= overlap_function

    out = Path(output_path)
    # if user passed a directory, build a default filename
    if out.is_dir():
        date = ds['time'].idxmin(dim='time').dt.strftime("%Y%m%d").values
        out = out / f"cl61_features_{date}.nc"

    return write_netcdf(ds, out, overwrite=overwrite)
