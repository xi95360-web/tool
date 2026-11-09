"""Multiscale LoG spot detection, local background measurement, and parent-cell assignment.

Uses published building blocks (LoG/top-hat, intensity watershed, per-cell assignment),
not a learned punctum classifier. Size/contrast parameters require image review.
"""
import numpy as np
from scipy import ndimage as ndi
from skimage import feature,morphology,segmentation,measure

DEFAULT={'diameter_min_um':.6,'diameter_max_um':2.,'minimum_area_um2':.15,
         'maximum_area_um2':3.2,'background_radius_um':2.5,
         'contrast_min_DN':3.,'noise_multiplier':3.,'minimum_pixels':3,
         'ring_inner_um':.4,'ring_outer_um':1.2,'minimum_parent_fraction':.8,
         'maximum_connected_area_um2':12.8}

def detect_and_measure(image,cells,pixel_um,metadata=None,config=None):
    cfg={**DEFAULT,**(config or {})};metadata=metadata or {}
    a=np.asarray(image,dtype=np.float64);cells=np.asarray(cells)
    if a.ndim!=2 or cells.shape!=a.shape:raise ValueError('Requires 2D GFP and same-size cell labels')
    radius=max(2,round(cfg['background_radius_um']/pixel_um))
    background=morphology.opening(a,morphology.disk(radius))
    enhanced=np.maximum(a-background,0)
    highpass=a-ndi.gaussian_filter(a,.7)
    vals=highpass[cells>0]
    mad=1.4826*np.median(np.abs(vals-np.median(vals))) if len(vals) else 0.
    noise=max(1.,float(mad));threshold=max(cfg['contrast_min_DN'],cfg['noise_multiplier']*noise)
    min_sigma=max(.6,cfg['diameter_min_um']/(2*np.sqrt(2)*pixel_um))
    max_sigma=max(min_sigma+.05,cfg['diameter_max_um']/(2*np.sqrt(2)*pixel_um))
    blobs=feature.blob_log(enhanced,min_sigma=min_sigma,max_sigma=max_sigma,
                           num_sigma=6,threshold=threshold*.45,overlap=.5,exclude_border=False)
    foreground=(enhanced>=threshold)&(cells>0)
    components,n=ndi.label(foreground)
    sizes=np.bincount(components.ravel())*pixel_um**2
    # Broad bright structures are not forced into many artificial puncta.
    too_large=sizes>cfg['maximum_connected_area_um2'];too_large[0]=False
    large_mask=too_large[components]
    foreground&=~large_mask
    seeds=np.zeros(a.shape,np.int32);seed_count=0
    for y,x,sigma in blobs:
        iy,ix=int(round(y)),int(round(x))
        if foreground[iy,ix] and seeds[iy,ix]==0:
            seed_count+=1;seeds[iy,ix]=seed_count
    detected=segmentation.watershed(-ndi.gaussian_filter(enhanced,.35),seeds,mask=foreground) if seed_count else np.zeros(cells.shape,np.int32)
    rows=[];accepted=np.zeros(cells.shape,np.uint32);inner=max(1,round(cfg['ring_inner_um']/pixel_um));outer=max(inner+1,round(cfg['ring_outer_um']/pixel_um))
    for region in measure.regionprops(detected):
        rr,cc=region.coords.T;parents,counts=np.unique(cells[rr,cc],return_counts=True)
        parent=int(parents[np.argmax(counts)]);fraction=float(max(counts)/region.area)
        flags=[];area=region.area*pixel_um**2
        if parent==0:flags.append('outside_cells')
        if fraction<cfg['minimum_parent_fraction']:flags.append('ambiguous_parent_cell')
        if region.area<cfg['minimum_pixels'] or area<cfg['minimum_area_um2']:flags.append('below_minimum_size')
        if area>cfg['maximum_area_um2']:flags.append('above_maximum_size')
        y0,x0,y1,x1=region.bbox
        sl=(slice(max(0,y0-outer),min(a.shape[0],y1+outer)),slice(max(0,x0-outer),min(a.shape[1],x1+outer)))
        obj=detected[sl]==region.label
        ring=ndi.binary_dilation(obj,iterations=outer)&~ndi.binary_dilation(obj,iterations=inner)
        ring&=(cells[sl]==parent)&~foreground[sl]&~large_mask[sl]
        ring_values=a[sl][ring]
        method='local_annulus'
        if len(ring_values)<5:
            ring=(cells==parent)&~foreground&~large_mask;ring_values=a[ring];method='cell_nonpunctate_fallback'
        if len(ring_values)<3:
            local_bg=float(np.median(background[rr,cc]));method='morphological_background_fallback'
        else:local_bg=float(np.median(ring_values))
        raw=a[rr,cc];corrected=raw-local_bg
        local_noise=max(1.,float(1.4826*np.median(abs(ring_values-np.median(ring_values))))) if len(ring_values)>=3 else noise
        local_threshold=max(threshold,cfg['noise_multiplier']*local_noise)
        if raw.max()-local_bg<local_threshold or corrected.mean()<local_threshold:flags.append('low_local_contrast')
        row={**metadata,'punctum_id':int(region.label),'cell_id':parent,
             'area_px':int(region.area),'area_um2':float(area),'parent_fraction':fraction,
             'centroid_y':float(region.centroid[0]),'centroid_x':float(region.centroid[1]),
             'raw_mean_DN':float(raw.mean()),'raw_max_DN':float(raw.max()),
             'local_background_DN':local_bg,'background_method':method,
             'mean_intensity_local_corrected_DN':float(corrected.mean()),
             'integrated_intensity_local_corrected_DN_px':float(corrected.sum()),
             'spatial_integral_local_corrected_DN_um2':float(corrected.sum()*pixel_um**2),
             'peak_contrast_DN':float(raw.max()-local_bg),'noise_floor_DN':noise,
             'local_noise_floor_DN':local_noise,'local_mean_SNR':float(corrected.mean()/local_noise),
             'detection_threshold_DN':threshold,'accepted':not flags,'rejection_flags':';'.join(flags)}
        rows.append(row)
        if not flags:accepted[rr,cc]=region.label
    info={'noise_floor_DN':noise,'contrast_threshold_DN':threshold,'candidate_puncta':len(rows),
          'accepted_puncta':sum(r['accepted'] for r in rows),'large_bright_structure_area_um2':float(large_mask.sum()*pixel_um**2),
          'resolution_warning':pixel_um>.3,'sampling_note':'XY > 0.3 um/pixel: small GFP-LC3 puncta can be unresolved' if pixel_um>.3 else ''}
    return rows,accepted,info,large_mask
