# Lab workflows release 0.1.0

Four independent projects, MIT code under the root LICENSE. Run locally without API keys. Dependencies and upstream model weights retain their own licenses.

| Project | Implemented | Status / next gate |
| --- | --- | --- |
| Sequencing QuickCheck | Generic reference, AB1/SEQ/FASTA/FASTQ, explicit/discovery targets, reverse reads/CDS, one-base indels, English alignment report, local upload UI | Preview; browser UI and additional real AB1 cases need acceptance review; circular whole-plasmid comparison is not implemented |
| Confocal Cell Measurements | Manifest/config interface, supplied masks or optional Cellpose, channel ratios, gated puncta, QC labels/overlays, provenance, Fiji export bridge | Preview; validate model execution and Fiji bridge on representative images |
| STING Structure Triage | Local PDB/mmCIF, sequence-to-structure mapping, explicit edits in prose, B-factor/pLDDT declaration, heteroatom proximity | Research prototype; no functional or conformation score backend yet |
| STING Mutant Databank | CrossEvidence relational schema, transactional CSV importer, read-only claim search | Schema prototype; no public literature data or Paperclip connector bundled |

Tests use synthetic inputs. Private data, machine-specific absolute paths, paper PDFs and model weights are excluded. The original rotation scripts/data are preserved in their existing locations. This repository is the new public implementation.

Validation performed on 2026-11-09: 12 automated tests passed; synthetic sequencing and confocal examples completed; QuickCheck wheel built and installed in an isolated target directory; optional Streamlit app rendered with AppTest. Three local AB1 reads were successfully processed against an annotated reference in discovery mode; their inputs and reports are not distributed. Cellpose inference and the Fiji script still require acceptance testing. Browser upload/download interactions have not yet received manual end-to-end testing.

Priority after this release: user acceptance of QuickCheck, confocal segmentation validation, structure scoring adapter calibration, curated evidence release. Treat prototype status explicitly in demos and presentations.

Paperclip official entry: https://paperclip.gxl.ai/datasets . No account, payment, or extraction job is created by this release.
