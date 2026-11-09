"""Explicit inputs; discovery mode never infers intentions from filenames."""
import argparse
import hashlib
import json
import re
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from . import core, __version__


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference', type=Path, required=True)
    p.add_argument('--input-dir', type=Path, required=True)
    p.add_argument('--feature-label', help='Exact CDS label, gene, locus_tag or protein_id')
    p.add_argument('--feature-index', type=int, help='1-based CDS index (used by the upload interface)')
    p.add_argument('--expected', help='Comma-separated AA substitutions, e.g. L90E,M120L')
    p.add_argument('--expected-file', type=Path, help='TSV: filename_regex<TAB>mutation1,mutation2')
    p.add_argument('--interactive', action='store_true')
    p.add_argument('--out-dir', type=Path)
    p.add_argument('--min-phred', type=int, default=20)
    p.add_argument('--open', action='store_true')
    args = p.parse_args(argv)
    try:
        if args.expected and args.expected_file:
            raise ValueError('Choose --expected or --expected-file')
        if not 0 <= args.min_phred <= 93:
            raise ValueError('Phred threshold must be between 0 and 93')
        if args.interactive and not (args.expected or args.expected_file):
            args.expected = input('Expected AA edits (comma-separated; blank = discovery): ').strip()
        expected = []
        if args.expected:
            expected = [x.strip().upper() for x in args.expected.split(',')]
            if any(not re.fullmatch(r'[ACDEFGHIKLMNPQRSTVWY][1-9]\d*[ACDEFGHIKLMNPQRSTVWY*]', x) for x in expected):
                raise ValueError('Invalid AA edit; use L90E or L90E,M120L')
        reference = args.reference.resolve()
        inputs = args.input_dir.resolve()
        record = core.load_reference(reference)
        if args.feature_index is not None:
            features = [f for f in record.features if f.type == 'CDS']
            if args.feature_label or not 1 <= args.feature_index <= len(features):
                raise ValueError('Invalid CDS index or conflicting CDS selection')
            feature = features[args.feature_index - 1]
        else:
            feature = core.reference_feature(record, args.feature_label)
        positions = core.feature_genomic_positions(feature) if feature else []
        cds = str(feature.extract(record.seq)).upper() if feature else ''
        mapping = core.load_expected_map(args.expected_file.resolve(), inputs, Path.cwd()) if args.expected_file else None
        if (expected or mapping) and not positions:
            raise ValueError('AA targets require a selected annotated CDS; use GenBank')
        files = core.sample_files(inputs)
        if not files:
            raise ValueError('No AB1/ABI/SEQ/FASTA/FASTQ input files found')
        out = args.out_dir or Path.cwd() / ('quickcheck_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
        if out.exists():
            raise ValueError('Output already exists; choose a new directory')
        results = [core.call_for_sample(f, record, positions, cds, args.min_phred, mapping,
                   None if mapping else expected) for f in files]
        report, _, report_json = core.write_reports(results, reference, inputs, out, args.min_phred)
        payload = json.loads(report_json.read_text())
        payload.update(version=__version__, reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
                       input_sha256={str(f): hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
                       selected_feature=args.feature_label, selected_feature_index=args.feature_index,
                       expected_source='map' if mapping else 'explicit' if expected else 'discovery')
        report_json.write_text(json.dumps(payload, indent=2))
        core.print_summary(results, inputs, reference, out)
        if args.open:
            webbrowser.open(report.resolve().as_uri())
        return 0
    except (ValueError, OSError, IndexError) as exc:
        print('Analysis failed: ' + str(exc), file=sys.stderr)
        return 1
