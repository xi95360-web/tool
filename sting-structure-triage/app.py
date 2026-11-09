"""Guided structural site descriptors for non-programmers."""
import hashlib
import io
import tempfile
from pathlib import Path
import streamlit as st
from Bio.PDB import PDBParser, MMCIFParser
from structure_ui import execute, demo

st.set_page_config(page_title='STING Structure',layout='wide')
st.title('STING Structure')
st.caption('Map named mutations onto your structure • Local processing • No API key')
st.info('This version reports structural site descriptors. Functional predictions, mutant structures and ΔΔG scores are not yet available.')
if st.button('Try a synthetic example'):
    with tempfile.TemporaryDirectory() as temp:
        st.session_state['result'] = demo(Path(temp))
        st.session_state['result_key'] = 'demo'
reference = st.file_uploader('1. Reference protein sequence (.fasta)',type=['fasta','fa'],help='Amino-acid sequence of your reference protein, not the DNA sequence of the plasmid.')
structure = st.file_uploader('2. Protein structure (.pdb or .cif)',type=['pdb','cif','mmcif'])
chain = None
valid = True
if structure:
    try:
        parser = PDBParser(QUIET=True) if structure.name.lower().endswith('.pdb') else MMCIFParser(QUIET=True)
        model = parser.get_structure('uploaded',io.StringIO(structure.getvalue().decode()))[0]
        ids = [c.id for c in model if any(r.id[0]==' ' for r in c)]
        if not ids: raise ValueError('No protein chains found in model 0.')
        chain = st.selectbox('3. Protein chain',ids,index=0 if len(ids)==1 else None,placeholder='Choose the chain you want to assess')
    except Exception as exc:
        st.error('Structure could not be read: '+str(exc)); valid=False
query = st.text_area('4. Mutations to assess',placeholder='Assess L90E and M120L',help='Include explicit amino-acid notation such as N154S. Multiple edits are assessed independently, not as an epistasis prediction.')
kind_label = st.selectbox('5. What do the structure B-factor fields contain?',[
    'Experimental B factors (default)', 'pLDDT — this file is known to store prediction confidence'])
kind = 'plddt' if kind_label.startswith('pLDDT') else 'bfactor'
signature = hashlib.sha256(repr((chain,query,kind)).encode())
for f in (reference,structure):
    if f: signature.update(f.getvalue())
current = signature.hexdigest()
if st.button('Assess mutations',type='primary',disabled=not reference or not structure or chain is None or not query.strip() or not valid):
    st.session_state.pop('result',None)
    try:
        with st.spinner('Mapping sequence to structure...'), tempfile.TemporaryDirectory() as temp:
            st.session_state['result'] = execute(Path(temp),reference.getvalue(),structure.getvalue(),
                Path(structure.name).suffix.lower(),chain,query,kind)
        st.session_state['result_key'] = current
    except Exception as exc:
        st.error('Assessment could not complete: '+str(exc))
if 'result' in st.session_state and st.session_state.get('result_key') in {'demo',current}:
    result = st.session_state['result']
    if st.session_state['result_key']=='demo': st.warning('SYNTHETIC DEMO — a four-residue artificial structure, not STING evidence.')
    st.metric('Reference / structure identity over aligned residues',f"{result['report']['aligned_identity']:.1%}")
    st.dataframe(result['report']['results'],hide_index=True)
    st.write('Unresolved means the residue was missing or could not be mapped confidently. It does not mean the mutation has no effect.')
    st.download_button('Save report (.zip)',result['zip'],file_name='structure_results.zip')
    for note in result['report']['limitations']: st.caption(note)
