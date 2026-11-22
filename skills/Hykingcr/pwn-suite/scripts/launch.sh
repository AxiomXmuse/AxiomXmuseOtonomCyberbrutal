#!/usr/bin/env bash
# HYKINGCR pwn-suite launcher — Axiom Web PWN pipeline
# Source: $HANGX_JAIL_ROOT/020-web-hacking-extreme/
set -euo pipefail

# shellcheck disable=SC1091
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../config" && pwd)/paths.sh"
WEB_EXTREME_ROOT="$HANGX_JAIL_ROOT/020-web-hacking-extreme"
PIPELINE="$WEB_EXTREME_ROOT/pipeline/axiom-web-pwn.py"
TARGET="${1:-}"

if [[ -z "$TARGET" ]]; then
  echo "Usage: $0 <target-url> [--aggressive] [--proxy http://127.0.0.1:8080]"
  echo ""
  echo "Examples:"
  echo "  $0 https://target.example.com"
  echo "  $0 https://target.example.com --aggressive"
  exit 1
fi

if [[ ! -f "$PIPELINE" ]]; then
  echo "ERROR: axiom-web-pwn.py not found at $PIPELINE"
  exit 2
fi

export WEB_EXTREME_ROOT
exec python3 "$PIPELINE" -t "$TARGET" "${@:2}"
