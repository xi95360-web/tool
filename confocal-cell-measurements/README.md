# Confocal Cell Measurements

Version 0.1.0 preview. Original single-plane analysis: one channel defines cells, the other is measured inside the same masks. Outputs background-corrected ratios of means and medians, candidate puncta, cell/field CSV tables, label TIFFs, QC overlays and run provenance. No API key required.

## Run

Use a dedicated Python 3.11/3.12 environment. From this directory:

```sh
python -m pip install -r requirements.txt
python analyze.py --manifest images.csv --config config.example.json --out new-results
```

Manifest columns are shown in `manifest.example.csv`. Paths resolve relative to the manifest. `reference` is the segmentation channel; `signal` is the measured channel. `labels` is optional and takes precedence over segmentation. Supply original-resolution integer labels, with 0=background and a unique positive ID per cell. `pixel_um` assumes square XY pixels. `original_size_z` records verified source metadata; a projected stack is not eligible. Do not change Z metadata merely to pass validation.

For CZI and other vendor files, run `export_channels.groovy` in Fiji's Groovy Script Editor. It exports unscaled channel TIFFs only from series with original Z=1 and T=1, plus source metadata. Verify channel identities and convert the physical calibration to micrometers before making a manifest. No channel identity is inferred from display colors. The bridge requires Fiji/Bio-Formats and has not yet been manually verified in Fiji.

## Segmentation

Use precomputed Cellpose/Fiji labels, or install `cellpose>=4.2,<5` separately and select `backend: cellpose` with `model: cpsam_v2`. The first model run may download upstream weights. The adapter supplies only the segmentation channel and zero-filled auxiliary channels, and verifies original output dimensions. See [Cellpose API](https://cellpose.readthedocs.io/en/latest/api.html) and upstream code/model licenses. Model execution is optional and not part of the lightweight test suite.

`backend: threshold` supplies a simple Otsu connected-component baseline, useful for smoke tests and well-separated cells. It is not equivalent to Cellpose and requires image-specific validation. This release does not resize inputs; externally resized masks must be restored before import.

## Measurements and QC

Image background is the median outside dilated cell masks. Ratios use corrected channel means/medians; a near-zero reference denominator yields a missing value, not infinity. Puncta use top-hat enhancement, multiscale LoG seeds, watershed, and size/local-contrast/parent-cell gates. Every candidate retains acceptance status and rejection reasons. `signal_fraction_in_puncta` is the fraction of nonnegative image-background-corrected cell signal inside accepted punctum masks. The local-background punctum integral is a separate metric.

Border cells, low reference mean and dtype-maximum saturation are flagged. Retain the `qc_pass` column when filtering. Detector thresholds require QC on representative controls; saturation below the file dtype maximum requires additional acquisition-specific checks. Single-plane puncta are candidate foci, not a direct autophagic-flux measurement. Group inference must use biological replicates; individual cells are nested observations. Group labels and replicates come from the manifest.

Open the output TIFF labels and overlays in Fiji for inspection. JSON records configuration, resolved inputs, input hashes and library versions. On failure, an incomplete output directory may remain; choose a fresh output path for the next run.

Synthetic demo from repository root:

```sh
python examples/make_demo.py --out /tmp/lab-demo
python confocal-cell-measurements/analyze.py --manifest /tmp/lab-demo/confocal/images.csv --config /tmp/lab-demo/confocal/config.json --out /tmp/confocal-demo-results
```
