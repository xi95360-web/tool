"""Start STING Structure from any folder; first launch prepares a private environment."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent
NAME = "STING Structure"
SUPPORTS_CELLPOSE = False

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate paths without installing')
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--with-cellpose', action='store_true', help='Confocal only: install optional segmentation model software')
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        raise RuntimeError('Install Python 3.10 or later from https://www.python.org/downloads/')
    requirements = ROOT/'requirements-ui.txt'
    app = ROOT/'app.py'
    if not requirements.is_file() or not app.is_file():
        raise RuntimeError('Incomplete application folder. Extract the complete repository ZIP again.')
    if args.check:
        print(NAME + ': launcher files found; current terminal folder does not matter.')
        return 0
    if args.with_cellpose and not SUPPORTS_CELLPOSE:
        raise RuntimeError('Cellpose setup is only available in Confocal Analysis.')
    environment = ROOT/'.workflow-env'
    python = environment/('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if not python.exists():
        print('First-time setup for '+NAME+'. Please wait...', flush=True)
        venv.EnvBuilder(with_pip=True).create(environment)
    inputs = [requirements] + ([ROOT/'requirements.txt'] if (ROOT/'requirements.txt').exists() else [])
    digest = hashlib.sha256(b''.join(p.read_bytes() for p in inputs)).hexdigest()
    stamp = environment/'setup.txt'
    ready = stamp.exists() and stamp.read_text() == digest
    if ready:
        ready = subprocess.run([str(python), '-c', 'import streamlit, Bio'],capture_output=True).returncode == 0
    if not ready:
        print('Installing application components. This first setup needs internet.', flush=True)
        subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(requirements)],check=True,cwd=ROOT)
        stamp.write_text(digest)
    if args.with_cellpose:
        print('Installing optional Cellpose. This is a large download and may take several minutes.',flush=True)
        subprocess.run([str(python), '-m', 'pip', 'install', 'cellpose>=4.2,<5'],check=True)
        print('Cellpose installed. Model weights may download on the first segmentation run.')
    if args.prepare_only:
        print('Setup complete. Double-click Start '+NAME+' to use the app.')
        return 0
    print('Opening '+NAME+' in your browser. Keep this terminal open. Control+C stops the app.',flush=True)
    return subprocess.call([str(python),'-m','streamlit','run',str(app),
        '--server.address','127.0.0.1','--server.headless','false','--browser.gatherUsageStats','false'],cwd=ROOT)

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError,RuntimeError,subprocess.CalledProcessError) as exc:
        print('\nCould not start '+NAME+': '+str(exc),file=sys.stderr)
        print('Check your Python installation and internet connection, then retry the launcher.',file=sys.stderr)
        raise SystemExit(1)
    except KeyboardInterrupt:
        print('\n'+NAME+' stopped.')
