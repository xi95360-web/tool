#!/usr/bin/env python3
"""Validate the manifest and build a reproducible Zotero XPI package."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_FILES = ("manifest.json", "bootstrap.js", "README.md")
FIXED_TIMESTAMP = (2020, 1, 1, 0, 0, 0)


def load_manifest() -> dict:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    required = ("name", "version", "applications")
    missing = [key for key in required if not manifest.get(key)]
    if missing:
        raise ValueError(f"manifest.json is missing: {', '.join(missing)}")
    zotero = manifest.get("applications", {}).get("zotero", {})
    if not zotero.get("id") or not zotero.get("strict_min_version") or not zotero.get("strict_max_version"):
        raise ValueError("manifest.json needs a Zotero id, strict_min_version, and strict_max_version")
    for key in ("homepage_url",):
        if "example.com" in str(manifest.get(key, "")):
            raise ValueError(f"manifest.json contains a placeholder {key}")
    if "example.com" in str(zotero.get("update_url", "")):
        raise ValueError("manifest.json contains a placeholder update_url")

    source = (ROOT / "bootstrap.js").read_text(encoding="utf-8")
    match = re.search(r'^const PLUGIN_ID = ["\']([^"\']+)["\'];', source, re.MULTILINE)
    if not match or match.group(1) != zotero["id"]:
        raise ValueError("bootstrap.js PLUGIN_ID must match applications.zotero.id")
    return manifest


def build(output: Path | None = None) -> Path:
    manifest = load_manifest()
    output = output or ROOT / "dist" / f"zotero-word-translate-{manifest['version']}.xpi"
    output.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name in PACKAGE_FILES:
            source = ROOT / name
            if not source.is_file():
                raise FileNotFoundError(f"required package file not found: {name}")
            info = ZipInfo(name, FIXED_TIMESTAMP)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes(), compress_type=ZIP_DEFLATED, compresslevel=9)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="custom output XPI path")
    args = parser.parse_args()
    package = build(args.output)
    print(package)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
