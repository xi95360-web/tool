"""Start the local upload interface from any working directory."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true', help='Validate files without installing or starting anything')
    p.add_argument('--prepare-only', action='store_true', help='Install dependencies without starting the interface')
    args = p.parse_args()
    if sys.version_info < (3, 10):
        raise RuntimeError('Python 3.10 or later is required. Install it from https://www.python.org/downloads/')
    project = ROOT/'pyproject.toml'
    app = ROOT/'src'/'quickcheck'/'app.py'
    if not project.is_file() or not app.is_file():
        raise RuntimeError('Application folder is incomplete. Download and extract the full ZIP again.')
    if args.check:
        print('Launcher files found. Paths work independently of the current terminal folder.')
        return 0
    env_dir = ROOT/'.quickcheck-env'
    python = env_dir/('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if not python.exists():
        print('First-time setup: creating an environment for QuickCheck...', flush=True)
        venv.EnvBuilder(with_pip=True).create(env_dir)
    digest = hashlib.sha256(project.read_bytes()).hexdigest()
    stamp = env_dir/'quickcheck-install.txt'
    ready = stamp.exists() and stamp.read_text() == digest
    if ready:
        ready = subprocess.run([str(python), '-c', 'import quickcheck, streamlit'], capture_output=True).returncode == 0
    if not ready:
        print('Installing QuickCheck and its interface. Internet is needed for this first setup.', flush=True)
        subprocess.run([str(python), '-m', 'pip', 'install', '-e', str(ROOT)+'[ui]'], check=True)
        stamp.write_text(digest)
    if args.prepare_only:
        print('Setup complete. Open Start QuickCheck to analyze your samples.')
        return 0
    print('Opening QuickCheck in your browser. Keep this terminal window open. Press Control+C to stop.', flush=True)
    return subprocess.call([str(python), '-m', 'streamlit', 'run', str(app),
        '--server.address', '127.0.0.1', '--server.headless', 'false', '--browser.gatherUsageStats', 'false'], cwd=ROOT)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print('\nQuickCheck could not start: '+str(exc), file=sys.stderr)
        print('Check your internet connection and Python installation, then open Start QuickCheck again.', file=sys.stderr)
        raise SystemExit(1)
    except KeyboardInterrupt:
        print('\nQuickCheck stopped.')
