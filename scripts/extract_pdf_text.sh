#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$SCRIPT_DIR/extract_pdf_text.swift"
BIN="${TMPDIR:-/tmp}/jlpt_n2_extract_pdf_text"

if [[ ! -x "$BIN" || "$SRC" -nt "$BIN" ]]; then
  swiftc "$SRC" -o "$BIN"
fi

exec "$BIN" "$@"
