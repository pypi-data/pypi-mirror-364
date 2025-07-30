# SPDX-License-Identifier: LGPL-2.1-or-later
"""
Command-line pipeline to process ceilometer NetCDF files and write results.

Usage
-----
python -m ceilfeat.pipeline --in /path/a.nc /path/b.nc --out /out/dir
python -m ceilfeat.pipeline --in "/data/*.nc" --out results.nc

If multiple inputs are given and --out is a file, an error is raised.
"""

from __future__ import annotations

import argparse
import glob
import logging
from pathlib import Path
from typing import Iterable

import xarray as xr
import act

from .wavelet import get_wavelets
from .layers import get_layers, get_clouds_and_precip
from .flags import get_flags
from .thresholds import get_thresh
from .denoise import remove_noisy_regions
from .io import create_file


LOG = logging.getLogger("ceilfeat.pipeline")


def _expand_inputs(inputs: Iterable[str]) -> list[Path]:
    """Expand any globs and return unique Paths in sorted order."""
    paths: set[Path] = set()
    for item in inputs:
        for p in glob.glob(item):
            paths.add(Path(p))
    return sorted(paths)


def process_one(input_path: Path, output_dest: Path, *, max_height: int = 5000, overwrite: bool = True) -> Path:
    """
    Run the full algorithm on one NetCDF file.

    Parameters
    ----------
    input_path : Path
        Source NetCDF.
    output_dest : Path
        Destination file OR directory. If directory, filename auto-generated.
    max_height : int
        Height cutoff used in several steps.
    overwrite : bool
        Allow overwriting output files.

    Returns
    -------
    Path
        Final written NetCDF path.
    """
    LOG.info("Opening %s", input_path)
    ds = xr.open_dataset(input_path).sortby("time")

    # Variable corrections (as in your notebook loop)
    variables = ["beta_att", "p_pol", "x_pol", "linear_depol_ratio"]
    for var in variables:
        if var != "linear_depol_ratio":
            ds = act.corrections.correct_ceil(ds, var_name=var)
    ds["linear_depol_ratio"] = ds["x_pol"] / (ds["x_pol"] + ds["p_pol"])

    # Save & drop overlap_function until the end
    overlap_function = ds["overlap_function"] if "overlap_function" in ds else None
    if overlap_function is not None:
        ds = ds.drop_vars(["overlap_function"])

    # Clean NaNs
    ds = ds.dropna(dim="range", how="all").dropna(dim="time", how="all")

    # Wavelets
    ds_copy = ds.copy(deep=True)
    row_wt, col_wt, remnant = get_wavelets(ds_copy, ds["range"].values, ds["time"].values)
    ds_copy.close()

    LOG.info("Detecting clouds/precip")
    clouds, precip = get_clouds_and_precip(
        ds["beta_att"].T.values,
        ds["range"].values,
        ds["time"].values,
    )

    fog_flags, precip_flags, cloud_flags, clear_air_flag = get_flags(
        ds["beta_att"].T.values,
        ds["range"].values,
        ds["time"].values,
        max_height=max_height,
    )

    LOG.info("Thresholding & denoising")
    thresh = get_thresh(remnant, row_wt, col_wt, max_height=max_height)
    cleaned_thresh = remove_noisy_regions(
        ds["beta_att"].T.values,
        thresh,
        ds["range"].values,
        ds["time"].values,
        max_height=max_height,
    )
    cleaned_thresh = cleaned_thresh.where(cleaned_thresh.range <= max_height, drop=True)

    layers = get_layers(cleaned_thresh.values, cleaned_thresh["range"].values)

    # Write output
    LOG.info("Writing output")
    out_path = create_file(
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
        output_path=output_dest,
        overwrite=overwrite,
        max_height=max_height,
    )
    LOG.info("Done: %s", out_path)
    return out_path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Ceilometer feature detection pipeline")
    parser.add_argument(
        "--in",
        dest="inputs",
        nargs="+",
        required=True,
        help="Input NetCDF file(s) or glob(s).",
    )
    parser.add_argument(
        "--out",
        dest="output",
        required=True,
        help="Output file OR directory.",
    )
    parser.add_argument(
        "--max-height",
        type=int,
        default=5000,
        help="Maximum height (same units as range) used in processing. Default: 5000.",
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Fail if output file exists.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v, -vv).",
    )

    args = parser.parse_args(argv)

    # Logging level
    level = logging.WARNING
    if args.verbose == 1:
        level = logging.INFO
    elif args.verbose >= 2:
        level = logging.DEBUG
    logging.basicConfig(format="%(levelname)s: %(message)s", level=level)

    in_paths = _expand_inputs(args.inputs)
    if not in_paths:
        parser.error("No input files matched.")

    out_path = Path(args.output)
    overwrite = not args.no_overwrite

    if len(in_paths) > 1 and out_path.is_file():
        parser.error("Multiple inputs require --out to be a directory.")

    if len(in_paths) > 1:
        out_path.mkdir(parents=True, exist_ok=True)

    for p in in_paths:
        process_one(p, out_path, max_height=args.max_height, overwrite=overwrite)


if __name__ == "__main__":
    main()