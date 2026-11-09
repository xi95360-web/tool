# STING Structure Triage

## Start here — no coding required

[中文入门](./START_HERE.zh-CN.md)

1. On the [GitHub homepage](https://github.com/xi95360-web/tool), click **Code → Download ZIP**.
2. Extract the ZIP. Open `tool-main`, then `sting-structure-triage`. Keep the whole folder together.
3. Make sure Python 3.10 or later is installed. If it is missing, use the installer from [python.org](https://www.python.org/downloads/).
4. On Mac, double-click **Start STING Structure.command**. On Windows, double-click **Start STING Structure.bat** (the Windows entry point has not yet been tested on Windows).
5. A terminal window opens. First launch needs internet and may take several minutes to install components. The application then opens in your browser. Keep that terminal window open.
6. Click **Try a synthetic example** to try the complete result flow before preparing real data. The example is artificial and clearly labeled.
7. Follow the steps below for your own files. No commands, manifest files, or configuration editing are needed in the browser interface.

This is a local browser application with automatic first-time setup, not a standalone installer with Python included. Ordinary analysis needs no API key. Files are processed on the computer running this app.

## Assess your own mutations

1. Upload a **protein FASTA** containing the reference amino-acid sequence. This is different from your plasmid DNA sequence or a GenBank plasmid file.
2. Upload the matching **PDB** or **mmCIF** structure file.
3. Select the **protein chain** from the dropdown. If several chains exist, choose the chain representing your protein of interest.
4. Enter a named mutation such as `N154S`, or text containing several edits, such as `Assess L90E and M120L`. Use the mutation you actually want to inspect; examples are not preset experimental targets.
5. Leave the confidence setting at **Experimental B factors** unless you know that the structure stores **pLDDT** in its B-factor field.
6. Click **Assess mutations**.
7. Review each mapping status and the structure residue number. **Unresolved** means the site is absent or cannot be mapped confidently; it does not mean the mutation has no effect.
8. Click **Save report (.zip)**. Unzip it and double-click `structure_report.html` to read the report, or open the CSV in Excel.

## What the result can tell you

This release maps sites and reports descriptors of the supplied structure, including a CA B factor or declared pLDDT and proximity to non-water heteroatoms. Heteroatoms may be ions or additives. It currently does not create a mutant structure, calculate ΔΔG, predict functional activity, or model interactions between simultaneous mutations. The corresponding prediction fields remain empty.

If you see **reference mismatch**, check the amino-acid sequence, protein background and mutation numbering. For **identity below 90%**, check species and chain. A partial structure may lack your target site.

## Save, close, and reopen

Save the result using the page's **Save** button before closing. Results are held in the running app session until you download them. Click the terminal window and press **Control+C** to stop the application. Next time, double-click **Start STING Structure** again; installed components are reused.

## If startup fails

- **Python missing / too old:** install Python 3.10 or later, then retry.
- **Installation download fails:** check your connection and retry the same launcher.
- **pip update notice:** this is information, not the cause of a failure.
- **Browser does not open:** open the local address printed in the terminal, usually `http://localhost:8501`.
- **Port already in use:** stop another workflow with Control+C, then retry. Only one default launcher can use port 8501 at a time.
- **Mac blocks double-clicking:** use Open only after verifying the downloaded file came from this repository. Alternatively, type `python3` plus a space in Terminal, drag this folder's **launch.py** into the window, then press Return. Do not disable macOS security settings.
- **An error appears during analysis:** the page shows the cause. Check the file type and required fields, correct them, and retry. Existing experiment files are not edited.

## Advanced reference (optional)

Version 0.1.0 research prototype. Offline, sequence-verified mapping of named AA substitutions to an input structure. Accepts free text containing explicit edits, e.g. `Assess L90E and M120L`. No language-model API is required. It does not interpret arbitrary prose descriptions without mutation notation.

```sh
python -m pip install -r requirements.txt
python triage.py --reference wt_protein.fasta --structure structure.cif --chain A --query 'Assess L90E and M120L' --out result.json
```

The reference is a protein FASTA, not a plasmid sequence. The supplied chain is globally aligned to it. At least 90% identity over aligned residues is required; missing target residues remain unresolved, and multiple optimal alignments are marked ambiguous. Actual structure residue numbers and insertion codes are preserved. Only model 0 is analyzed. Partial constructs and sequence backgrounds require inspection.

Outputs: mapping status, aligned identity, residue identity, CA B factor (or user-declared pLDDT), nearest non-water heteroatom distance, input hashes and limitations. Declare `--confidence-kind plddt` only for a file known to encode pLDDT in its B-factor field. Heteroatoms include ions and additives; distance is not a ligand-affinity score.

`functional_prediction` and `ddg` intentionally remain null until a validated backend is integrated. This release neither models the mutant structure nor computes a conformation-preference score. The existing protein-to-cb research project can later supply a separately versioned, sequence-mapped scoring adapter; calibration, structural-state definition and source citations are prerequisites for publishing comparable scores. Multi-mutant inputs are independent site descriptors, not an epistasis model.
