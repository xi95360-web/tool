#!/bin/bash
WORKFLOW_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
    echo "Install Python 3.10 or later from https://www.python.org/downloads/ and try again."
    read -r -p "Press Return to close. "
    exit 1
fi
python3 "$WORKFLOW_DIR/launch.py" --with-cellpose --prepare-only
WORKFLOW_EXIT=$?
if [ "$WORKFLOW_EXIT" -ne 0 ]; then
    read -r -p "Copy the error above if you need help. Press Return to close. "
fi
exit "$WORKFLOW_EXIT"
