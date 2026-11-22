---
name: hykingcr-geo-osint
description: "Photo geolocation OSINT — locates where a photo was taken without GPS: EXIF/OCR intake, DEM skyline matching, OpenStreetMap Overpass queries, CLIP satellite imagery scoring, shadow/sun math, reverse image search (Baidu/Yandex), Bayesian candidate tracking. Outputs (lat, lon) ± radius + heading."
---

# HYKINGCR — Geo OSINT (geo-sleuth)

Source: `repos/geo-sleuth/skills/geo-sleuth/SKILL.md` (26.8KB, full methodology)

**Full methodology:** Read the source SKILL.md directly:
```
$OMP_REPOS_ROOT/geo-sleuth/skills/geo-sleuth/SKILL.md
```

## Overview

Three-layer analysis system:

| Layer | Who | Tools |
|---|---|---|
| Decision: candidate tracking, evidence scoring, next step | **Script** (board.py) | `board.py` |
| Perception: OCR, satellite image ranking, sun math, terrain match | **Scripts compute first; you examine top few** | `intake.py`, `sat_scan.py`, `match.py`, `sun.py` |
| Judgment: pulling clues, proposing hypotheses, deciding among top candidates | **You** | — |

## Setup

```bash
GEO_SLEUTH_ROOT=$OMP_REPOS_ROOT/geo-sleuth

# Install uv if needed:
# curl -LsSf https://astral.sh/uv/install.sh | sh

# Scripts use PEP 723 inline metadata — uv installs deps automatically:
uv run "$GEO_SLEUTH_ROOT/skills/geo-sleuth/scripts/intake.py" --help
```

**Without uv:** Install deps manually:
```bash
pip install pillow exifread requests beautifulsoup4 numpy scipy opencv-python shapely pyproj osmnx
```

## Scripts

All wrappers set `GEO_SLEUTH_ROOT` and delegate to geo-sleuth scripts via `uv run`:

| Wrapper | Source Script | Purpose |
|---|---|---|
| `scripts/intake.sh` | `intake.py` | EXIF, OCR, reverse image search (Baidu/Yandex), initial candidate board init |
| `scripts/board.sh` | `board.py` | Candidate board: add, rank, evidence score, next step, children, report |
| `scripts/terrain.sh` | `terrain.py` | DEM terrain: elevation, skyline render, terrain match |
| `scripts/sat_scan.sh` | `sat_scan.py` | CLIP satellite imagery scoring against candidate areas |
| `scripts/osm.sh` | `osm.py` | OSM Overpass queries: POI search, road network, route |
| `scripts/sun.sh` | `sun.py` | Shadow/sun math: solar position, heading from shadow, locate by latitude |

## Workflow

### Step 1 — One-command intake

```bash
bash '${CLAUDE_SKILL_DIR}/scripts/intake.sh' photo.jpg --out-dir intake/
bash '${CLAUDE_SKILL_DIR}/scripts/board.sh' init --photo photo.jpg
```

`intake.py` runs EXIF extraction, OCR (tiled/upscaled), and reverse image search (Baidu similar images + labels). Takes 1–2 min; first run longer (dep install). Output: `intake.md`.

### Step 2 — Rank candidates

```bash
# List all sub-divisions of a region
bash '${CLAUDE_SKILL_DIR}/scripts/board.sh' children '<parent admin area>'

# Score evidence for/against candidates
bash '${CLAUDE_SKILL_DIR}/scripts/board.sh' evidence --clue K1 \
  --for 'CandidateA':5 --for 'CandidateB':2 --against 'CandidateC':0.3 \
  --why "plate prefix matches" --file zoomed_crop.jpg

bash '${CLAUDE_SKILL_DIR}/scripts/board.sh' rank
bash '${CLAUDE_SKILL_DIR}/scripts/board.sh' next
```

### Step 3 — Narrow down

```bash
# Terrain match (compare DEM skyline to photo skyline)
bash '${CLAUDE_SKILL_DIR}/scripts/terrain.sh' view --lat 35.6 --lon 139.7 --radius 10

# Satellite imagery scoring
bash '${CLAUDE_SKILL_DIR}/scripts/sat_scan.sh' --bbox 35.5,139.6,35.7,139.8 --photo photo.jpg

# OSM POI search
bash '${CLAUDE_SKILL_DIR}/scripts/osm.sh' route --type highway --near 35.65,139.72

# Sun position → camera heading / latitude band
bash '${CLAUDE_SKILL_DIR}/scripts/sun.sh' compass --photo photo.jpg
bash '${CLAUDE_SKILL_DIR}/scripts/sun.sh' locate --shadow-dir 220 --time 14:30
```

### Step 4 — Confirm and report

```bash
bash '${CLAUDE_SKILL_DIR}/scripts/board.sh' report
```

Output: `(lat, lon) ± radius_m`, heading, confidence tier (verified/high/medium/low/unverified), evidence chain.

## Hard Rules (summary — full rules in source SKILL.md)

1. **No fabricated verification** — "measured on map" / "matched street view" requires commands actually run and files produced this session.
2. **Precision needs source** — error radius ≤100m requires intersection of two independent constraints.
3. **Anchor first, then search** — once a unique anchor is found, all later search starts from it.
4. **List whole category before inferring** — use `board.py children` to add all sub-divisions before ranking.
5. **Image evidence beats metadata** — if EXIF and visual content conflict, the image wins.
