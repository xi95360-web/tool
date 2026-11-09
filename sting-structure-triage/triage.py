"""Map natural-language AA substitutions to a local structure; report descriptors."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from Bio import Align, SeqIO
from Bio.PDB import PDBParser, MMCIFParser
from Bio.SeqUtils import seq1


def analyze(reference, structure_path, chain_id, text, confidence_kind='bfactor'):
    reference_seq = str(SeqIO.read(reference, 'fasta').seq).upper()
    mutations = list(dict.fromkeys(re.findall(r'(?<![A-Za-z0-9])([ACDEFGHIKLMNPQRSTVWY][1-9]\d*[ACDEFGHIKLMNPQRSTVWY])(?![A-Za-z0-9])', text)))
    if not mutations:
        raise ValueError('Include explicit AA edits in the text, e.g. assess L90E and M120L')
    parser = MMCIFParser(QUIET=True) if structure_path.suffix.lower() in {'.cif','.mmcif'} else PDBParser(QUIET=True)
    model = parser.get_structure('input', structure_path)[0]
    chain = model[chain_id]
    residues = [r for r in chain if r.id[0] == ' ' and seq1(r.resname) != 'X']
    chain_seq = ''.join(seq1(r.resname) for r in residues)
    if not chain_seq:
        raise ValueError('Selected chain has no recognized protein residues')
    aligner = Align.PairwiseAligner(mode='global', match_score=2, mismatch_score=-3, open_gap_score=-8, extend_gap_score=-0.5)
    alignments = aligner.align(reference_seq, chain_seq)
    first = alignments[0]
    pairs = list(zip(*first.indices))
    mapping = {int(i): int(j) for i,j in pairs if i >= 0 and j >= 0}
    identity = sum(reference_seq[i] == chain_seq[j] for i,j in mapping.items()) / max(len(mapping),1)
    if identity < .9:
        raise ValueError('Chain/reference aligned identity below 90%; verify species, allele and chain')
    ambiguous = len(alignments) > 1
    ligands = [a for r in model.get_residues() if r.id[0].startswith('H_') for a in r if a.element != 'H']
    rows = []
    for edit in mutations:
        position = int(edit[1:-1])-1
        if not 0 <= position < len(reference_seq) or reference_seq[position] != edit[0]:
            raise ValueError('Reference mismatch for ' + edit)
        row = {'mutation': edit, 'mapping_status': 'unresolved', 'functional_prediction': None, 'ddg': None}
        j = mapping.get(position)
        if j is not None and chain_seq[j] == edit[0] and not ambiguous:
            residue = residues[j]
            heavy = [a for a in residue if a.element != 'H']
            distance = min((float(a-b) for a in heavy for b in ligands), default=None)
            row.update(mapping_status='mapped', chain=chain_id, structure_residue=str(residue.id[1])+residue.id[2].strip(),
                residue_name=residue.resname, nearest_heteroatom_distance_A=distance,
                confidence_kind=confidence_kind,
                ca_value=float(residue['CA'].bfactor) if 'CA' in residue else None)
        elif ambiguous:
            row['mapping_status'] = 'ambiguous_alignment'
        rows.append(row)
    return {'version':'0.1.0', 'input_text':text, 'aligned_identity':identity,
        'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),
        'structure_sha256':hashlib.sha256(structure_path.read_bytes()).hexdigest(),
        'model_index':0, 'results':rows,
        'limitations':['Descriptors describe the input structure, not a modeled mutant.',
            'No calibrated functional score or delta-delta-G backend is configured.',
            'B factors are interpreted as pLDDT only when explicitly declared.',
            'Heteroatoms include ions and additives; proximity does not establish ligand binding.',
            'Model 0 and supplied coordinates only; no biological assembly expansion.']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference', type=Path, required=True, help='WT protein FASTA')
    p.add_argument('--structure', type=Path, required=True)
    p.add_argument('--chain', required=True)
    p.add_argument('--query', required=True)
    p.add_argument('--confidence-kind', choices=['bfactor','plddt'], default='bfactor')
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if a.out.exists():
        p.error('Output exists; choose a new path')
    result = analyze(a.reference,a.structure,a.chain,a.query,a.confidence_kind)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2))
    print(a.out)

if __name__ == '__main__':
    main()
