# Confocal Cell Measurements

## Start here — no coding required

[中文入门](./START_HERE.zh-CN.md)

1. On the [GitHub homepage](https://github.com/xi95360-web/tool), click **Code → Download ZIP**.
2. Extract the ZIP. Open `tool-main`, then `confocal-cell-measurements`. Keep the whole folder together.
3. Make sure Python 3.10 or later is installed. If it is missing, use the installer from [python.org](https://www.python.org/downloads/).
4. On Mac, double-click **Start Confocal Analysis.command**. On Windows, double-click **Start Confocal Analysis.bat** (the Windows entry point has not yet been tested on Windows).
5. A terminal window opens. First launch needs internet and may take several minutes to install components. The application then opens in your browser. Keep that terminal window open.
6. Click **Try a synthetic example** to try the complete result flow before preparing real data. The example is artificial and clearly labeled.
7. Follow the steps below for your own files. No commands, manifest files, or configuration editing are needed in the browser interface.

This is a local browser application with automatic first-time setup, not a standalone installer with Python included. Ordinary analysis needs no API key. Files are processed on the computer running this app.

## Analyze your own images

1. Prepare one original-resolution 2D TIFF per channel and field. This version accepts original **Z=1, T=1** images with equal X/Y pixel sizes, not projections or time series. Pixel size must come from acquisition metadata.
2. Upload the **cell-boundary channel** images (e.g. RFP), then the **measured channel** images (e.g. GFP). Do not upload an RGB screenshot.
3. Choose how to outline cells:
   - **Use existing cell masks:** upload integer-label TIFFs from a segmentation tool. Every cell needs a unique positive integer; background is 0. A binary foreground mask containing all cells as one value is not sufficient for single-cell measurements.
   - **Cellpose-SAM:** close the running app, double-click **Install Cellpose.command** (Mac) or **Install Cellpose.bat** (Windows), wait for installation, then reopen the app. This optional installation is large. The first segmentation run may additionally download model weights. CPU mode works more slowly; GPU availability depends on your system.
   - **Simple threshold (baseline):** immediately available; suitable for a trial on separated cells. Touching cells may merge, so review overlays.
4. Enter the **pixel size in micrometers per pixel** and confirm the source metadata checkbox. If images have different pixel sizes, analyze them in separate batches.
5. In the matching table, select the measured image and mask belonging to each boundary image. Pair them by field, not by upload order. Add condition/replicate labels if known. A replicate label identifies an independent biological experiment, not an individual cell.
6. Open **Measurement settings** only if you need to change the size/contrast gates. Defaults are starting values, not validated universal thresholds.
7. Click **Analyze images**. Inspect the cyan cell boundaries and magenta puncta outlines before accepting the measurements.
8. Click **Save all results (.zip)**. Unzip it and open `cells.csv`, `puncta.csv` or `fields.csv` in Excel. CSV files include QC flags. TIFF masks and overlays can also be opened in Fiji.

## If your files are CZI

The upload page currently accepts TIFF only. Use the included Fiji bridge first; no code editing is required:

1. Open Fiji. Choose **File → New → Script** to open its Script Editor.
2. In the Script Editor, open **export_channels.groovy** from this project folder.
3. Select **Language → Groovy**, then click **Run**.
4. Choose the original CZI file and a new, empty export folder. The script exports eligible single-plane channels plus metadata.
5. Check which exported channel corresponds to RFP/GFP and check the physical units. Enter the pixel size in micrometers in the browser app. Do not assume a channel identity from its display color.
6. Upload the exported TIFF pairs as described above. For additional source files, use separate export folders so series filenames do not collide.

This bridge still needs manual acceptance testing in Fiji. The Script Editor route is documented in the [official Fiji guide](https://imagej.net/scripting/script-editor).

## Save, close, and reopen

Save the result using the page's **Save** button before closing. Results are held in the running app session until you download them. Click the terminal window and press **Control+C** to stop the application. Next time, double-click **Start Confocal Analysis** again; installed components are reused.

## If startup fails

- **Python missing / too old:** install Python 3.10 or later, then retry.
- **Installation download fails:** check your connection and retry the same launcher.
- **pip update notice:** this is information, not the cause of a failure.
- **Browser does not open:** open the local address printed in the terminal, usually `http://localhost:8501`.
- **Port already in use:** stop another workflow with Control+C, then retry. Only one default launcher can use port 8501 at a time.
- **Mac blocks double-clicking:** use Open only after verifying the downloaded file came from this repository. Alternatively, type `python3` plus a space in Terminal, drag this folder's **launch.py** into the window, then press Return. Do not disable macOS security settings.
- **An error appears during analysis:** the page shows the cause. Check the file type and required fields, correct them, and retry. Existing experiment files are not edited.

## Advanced reference (optional)

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
