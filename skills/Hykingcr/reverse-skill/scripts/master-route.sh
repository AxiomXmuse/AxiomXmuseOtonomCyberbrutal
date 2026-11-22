#!/usr/bin/env bash
# Delegates to reverse-skill master-route.sh with correct SKILL_ROOT.
set -euo pipefail

# shellcheck disable=SC1091
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../config" && pwd)/paths.sh"
SKILL_ROOT="$OMP_REPOS_ROOT/reverse-skill/skills"
UPSTREAM="$SKILL_ROOT/scripts/master-route.sh"

if [[ ! -f "$UPSTREAM" ]]; then
  echo "ERROR: reverse-skill master-route.sh not found at $UPSTREAM"
  exit 1
fi

export SKILL_ROOT
exec bash "$UPSTREAM" "$@"
