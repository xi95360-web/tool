# Sequencing QuickCheck

Local Sanger read screening against any explicit DNA reference. English HTML reports and optional browser upload interface. No API key or account is required.

Status: **0.1.0 preview**. AB1/ABI, plain DNA or FASTA SEQ, single-record FASTA and FASTQ inputs. Prefer AB1 for quality evidence. Match an AB1 and SEQ by filename stem to avoid counting the same read twice. Unmatched SEQ reads remain included.

## Install and run

From this directory, with Python 3.10 or later:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
quickcheck --reference reference.gb --input-dir reads --feature-label YOUR_GENE --expected L90E,M120L --open
```

To discover observed differences, omit `--expected`. Filenames never imply intended mutations. For multiple expected genotypes, use `--expected-file targets.tsv` with two tab-separated columns and no header:

```text
clone_A.*	L90E,M120L
clone_B.*	L90E
```

Patterns apply to filename stems. The first matching pattern wins; an unmatched read enters discovery mode. Explicit nucleotide target matching and intended indel matching are future features; observed indels are reported now.

Relative paths resolve from the current directory. Select the CDS by exact label/gene/locus_tag/protein_id when multiple CDS features exist. FASTA references support DNA differences; AA target checks require an annotated GenBank CDS. Translation currently supports codon_start=1 and genetic code 1.

## Browser interface

```sh
python -m pip install '.[ui]'
streamlit run src/quickcheck/app.py
```

Open the local address shown in the terminal. Upload the reference and reads, optionally specify the CDS and expected edits, then download HTML/TSV/JSON. Analysis runs on the machine hosting Streamlit. Do not expose it as a public data-upload service without adding authentication and resource limits.

## Interpretation

- PASS: requested AA edits supported by quality-bearing reads, with no additional called differences in the aligned region.
- PASS_WITH_EXTRA: requested edits plus other substitutions or internal gaps.
- PROVISIONAL: requested sequence observed in a read without base qualities; inspect extra calls too.
- FAIL: a confidently covered target differs from the requested edit.
- UNCERTAIN: insufficient target coverage or quality.
- CONFIG_ERROR: expected residue/position does not match the selected reference CDS.
- NO_EXPECTATION: differences reported without judging experimental intent.

Output: `quickchange_report.html`, `quickchange_summary.tsv`, `quickchange_report.json`. JSON includes input hashes and software version. HTML includes each read's alignment. One-base insertions/deletions are included. Reverse-complement reads and reverse-strand CDS features are supported.

Coverage is per read. There is no consensus assembly or sample-level merging in this release. Local alignment can clip large/terminal changes and does not normalize circular origins. This is a Sanger screening tool, not whole-plasmid assembly validation. A clean partial read cannot exclude errors outside its coverage or guarantee expression. Inspect suspicious AB1 traces. AA targets permit any codon encoding the requested residue; they do not validate a specific designed nucleotide sequence. Frameshift-associated downstream AA annotations are reference-coordinate descriptions, not reconstructed mutant proteins.

## Demo and verification

From the repository root:

```sh
python examples/make_demo.py --out /tmp/lab-demo
quickcheck --reference /tmp/lab-demo/sequence/reference.gb --input-dir /tmp/lab-demo/sequence/reads --expected A41E --open
python -m unittest discover -s tests -v
```

Demo sequences are synthetic. Original experiment files and private absolute paths are excluded from this repository. The rotation scripts remain separate and unchanged; use this package for the new generic interface.
