"""Local structure upload adapter and synthetic demonstration."""
import csv
import html
import io
import json
from pathlib import Path
import zipfile
from triage import analyze


def execute(folder, reference, structure, suffix, chain, query, kind='bfactor'):
    ref = folder/'reference.fasta'; ref.write_bytes(reference)
    coords = folder/('structure'+suffix); coords.write_bytes(structure)
    result = analyze(ref,coords,chain,query,kind)
    buffer = io.BytesIO()
    table = io.StringIO()
    columns = list(dict.fromkeys(k for row in result['results'] for k in row))
    writer = csv.DictWriter(table,fieldnames=columns); writer.writeheader(); writer.writerows(result['results'])
    report = ('<!doctype html><html lang="en"><meta charset="utf-8"><title>Structure Triage</title>'
        '<h1>Structure Triage</h1><p>Input-structure descriptors. No functional prediction or ΔΔG backend is configured.</p><pre>'
        +html.escape(json.dumps(result,indent=2))+'</pre></html>')
    with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('structure_report.json',json.dumps(result,indent=2))
        z.writestr('structure_report.csv',table.getvalue())
        z.writestr('structure_report.html',report)
    return {'report':result,'zip':buffer.getvalue()}


def demo(folder):
    names = ['MET','ALA','GLY','TRP']
    pdb = ''.join(f'ATOM  {i:5d}  CA  {name} A{i:4d}    {i*3.:8.3f}{0.:8.3f}{0.:8.3f}{1.:6.2f}{80.:6.2f}           C  \n' for i,name in enumerate(names,1))+'END\n'
    return execute(folder,b'>SYNTHETIC DEMO\nMAGW\n',pdb.encode(),'.pdb','A','Assess A2E')
