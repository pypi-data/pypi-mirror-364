# SPDX-License-Identifier: LGPL-2.1-or-later
from __future__ import annotations

import numpy as np
import pandas as pd
import cv2
import xarray as xr

__all__ = ["split_and_thresh", "get_thresh"]


def split_and_thresh(combined, resample_time="3h"):
    """
    Splits the combined data into 3-hour blocks and applies automated OTSU thresholding on each block, returning the combined thresholded result.
    Parameters
    ----------
    combined : xarray.DataArray
        2D array with dimensions (range, time) containing the combined data to be thresholded.
    Returns
    -------
    result : np.ndarray
        2D array with dimensions (range, time) containing the thresholded data.
    """
    times = combined.time.values                      # shape (1440,)
    n_range, n_time = combined.shape
    result   = np.zeros((n_range, n_time), dtype=np.uint8)
    time_idx = pd.Index(times)
    for _, block in combined.resample(time=resample_time):
        arr = block.values.astype(np.float32)  
        block_normalized = cv2.normalize(arr, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        smooth_block = cv2.morphologyEx(block_normalized, cv2.MORPH_OPEN, kernel)
        _,th = cv2.threshold(smooth_block,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        locs = time_idx.get_indexer(block.time.values)
        result[:, locs] = th

    return result    


def get_thresh(remnant, row_wt, col_wt, max_height=5000, resample_time="3h"):
    """
    Trim inputs to `max_height`, sum selected wavelet scales plus the remnant,
    then threshold each time block (default 3 h) with Otsu via `split_and_thresh`.

    Parameters
    ----------
    remnant : xarray.DataArray
        2D (range, time) low-frequency residual.
    row_wt : xarray.DataArray
        3D (scale, range, time) row-wise wavelet planes; uses indices 2 and 3.
    col_wt : xarray.DataArray
        3D (scale, range, time) column-wise planes; uses indices 4–7.
    max_height : int or float, optional
        Max range to keep. Default 5000.
    resample_time : str, optional
        Pandas offset for block size (e.g. "3h"). Default "3h".

    Returns
    -------
    numpy.ndarray
        2D uint8 mask (range, time): 255 where detected, 0 otherwise.
    """
    row_wt = row_wt.where(row_wt['range'] <= max_height, drop=True)
    col_wt = col_wt.where(col_wt['range'] <= max_height, drop=True)
    remnant = remnant.where(remnant['range'] <= max_height, drop=True)
    combined = (row_wt[2] + row_wt[3] + col_wt[4] + col_wt[5] + col_wt[6] + col_wt[7] + remnant).rename("combined")
    thresh = split_and_thresh(combined, resample_time)
    return thresh
