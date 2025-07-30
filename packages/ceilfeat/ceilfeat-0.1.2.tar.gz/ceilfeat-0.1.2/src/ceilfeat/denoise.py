# SPDX-License-Identifier: LGPL-2.1-or-later
from __future__ import annotations

import numpy as np
import pandas as pd
import xarray as xr
from skimage.measure import label, regionprops
from skimage.morphology import remove_small_objects, binary_closing

from .precip import get_precip_flags
from .flags import get_cloud_flags

__all__ = ["remove_noisy_regions"]


def remove_noisy_regions(backscatter, thresh, ranges, times, max_height=5000,
                         cloud_threshold=-5.5, surface_tol = 5):
    """
    Remove any regions that touch the top of the image and don't contain a cloud base .

    Parameters
    ----------
    backscatter : 2D ndarray, shape (n_range, n_time)
        The attenuated backscatter coefficient data.
    thresh : np.ndarray
        Binary mask of the thresholded image.
    ranges : 1D ndarray, shape (n_range,)
        The height (range) values corresponding to each gate index.
    times : 1D ndarray, shape (n_time,)
        The time values corresponding to each column in the backscatter data.
    max_height : int, optional
        The maximum height to consider for region removal, by default 5000.
    cloud_threshold : float, optional
        The threshold for cloud/fog/rain detection, by default -5.5.
    surface_tol : int, optional
        Tolerance for surface height, by default 5.
    Return
    -------
    cleaned : 2D uint8 array
        Copy of 'thresh' with the noisy regions removed.
    """
    max_idx        = np.where(ranges <= max_height)[0].max()
    cleared_thr    = remove_small_objects(thresh > 0, min_size=900)
    labels         = label(cleared_thr, connectivity=2)
    precip_flags   = get_precip_flags(backscatter, ranges, times,
                                      cloud_threshold=cloud_threshold, surface_tol=surface_tol)
    cloud_flags    = get_cloud_flags(backscatter, ranges, max_height=max_height,
                                     cloud_threshold=cloud_threshold, surface_tol=surface_tol)
    combined_flags = precip_flags | cloud_flags
    
    valid_labels = labels.copy()
    for region in regionprops(labels):
        rows = region.coords[:, 0]
        cols = region.coords[:, 1]
        touches_ceiling = (rows.max() >= max_idx)
        cloudy_or_rainy = np.any(combined_flags[cols])
        small_blob = region.area < 2000
        if (touches_ceiling or small_blob) and not cloudy_or_rainy:
            valid_labels[labels == region.label] = 0

    valid_labels_da = xr.DataArray(
        valid_labels.astype(np.uint8),
        dims=('range', 'time'),
        coords={'time': times, 'range': ranges[ranges <= max_height]},
        attrs={'long_name': '3-hourly thresholds using OTSU method'}
    )
    return valid_labels_da
