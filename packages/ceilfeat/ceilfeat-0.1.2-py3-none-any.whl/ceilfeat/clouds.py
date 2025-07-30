# SPDX-License-Identifier: LGPL-2.1-or-later
from __future__ import annotations

import numpy as np
from skimage.measure import label, regionprops
from skimage.morphology import remove_small_objects
import cv2

__all__ = ["get_clouds", "get_cloud_base_height"]


def get_clouds(backscatter, ranges, max_height=10000, cloud_threshold=-5.5, surface_tol=50):
    """
    Identify cloud regions in the attenuated backscatter data.
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
        Tolerance for surface height, by default 50.
    Returns
    ------- 
    valid_labels : 2D ndarray, shape (n_range, n_time) 
        Binary mask where 1 indicates the presence of a cloud region and 0 indicates clear air.
    """
    near_surface = np.where(ranges <= surface_tol + ranges.min())[0]
    max_idx      = np.where(ranges <= max_height + ranges.min())[0].max()

    blurred_att  = cv2.GaussianBlur(backscatter.astype(np.float32), (5, 5), 0)
    water_mask   = (blurred_att > cloud_threshold)
    water_mask   = remove_small_objects(water_mask, min_size=500)

    labels       = label(water_mask, connectivity=2)
    valid_labels = labels.copy()

    for region in regionprops(labels):
        rows = region.coords[:, 0]
        touches_surface = np.any(np.isin(rows, near_surface))
        under_ceiling   = rows.min() <= max_idx
        if touches_surface or not under_ceiling:
            valid_labels[labels == region.label] = 0
    
    return valid_labels


def get_cloud_base_height(backscatter, ranges, max_height=10000, cloud_threshold=-5.5, surface_tol=5):
    """
    For each time‐column, find the lowest (smallest) row‐index
    where a cloud region is present.
    
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
    first : 1D ndarray, shape (n_time,)
        1D array where each element is the index of the lowest cloud base height for that time.
        If no cloud is detected, the value is NaN.
    """
    labels  = get_clouds(backscatter, ranges, max_height=max_height,
                         cloud_threshold=cloud_threshold, surface_tol=surface_tol)

    present = labels > 0
    first = np.argmax(present, axis=0).astype(float)
    no_region = ~present.any(axis=0)
    first[no_region] = np.nan
    return first
