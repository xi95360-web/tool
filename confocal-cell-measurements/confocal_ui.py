"""Upload adapters and synthetic demo for the local imaging interface."""
import csv
import io
import json
from pathlib import Path
import zipfile
import numpy as np
import tifffile
from analyze import run


def archive(folder):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in sorted(folder.iterdir()):
            if path.is_file(): z.writestr(path.name, path.read_bytes())
    return buffer.getvalue()


def execute(folder, rows, files, config):
    for role, contents in files.items():
        target = folder/role; target.mkdir()
        for name, data in contents.items():
            if Path(name).name != name or name in {'','.', '..'}:
                raise ValueError('Invalid image filename')
            (target/name).write_bytes(data)
    manifest = folder/'images.csv'
    with manifest.open('w',newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['image_id','reference','signal','labels','original_size_z','pixel_um','condition','biological_replicate'])
        writer.writeheader()
        for index,row in enumerate(rows):
            writer.writerow({'image_id':str(row.get('image_id') or f'field_{index+1}'),
                'reference':'reference/'+row['reference'], 'signal':'signal/'+row['signal'],
                'labels':'labels/'+row['labels'] if row.get('labels') else '',
                'original_size_z':1, 'pixel_um':row['pixel_um'],
                'condition':row.get('condition',''), 'biological_replicate':row.get('biological_replicate','')})
    cells = run(manifest,config,folder/'results')
    output = folder/'results'
    return {'cells':cells, 'zip':archive(output),
        'overlays':{p.name:p.read_bytes() for p in output.glob('*_overlay.png')}}


def demo(folder):
    yy,xx = np.mgrid[:96,:96]
    labels = np.zeros((96,96),np.uint16)
    labels[(yy-45)**2+(xx-45)**2<20**2] = 1
    reference = np.where(labels>0,110,10).astype(np.uint16)
    signal = np.where(labels>0,205,5)+80*np.exp(-((yy-45)**2+(xx-45)**2)/4)
    files = {}
    for role,array in [('reference',reference),('signal',signal.astype(np.uint16)),('labels',labels)]:
        buffer = io.BytesIO(); tifffile.imwrite(buffer,array)
        files[role] = {'synthetic.tif':buffer.getvalue()}
    rows = [{'image_id':'SYNTHETIC DEMO','reference':'synthetic.tif','signal':'synthetic.tif',
        'labels':'synthetic.tif','pixel_um':.2,'condition':'Synthetic example'}]
    return execute(folder,rows,files,{'backend':'threshold'})
