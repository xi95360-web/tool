import importlib.util
import json
import random
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
import tifffile
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'quickchange-seq-check/src'))
sys.path.insert(0, str(ROOT/'confocal-cell-measurements'))
from quickcheck import core
from quickcheck.cli import main
from analyze import run


def load(name, folder, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT/folder/filename)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Workflows(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        rng = random.Random(11)
        self.seq = ''.join(rng.choice('ACGT') for _ in range(270))
        self.record = SeqRecord(Seq(self.seq), id='synthetic', annotations={'molecule_type':'DNA'})
        self.record.features = [SeqFeature(FeatureLocation(0,270), type='CDS')]

    def query(self, seq, quality=35, name='sample'):
        r = SeqRecord(Seq(seq), id=name, description='synthetic test')
        r.letter_annotations['phred_quality'] = [quality]*len(seq)
        path = self.path/(name+'.fastq')
        SeqIO.write(r, path, 'fastq')
        return path

    def call(self, seq, expected=None, quality=35):
        return core.call_for_sample(self.query(seq,quality), self.record, list(range(270)), self.seq, 20, explicit_expected=expected or [])

    def test_discovery_does_not_infer_filename(self):
        self.assertEqual(core.parse_expected('H72N_primer_V147L'), [])
        self.assertEqual(self.call(self.seq).status, 'NO_EXPECTATION')

    def test_target_and_reverse_complement(self):
        seq = self.seq[:120]+'GAA'+self.seq[123:]
        target = str(Seq(self.seq[120:123]).translate())+'41E'
        result = self.call(str(Seq(seq).reverse_complement()), [target])
        self.assertEqual(result.status, 'PASS')
        self.assertEqual(result.orientation, 'reverse')

    def test_one_base_indels(self):
        self.assertTrue(any(i.kind == 'insertion' for i in self.call(self.seq[:120]+'A'+self.seq[120:]).indels))
        self.assertTrue(any(i.kind == 'deletion' for i in self.call(self.seq[:120]+self.seq[121:]).indels))

    def test_quality_and_extra_change(self):
        seq = self.seq[:120]+'GAA'+self.seq[123:]
        target = str(Seq(self.seq[120:123]).translate())+'41E'
        self.assertEqual(self.call(seq,[target],2).status, 'UNCERTAIN')
        seq = seq[:180]+('C' if seq[180]!='C' else 'A')+seq[181:]
        self.assertEqual(self.call(seq,[target]).status, 'PASS_WITH_EXTRA')

    def test_multiple_cds_rejected(self):
        self.record.features *= 2
        with self.assertRaises(ValueError): core.reference_feature(self.record)

    def test_double_mutant_and_outside_target(self):
        seq = self.seq[:120]+'GAA'+self.seq[123:180]+'TTT'+self.seq[183:]
        targets = [str(Seq(self.seq[120:123]).translate())+'41E', str(Seq(self.seq[180:183]).translate())+'61F']
        self.assertEqual(self.call(seq,targets).status,'PASS')
        self.assertEqual(self.call(seq,['L999E']).status,'CONFIG_ERROR')

    def test_plain_sequence_stays_provisional(self):
        seq = self.seq[:120]+'GAA'+self.seq[123:]
        target = str(Seq(self.seq[120:123]).translate())+'41E'
        path = self.path/'sample.seq'; path.write_text(seq)
        result = core.call_for_sample(path,self.record,list(range(270)),self.seq,20,explicit_expected=[target])
        self.assertEqual(result.status,'PROVISIONAL')

    def test_reverse_cds(self):
        self.record.seq = self.record.seq.reverse_complement()
        positions = list(range(269,-1,-1))
        changed = self.seq[:120]+'GAA'+self.seq[123:]
        target = str(Seq(self.seq[120:123]).translate())+'41E'
        result = core.call_for_sample(self.query(str(Seq(changed).reverse_complement())), self.record, positions, self.seq,20, explicit_expected=[target])
        self.assertEqual(result.status,'PASS')

    def test_report_and_no_quality(self):
        reference = self.path/'reference.gb'
        SeqIO.write(self.record,reference,'genbank')
        reads = self.path/'reads'
        reads.mkdir()
        (reads/'H72N.seq').write_text(self.seq)
        out = self.path/'report'
        self.assertEqual(main(['--reference',str(reference),'--input-dir',str(reads),'--out-dir',str(out)]),0)
        payload = json.loads((out/'quickchange_report.json').read_text())
        self.assertFalse(payload['results'][0]['quality_available'])
        self.assertEqual(payload['expected_source'],'discovery')
        self.assertIn('Alignment',(out/'quickchange_report.html').read_text())

    def test_confocal_known_ratio(self):
        labels = np.zeros((64,64),np.uint16)
        labels[20:40,20:40] = 1
        ref = np.full((64,64),10,np.uint16); ref[labels>0] = 110
        sig = np.full((64,64),5,np.uint16); sig[labels>0] = 205
        for name, array in [('ref',ref),('sig',sig),('labels',labels)]:
            tifffile.imwrite(self.path/(name+'.tif'),array)
        manifest = self.path/'images.csv'
        manifest.write_text('image_id,reference,signal,labels,original_size_z,pixel_um\ntest,ref.tif,sig.tif,labels.tif,1,0.2\n')
        cells = run(manifest,{'backend':'threshold'},self.path/'measurements')
        self.assertAlmostEqual(cells[0]['ratio_of_means'],2.)
        self.assertEqual(cells[0]['puncta_count'],0)
        manifest.write_text(manifest.read_text().replace(',1,0.2',',5,0.2'))
        with self.assertRaises(ValueError): run(manifest,{},self.path/'bad')

    def test_databank_empty_search_and_no_overwrite(self):
        db = load('databank','sting-mutant-databank','databank.py')
        path = self.path/'evidence.sqlite'
        db.build(path)
        self.assertEqual(db.search(path,"' OR 1=1 --"),[])
        with self.assertRaises(ValueError): db.build(path)

    def test_structure_mapping(self):
        triage = load('triage','sting-structure-triage','triage.py')
        fasta = self.path/'protein.fa'; fasta.write_text('>synthetic\nMAGW\n')
        pdb = self.path/'protein.pdb'
        names = ['MET','ALA','GLY','TRP']
        pdb.write_text(''.join(f'ATOM  {i:5d}  CA  {name} A{i:4d}    {i*3.:8.3f}{0.:8.3f}{0.:8.3f}{1.:6.2f}{80.:6.2f}           C  \n' for i,name in enumerate(names,1))+'END\n')
        result = triage.analyze(fasta,pdb,'A','Assess A2E')
        self.assertEqual(result['results'][0]['mapping_status'],'mapped')
        self.assertIsNone(result['results'][0]['functional_prediction'])

if __name__ == '__main__':
    unittest.main()
