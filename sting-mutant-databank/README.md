# STING Mutant Databank

Version 0.1.0 schema and offline import/search engine, derived from the rotation's CrossEvidence schema. Python standard library only; no API key. This public release contains no literature-derived experimental records. An empty search result means no imported matching record, not a demonstrated lack of biological response.

```sh
python databank.py build --out evidence.sqlite
python databank.py build --csv-dir curated-tables --out imported.sqlite
python databank.py search --database imported.sqlite 'cGAMP'
```

The CSV directory contains one UTF-8 CSV per SQL table, named after that table; columns must match schema.sql. Empty cells become SQL NULL. Source/variant/assay links and SQL constraints are validated together in a transaction. Imports preserve existing databases; select a new output. Failed imports can leave an empty schema-only file. View exports should not be passed back as input tables.

Data model: sources → study-scoped variants, compounds and endpoints → contexts and experimental treatment arms → measurements; structures and field-level provenance retain separate links. Multi-ligand treatment stays linked to one experimental arm. Literature claims remain distinct from quantitative measurements. Preserve dose/time/units, reference background, assay, cell context, source locator and review status. Missing values are NULL, not zero. Inspect `schema.sql` for all tables, constraints and two query views.

The search command queries source-level claims through `v_claim_crosslinks`. Measurement-level data are available through `v_measurement_crosslinks` using SQLite tools. Search is parameterized and opens the database read-only.

Paperclip is a possible upstream extraction source, not a runtime dependency. No Paperclip account/API task has been run. To import future exports, first map fields into the documented tables and retain source and review status. Service pricing, API access and dataset reuse terms require verification for the specific export. Private research notes and copyrighted source documents are not bundled.

Next milestones: curator review UI, import templates for Paperclip exports, evidence-linked variant/ligand browser, and versioned curated data releases.
