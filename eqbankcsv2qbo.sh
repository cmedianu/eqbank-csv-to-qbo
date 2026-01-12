#!/bin/bash
# Convert EQ Bank CSV to QBO format
# Usage: ./eqbankcsv2qbo.sh <csv_file>

if [ $# -eq 0 ]; then
    echo "Usage: $0 <csv_file>"
    echo "Example: $0 '400000395 Details.csv'"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
uv run "$SCRIPT_DIR/eqbankcsv2qbo.py" "$1"
