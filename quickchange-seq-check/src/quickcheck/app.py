"""Launch: streamlit run src/quickcheck/app.py"""
import tempfile
from pathlib import Path
import streamlit as st
from quickcheck.cli import main

st.set_page_config(page_title='Sequencing QuickCheck', layout='wide')
st.title('Sequencing QuickCheck')
st.caption('Local analysis • No API key • Explicit reference • Aligned regions only')
ref = st.file_uploader('Reference', type=['gb', 'gbk', 'genbank', 'fasta', 'fa'])
reads = st.file_uploader('Sequencing reads', type=['ab1', 'abi', 'seq', 'fasta', 'fa', 'fastq'], accept_multiple_files=True)
feature = st.text_input('CDS label (required when the reference has multiple CDS features)')
expected = st.text_input('Expected AA edits (optional)', placeholder='L90E,M120L; leave blank for discovery')
if st.button('Analyze', disabled=not ref or not reads):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        rp = root / ('reference.' + ref.name.rsplit('.', 1)[-1])
        rp.write_bytes(ref.getvalue())
        folder = root / 'reads'
        folder.mkdir()
        names = [Path(r.name).name for r in reads]
        if len(names) != len(set(names)):
            st.error('Duplicate filenames: rename reads before uploading.')
            st.stop()
        for name, read in zip(names, reads):
            (folder / name).write_bytes(read.getvalue())
        args = ['--reference', str(rp), '--input-dir', str(folder), '--out-dir', str(root/'report')]
        if feature: args += ['--feature-label', feature]
        if expected: args += ['--expected', expected]
        if main(args):
            st.error('Analysis could not complete. Check CDS selection and input files; see terminal details.')
        else:
            st.session_state['reports'] = {p.name: p.read_bytes() for p in (root/'report').iterdir()}
if 'reports' in st.session_state:
    for name, data in st.session_state['reports'].items():
        st.download_button('Download ' + name, data, file_name=name)
    import streamlit.components.v1 as components
    components.html(st.session_state['reports']['quickchange_report.html'].decode(), height=900, scrolling=True)
