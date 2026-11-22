---
name: hykingcr-api-recon
description: "API surface recon — SPA harvest, Webpack/Vite map extraction, XHR/fetch stub replay, Swagger/OpenAPI discovery. Runs ARTEX api-recon methodology."
---

# HYKINGCR — API Recon (ARTEX Methodology)

Source: `repos/ARTEX/skills/api-recon/SKILL.md`

## Overview

Two-layer model: static (JS bundle analysis) + runtime (live session capture).

| Layer | Output | Limit |
|---|---|---|
| **Static** (JS bundle) | Full endpoint paths, route draft, component field candidates | No HTTP method; params need Phase 1b |
| **Runtime** (live session) | Method + body + response + dynamic URL + WS/SSE | Requires page render |

Run modes:
- `depth` — `runtime_harvest.js` (Puppeteer): API list, METHOD/params/response, WS/SSE
- `coverage` — browser + `preload.js`: tab/dialog/table clicks for deeper coverage
- `both` — sequential: most complete

## Scope Boundary

This skill does **API/parameter surface recon only** — not vulnerability exploitation.

| Allowed | Forbidden |
|---|---|
| Enumerate path, method, param, route, UI trigger | SQLi/XSS/IDOR/brute/fuzz/attack/irreversible ops |
| Hook + stub/mock to bypass client-side auth gates | Real credentials, OTP, OAuth toward real backend |
| Record outbound requests | Depend on real backend session to continue |

## Launch

```bash
python3 '${CLAUDE_SKILL_DIR}/scripts/api-recon.py' --target <URL> [--mode depth|coverage|both]
```

## Phases

### Phase 1 — Static harvest
```bash
# Runs harvest_static.py from ARTEX skill dir
ARTEX_SKILL=$OMP_REPOS_ROOT/ARTEX/skills/api-recon
python3 "$ARTEX_SKILL/scripts/harvest_static.py" --target <URL> --outdir OUTDIR/
```
Outputs: `api_static.txt`, `routes.txt`, `js/`

### Phase 2 — Runtime (depth)
```bash
node "$ARTEX_SKILL/scripts/runtime_harvest.js" --target <URL> --outdir OUTDIR/
```

### Phase 3 — Runtime (coverage, no-credentials)
```bash
# preload.js stubs auth/menu/bootstrap APIs; mocks them so SPA renders post-login shell
node "$ARTEX_SKILL/scripts/preload.js" --target <URL> --outdir OUTDIR/
```

### Phase 4 — Permission tree restoration
When module pages are blank, restore permission tree and re-run until module-level APIs appear.

### Phase 5 — Merge and deliver
```bash
python3 "$ARTEX_SKILL/scripts/merge_params.py" --outdir OUTDIR/ --out params_merged.json
```
Outputs: `api_surface.json`, `params_merged.json`, `endpoint_matrix.csv`

## Completion Criteria

- [ ] Static: Phase 1 harvest produces `api_static.txt`, `routes.txt`, `js/`
- [ ] Runtime: at least depth or coverage mode; coverage needs hook live + dynamic enum loop
- [ ] Shell access: business path renders (not `/login`)
- [ ] Parameters: coverage/both completes trigger matrix + `param_samples.json`; Phase 5 merges to `params_merged.json`
- [ ] Delivery: Phase 5 outputs complete

## ARTEX Skill Reference

Full methodology in:
```
$OMP_REPOS_ROOT/ARTEX/skills/api-recon/SKILL.md
```
