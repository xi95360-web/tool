"""Create, import, validate and search a provenance-aware SQLite databank."""
import argparse
import csv
import json
import sqlite3
from pathlib import Path

SCHEMA = Path(__file__).with_name('schema.sql')


def build(output, folder=None):
    if output.exists():
        raise ValueError('Output exists; choose a new database')
    output.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(output)
    try:
        conn.executescript(SCHEMA.read_text())
        conn.execute('PRAGMA foreign_keys=ON')
        conn.execute('BEGIN')
        conn.execute('PRAGMA defer_foreign_keys=ON')
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for file in sorted(folder.glob('*.csv')) if folder else []:
            table = file.stem
            if table not in tables:
                raise ValueError('Unknown table: ' + table)
            allowed = {r[1] for r in conn.execute('PRAGMA table_info("'+table+'")')}
            with file.open(encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                columns = reader.fieldnames
                if not columns or not set(columns) <= allowed:
                    raise ValueError('Invalid columns in ' + file.name)
                sql = 'INSERT INTO "'+table+'" ('+','.join('"'+c+'"' for c in columns)+') VALUES ('+','.join('?' for c in columns)+')'
                for row in reader:
                    conn.execute(sql, [row[c] if row[c] != '' else None for c in columns])
        if conn.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Unresolved source/variant/experiment links')
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def search(database, query):
    conn = sqlite3.connect(database.resolve().as_uri()+'?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute('SELECT * FROM v_claim_crosslinks WHERE variant LIKE ? OR compounds LIKE ? OR endpoint LIKE ?',
                            ['%'+query+'%']*3)
        return [dict(r) for r in rows]
    finally:
        conn.close()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    subs = p.add_subparsers(dest='command', required=True)
    b = subs.add_parser('build')
    b.add_argument('--out', type=Path, required=True)
    b.add_argument('--csv-dir', type=Path)
    q = subs.add_parser('search')
    q.add_argument('--database', type=Path, required=True)
    q.add_argument('query')
    a = p.parse_args()
    if a.command == 'build':
        build(a.out, a.csv_dir)
        print(a.out)
    else:
        print(json.dumps(search(a.database, a.query), indent=2))

if __name__ == '__main__':
    main()
