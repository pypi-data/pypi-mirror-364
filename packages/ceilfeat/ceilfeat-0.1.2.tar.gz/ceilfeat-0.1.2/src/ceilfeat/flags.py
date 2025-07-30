# SPDX-License-Identifier: LGPL-2.1-or-later
from __future__ import annotations

import numpy as np
import cv2
from skimage.measure import label, regionprops
from skimage.morphology import remove_small_objects

from .precip import get_precip_flags
from .clouds import get_clouds
# Note: get_cloud_flags is our own function; `get_clouds` comes from clouds.py

__all__ = ["get_cloud_flags", "get_fog_flags", "get_clear_air_flag", "get_flags"]


def get_cloud_flags(backscatter, ranges, max_height=10000, cloud_threshold=-5.5, surface_tol=5):
    """
    Get cloud flags from the attenuated backscatter data.
    Parameters
    ----------
    backscatter : 2D ndarray, shape (n_range, n_time)
        The attenuated backscatter coefficient data.
    ranges : 1D ndarray, shape (n_range,)
        The height (range) values corresponding to each gate index.
    max_height : int, optional
        The maximum height to consider for cloud detection, by default 10000.
    cloud_threshold : float, optional
        The threshold for cloud/fog/rain detection, by default -5.5.
    surface_tol : int, optional
        Tolerance for surface height, by default 5.
    Returns
    -------
    flags : 1D ndarray, shape (n_time,)
        1D array where 0 indicates clear air and 1 indicates the presence of clouds.
    """
    labels  = get_clouds(backscatter, ranges, max_height=max_height,
                         cloud_threshold=cloud_threshold, surface_tol=surface_tol)
    present = (labels > 0).any(axis=0)
    flags   = present.astype(np.uint8)
    return flags


def get_fog_flags(backscatter, ranges, times, surface_tol=5, cloud_threshold=-5.5,
                  fog_threshold=-4.75, min_size=500, min_extent=500, time_tol='10min'):
    """
        Get fog flags from the attenuated backscatter data.
    Parameters
    ----------
    backscatter : 2D ndarray, shape (n_range, n_time)
        The attenuated backscatter coefficient data.
    ranges : 1D ndarray, shape (n_range,)
        The height (range) values corresponding to each gate index.
    times : 1D ndarray, shape (n_time,)
        The time values corresponding to each column in the backscatter data.
    surface_tol : int, optional
        Tolerance for surface height, by default 5.
    cloud_threshold : float, optional
        The threshold for cloud/fog/rain detection, by default -5.5.
    min_size : int, optional
        Minimum size of a region to be considered, by default 500.
    min_extent : int, optional
        Minimum vertical extent of a region to be considered by the precip flag, by default 500.
    time_tol : str, optional
        Time tolerance for considering a region as rain, by default '10min'.
    
    Returns
    -------
    flags : 1D ndarray, shape (n_time,)
        1D array where 0 indicates clear air and 1 indicates the presence of fog
    """
    blur_kernel = (5, 5)
    sigma_x = 0
    near_surface = np.where(ranges <= surface_tol + ranges.min())[0]
    blurred_att  = cv2.GaussianBlur(backscatter.astype(np.float32), blur_kernel, sigma_x)

    water_mask   = (blurred_att > fog_threshold)
    water_mask   = remove_small_objects(water_mask, min_size=500)
    precip_flags = get_precip_flags(backscatter, ranges, times, surface_tol=surface_tol,
                                    min_size=min_size, min_extent=min_extent, time_tol=time_tol,
                                    cloud_threshold=cloud_threshold)

    labels = label(water_mask, connectivity=2)
    n_time = labels.shape[1]
    flags  = np.zeros(n_time, dtype=np.uint8)

    for region in regionprops(labels):
        rows = region.coords[:,0]
        cols = region.coords[:,1]
        if np.any(np.isin(rows, near_surface)):
            flags[np.unique(cols)] = 1

    nan_times = np.isnan(backscatter[near_surface, :]).any(axis=0)
    flags[nan_times] = 1
    flags[precip_flags == 1] = 0 
    return flags


def get_clear_air_flag(backscatter, ranges, times, min_rain_size=500, min_rain_extent=500,
                       time_tol='30min', max_height=10000, cloud_threshold=-5.5,
                       fog_threshold = -4.75, surface_tol=5):
    """
    1D ndarray where 0 is clear air and 1 is not clear air.

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
    combined_flag : 1D ndarray, shape (n_time,)
        1D array where 0 indicates clear air and 1 indicates the presence of fog
    """
    fog    = get_fog_flags(backscatter, ranges, times, min_size=min_rain_size,
                           min_extent=min_rain_extent, time_tol=time_tol,
                           cloud_threshold=cloud_threshold, fog_threshold=fog_threshold,
                           surface_tol=surface_tol)
    clouds = get_cloud_flags(backscatter, ranges, max_height=max_height,
                             cloud_threshold=cloud_threshold, surface_tol=surface_tol)
    precip = get_precip_flags(backscatter, ranges, times, min_size=min_rain_size,
                              min_extent=min_rain_extent, cloud_threshold=cloud_threshold,
                              surface_tol=surface_tol, time_tol=time_tol)

    combined_flag = ((fog == 1) | (clouds == 1) | (precip == 1))
    return combined_flag.astype(np.uint8)


def get_flags(backscatter, ranges, times, min_rain_size=500, min_rain_extent=2000,
              time_tol='10min', max_height=10000, cloud_threshold=-5.5,
              fog_threshold = -4.75, surface_tol=5):
    """
    (Unchanged body)
    """
    fog_flags = get_fog_flags(backscatter, ranges, times, min_size=min_rain_size,
                              min_extent=min_rain_extent, time_tol=time_tol,
                              cloud_threshold=cloud_threshold, fog_threshold=fog_threshold,
                              surface_tol=surface_tol)
    cloud_flags = get_cloud_flags(backscatter, ranges, max_height=max_height,
                                  cloud_threshold=cloud_threshold, surface_tol=surface_tol)
    precip_flags = get_precip_flags(backscatter, ranges, times, min_size=min_rain_size,
                                    min_extent=min_rain_extent, cloud_threshold=cloud_threshold,
                                    surface_tol=surface_tol, time_tol=time_tol)
    clear_air_flags = get_clear_air_flag(backscatter, ranges, times, min_rain_size=min_rain_size,
                                         min_rain_extent=min_rain_extent, time_tol=time_tol,
                                         max_height=max_height, cloud_threshold=cloud_threshold,
                                         surface_tol=surface_tol)

    return (fog_flags.astype(np.uint8),
            cloud_flags.astype(np.uint8),
            precip_flags.astype(np.uint8),
            clear_air_flags.astype(np.uint8))
