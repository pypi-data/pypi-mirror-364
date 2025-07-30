# SPDX-License-Identifier: LGPL-2.1-or-later
from __future__ import annotations

import numpy as np
from skimage.measure import label, regionprops
from skimage.morphology import binary_closing

from .precip import get_precip
from .clouds import get_clouds

__all__ = ["get_layers", "get_clouds_and_precip"]


def get_layers(cleaned_regions, ranges, tolerance = 5, max_height = 5000):
    """
    Parameters
    ----------
    mask : bool ndarray, shape (ntime, n_range, n_ray)
        True wherever you have a thresholded return.
    ranges : 1D float array, shape (n_range,)
        The height (range) values corresponding to each gate index.
    surface_tol : float
        Discard any edge at or below this height (e.g. ground clutter).

    Returns
    -------
    layers : float64 ndarray, shape (ntime, max_edges)
        Each row t contains, in blob order:
          [ bottom₁, top₁, bottom₂, top₂, … ]
        for all regions at time t.  Rows are padded with NaN out to
        the maximum number of edges seen in any time slice.
    """
    max_regions = int(cleaned_regions.max())
    max_layers  = max_regions * 2
    n_time      = cleaned_regions.shape[1]
    layers      = np.full((n_time, max_layers), np.nan, dtype=np.float64) 
    foorprint   = np.ones(50, dtype=bool)
    
    for t in range(n_time):
        profile_1d = cleaned_regions[:, t]
        profile_1d = binary_closing(profile_1d, footprint=foorprint)
        profile_2d = profile_1d[:, np.newaxis]
        lbl = label(profile_2d, connectivity=1)
        props = regionprops(lbl)
        idx = 0

        for region in props[:max_layers]:
            rows     = region.coords[:, 0]
            bottom_h = ranges[rows.min()]
            top_h    = ranges[rows.max()]

            if bottom_h <= tolerance + ranges.min():
                if top_h > tolerance and idx < max_layers:
                    layers[t, idx] = top_h
                    idx += 1
                    
            elif top_h >= max_height - tolerance:
                if bottom_h > tolerance and idx < max_layers:
                    layers[t, idx] = bottom_h
                    idx += 1

            else:
                if bottom_h > tolerance and idx < max_layers:
                    layers[t, idx] = bottom_h
                    idx += 1
                if top_h > tolerance and idx < max_layers:
                    layers[t, idx] = top_h
                    idx += 1
            
            if idx >= max_layers:
                break
            
    return layers


def get_clouds_and_precip(backscatter, ranges, times,  min_rain_size=500, min_rain_extent=2000,
                           time_tol='10min', max_height=10000, cloud_threshold=-5.5, surface_tol=5):
    """
        Get regions of interest from the attenuated backscatter data.
    
    Parameters
    ----------
    backscatter : 2D ndarray, shape (n_range, n_time)
        The attenuated backscatter coefficient data.
    ranges : 1D ndarray, shape (n_range,)
        The height (range) values corresponding to each gate index.
    times : 1D ndarray, shape (n_time,)
        The time values corresponding to each column in the backscatter data.
    min_rain_size : int, optional
        Minimum size of a rain region to be considered, by default 500.
    min_rain_extent : int, optional
        Minimum vertical extent of a rain region to be considered, by default 500.
    time_tol : str, optional
        Time tolerance for considering a region as rain, by default '10min'.
    max_height : int, optional
        Maximum height to consider for cloud detection, by default 10000.
    cloud_threshold : float, optional
        Threshold for cloud/fog/rain detection, by default -5.5.
    surface_tol : float, optional
        Tolerance for surface height, by default 5.

    Returns
    -------
        precip_regions : 2D ndarray, shape (n_range, n_time)
            Binary mask where 1 indicates the presence of a precipitation region and 0 indicates clear air
        cloud_regions : 2D ndarray, shape (n_range, n_time)
            Binary mask where 1 indicates the presence of a cloud region and 0 indicates clear air
    """
    precip_regions = get_precip(backscatter, ranges, times, min_size=min_rain_size,
                                min_extent=min_rain_extent, time_tol=time_tol,
                                cloud_threshold=cloud_threshold, surface_tol=surface_tol)
    cloud_regions = get_clouds(backscatter, ranges, max_height=max_height,
                               cloud_threshold=cloud_threshold, surface_tol=surface_tol)
    return cloud_regions, precip_regions
