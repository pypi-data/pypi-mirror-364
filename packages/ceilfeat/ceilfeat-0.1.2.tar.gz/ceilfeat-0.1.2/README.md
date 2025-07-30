# ceil-feature-detection

[![PyPI version](https://img.shields.io/pypi/v/ceilfeat)](https://pypi.org/project/ceilfeat)
[![License](https://img.shields.io/pypi/l/ceilfeat)](LICENSE)

Ceilometer feature detection from NetCDF files: clouds, precipitation, fog, and boundary-layer detection.

---

## Features

* **A-trous (stationary) wavelet transform**: multi‑scale analysis of attenuated backscatter.
* **Automated thresholding**: blockwise Otsu on combined wavelet/remnant field.
* **Denoising**: remove erroneous regions/artifacts prior to layer extraction
* **Cloud/precip/fog flags**: per-time-step boolean indicators.
* **Layer extraction**: Thresholded PBL/Residual Layer/other stored in a multidimensional ndarray. 
* **NetCDF I/O**: read/write with atomic file replacement.
* **Command-line & Python API**

## Installation

```bash
pip install ceilfeat
```

To install the latest version from GitHub:

```bash
pip install git+https://github.com/DanielWefer/ceil-feature-detection.git
```

For development (editable) install with tests:

```bash
git clone https://github.com/DanielWefer/ceil-feature-detection.git
cd ceil-feature-detection
env=".venv"
python -m venv "$env"
source "$env/bin/activate"
pip install -e '.[dev]'
pytest -q
```

## Quickstart CLI

Process one or more NetCDF files via the built-in pipeline:

```bash
python -m ceilfeat.pipeline --in /path/to/input1.nc /path/to/input2.nc \
    --out /path/to/output_dir -vv
```

* `--in`: input file(s) or glob(s).
* `--out`: output file or directory. If a directory, filenames are auto-generated.
* `-v, -vv`: increase verbosity.

## Python API

```python
import xarray as xr
import ceilfeat as cf

# 1. Open dataset
 ds = xr.open_dataset("input.nc").sortby("time")

# 2. Compute wavelet transforms
 row_wt, col_wt, remnant = cf.get_wavelets(ds.copy(), ds.range.values, ds.time.values)

# 3. Detect clouds & precip
 clouds, precip = cf.get_clouds_and_precip(
     ds.beta_att.T.values, ds.range.values, ds.time.values
 )

# 4. Flags and threshold
 fog, cloud, rain, clear = cf.get_flags(
     ds.beta_att.T.values, ds.range.values, ds.time.values
 )
 thresh = cf.get_thresh(remnant, row_wt, col_wt)

# 5. Denoise & extract layers
 clean = cf.remove_noisy_regions(
     ds.beta_att.T.values, thresh, ds.range.values, ds.time.values
 )
 layers = cf.get_layers(clean.values, clean.range.values)

# 6. Write results
 cf.create_file(
     ds, row_wt, col_wt, remnant,
     clouds, precip, fog, rain, cloud, clear,
     clean, layers, ds.overlap_function,
     output_path="output.nc",
     overwrite=True
 )
```

## Contributing

1. Fork the repo and create a feature branch.
2. Write code, tests, and update docs.
3. Follow style: `ruff`, `mypy`, `pytest`.
4. Submit a pull request.

## License

This project is licensed under the GNU Lesser General Public License v2.1 or later. See [LICENSE](LICENSE) for details.
