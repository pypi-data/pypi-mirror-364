# SPDX-License-Identifier: LGPL-2.1-or-later
from __future__ import annotations

import numpy as np
import pandas as pd
from skimage.measure import label, regionprops
from skimage.morphology import remove_small_objects

__all__ = ["get_precip", "get_precip_flags"]

def get_precip(backscatter, ranges, times, min_size=500, cloud_threshold=-5.5,
               surface_tol=10, min_extent=500, time_tol='10min'):
    """
    Identify precipitation regions in the attenuated backscatter data.
    Parameters
    ----------
    backscatter : 2D ndarray, shape (n_range, n_time)
        The attenuated backscatter coefficient data.
    ranges : 1D ndarray, shape (n_range,)
        The height (range) values corresponding to each gate index.
    times : 1D ndarray, shape (n_time,)
        The time values corresponding to each column in the backscatter data.
    min_size : int, optional
        Minimum size of a region to be considered, by default 500.
    cloud_threshold : float, optional
        The threshold for cloud/fog/rain detection, by default -5.5.
    surface_tol : int, optional
        Tolerance for surface height, by default 10.
    min_extent : int, optional
        Minimum vertical extent of a region to be considered, by default 500.
    time_tol : str, optional
        Time tolerance for considering a region as rain, by default '10min'.
    Returns
    -------
    clean_labels : 2D ndarray, shape (n_range, n_time)
        Binary mask where 1 indicates the presence of a precipitation region and 0 indicates clear air.
    """
    
    water_mask   = backscatter > cloud_threshold
    water_mask   = remove_small_objects(water_mask, min_size=min_size)
    labels       = label(water_mask, connectivity=2)

    height_coords = ranges
    pd_times      = pd.to_datetime(times)
    tol_td        = pd.to_timedelta(time_tol)

    near_surface  = np.where(height_coords <= surface_tol + ranges.min())[0]
    clean_labels = labels.copy()

    for region in regionprops(labels):
        rid    = region.label
        coords = region.coords
        rows   = coords[:,0]
        cols   = coords[:,1]

        large_cols = []
        for c in np.unique(cols):
            rows_c = rows[cols == c]
            h_min  = height_coords[rows_c.min()]
            h_max  = height_coords[rows_c.max()]
            if (h_max - h_min) >= min_extent:
                large_cols.append(c)

        if not large_cols:
            clean_labels[labels == rid] = 0
            continue

        large_times = pd_times[large_cols]
        keep_times  = np.array([any(abs(t - large_times) <= tol_td) for t in pd_times])

        bad = np.isin(cols, np.where(~keep_times)[0])
        bad_rows, bad_cols = rows[bad], cols[bad]
        clean_labels[bad_rows, bad_cols] = 0

        touches_surface = np.any(np.isin(rows, near_surface))
        if not touches_surface:
            clean_labels[labels == rid] = 0

    return clean_labels


def get_precip_flags(backscatter, ranges, times, min_size=500, cloud_threshold=-5.5,
                     surface_tol=10, min_extent=500, time_tol='10min'):
    """ 
    Get precipitation flags from the attenuated backscatter data.
    Parameters
    ----------
    backscatter : 2D ndarray, shape (n_range, n_time)
        The attenuated backscatter coefficient data.
    ranges : 1D ndarray, shape (n_range,)
        The height (range) values corresponding to each gate index.
    times : 1D ndarray, shape (n_time,)
        The time values corresponding to each column in the backscatter data.
    min_size : int, optional
        Minimum size of a region to be considered, by default 500.
    cloud_threshold : float, optional
        The threshold for cloud/fog/rain detection, by default -5.5.
    surface_tol : int, optional
        Tolerance for surface height, by default 10.
    min_extent : int, optional
        Minimum vertical extent of a region to be considered, by default 500.
    time_tol : str, optional
        Time tolerance for considering a region as rain, by default '10min'.
    Returns
    -------
    flags : 1D ndarray, shape (n_time,)
        1D array where 0 indicates clear air and 1 indicates the presence of precipitation.
    """    
    precip     = get_precip(backscatter, ranges, times, min_size=min_size,
                            cloud_threshold=cloud_threshold, surface_tol=surface_tol,
                            min_extent=min_extent, time_tol=time_tol)
    valid_rows = np.where(ranges <= surface_tol)[0]
    flags      = (precip[valid_rows, :] > 0).any(axis=0).astype(np.uint8)
    return flags
