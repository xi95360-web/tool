"""Guided, local evidence collection and search."""
import hashlib
import streamlit as st
from databank_ui import create, browse, add_claim, templates, demo

st.set_page_config(page_title='STING Databank',layout='wide')
st.title('STING Databank')
st.caption('Collect literature evidence and search your own records • Local processing • No API key')
st.info('This release starts empty. It does not automatically retrieve papers or connect to Paperclip. An empty search means no matching imported evidence.')
if 'database' in st.session_state:
    st.caption('Save your current databank before starting a new one, opening another file or importing tables: these replace the current session.')
col1,col2 = st.columns(2)
if col1.button('Start a new empty databank'):
    st.session_state['database'] = create(); st.session_state['demo'] = False
if col2.button('Try a synthetic example'):
    st.session_state['database'] = demo(); st.session_state['demo'] = True
with st.expander('Open a saved databank'):
    uploaded = st.file_uploader('Choose a databank saved by this app',type=['sqlite','db'])
    if st.button('Open database',disabled=not uploaded):
        try:
            browse(uploaded.getvalue())
            st.session_state['database'] = uploaded.getvalue(); st.session_state['demo'] = False
        except Exception as exc: st.error('Database could not be opened: '+str(exc))
with st.expander('Import existing structured CSV tables (optional)'):
    st.caption('If you are starting from papers, use the simple Add literature record form below instead. CSV imports require the linked table format; arbitrary Paperclip exports are not yet supported.')
    st.download_button('Save empty table templates (.zip)',templates(),file_name='databank_templates.zip')
    files = st.file_uploader('Select table CSVs',type=['csv'],accept_multiple_files=True)
    if st.button('Build databank from these CSVs',disabled=not files):
        try:
            if len({f.name for f in files})!=len(files): raise ValueError('Duplicate table filenames')
            data = create({f.name:f.getvalue() for f in files}); browse(data)
            st.session_state['database'] = data; st.session_state['demo'] = False
        except Exception as exc: st.error('Import failed; existing session preserved: '+str(exc))
if 'database' in st.session_state:
    if st.session_state.get('demo'): st.warning('SYNTHETIC DEMO. Start an empty databank before collecting real evidence.')
    st.write('Add literature record')
    st.caption('Each record keeps the protein background and source separate. Records are source-level claims, not fully curated quantitative measurements.')
    with st.form('add_record',clear_on_submit=False):
        title = st.text_input('Paper title')
        url = st.text_input('Source link',placeholder='https://...')
        doi = st.text_input('DOI (optional)')
        variant = st.text_input('Protein / variant label',placeholder='Human STING N154S')
        mutations = st.text_input('Mutations as reported (optional)')
        species = st.text_input('Protein species',value='Homo sapiens')
        taxon = st.number_input('Species taxonomy ID (human 9606; mouse 10090)',min_value=1,value=9606)
        background = st.text_input('Protein background / construct',placeholder='Exact background if known; otherwise write unresolved')
        ligands = st.text_input('Ligands (optional; separate combined treatments with semicolons)',placeholder='Ligand A; Ligand B')
        endpoint = st.text_input('Measured endpoint',placeholder='e.g. IFNB1 mRNA, LC3 puncta, direct ligand binding')
        assay = st.text_input('Assay / context description (optional)')
        relation = st.text_input('Reported direction or relation',placeholder='Use the wording supported by the paper')
        comparator = st.text_input('Compared with (optional)')
        summary = st.text_area('Finding supported by this source')
        locator = st.text_input('Where to find it',placeholder='Figure 2B, Table S1, or Abstract')
        scope = st.selectbox('Part of the source inspected',['abstract','figure_caption','full_text','supplement'])
        checked = st.checkbox('I checked this finding against the original source.')
        submitted = st.form_submit_button('Add record',disabled=st.session_state.get('demo',False))
    if submitted:
        try:
            record = {k: v for k, v in [('title',title),('url',url),('doi',doi),('variant',variant),
                ('mutations',mutations),('species',species),('taxon',taxon),('background',background),
                ('ligands',ligands),('endpoint',endpoint),('assay',assay),('relation',relation),
                ('comparator',comparator),('summary',summary),('locator',locator),('scope',scope),('checked',checked)]}
            st.session_state['database'] = add_claim(st.session_state['database'],record)
            st.success('Record added. Save the databank below to keep your changes.')
        except Exception as exc: st.error('Record could not be added: '+str(exc))
    query = st.text_input('Search variant, ligand or endpoint',placeholder='Leave blank to browse all collected records')
    view = st.radio('Evidence to browse',['Source-level claims','Detailed measurements'],horizontal=True)
    counts,rows = browse(st.session_state['database'],query,'claims' if view=='Source-level claims' else 'measurements')
    st.caption(f"{counts['claims']} source claims • {counts['measurements']} measurements • Results capped at 1,000 rows")
    if rows: st.dataframe(rows,hide_index=True)
    else: st.info('No matching records in this databank. This is not evidence that a biological response is absent.')
    st.download_button('Save databank (.sqlite)',st.session_state['database'],file_name='sting_evidence.sqlite')
    st.caption('Save before closing or restarting. Your work lives in this browser session until you download it. Use Open database next time. Starting a new databank or opening another replaces the current session; save first.')
