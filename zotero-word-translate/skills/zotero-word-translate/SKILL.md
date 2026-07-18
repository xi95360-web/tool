---
name: zotero-word-translate
description: Build, package, validate, or troubleshoot the Zotero Word Translate plugin for Zotero 7–9. Use when changing manifest.json or bootstrap.js, producing an installable XPI, diagnosing selection-popup translation behavior, or preparing a GitHub release of this repository.
---

# Zotero Word Translate

Maintain the small bootstrapped Zotero plugin in this repository. Preserve its narrow privacy boundary: send only the current text selection to MyMemory and never access PDFs, library metadata, notes, or Zotero credentials.

## Workflow

1. Locate the repository root with `git rev-parse --show-toplevel` and inspect `manifest.json`, `bootstrap.js`, and `README.md`. If the files were supplied without Git metadata, use the user-provided directory after confirming those three files exist.
2. Keep the plugin ID stable unless a deliberate migration is planned; changing it makes Zotero treat the package as a different add-on.
3. Keep `strict_max_version` limited to a Zotero major version that was actually tested.
4. Run `node --check bootstrap.js` after JavaScript changes.
5. Run `python3 scripts/build_xpi.py` to validate the manifest and create the package in `dist/`.
6. Run `unzip -t dist/*.xpi` and confirm the archive contains only `manifest.json`, `bootstrap.js`, and `README.md`.
7. Test installation through Zotero's Add-ons page and verify English-to-Chinese and Chinese-to-English selections before publishing a release.

## Implementation guardrails

- Register `renderTextSelectionPopup` with the plugin ID. Unregister it with the same event type and handler, following Zotero's `unregisterEventListener(type, handler)` API.
- Treat selection text as untrusted input; use `textContent`, not HTML insertion.
- URL-encode query text and retain the selection-length limit, timeout, and bounded in-memory cache.
- Keep network failures non-destructive and user-readable.
- Do not write the selected text or request URL into diagnostic logs.
- Do not add API keys, personal email addresses, local paths, PDF content, or Zotero database access.
- Update the README when installation steps, compatibility, the translation provider, or data handling changes.
