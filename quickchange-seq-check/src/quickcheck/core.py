"""Deterministic Sanger read screening against an explicit reference."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import webbrowser
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

try:
    from Bio import Align, SeqIO
    from Bio.Seq import Seq
except ImportError as exc:  # pragma: no cover - user-facing bootstrap message
    print(
        "Install dependencies: python -m pip install biopython",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


AA_MUTATION_RE = re.compile(r"(?<![A-Za-z])([A-Z])([1-9][0-9]*)([A-Z])(?![A-Za-z])")


@dataclass
class ExpectedMutation:
    ref_aa: str
    position: int
    alt_aa: str

    @property
    def label(self) -> str:
        return f"{self.ref_aa}{self.position}{self.alt_aa}"


@dataclass
class Mutation:
    position: int
    ref_aa: str
    alt_aa: str
    ref_codon: str
    observed_codon: str
    ref_nt: str
    observed_nt: str
    quality: str
    reference_coordinates: str

    @property
    def label(self) -> str:
        return f"{self.ref_aa}{self.position}{self.alt_aa}"


@dataclass
class NucleotideVariant:
    reference_coordinate: int
    ref_base: str
    observed_base: str
    region: str
    effect: str
    amino_acid_change: str
    quality: str


@dataclass
class IndelCall:
    kind: str
    reference_coordinates: str
    reference_sequence: str
    observed_sequence: str
    region: str
    quality: str


@dataclass
class TargetResult:
    expected: str
    position: int
    reference_codon: str
    observed_codon: str
    reference_aa: str
    observed_aa: str
    quality: str
    status: str
    note: str


@dataclass
class SampleResult:
    sample: str
    source_file: str
    input_format: str
    orientation: str
    read_length: int
    aligned_reference_range: str
    expected: List[str] = field(default_factory=list)
    targets: List[TargetResult] = field(default_factory=list)
    observed_mutations: List[Mutation] = field(default_factory=list)
    nucleotide_variants: List[NucleotideVariant] = field(default_factory=list)
    unexpected_variants: List[NucleotideVariant] = field(default_factory=list)
    indels: List[IndelCall] = field(default_factory=list)
    nucleotide_differences: int = 0
    cds_confident_bases: int = 0
    cds_length: int = 0
    status: str = "UNCERTAIN"
    note: str = ""
    alignment_text: str = ""
    quality_available: bool = False
    reference_covered_bases: int = 0
    reference_length: int = 0


def sample_files(directory: Path) -> List[Path]:
    candidates = sorted(p for p in directory.rglob("*") if p.is_file())
    abi = {p.with_suffix("") for p in candidates if p.suffix.lower() in {".ab1", ".abi"}}
    return [p for p in candidates if p.suffix.lower() in {".ab1", ".abi", ".seq", ".fasta", ".fa", ".fastq", ".fq"}
            and (p.suffix.lower() in {".ab1", ".abi"} or p.with_suffix("") not in abi)]


def reference_feature(record, label=None):
    cds = [f for f in record.features if f.type == "CDS"]
    if label:
        matches = [f for f in cds if label.lower() in {
            v.lower() for key in ("label", "gene", "locus_tag", "protein_id")
            for v in f.qualifiers.get(key, [])}]
        if len(matches) != 1:
            raise ValueError("CDS label must match exactly one CDS")
        return matches[0]
    if len(cds) > 1:
        raise ValueError("Multiple CDS features: select one with --feature-label")
    return cds[0] if cds else None


def load_reference(path):
    return SeqIO.read(path, "genbank" if path.suffix.lower() in {".gb", ".gbk", ".genbank"} else "fasta")


def feature_genomic_positions(feature):
    if feature.qualifiers.get("codon_start", ["1"]) != ["1"] or feature.qualifiers.get("transl_table", ["1"]) != ["1"]:
        raise ValueError("This release requires codon_start=1 and translation table 1")
    return list(feature.location)


def parse_expected(
    name: str,
    expected_map: Optional[Dict[str, List[str]]] = None,
    explicit_expected: Optional[List[str]] = None,
) -> List[ExpectedMutation]:
    """Use explicit targets or the first matching mapping rule; default to discovery."""
    if explicit_expected is not None:
        return [ExpectedMutation(x[0], int(x[1:-1]), x[-1]) for x in explicit_expected]
    if expected_map:
        for pattern, labels in expected_map.items():
            if re.search(pattern, name, flags=re.IGNORECASE):
                return [ExpectedMutation(x[0], int(x[1:-1]), x[-1]) for x in labels]
    return []


def load_expected_map(requested: Optional[Path], input_dir: Path, root: Path) -> Optional[Dict[str, List[str]]]:
    """Load optional filename-regex to expected-mutation mapping TSV."""
    path = requested
    if path is not None and not path.is_absolute():
        path = root / path
    if path is None:
        candidate = input_dir / "expected_mutations.tsv"
        path = candidate if candidate.exists() else None
    if path is None:
        return None
    if not path.exists():
        raise FileNotFoundError(f"Expected-mutation file not found: {path}")
    mapping: Dict[str, List[str]] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split("\t")
            if len(fields) != 2:
                raise ValueError(f"{path}:{line_number} requires two columns: filename_regex<TAB>Y240C,V147L")
            pattern, labels = fields
            parsed = [x.strip().upper() for x in labels.split(",") if x.strip()]
            if not parsed or any(not re.fullmatch(r"[A-Z][1-9][0-9]*[A-Z]", x) for x in parsed):
                raise ValueError(f"{path}:{line_number} invalid mutation format: {labels}")
            re.compile(pattern)
            mapping[pattern] = parsed
    return mapping


def load_query(path):
    if path.suffix.lower() in {".ab1", ".abi"}:
        record = SeqIO.read(path, "abi")
        return record, record.letter_annotations.get("phred_quality"), "AB1"
    if path.suffix.lower() in {".fastq", ".fq"}:
        record = SeqIO.read(path, "fastq")
        return record, record.letter_annotations["phred_quality"], "FASTQ"
    text = path.read_text().strip()
    if text.startswith(">"):
        record = SeqIO.read(path, "fasta")
    else:
        from Bio.SeqRecord import SeqRecord
        seq = "".join(text.split()).upper()
        if not seq or set(seq) - set("ACGTRYSWKMBDHVN"):
            raise ValueError("Invalid plain DNA sequence: " + str(path))
        record = SeqRecord(Seq(seq), id=path.stem)
    return record, None, "SEQ"


def make_aligner() -> Align.PairwiseAligner:
    aligner = Align.PairwiseAligner(mode="local")
    aligner.match_score = 2
    aligner.mismatch_score = -3
    aligner.open_gap_score = -8
    aligner.extend_gap_score = -1
    return aligner


def align_both_directions(reference: str, query: str, aligner: Align.PairwiseAligner):
    forward = aligner.align(reference, query)[0]
    reverse_query = str(Seq(query).reverse_complement())
    reverse = aligner.align(reference, reverse_query)[0]
    if reverse.score > forward.score:
        return reverse, reverse_query, "reverse"
    return forward, query, "forward"


def alignment_mapping(alignment) -> Dict[int, int]:
    mapping: Dict[int, int] = {}
    indices = alignment.indices
    for ref_index, query_index in zip(indices[0], indices[1]):
        if ref_index >= 0 and query_index >= 0:
            mapping[int(ref_index)] = int(query_index)
    return mapping


def quality_text(values: Sequence[Optional[int]]) -> str:
    if not values or any(v is None for v in values):
        return "NA"
    return "/".join(str(int(v)) for v in values)


def call_for_sample(
    path: Path,
    reference_record,
    cds_positions: Sequence[int],
    cds_seq: str,
    min_phred: int,
    expected_map: Optional[Dict[str, List[str]]] = None,
    explicit_expected: Optional[List[str]] = None,
) -> SampleResult:
    query_record, qualities, fmt = load_query(path)
    query = str(query_record.seq).upper().replace("U", "T")
    if not query or set(query) - set("ACGTRYSWKMBDHVN"):
        raise ValueError("Query must contain DNA IUPAC letters")
    reference = str(reference_record.seq).upper()
    aligner = make_aligner()
    alignment, oriented_query, direction = align_both_directions(reference, query, aligner)
    mapping = alignment_mapping(alignment)
    negative = len(cds_positions) > 1 and cds_positions[0] > cds_positions[1]
    def coding(seq):
        return str(Seq(seq).complement()) if negative else seq
    expected = parse_expected(path.stem, expected_map, explicit_expected)
    aligned_refs = sorted(mapping)
    ref_range = f"{aligned_refs[0] + 1}-{aligned_refs[-1] + 1}" if aligned_refs else "none"
    result = SampleResult(
        sample=path.stem,
        source_file=str(path),
        input_format=fmt,
        orientation=direction,
        read_length=len(query),
        aligned_reference_range=ref_range,
        expected=[x.label for x in expected],
    )

    result.alignment_text = str(alignment)
    result.quality_available = qualities is not None
    result.reference_covered_bases = len(mapping)
    result.reference_length = len(reference)

    def good_base(query_index: int) -> bool:
        base = oriented_query[query_index]
        if base not in "ACGT":
            return False
        if qualities is None:
            return True
        # AB1 quality values need to be reverse-complemented with the sequence.
        original_index = query_index if direction == "forward" else len(qualities) - 1 - query_index
        return int(qualities[original_index]) >= min_phred

    def q_at(query_index: int) -> Optional[int]:
        if qualities is None:
            return None
        original_index = query_index if direction == "forward" else len(qualities) - 1 - query_index
        return int(qualities[original_index])

    confident_cds = [
        ref_index for ref_index in cds_positions
        if mapping.get(ref_index) is not None and good_base(int(mapping[ref_index]))
    ]
    result.cds_confident_bases = len(confident_cds)
    result.cds_length = len(cds_positions)

    # Index each CDS base so every high-quality substitution can be classified.
    cds_set = set(cds_positions)
    codon_info: Dict[int, Tuple[int, List[int], str, str]] = {}
    for codon_offset in range(0, len(cds_positions) - 2, 3):
        ref_indices = cds_positions[codon_offset : codon_offset + 3]
        ref_codon = coding("".join(reference[i] for i in ref_indices))
        ref_aa = str(Seq(ref_codon).translate())
        for ref_index in ref_indices:
            codon_info[ref_index] = (codon_offset // 3 + 1, ref_indices, ref_codon, ref_aa)

    # Call all high-quality base substitutions, including synonymous and non-CDS changes.
    for ref_index, query_index in sorted(mapping.items()):
        ref_base = reference[ref_index]
        observed_base = oriented_query[query_index]
        if ref_base == observed_base or not good_base(query_index):
            continue
        info = codon_info.get(ref_index)
        region = "CDS" if ref_index in cds_set else "non-CDS"
        effect = "non-CDS"
        aa_change = ""
        if info:
            aa_position, ref_indices, ref_codon, ref_aa = info
            query_indices = [mapping.get(i) for i in ref_indices]
            if all(i is not None and good_base(int(i)) for i in query_indices):
                observed_codon = coding("".join(oriented_query[int(i)] for i in query_indices))
                observed_aa = str(Seq(observed_codon).translate())
                effect = "nonsynonymous" if observed_aa != ref_aa else "synonymous"
                aa_change = f"{ref_aa}{aa_position}{observed_aa}" if observed_aa != ref_aa else f"{ref_aa}{aa_position}{ref_aa} (synonymous)"
            else:
                effect = "unresolved-CDS"
                aa_change = f"codon {aa_position} (low quality/incomplete)"
        result.nucleotide_variants.append(
            NucleotideVariant(
                reference_coordinate=ref_index + 1,
                ref_base=ref_base,
                observed_base=observed_base,
                region=region,
                effect=effect,
                amino_acid_change=aa_change,
                quality=quality_text([q_at(query_index)]),
            )
        )

    # Keep the historical amino-acid list for a compact summary.
    seen_aa = set()
    for variant in result.nucleotide_variants:
        if variant.effect != "nonsynonymous" or not variant.amino_acid_change:
            continue
        label = variant.amino_acid_change
        if label in seen_aa:
            continue
        seen_aa.add(label)
        aa_match = re.fullmatch(r"([A-Z])([0-9]+)([A-Z])", label)
        if not aa_match:
            continue
        aa_position = int(aa_match.group(2))
        ref_indices = cds_positions[(aa_position - 1) * 3 : aa_position * 3]
        ref_codon = coding("".join(reference[i] for i in ref_indices))
        observed_indices = [mapping.get(i) for i in ref_indices]
        if any(i is None for i in observed_indices):
            continue
        observed_codon = coding("".join(oriented_query[int(i)] for i in observed_indices))
        result.observed_mutations.append(
            Mutation(
                position=aa_position,
                ref_aa=aa_match.group(1),
                alt_aa=aa_match.group(3),
                ref_codon=ref_codon,
                observed_codon=observed_codon,
                ref_nt=ref_codon,
                observed_nt=observed_codon,
                quality=quality_text([q_at(int(i)) for i in observed_indices]),
                reference_coordinates="-".join(str(i + 1) for i in ref_indices),
            )
        )

    # Report internal alignment gaps; unaligned primer/read ends are not treated as indels.
    aligned_blocks = alignment.aligned
    for block_index in range(len(aligned_blocks[0]) - 1):
        ref_end = int(aligned_blocks[0][block_index][1])
        next_ref_start = int(aligned_blocks[0][block_index + 1][0])
        query_end = int(aligned_blocks[1][block_index][1])
        next_query_start = int(aligned_blocks[1][block_index + 1][0])
        ref_gap = next_ref_start - ref_end
        query_gap = next_query_start - query_end
        if not ref_gap and not query_gap:
            continue
        # Include single-base gaps; require confident flanks and inserted bases.
        if max(ref_gap, query_gap) < 1:
            continue
        if query_gap and not all(good_base(i) for i in range(query_end, next_query_start)):
            continue
        if not all(good_base(i) for i in (query_end - 1, next_query_start) if 0 <= i < len(oriented_query)):
            continue
        ref_gap_seq = reference[ref_end:next_ref_start]
        query_gap_seq = oriented_query[query_end:next_query_start]
        if ref_gap and not query_gap:
            kind = "deletion"
            coordinates = f"{ref_end + 1}-{next_ref_start}"
            quality = "NA"
        elif query_gap and not ref_gap:
            kind = "insertion"
            coordinates = f"after {ref_end}"
            quality = quality_text([q_at(i) for i in range(query_end, next_query_start)])
        else:
            kind = "complex gap"
            coordinates = f"{ref_end + 1}-{next_ref_start}"
            quality = quality_text([q_at(i) for i in range(query_end, next_query_start)])
        region = "CDS" if any(i in cds_set for i in range(ref_end, next_ref_start)) or (query_gap and ref_end - 1 in cds_set and ref_end in cds_set) else "non-CDS"
        result.indels.append(IndelCall(kind, coordinates, ref_gap_seq, query_gap_seq, region, quality))

    result.nucleotide_differences = len(result.nucleotide_variants)

    for item in expected:
        offset = (item.position - 1) * 3
        if offset < 0 or offset + 3 > len(cds_positions):
            result.targets.append(TargetResult(item.label, item.position, "", "", "", "", "", "CONFIG_ERROR", "position outside CDS"))
            continue
        ref_indices = cds_positions[offset : offset + 3]
        ref_codon = coding("".join(reference[i] for i in ref_indices))
        ref_aa = str(Seq(ref_codon).translate())
        query_indices = [mapping.get(i) for i in ref_indices]
        if any(i is None for i in query_indices):
            result.targets.append(TargetResult(item.label, item.position, ref_codon, "", ref_aa, "", "", "UNCERTAIN", "not covered by this read"))
            continue
        qi = [int(i) for i in query_indices]
        qs = [q_at(i) for i in qi]
        observed_codon = coding("".join(oriented_query[i] for i in qi))
        observed_aa = str(Seq(observed_codon).translate()) if all(c in "ACGT" for c in observed_codon) else "?"
        qtext = quality_text(qs)
        if not all(good_base(i) for i in qi):
            status = "UNCERTAIN"
            note = f"low quality or ambiguous base (minimum Phred {min_phred})"
        elif ref_aa != item.ref_aa:
            status = "CONFIG_ERROR"
            note = f"reference encodes {ref_aa}, but filename expects {item.ref_aa}"
        elif observed_aa == item.alt_aa:
            status = "PASS"
            note = "expected amino-acid substitution observed"
        elif observed_aa == ref_aa:
            status = "FAIL"
            note = "reference amino acid remains unchanged"
        else:
            status = "FAIL"
            note = f"observed {observed_aa}, expected {item.alt_aa}"
        result.targets.append(TargetResult(item.label, item.position, ref_codon, observed_codon, ref_aa, observed_aa, qtext, status, note))

    expected_coordinates = set()
    for item in expected:
        offset = (item.position - 1) * 3
        if 0 <= offset and offset + 3 <= len(cds_positions):
            expected_coordinates.update(i + 1 for i in cds_positions[offset : offset + 3])
    result.unexpected_variants = [
        variant for variant in result.nucleotide_variants
        if variant.reference_coordinate not in expected_coordinates
    ]

    statuses = [x.status for x in result.targets]
    if not statuses:
        result.status = "NO_EXPECTATION"
        result.note = "Discovery mode: no expected edits supplied"
    elif "CONFIG_ERROR" in statuses:
        result.status = "CONFIG_ERROR"
        result.note = "check reference CDS or expected-mutation naming"
    elif "FAIL" in statuses:
        result.status = "FAIL"
        result.note = "one or more expected substitutions were not observed"
    elif "UNCERTAIN" in statuses:
        result.status = "UNCERTAIN"
        result.note = "one or more expected positions lack confident coverage"
    elif result.unexpected_variants or result.indels:
        extras = []
        for variant in result.unexpected_variants:
            label = variant.amino_acid_change or f"{variant.ref_base}>{variant.observed_base} @ {variant.reference_coordinate}"
            if label not in extras:
                extras.append(label)
        extras.extend(f"{i.kind} {i.reference_coordinates}" for i in result.indels)
        result.status = "PASS_WITH_EXTRA"
        result.note = "expected substitutions observed; extra changes: " + ", ".join(extras)
    else:
        result.status = "PASS"
        result.note = "expected substitutions observed"
    if not result.quality_available and result.status in {"PASS", "PASS_WITH_EXTRA"}:
        result.status = "PROVISIONAL"
    if any(i.region == "CDS" and (len(i.observed_sequence)-len(i.reference_sequence)) % 3 for i in result.indels):
        result.note += "; frameshifting CDS indel: downstream AA labels use reference codons, not reconstructed mutant translation"
    result.note += "; conclusions apply only to aligned bases; unsequenced regions remain unchecked"
    if not result.quality_available:
        result.note += "; base quality unavailable"
    return result


def compact(value: str, max_len: int = 70) -> str:
    return value if len(value) <= max_len else value[: max_len - 3] + "..."


def extra_summary(result: SampleResult) -> str:
    changes = []
    for variant in result.unexpected_variants:
        change = variant.amino_acid_change or f"{variant.ref_base}>{variant.observed_base} nt{variant.reference_coordinate}"
        if change not in changes:
            changes.append(change)
    changes.extend(f"{indel.kind}({indel.reference_coordinates})" for indel in result.indels)
    return ", ".join(changes) or "-"


def print_summary(results: Sequence[SampleResult], input_dir: Path, reference: Path, out_dir: Path) -> None:
    print(f"QuickChange | reference: {reference.name} | input: {input_dir}")
    print(f"samples: {len(results)} | report: {out_dir / 'quickchange_report.html'}")
    print("-" * 120)
    print(f"{'STATUS':<15} {'SAMPLE':<46} {'EXPECTED':<20} {'OBSERVED AA CHANGES':<35} {'EXTRA/INDEL':<35}")
    print("-" * 120)
    for r in results:
        observed = ", ".join(m.label for m in r.observed_mutations) or "-"
        print(f"{r.status:<15} {compact(r.sample, 46):<46} {','.join(r.expected) or '-':<20} {compact(observed, 35):<35} {compact(extra_summary(r), 35)}")
    print("-" * 120)
    counts: Dict[str, int] = {}
    for r in results:
        counts[r.status] = counts.get(r.status, 0) + 1
    print("summary: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))


def write_reports(results: Sequence[SampleResult], reference: Path, input_dir: Path, out_dir: Path, min_phred: int) -> Tuple[Path, Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "reference": str(reference),
        "input_directory": str(input_dir),
        "minimum_phred": min_phred,
        "results": [asdict(x) for x in results],
    }
    json_path = out_dir / "quickchange_report.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    tsv_path = out_dir / "quickchange_summary.tsv"
    with tsv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["status", "sample", "source_file", "expected", "target_results", "observed_aa_changes", "unexpected_variants", "indels", "nucleotide_differences", "cds_confident_bases", "cds_length", "orientation", "aligned_reference_range", "note"])
        for r in results:
            targets = "; ".join(f"{t.expected}:{t.status}:{t.observed_codon or '-'}" for t in r.targets)
            observed = "; ".join(f"{m.label}({m.observed_codon})" for m in r.observed_mutations)
            variants = "; ".join(f"nt{v.reference_coordinate}:{v.ref_base}>{v.observed_base}:{v.effect}" for v in r.unexpected_variants)
            indels = "; ".join(f"{i.kind}:{i.reference_coordinates}:{i.reference_sequence}>{i.observed_sequence}" for i in r.indels)
            writer.writerow([r.status, r.sample, r.source_file, ",".join(r.expected), targets, observed, variants, indels, r.nucleotide_differences, r.cds_confident_bases, r.cds_length, r.orientation, r.aligned_reference_range, r.note])

    html_path = out_dir / "quickchange_report.html"
    html_path.write_text(render_html(results, reference, input_dir, min_phred), encoding="utf-8")
    return html_path, tsv_path, json_path

def render_html(results, reference, input_dir, min_phred):
    def esc(value):
        return html.escape(str(value))
    sections = []
    for i, r in enumerate(results):
        payload = asdict(r)
        rows = "".join("<tr><th>" + esc(k) + "</th><td>" + esc(v) + "</td></tr>"
                       for k, v in payload.items() if k not in {"alignment_text", "source_file"})
        sections.append(f"<details class='sample' open><summary>{esc(r.sample)} — {esc(r.status)}</summary>"
                        f"<p>{esc(r.note)}</p><table>{rows}</table><h3>Alignment</h3>"
                        f"<pre>{esc(r.alignment_text)}</pre></details>")
    return ("<!doctype html><html lang='en'><meta charset='utf-8'><title>Sequencing QuickCheck</title>"
            "<style>body{font:16px system-ui;max-width:1200px;margin:32px auto;padding:16px;color:#172338}"
            "details{border:1px solid #ccd7e5;padding:20px;margin:18px 0;border-radius:10px}"
            "summary{font-weight:700;cursor:pointer}td,th{text-align:left;padding:8px;border-bottom:1px solid #eee}"
            "td{overflow-wrap:anywhere}table{width:100%;table-layout:fixed}pre{overflow:auto;background:#f4f6fa;padding:16px}"
            "input{padding:10px;width:90%}</style><h1>Sequencing QuickCheck</h1>"
            "<p>Results apply to aligned regions only. Partial reads do not validate an entire plasmid. "
            "SEQ/FASTA inputs lack base-quality evidence. Local alignment can miss terminal or very large rearrangements; "
            "circular-origin spanning reads are not normalized in this release. Review suspicious AB1 traces.</p>"
            f"<p>Reference: {esc(reference.name)} | Minimum Phred: {min_phred}</p>"
            "<p>PASS: targets supported, no extra calls in aligned region. PASS_WITH_EXTRA: targets plus extra calls. "
            "PROVISIONAL: target sequence observed without base qualities. NO_EXPECTATION: discovery only. "
            "FAIL: target not observed. UNCERTAIN: target lacks coverage or quality. CONFIG_ERROR: target/reference mismatch.</p>"
            "<input placeholder='Search samples or mutations' oninput=\"document.querySelectorAll('.sample').forEach(x=>x.hidden=!x.textContent.toLowerCase().includes(this.value.toLowerCase()))\">"
            + "".join(sections) + "</html>")
