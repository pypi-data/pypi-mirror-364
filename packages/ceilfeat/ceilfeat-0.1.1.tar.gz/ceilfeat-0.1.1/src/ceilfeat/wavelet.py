# SPDX-License-Identifier: LGPL-2.1-or-later
from __future__ import annotations

import sys
import numpy as np
import xarray as xr

__all__ = ["atwt2d", "get_wavelets"]


def atwt2d(data2d, max_scale=-1):
    """
    Computes a trous wavelet transform (ATWT). Computes ATWT of the 2d array
    up to max_scale. If max_scale is outside the boundaries, number of scales
    will be reduced.

    Data is mirrored at the boundaries. 'Negative WT are removed. Not tested
    for non-square data.

    @authors: Bhupendra Raut and Dileep M. Puranik
    @references: Press et al. (1992) Numerical Recipes in C.

    Parameters:
    ===========
    data2d: ndarray
        2D image as array or matrix.
    max_scale:
        Computes wavelets up to max_scale. Leave blank for maximum possible
        scales.

    Returns:
    ========
    row_wt: ndarray (scales, ny, nx)
        Wavelet extracted by row-wise differencing (original – row-smoothed).
    col_wt: ndarray (scales, ny, nx)
        Wavelet extracted by column-wise differencing (row-smoothed – fully-smoothed).
    """
    if not isinstance(data2d, np.ndarray):
        sys.exit("the input is not a numpy array")

    # determine scales
    ny, nx = data2d.shape
    min_dim = min(ny, nx)
    max_possible = int(np.floor(np.log(min_dim) / np.log(2)))
    if max_scale < 0 or max_scale > max_possible:
        max_scale = max_possible

    # allocate output arrays
    total_wt = np.zeros((max_scale, ny, nx))
    row_wt   = np.zeros((max_scale, ny, nx))
    col_wt   = np.zeros((max_scale, ny, nx))

    # working buffers
    temp1 = np.zeros_like(data2d)
    temp2 = np.zeros_like(data2d)

    # scaling function coefficients
    sf = (0.0625, 0.25, 0.375)

    for scale in range(1, max_scale + 1):
        x1 = 2**(scale - 1)
        x2 = 2 * x1

        # --- row-wise smoothing into temp1 ---
        for i in range(nx):
            prev2 = abs(i - x2)
            prev1 = abs(i - x1)
            next1 = i + x1
            next2 = i + x2

            # mirror at edges
            if next1 > nx - 1:
                next1 = 2*(nx - 1) - next1
            if next2 > nx - 1:
                next2 = 2*(nx - 1) - next2
            if prev1 < 0 or prev2 < 0:
                prev1, prev2 = next1, next2

            for j in range(ny):
                left2  = data2d[j, prev2]
                left1  = data2d[j, prev1]
                right1 = data2d[j, next1]
                right2 = data2d[j, next2]
                temp1[j, i] = (
                    sf[0]*(left2 + right2) +
                    sf[1]*(left1 + right1) +
                    sf[2]* data2d[j, i]
                )

        # row-wise wavelet = original – row-smoothed
        row_wt[scale-1] = data2d - temp1

        # --- column-wise smoothing into temp2 ---
        for i in range(ny):
            prev2 = abs(i - x2)
            prev1 = abs(i - x1)
            next1 = i + x1
            next2 = i + x2

            if next1 > ny - 1:
                next1 = 2*(ny - 1) - next1
            if next2 > ny - 1:
                next2 = 2*(ny - 1) - next2
            if prev1 < 0 or prev2 < 0:
                prev1, prev2 = next1, next2

            for j in range(nx):
                top2    = temp1[prev2, j]
                top1    = temp1[prev1, j]
                bottom1 = temp1[next1, j]
                bottom2 = temp1[next2, j]
                temp2[i, j] = (
                    sf[0]*(top2 + bottom2) +
                    sf[1]*(top1 + bottom1) +
                    sf[2]* temp1[i, j]
                )

        # column-wise wavelet = row-smoothed – fully-smoothed
        col_wt[scale-1] = temp1 - temp2
        # total wavelet = original – fully-smoothed
        total_wt[scale-1] = data2d - temp2

        # prepare for next scale
        data2d[:] = temp2

    row_wt = np.where(row_wt > 0, row_wt, 0)
    col_wt = np.where(col_wt > 0, col_wt, 0)
    return row_wt, col_wt

def get_wavelets(ds_copy, ranges, time, varname='beta_att'):
    """
    Computes a trous wavelet transform of the attenuated backscatter coefficient

    Parameters
    ===========
    ds_copy: xarray.Dataset
        Copy of the dataset containing the variable to be transformed
    ranges: ndarray
        1D array of range values corresponding to the vertical dimension
    time: ndarray
        1D array of time values corresponding to the time dimension
    varname: str
        Name of the variable in the dataset to be transformed (default is 'beta_att')
    
    Returns
    ===========
    row_wt: xarray.DataArray
        Row-wise a trous wavelet transform of the attenuated backscatter coefficient
    col_wt: xarray.DataArray
        Column-wise a trous wavelet transform of the attenuated backscatter coefficient
    remnant: xarray.DataArray
        Remnant of the a trous wavelet transform of the attenuated backscatter
        coefficient
    """
    remnant = ds_copy[varname].T.values.copy()
    row_wt, col_wt = atwt2d(remnant, 8)

    col_wt = xr.DataArray(
        col_wt,
        dims=('scale', 'range', 'time'),
        coords={'scale': range(1,9), 'range': ranges, 'time': time},
        attrs={'long_name': 'column-wise a trous wavelet transform of attenuated backscatter coefficient',
               'units': ds_copy[varname].units}
    )
    row_wt = xr.DataArray(
        row_wt,
        dims=('scale', 'range', 'time'),
        coords={'scale': range(1,9), 'range': ranges, 'time': time},
        attrs={'long_name': 'row-wise a trous wavelet transform of attenuated backscatter coefficient',
               'units': ds_copy[varname].units}
    )
    remnant = xr.DataArray(
        remnant,
        dims=('range', 'time'),
        coords={'range': ranges, 'time': time},
        attrs={'long_name': 'remnant of 8-scale a trous wavelet transform of attenuated backscatter coefficient',
               'units': ds_copy[varname].units}
    )
    return row_wt, col_wt, remnant
