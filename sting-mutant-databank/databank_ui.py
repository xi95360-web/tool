"""Byte-based database operations for a local session; no SQL editing needed."""
from datetime import date
import io
import csv
from pathlib import Path
import sqlite3
import tempfile
from uuid import uuid4
import zipfile
from databank import build

TABLES = ['sources','variants','compounds','endpoints','claims','claim_compounds','contexts','experiments',
    'treatments','measurements','structures','structure_compounds','field_provenance','collection_queue']


def create(csv_files=None):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp); folder = root/'csv'; folder.mkdir()
        for name,data in (csv_files or {}).items():
            if name not in {t+'.csv' for t in TABLES}: raise ValueError('Unknown table filename: '+name)
            (folder/name).write_bytes(data)
        path = root/'evidence.sqlite'; build(path,folder)
        return path.read_bytes()


def browse(data,query='',view='claims'):
    if view not in {'claims','measurements'}: raise ValueError('Choose claims or measurements')
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp)/'evidence.sqlite'; path.write_bytes(data)
        conn = sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True)
        try:
            names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not set(TABLES)<=names: raise ValueError('This is not a compatible STING Databank database.')
            if conn.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or conn.execute('PRAGMA foreign_key_check').fetchall():
                raise ValueError('Database integrity or source links failed validation.')
            counts = {t:conn.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in TABLES}
            conn.row_factory = sqlite3.Row
            sql = 'SELECT * FROM v_'+('claim' if view=='claims' else 'measurement')+'_crosslinks WHERE variant LIKE ? OR compounds LIKE ? OR endpoint LIKE ? LIMIT 1000'
            rows = [dict(r) for r in conn.execute(sql,['%'+query+'%']*3)]
            return counts,rows
        finally: conn.close()


def add_claim(data,record):
    required = ['title','url','variant','species','background','endpoint','summary','locator','relation','scope']
    if any(not str(record.get(k,'')).strip() for k in required): raise ValueError('Fill in the source, protein context, endpoint, finding and source location.')
    if not record.get('checked'): raise ValueError('Confirm that you checked the original source before adding this record.')
    if record['scope'] not in {'abstract','figure_caption','full_text','supplement'}: raise ValueError('Invalid source scope')
    taxon = int(record.get('taxon',0))
    if taxon < 1: raise ValueError('Taxonomy ID must be positive; human=9606, mouse=10090.')
    browse(data)
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp)/'evidence.sqlite'; path.write_bytes(data)
        conn = sqlite3.connect(path)
        try:
            conn.execute('PRAGMA foreign_keys=ON')
            suffix = uuid4().hex
            sid,vid,eid,cid = ['S_'+suffix,'V_'+suffix,'E_'+suffix,'K_'+suffix]
            with conn:
                conn.execute('INSERT INTO sources(source_id,title,doi,url,source_type,inspected_scope,accessed_date) VALUES(?,?,?,?,?,?,?)',
                    (sid,record['title'],record.get('doi') or None,record['url'],'paper',record['scope'],date.today().isoformat()))
                conn.execute('INSERT INTO variants(variant_id,label,protein_species,taxon_id,mutations_as_reported,background_as_reported,identity_status,source_id) VALUES(?,?,?,?,?,?,?,?)',
                    (vid,record['variant'],record['species'],taxon,record.get('mutations') or None,record['background'],'study_scoped',sid))
                conn.execute('INSERT INTO endpoints(endpoint_id,name,definition) VALUES(?,?,?)',(eid,record['endpoint'],record.get('assay') or record['endpoint']))
                ligands = list(dict.fromkeys(x.strip() for x in record.get('ligands','').split(';') if x.strip()))
                kind = 'baseline' if not ligands else 'single' if len(ligands)==1 else 'combination'
                conn.execute('INSERT INTO claims(claim_id,source_id,variant_id,endpoint_id,treatment_kind,relation,comparator_as_reported,summary,locator,evidence_scope,review_status) VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                    (cid,sid,vid,eid,kind,record['relation'],record.get('comparator') or None,record['summary'],record['locator'],record['scope'],'source_checked'))
                for index,ligand in enumerate(ligands):
                    compound = 'C_'+suffix+'_'+str(index)
                    conn.execute('INSERT INTO compounds(compound_id,name,identity_status,identity_source_id) VALUES(?,?,?,?)',
                        (compound,ligand,'name_only_study_scoped',sid))
                    conn.execute('INSERT INTO claim_compounds VALUES(?,?,?)',(cid,compound,'ligand' if len(ligands)==1 else 'co_treatment'))
            return path.read_bytes()
        finally: conn.close()


def templates():
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp)/'empty.sqlite'; build(path)
        conn = sqlite3.connect(path)
        buffer = io.BytesIO()
        try:
            with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as z:
                for table in TABLES:
                    columns = [r[1] for r in conn.execute('PRAGMA table_info('+table+')')]
                    output = io.StringIO(); csv.writer(output).writerow(columns)
                    z.writestr(table+'.csv',output.getvalue())
            return buffer.getvalue()
        finally: conn.close()


def demo():
    return add_claim(create(),{'title':'SYNTHETIC DEMO — not a publication','url':'https://example.org/synthetic',
        'variant':'Synthetic example variant','species':'Synthetic example','taxon':9606,'background':'Synthetic fixture; no biological interpretation',
        'endpoint':'Synthetic endpoint','summary':'Synthetic record for learning the interface only. No biological result is asserted.',
        'locator':'Synthetic example','relation':'synthetic_example','scope':'abstract','checked':True})
