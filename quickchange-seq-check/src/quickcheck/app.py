"""Local upload interface, started by launch.py."""
from contextlib import redirect_stderr
import hashlib
import io
import json
import tempfile
from pathlib import Path
import streamlit as st
from Bio import SeqIO
from quickcheck.cli import main

st.set_page_config(page_title='Sequencing QuickCheck', layout='wide')
st.title('Sequencing QuickCheck')
st.caption('Analyze files on this computer. No API key or subscription required.')
st.info('Upload your original reference and sequencing reads below. Leave the expected edits blank to discover differences.')
ref = st.file_uploader('1. Choose your reference sequence', type=['gb', 'gbk', 'genbank', 'fasta', 'fa'],
    help='Choose the original plasmid reference. GenBank (.gb/.gbk) includes gene annotations needed for amino-acid checks.')
reads = st.file_uploader('2. Choose your sequencing files', type=['ab1', 'abi', 'seq', 'fasta', 'fa', 'fastq'],
    accept_multiple_files=True, help='Select several files together. Prefer .ab1 files because they include base quality.')
feature_index = None
valid_reference = True
features = []
if ref:
    try:
        fmt = 'genbank' if ref.name.lower().endswith(('.gb','.gbk','.genbank')) else 'fasta'
        record = SeqIO.read(io.StringIO(ref.getvalue().decode('utf-8-sig')), fmt)
        features = [f for f in record.features if f.type == 'CDS']
        if features:
            def feature_name(index):
                f = features[index-1]
                label = next((f.qualifiers[k][0] for k in ('label','gene','product','locus_tag') if f.qualifiers.get(k)), 'Unnamed CDS')
                return f'{label} — {f.location}'
            feature_index = st.selectbox('3. Select the gene you want to check', list(range(1,len(features)+1)),
                index=0 if len(features)==1 else None, placeholder='Choose a gene from your reference', format_func=feature_name)
        else:
            st.warning('No annotated coding sequence found. DNA differences can be checked; amino-acid targets require an annotated GenBank reference.')
    except (ValueError, UnicodeError) as exc:
        st.error('The reference could not be read: '+str(exc))
        valid_reference = False
expected = st.text_input('4. Expected amino-acid edits (optional)', placeholder='Example: N154S or H72N,M120L',
    help='One edit or comma-separated edits. These apply to every uploaded read. Leave blank for discovery; filenames do not define targets.')
if expected:
    st.caption('The same expected edits will be checked in every uploaded read. Partial reads may not cover every target.')
signature = hashlib.sha256()
for f in ([ref] if ref else []) + list(reads or []):
    signature.update(f.name.encode()); signature.update(f.getvalue())
signature.update(str((feature_index,expected)).encode())
current = signature.hexdigest()
if st.button('Analyze sequences', type='primary', disabled=not ref or not reads or not valid_reference or (bool(features) and feature_index is None)):
    st.session_state.pop('reports', None)
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        rp = root / ('reference.' + ref.name.rsplit('.', 1)[-1])
        rp.write_bytes(ref.getvalue())
        folder = root / 'reads'; folder.mkdir()
        names = [Path(r.name).name for r in reads]
        if len(names) != len(set(names)):
            st.error('Two files have the same name. Rename one before selecting them again.')
            st.stop()
        for name, read in zip(names, reads):
            (folder / name).write_bytes(read.getvalue())
        args = ['--reference', str(rp), '--input-dir', str(folder), '--out-dir', str(root/'report')]
        if feature_index: args += ['--feature-index', str(feature_index)]
        if expected: args += ['--expected', expected]
        errors = io.StringIO()
        with st.spinner('Aligning and checking your sequences...'), redirect_stderr(errors):
            code = main(args)
        if code:
            st.error(errors.getvalue() or 'Analysis could not complete. Please check your input files.')
        else:
            st.session_state['reports'] = {p.name: p.read_bytes() for p in (root/'report').iterdir()}
            st.session_state['report_signature'] = current
if 'reports' in st.session_state and st.session_state.get('report_signature') == current:
    st.success('Analysis complete. Review the summary and save your report below.')
    payload = json.loads(st.session_state['reports']['quickchange_report.json'])
    st.dataframe([{'Sample': r['sample'], 'Result': r['status'], 'Expected edits': ', '.join(r['expected']) or 'Discovery mode',
        'Extra substitutions': len(r['unexpected_variants']), 'Insertions / deletions': len(r['indels']),
        'Covered reference range': r['aligned_reference_range']} for r in payload['results']], hide_index=True)
    for name, data in st.session_state['reports'].items():
        st.download_button('Save ' + name, data, file_name=name)
    st.caption('Save the HTML report before closing the application. A clean partial read does not verify the entire plasmid.')
    import streamlit.components.v1 as components
    components.html(st.session_state['reports']['quickchange_report.html'].decode(), height=900, scrolling=True)
