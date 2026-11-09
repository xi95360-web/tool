# Sequencing QuickCheck

Local Sanger read screening against any explicit DNA reference. English HTML reports and optional browser upload interface. No API key or account is required.

Status: **0.1.1 preview**. No coding experience is needed for the browser interface. Python 3.10 or later is still required; this is not a standalone desktop installer. [中文上手说明](./START_HERE.zh-CN.md).

## Start here — no terminal commands needed

### Get the application

1. On the [repository homepage](https://github.com/xi95360-web/tool), click the green **Code** button, then **Download ZIP**.
2. Extract the ZIP. Open `tool-main`, then open `quickchange-seq-check`.
3. Keep this whole folder together. Downloading only a single script will not work.

### Open it on a Mac

1. Make sure Python 3.10 or later is installed. If needed, get the macOS installer from [python.org](https://www.python.org/downloads/).
2. In Finder, double-click **Start QuickCheck.command** inside `quickchange-seq-check`.
3. A terminal window opens and shows setup progress. First launch needs internet to download components and may take several minutes. Later launches reuse the installed components.
4. Your browser opens the analysis page. Keep the terminal window open while using it.

If macOS blocks the launcher, follow the prompt and use **Open** only after checking that the file came from this repository. If it still cannot open, use the drag-and-drop fallback below. There is no need to turn off macOS security settings.

### Open it on Windows

Install Python 3.10 or later from [python.org](https://www.python.org/downloads/), including the Python launcher, then double-click **Start QuickCheck.bat**. The Windows launcher is included but has not yet been tested on Windows.

### Analyze your samples

1. **Choose your reference sequence:** select your original plasmid `.gb` or `.gbk` file. This is the control sequence, not a sequencing read.
2. **Choose your sequencing files:** select one or more `.ab1` files from the sequencing provider. `.seq` files also work, but lack base-quality evidence.
3. **Select the gene you want to check:** choose the correct gene from the dropdown. You do not need to type a CDS label. A plasmid may also contain antibiotic-resistance genes; select your gene of interest.
4. **Expected amino-acid edits:** enter your real target, such as `N154S`. For a double mutant in the same clone, enter `H72N,M120L`. Leave it blank to discover differences without judging experimental intent. The entry applies to every uploaded read; analyze separate batches if samples have different targets.
5. Click **Analyze sequences**. Review the summary, alignment, extra substitutions and insertion/deletion calls.
6. Click **Save quickchange_report.html** to keep a report you can reopen later. Save reports before closing or restarting the application.

A FASTA reference can be used for DNA differences; amino-acid target checks need GenBank CDS annotations. A clean partial read does not verify the whole plasmid.

### Close or reopen

To stop, click the terminal window and press **Control+C**. To start another day, double-click **Start QuickCheck.command** again. The browser page runs on your own computer; it is not a hosted website. Files selected in this local interface are processed locally.

### If the launcher does not open: drag-and-drop fallback (Mac)

1. Open **Terminal**.
2. Type `python3` followed by one space. Do not press Return yet.
3. Drag **launch.py** from the application folder into the terminal window. The full path is filled in automatically, including spaces.
4. Press Return.

This works regardless of the terminal's current folder. Do not paste the advanced examples below as a first-time setup command.

## Troubleshooting

| What you see | What it means / what to do |
| --- | --- |
| `Directory '.' is not installable` | The old install command was run from another folder. Start the launcher above; it finds the application folder automatically. |
| `command not found: quickcheck` | Installation did not finish, or the terminal is using another environment. Use the launcher; no activation step is required. |
| `A new release of pip is available` | An informational notice. Updating pip is not required to use this app. Look for an actual `ERROR` line if setup failed. |
| No browser opens | Keep the terminal open and use the local address it prints, usually `http://localhost:8501`. |
| Setup fails while downloading | Check the internet connection and retry the launcher. First launch needs internet; ordinary analysis needs no API key. |
| Python not found or too old | Install Python 3.10 or later, close the terminal, and reopen the launcher. |
| Several genes appear | Choose your gene of interest, not the resistance gene. |

## Advanced: command-line use

The following examples are for users who prefer the terminal. `reference.gb`, `reads`, `YOUR_GENE`, and `L90E,M120L` are placeholders for your own files, gene and edits; they are not files or experimental targets supplied by the app.

First navigate to the extracted `quickchange-seq-check` folder. Confirm it contains `pyproject.toml` before using `pip install .`. The dot means the terminal's current directory, not the location of this README.

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

## Advanced: manual browser setup

```sh
python -m pip install '.[ui]'
streamlit run src/quickcheck/app.py
```

Run these commands only from `quickchange-seq-check` after activating the environment created in the advanced instructions. The beginner launcher performs setup automatically.

AB1/ABI, plain DNA or FASTA SEQ, single-record FASTA and FASTQ inputs are accepted. Prefer AB1 for quality evidence. Match an AB1 and SEQ by filename stem to avoid counting the same read twice. Unmatched SEQ reads remain included.

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
