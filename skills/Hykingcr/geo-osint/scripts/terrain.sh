#!/usr/bin/env bash
# geo-osint wrapper: terrain.sh
# shellcheck disable=SC1091
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../config" && pwd)/paths.sh"
GEO_SLEUTH_ROOT="$OMP_REPOS_ROOT/geo-sleuth"
export GEO_SLEUTH_ROOT
exec uv run "$GEO_SLEUTH_ROOT/skills/geo-sleuth/scripts/terrain.py" "$@"
