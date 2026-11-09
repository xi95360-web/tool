"""Exercise the same synthetic examples exposed to first-time users."""
import importlib.util
import io
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ['confocal-cell-measurements','sting-structure-triage','sting-mutant-databank']
for folder in PROJECTS: sys.path.insert(0,str(ROOT/folder))


class Desktop(unittest.TestCase):
    def test_launchers_with_spaces_and_unrelated_working_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            for project in PROJECTS:
                target = Path(temp)/('folder with spaces '+project)
                shutil.copytree(ROOT/project,target,ignore=shutil.ignore_patterns('.workflow-env','__pycache__'))
                result = subprocess.run([sys.executable,str(target/'launch.py'),'--check'],cwd=temp,capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stderr)

    def test_databank_addition_and_save_reopen(self):
        from databank_ui import create, add_claim, browse, templates
        original = create()
        record = {'title':'Synthetic source','url':'https://example.org/synthetic','variant':'Example variant',
            'species':'Homo sapiens','taxon':9606,'background':'Unresolved study background','endpoint':'Example readout',
            'summary':'Synthetic claim','locator':'Synthetic figure','relation':'example','scope':'abstract','checked':True,
            'ligands':'Example A; Example B'}
        saved = add_claim(original,record)
        counts,rows = browse(saved,'Example B')
        self.assertEqual(counts['claims'],1)
        self.assertEqual(rows[0]['treatment_kind'],'combination')
        self.assertEqual(browse(original)[0]['claims'],0)
        self.assertEqual(browse(saved,"' OR 1=1 --")[1],[])
        with self.assertRaises(ValueError): add_claim(original,{**record,'checked':False})
        self.assertIn('sources.csv',zipfile.ZipFile(io.BytesIO(templates())).namelist())

    @unittest.skipUnless(importlib.util.find_spec('streamlit'),'UI dependencies not installed')
    def test_all_three_first_run_screens_and_demo_buttons(self):
        from streamlit.testing.v1 import AppTest
        for project in PROJECTS:
            with self.subTest(project=project):
                app = AppTest.from_file(str(ROOT/project/'app.py'),default_timeout=20).run()
                self.assertFalse(app.exception, str(app.exception))
                next(b for b in app.button if b.label=='Try a synthetic example').click().run()
                self.assertFalse(app.exception,str(app.exception))
                self.assertTrue(any('SYNTHETIC DEMO' in w.value for w in app.warning))
                if project!='sting-mutant-databank':
                    self.assertIn('result',app.session_state)
                    self.assertTrue(app.session_state['result']['zip'])
                else:
                    from databank_ui import browse
                    self.assertEqual(browse(app.session_state['database'])[0]['claims'],1)

    @unittest.skipUnless(importlib.util.find_spec('streamlit'),'UI dependencies not installed')
    def test_databank_guided_form(self):
        from streamlit.testing.v1 import AppTest
        from databank_ui import browse
        app = AppTest.from_file(str(ROOT/'sting-mutant-databank/app.py'),default_timeout=20).run()
        next(b for b in app.button if b.label=='Start a new empty databank').click().run()
        values = {'Paper title':'Synthetic source','Source link':'https://example.org/synthetic',
            'Protein / variant label':'Example variant','Protein background / construct':'Unresolved',
            'Measured endpoint':'Synthetic endpoint','Reported direction or relation':'synthetic_example','Where to find it':'Abstract'}
        for element in app.text_input:
            if element.label in values: element.set_value(values[element.label])
        app.text_area[0].set_value('Synthetic claim for interface testing only')
        app.checkbox[0].check()
        next(b for b in app.button if b.label=='Add record').click().run()
        self.assertFalse(app.exception,str(app.exception))
        self.assertEqual(browse(app.session_state['database'])[0]['claims'],1)

    @unittest.skipUnless(importlib.util.find_spec('streamlit'),'UI dependencies not installed')
    def test_confocal_uploaded_pair(self):
        import numpy as np
        import tifffile
        from streamlit.testing.v1 import AppTest
        labels = np.zeros((64,64),np.uint16); labels[20:40,20:40] = 1
        uploads = []
        for name,array in [('reference.tif',np.where(labels>0,110,10).astype(np.uint16)),
                           ('signal.tif',np.where(labels>0,205,5).astype(np.uint16)),('mask.tif',labels)]:
            buffer = io.BytesIO(); tifffile.imwrite(buffer,array)
            uploads.append(SimpleNamespace(name=name,getvalue=lambda data=buffer.getvalue():data))
        def choose(label,**kwargs):
            return [uploads[0]] if label.startswith('1.') else [uploads[1]] if label.startswith('2.') else [uploads[2]]
        with patch('streamlit.file_uploader',side_effect=choose):
            app = AppTest.from_file(str(ROOT/'confocal-cell-measurements/app.py'),default_timeout=20).run()
            next(n for n in app.number_input if n.label.startswith('4.')).set_value(.2)
            app.checkbox[0].check().run()
            next(b for b in app.button if b.label=='Analyze images').click().run()
            self.assertFalse(app.exception,str(app.exception))
            self.assertFalse(app.error,str(app.error))
            self.assertAlmostEqual(app.session_state['result']['cells'][0]['ratio_of_means'],2.)

    @unittest.skipUnless(importlib.util.find_spec('streamlit'),'UI dependencies not installed')
    def test_structure_uploaded_pair(self):
        from streamlit.testing.v1 import AppTest
        names = ['MET','ALA','GLY','TRP']
        pdb = ''.join(f'ATOM  {i:5d}  CA  {name} A{i:4d}    {i*3.:8.3f}{0.:8.3f}{0.:8.3f}{1.:6.2f}{80.:6.2f}           C  \n' for i,name in enumerate(names,1))+'END\n'
        reference = SimpleNamespace(name='protein.fasta',getvalue=lambda:b'>synthetic\nMAGW\n')
        structure = SimpleNamespace(name='protein.pdb',getvalue=lambda:pdb.encode())
        with patch('streamlit.file_uploader',side_effect=lambda label,**kwargs: reference if label.startswith('1.') else structure):
            app = AppTest.from_file(str(ROOT/'sting-structure-triage/app.py'),default_timeout=20).run()
            app.text_area[0].set_value('Assess A2E').run()
            next(b for b in app.button if b.label=='Assess mutations').click().run()
            self.assertFalse(app.exception,str(app.exception))
            self.assertFalse(app.error,str(app.error))
            self.assertEqual(app.session_state['result']['report']['results'][0]['mapping_status'],'mapped')


if __name__=='__main__': unittest.main()
