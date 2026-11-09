"""Guided image uploads; no manifest or parameter file editing required."""
import hashlib
import importlib.util
import tempfile
from pathlib import Path
import streamlit as st
from confocal_ui import execute, demo

st.set_page_config(page_title='Confocal Analysis',layout='wide')
st.title('Confocal Analysis')
st.caption('Two-channel cell ratios and candidate puncta • Local processing • No API key')
st.info('Use original single-plane TIFF channels. For CZI files, follow the Fiji export steps in the README first.')
if st.button('Try a synthetic example'):
    with tempfile.TemporaryDirectory() as temp:
        st.session_state['result'] = demo(Path(temp))
        st.session_state['result_key'] = 'demo'
        st.session_state['demo_mode'] = True
reference = st.file_uploader('1. Cell-boundary channel images (for example RFP)',type=['tif','tiff'],accept_multiple_files=True)
signal = st.file_uploader('2. Measured channel images (for example GFP)',type=['tif','tiff'],accept_multiple_files=True)
mode = st.selectbox('3. How should cells be outlined?', ['Use existing cell masks','Cellpose-SAM','Simple threshold (baseline)'])
labels = st.file_uploader('Cell mask TIFFs',type=['tif','tiff'],accept_multiple_files=True) if mode=='Use existing cell masks' else []
if mode=='Use existing cell masks':
    st.caption('Masks must contain a different positive integer for each cell, 0 for background, and match the original image size.')
if mode=='Cellpose-SAM' and importlib.util.find_spec('cellpose') is None:
    st.warning('Cellpose is not installed in this app. Close this app, double-click Install Cellpose in this folder, then restart. This optional setup is a large download; first segmentation may also download model weights.')
if mode=='Simple threshold (baseline)':
    st.warning('This baseline can merge touching cells. Review every overlay before using measurements.')
pixel = st.number_input('4. Pixel size (micrometers per pixel)',min_value=.000001,value=None,format='%.6f',placeholder='Read this from your microscope metadata')
verified = st.checkbox('I verified that the source images have original Z=1, T=1 and equal X/Y pixel size; these are not projections.')
rows = []
if reference and signal:
    st.write('5. Match each boundary image to its measured channel and optional mask.')
    st.caption('Choose pairs explicitly. Filenames and upload order do not establish a valid pairing. Leave optional experiment labels blank if unknown.')
    initial = [{'image_id':f'field_{i+1}', 'reference':f.name,
        'signal':signal[0].name if len(reference)==len(signal)==1 else None,
        'labels':labels[0].name if mode=='Use existing cell masks' and len(reference)==len(labels)==1 else None,
        'condition':'', 'biological_replicate':''} for i,f in enumerate(reference)]
    table = st.data_editor(initial,hide_index=True,disabled=['reference'],column_config={
        'signal':st.column_config.SelectboxColumn('Measured channel',options=[f.name for f in signal],required=True),
        'labels':st.column_config.SelectboxColumn('Cell mask',options=[f.name for f in labels]),
        'biological_replicate':st.column_config.TextColumn('Biological replicate (optional)')})
    rows = table.to_dict('records') if hasattr(table,'to_dict') else table
with st.expander('Measurement settings (optional)'):
    minimum = st.number_input('Minimum cell pixels for automatic segmentation',min_value=1,value=100)
    denominator = st.number_input('Minimum corrected boundary-channel mean for a ratio',min_value=.000001,value=1.)
    contrast = st.number_input('Minimum punctum contrast (image intensity units)',min_value=.000001,value=3.)
    noise = st.number_input('Punctum contrast / noise threshold',min_value=.000001,value=3.)
    diameter_min = st.number_input('Minimum punctum diameter (micrometers)',min_value=.000001,value=.6)
    diameter_max = st.number_input('Maximum punctum diameter (micrometers)',min_value=.000001,value=2.)
    gpu = st.checkbox('Use GPU for Cellpose',value=False)
cfg = {'backend':'cellpose' if mode=='Cellpose-SAM' else 'threshold', 'model':'cpsam_v2','gpu':gpu,
    'min_cell_pixels':int(minimum),'min_denominator':denominator,
    'puncta':{'contrast_min_DN':contrast,'noise_multiplier':noise,'diameter_min_um':diameter_min,'diameter_max_um':diameter_max}}
signature = hashlib.sha256(repr((rows,pixel,verified,cfg,mode)).encode())
for group in (reference,signal,labels):
    for f in group: signature.update(f.name.encode()); signature.update(f.getvalue())
current = signature.hexdigest()
if st.button('Analyze images',type='primary',disabled=not rows or not verified or pixel is None):
    st.session_state.pop('result',None)
    try:
        if diameter_min>diameter_max: raise ValueError('Minimum punctum diameter exceeds the maximum.')
        files = {}
        for role,group in [('reference',reference),('signal',signal),('labels',labels)]:
            names = [f.name for f in group]
            if len(names)!=len(set(names)): raise ValueError('Duplicate filenames in '+role+' uploads. Rename them first.')
            files[role] = {f.name:f.getvalue() for f in group}
        measure_rows = []
        for row in rows:
            if row.get('signal') not in files['signal']: raise ValueError('Choose a measured channel for every row.')
            if mode=='Use existing cell masks' and row.get('labels') not in files['labels']:
                raise ValueError('Choose a cell mask for every row.')
            measure_rows.append({**row,'labels':row.get('labels') if mode=='Use existing cell masks' else '', 'pixel_um':pixel})
        if mode=='Cellpose-SAM' and importlib.util.find_spec('cellpose') is None:
            raise ValueError('Run Install Cellpose first, then restart this app.')
        with st.spinner('Analyzing images. Cellpose may take several minutes...'), tempfile.TemporaryDirectory() as temp:
            st.session_state['result'] = execute(Path(temp),measure_rows,files,cfg)
        st.session_state['result_key'] = current
        st.session_state['demo_mode'] = False
    except Exception as exc:
        st.error('Analysis could not complete: '+str(exc))
if 'result' in st.session_state and (st.session_state.get('result_key')=='demo' or st.session_state.get('result_key')==current):
    result = st.session_state['result']
    if st.session_state.get('demo_mode'): st.warning('SYNTHETIC DEMO — not experimental measurements. Upload your images above for your own analysis.')
    st.success('Results are ready. Save the ZIP before closing the app.')
    st.dataframe(result['cells'],hide_index=True)
    for name,data in result['overlays'].items():
        st.image(data,caption=name+' — cyan: cell boundaries; magenta: accepted puncta')
    st.download_button('Save all results (.zip)',result['zip'],file_name='confocal_results.zip')
    st.caption('ZIP includes cell/focus/field CSV tables, masks, overlays and settings. Review QC flags. Candidate puncta alone do not demonstrate autophagic flux.')
