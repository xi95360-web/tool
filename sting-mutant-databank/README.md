# STING Mutant Databank

## Start here — no coding required

[中文入门](./START_HERE.zh-CN.md)

1. On the [GitHub homepage](https://github.com/xi95360-web/tool), click **Code → Download ZIP**.
2. Extract the ZIP. Open `tool-main`, then `sting-mutant-databank`. Keep the whole folder together.
3. Make sure Python 3.10 or later is installed. If it is missing, use the installer from [python.org](https://www.python.org/downloads/).
4. On Mac, double-click **Start STING Databank.command**. On Windows, double-click **Start STING Databank.bat** (the Windows entry point has not yet been tested on Windows).
5. A terminal window opens. First launch needs internet and may take several minutes to install components. The application then opens in your browser. Keep that terminal window open.
6. Click **Try a synthetic example** to try the complete result flow before preparing real data. The example is artificial and clearly labeled.
7. Follow the steps below for your own files. No commands, manifest files, or configuration editing are needed in the browser interface.

This is a local browser application with automatic first-time setup, not a standalone installer with Python included. Ordinary analysis needs no API key. Files are processed on the computer running this app.

## Start collecting evidence from a paper

1. Click **Start a new empty databank**. It is normal to have zero records; this release does not contain a complete STING literature dataset.
2. In **Add literature record**, enter the paper title and source link. Add a DOI if available.
3. Enter the variant, species, and protein background/construct exactly as supported by that paper. If the background is unknown, write `unresolved` instead of guessing.
4. Enter the ligand. For combined treatments in the same experiment, separate names with semicolons, such as `Ligand A; Ligand B`. Leave this blank for a baseline with no exogenous ligand.
5. Enter the measured endpoint, reported relation, finding, and specific source location such as **Figure 2B** or **Abstract**. Keep distinct assays/endpoints as separate records.
6. Select which source section you inspected and tick the confirmation only after checking the original source.
7. Click **Add record**. This creates a source-level literature claim, not a complete quantitative measurement.
8. Search by variant, ligand or endpoint. Leave the search blank to browse your records.
9. Click **Save databank (.sqlite)** to keep your work. The browser session is temporary; closing/restarting without saving can lose unsaved records.
10. On another day, start the app, expand **Open a saved databank**, select the downloaded file and click **Open database**.

Save before starting another empty databank, opening another file, or importing CSV tables: those actions replace the current session. The source-only form deliberately preserves each record's study-specific identity; it does not automatically merge variants across papers.

## Optional: import existing tables

Use **Import existing structured CSV tables** only if you already have curated tables matching this app's schema. **Save empty table templates** provides the required column names. Select the related CSVs together and click **Build databank from these CSVs**. The app validates links before replacing your session. Arbitrary spreadsheets or Paperclip exports require a separate field-mapping step and cannot yet be imported directly.

The **Detailed measurements** view stays empty until measurement-level tables have been imported. The form above adds claims only. No matching record means no matching collected evidence, not an experimentally established negative result.

## Save, close, and reopen

Save the result using the page's **Save** button before closing. Results are held in the running app session until you download them. Click the terminal window and press **Control+C** to stop the application. Next time, double-click **Start STING Databank** again; installed components are reused.

## If startup fails

- **Python missing / too old:** install Python 3.10 or later, then retry.
- **Installation download fails:** check your connection and retry the same launcher.
- **pip update notice:** this is information, not the cause of a failure.
- **Browser does not open:** open the local address printed in the terminal, usually `http://localhost:8501`.
- **Port already in use:** stop another workflow with Control+C, then retry. Only one default launcher can use port 8501 at a time.
- **Mac blocks double-clicking:** use Open only after verifying the downloaded file came from this repository. Alternatively, type `python3` plus a space in Terminal, drag this folder's **launch.py** into the window, then press Return. Do not disable macOS security settings.
- **An error appears during analysis:** the page shows the cause. Check the file type and required fields, correct them, and retry. Existing experiment files are not edited.

## Advanced reference (optional)

Version 0.1.0 schema and offline import/search engine, derived from the rotation's CrossEvidence schema. The command-line core uses the Python standard library; the browser launcher adds Streamlit automatically. No API key is needed. This public release contains no literature-derived experimental records. An empty search result means no imported matching record, not a demonstrated lack of biological response.

```sh
python databank.py build --out evidence.sqlite
python databank.py build --csv-dir curated-tables --out imported.sqlite
python databank.py search --database imported.sqlite 'cGAMP'
```

The CSV directory contains one UTF-8 CSV per SQL table, named after that table; columns must match schema.sql. Empty cells become SQL NULL. Source/variant/assay links and SQL constraints are validated together in a transaction. Imports preserve existing databases; select a new output. Failed imports can leave an empty schema-only file. View exports should not be passed back as input tables.

Data model: sources → study-scoped variants, compounds and endpoints → contexts and experimental treatment arms → measurements; structures and field-level provenance retain separate links. Multi-ligand treatment stays linked to one experimental arm. Literature claims remain distinct from quantitative measurements. Preserve dose/time/units, reference background, assay, cell context, source locator and review status. Missing values are NULL, not zero. Inspect `schema.sql` for all tables, constraints and two query views.

The search command queries source-level claims through `v_claim_crosslinks`. Measurement-level data are available through `v_measurement_crosslinks` using SQLite tools. Search is parameterized and opens the database read-only.

Paperclip is a possible upstream extraction source, not a runtime dependency. No Paperclip account/API task has been run. To import future exports, first map fields into the documented tables and retain source and review status. Service pricing, API access and dataset reuse terms require verification for the specific export. Private research notes and copyrighted source documents are not bundled.

Next milestones: richer curator review and measurement entry, mapped import of Paperclip exports, and versioned curated data releases. The basic claim-entry form and local search interface are available above.
