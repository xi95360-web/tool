"""Two-channel, original single-plane measurements; no API required."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
import tifffile
from scipy import ndimage as ndi
from skimage import filters, measure, morphology, segmentation, io
from puncta import detect_and_measure, DEFAULT


def read_plane(path):
    a = tifffile.imread(path)
    if a.ndim != 2 or not np.all(np.isfinite(a)):
        raise ValueError('Requires finite original 2D data: ' + str(path))
    return a


def segment(image, cfg):
    if cfg['backend'] == 'cellpose':
        from cellpose import models
        model = models.CellposeModel(gpu=cfg.get('gpu', False), pretrained_model=cfg.get('model', 'cpsam_v2'))
        x = np.stack([image, np.zeros_like(image), np.zeros_like(image)], axis=-1)
        return model.eval(x, channel_axis=-1, do_3D=False, min_size=cfg['min_cell_pixels'])[0]
    if cfg['backend'] != 'threshold':
        raise ValueError('backend must be cellpose or threshold')
    smooth = ndi.gaussian_filter(image.astype(float), 1)
    binary = smooth > filters.threshold_otsu(smooth)
    binary = morphology.remove_small_objects(binary, min_size=cfg['min_cell_pixels'])
    return measure.label(ndi.binary_fill_holes(binary))


def export_csv(path, rows, fields=None):
    fields = fields or list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run(manifest, config, output):
    cfg = {'backend': 'cellpose', 'min_cell_pixels': 100, 'min_denominator': 1.,
           'background_margin_pixels': 3, 'min_background_pixels': 100, **config}
    if output.exists():
        raise ValueError('Output exists; choose a new directory')
    if cfg['min_denominator'] <= 0 or cfg['min_cell_pixels'] < 1:
        raise ValueError('Invalid denominator or cell-size threshold')
    with manifest.open(newline='') as f:
        fields = list(csv.DictReader(f))
    if not fields or len({x['image_id'] for x in fields}) != len(fields):
        raise ValueError('Manifest needs unique, nonempty image_id rows')
    allcells, allspots, summaries, provenance = [], [], [], []
    output.mkdir(parents=True)
    for index, row in enumerate(fields):
        if int(row['original_size_z']) != 1:
            raise ValueError('Original SizeZ must be verified as 1: ' + row['image_id'])
        um = float(row['pixel_um'])
        if not np.isfinite(um) or um <= 0:
            raise ValueError('pixel_um must be positive')
        def resolve(key):
            p = Path(row[key])
            return p if p.is_absolute() else manifest.parent / p
        ref, signal = read_plane(resolve('reference')), read_plane(resolve('signal'))
        if ref.shape != signal.shape:
            raise ValueError('Channel shape mismatch')
        if row.get('labels'):
            labels = read_plane(resolve('labels'))
        else:
            labels = segment(ref, cfg)
        if labels.shape != ref.shape or labels.dtype.kind not in 'iu' or np.any(labels < 0):
            raise ValueError('Labels must be nonnegative integers at original image dimensions')
        labels = labels.astype(np.uint32)
        bg = ~ndi.binary_dilation(labels > 0, iterations=cfg['background_margin_pixels'])
        if bg.sum() < cfg['min_background_pixels']:
            raise ValueError('Insufficient clean image background: ' + row['image_id'])
        rb, sb = float(np.median(ref[bg])), float(np.median(signal[bg]))
        metadata = {k: row.get(k, '') for k in ('image_id', 'condition', 'biological_replicate')}
        spots, spot_labels, info, large = detect_and_measure(signal, labels, um, metadata, cfg.get('puncta'))
        allspots.extend(spots)
        cells = []
        for region in measure.regionprops(labels):
            mask = labels == region.label
            r, s = ref[mask].astype(float)-rb, signal[mask].astype(float)-sb
            accepted = [p for p in spots if p['cell_id'] == region.label and p['accepted']]
            rm, sm = float(r.mean()), float(s.mean())
            rmed, smed = float(np.median(r)), float(np.median(s))
            edge = bool(mask[0].any() or mask[-1].any() or mask[:,0].any() or mask[:,-1].any())
            flags = ['border_cell'] if edge else []
            if rm <= cfg['min_denominator']: flags.append('low_reference_mean')
            if np.issubdtype(ref.dtype, np.integer) and np.any(ref[mask] == np.iinfo(ref.dtype).max):
                flags.append('reference_saturation')
            if np.issubdtype(signal.dtype, np.integer) and np.any(signal[mask] == np.iinfo(signal.dtype).max):
                flags.append('signal_saturation')
            fraction = float(np.maximum(s[spot_labels[mask] > 0], 0).sum()/np.maximum(s, 0).sum()) if np.maximum(s, 0).sum() else None
            cells.append({**metadata, 'cell_id': int(region.label), 'area_px': int(region.area),
                'area_um2': float(region.area*um**2), 'reference_background': rb, 'signal_background': sb,
                'reference_mean_corrected': rm, 'signal_mean_corrected': sm,
                'ratio_of_means': sm/rm if rm > cfg['min_denominator'] else None,
                'ratio_of_medians': smed/rmed if rmed > cfg['min_denominator'] else None,
                'puncta_count': len(accepted), 'signal_fraction_in_puncta': fraction,
                'puncta_excess_integral': sum(p['integrated_intensity_local_corrected_DN_px'] for p in accepted),
                'qc_pass': not flags, 'qc_flags': ';'.join(flags)})
        allcells.extend(cells)
        summaries.append({**metadata, 'n_cells': len(cells), 'n_qc_pass': sum(c['qc_pass'] for c in cells), **info})
        prefix = f'field_{index:04d}'
        tifffile.imwrite(output/(prefix+'_cells.tif'), labels)
        tifffile.imwrite(output/(prefix+'_puncta.tif'), spot_labels)
        def norm(x):
            low, high = np.percentile(x, [1,99.8])
            return np.clip((x.astype(float)-low)/max(high-low, 1), 0, 1)
        rgb = np.stack([norm(ref), norm(signal), np.zeros_like(ref, dtype=float)], axis=-1)
        rgb[segmentation.find_boundaries(labels)] = [0, 1, 1]
        rgb[segmentation.find_boundaries(spot_labels)] = [1, 0, 1]
        io.imsave(output/(prefix+'_overlay.png'), (rgb*255).astype(np.uint8), check_contrast=False)
        provenance.append({'image_id': row['image_id'], 'output_prefix': prefix,
            'inputs': {key: {'path': str(resolve(key)), 'sha256': hashlib.sha256(resolve(key).read_bytes()).hexdigest()}
                       for key in ('reference', 'signal', 'labels') if row.get(key)}})
    export_csv(output/'cells.csv', allcells, None if allcells else ['image_id','cell_id','qc_pass'])
    export_csv(output/'puncta.csv', allspots, None if allspots else ['image_id','cell_id','punctum_id','accepted'])
    export_csv(output/'fields.csv', summaries)
    import importlib.metadata as md
    (output/'run.json').write_text(json.dumps({'config': cfg, 'puncta_defaults': DEFAULT,
        'manifest': fields, 'provenance': provenance,
        'versions': {p: md.version(p) for p in ('numpy','scipy','scikit-image','tifffile')},
        'note': 'Original 2D only. Candidate puncta are not evidence of autophagic flux. Cells are nested within fields and biological replicates.'}, indent=2))
    return allcells


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    run(a.manifest, json.loads(a.config.read_text()), a.out)
    print(a.out)

if __name__ == '__main__':
    main()
