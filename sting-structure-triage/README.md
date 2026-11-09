# STING Structure Triage

Version 0.1.0 research prototype. Offline, sequence-verified mapping of named AA substitutions to an input structure. Accepts free text containing explicit edits, e.g. `Assess L90E and M120L`. No language-model API is required. It does not interpret arbitrary prose descriptions without mutation notation.

```sh
python -m pip install -r requirements.txt
python triage.py --reference wt_protein.fasta --structure structure.cif --chain A --query 'Assess L90E and M120L' --out result.json
```

The reference is a protein FASTA, not a plasmid sequence. The supplied chain is globally aligned to it. At least 90% identity over aligned residues is required; missing target residues remain unresolved, and multiple optimal alignments are marked ambiguous. Actual structure residue numbers and insertion codes are preserved. Only model 0 is analyzed. Partial constructs and sequence backgrounds require inspection.

Outputs: mapping status, aligned identity, residue identity, CA B factor (or user-declared pLDDT), nearest non-water heteroatom distance, input hashes and limitations. Declare `--confidence-kind plddt` only for a file known to encode pLDDT in its B-factor field. Heteroatoms include ions and additives; distance is not a ligand-affinity score.

`functional_prediction` and `ddg` intentionally remain null until a validated backend is integrated. This release neither models the mutant structure nor computes a conformation-preference score. The existing protein-to-cb research project can later supply a separately versioned, sequence-mapped scoring adapter; calibration, structural-state definition and source citations are prerequisites for publishing comparable scores. Multi-mutant inputs are independent site descriptors, not an epistasis model.
