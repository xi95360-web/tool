"""Generate reproducible synthetic inputs without distributing experiment data."""
import argparse
import json
import random
from pathlib import Path
import numpy as np
import tifffile
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if a.out.exists():
        p.error('Output exists; choose a new directory')
    sequence = a.out/'sequence'
    reads = sequence/'reads'
    reads.mkdir(parents=True)
    rng = random.Random(100)
    dna = ''.join(rng.choice('ACGT') for _ in range(300))
    dna = dna[:120]+'GCT'+dna[123:]
    reference = SeqRecord(Seq(dna),id='synthetic',description='Synthetic DNA fixture; A41E target',annotations={'molecule_type':'DNA'})
    reference.features = [SeqFeature(FeatureLocation(0,300),type='CDS',qualifiers={'gene':['synthetic']})]
    SeqIO.write(reference,sequence/'reference.gb','genbank')
    edited = dna[:120]+'GAA'+dna[123:]
    for name,seq in [('correct',edited),('unchanged',dna),('insertion',edited[:200]+'A'+edited[200:])]:
        r = SeqRecord(Seq(seq),id=name,description='synthetic')
        r.letter_annotations['phred_quality'] = [35]*len(seq)
        SeqIO.write(r,reads/(name+'.fastq'),'fastq')
    folder = a.out/'confocal'
    folder.mkdir()
    yy,xx = np.mgrid[:128,:128]
    labels = np.zeros((128,128),np.uint16)
    labels[(yy-40)**2+(xx-40)**2 < 18**2] = 1
    labels[(yy-85)**2+(xx-85)**2 < 20**2] = 2
    ref = np.where(labels>0,110,10).astype(np.uint16)
    sig = np.where(labels>0,205,5).astype(float)
    sig += 100*np.exp(-((yy-40)**2+(xx-40)**2)/4)
    for name,array in [('reference',ref),('signal',sig.astype(np.uint16)),('labels',labels)]:
        tifffile.imwrite(folder/(name+'.tif'),array)
    (folder/'images.csv').write_text('image_id,reference,signal,labels,original_size_z,pixel_um,condition,biological_replicate\nsynthetic,reference.tif,signal.tif,labels.tif,1,0.2,synthetic,demo\n')
    (folder/'config.json').write_text(json.dumps({'backend':'threshold'}))
    print(a.out)

if __name__ == '__main__':
    main()
