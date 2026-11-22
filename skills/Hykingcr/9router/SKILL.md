---
name: 9router
description: Akses 9Router (gateway AI Fahmi) untuk WEB SEARCH (/v1/search), WEB FETCH URL→markdown (/v1/web/fetch), EMBEDDINGS/RAG (/v1/embeddings), chat, dan discovery model. Gunakan setiap kali butuh mencari di web, membaca isi URL/artikel/paper, membuat embedding atau semantic search, atau mengecek model yang tersedia. Pakai ini, BUKAN tool WebSearch bawaan atau curl.
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/nr.py *)
---

# 9Router

Ringkasan dari SKILL.md resmi (dibaca 20 Okt 2026):
- Hub: https://raw.githubusercontent.com/decolua/9router/refs/heads/master/skills/9router/SKILL.md
- Chat: …/skills/9router-chat/SKILL.md · Web search: …/skills/9router-web-search/SKILL.md
- Web fetch: …/skills/9router-web-fetch/SKILL.md · Embeddings: …/skills/9router-embeddings/SKILL.md
- (ada juga: …/9router-image, …/9router-tts, …/9router-stt — dengan prefix URL yang sama)

Prefix URL lengkap: `https://raw.githubusercontent.com/decolua/9router/refs/heads/master/skills/`.
Kalau perilaku endpoint terasa berbeda, baca ulang SKILL.md resmi itu — dokumen ini hanya ringkasan.

## Setup (env, bukan file)
- `NINEROUTER_URL` — mis. `http://localhost:20128` (atau URL VPS/tunnel)
- `NINEROUTER_KEY` — dari Dashboard → Keys (hanya bila `requireApiKey=true`). Jangan tulis nilainya ke file.
- Opsional default model: `NR_SEARCH_MODEL`, `NR_FETCH_MODEL`, `NR_EMBED_MODEL` (isi dari hasil discovery).

## Perintah (selalu lewat skrip ini)
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/nr.py health                  # GET /api/health → {"ok":true}
python3 ${CLAUDE_SKILL_DIR}/scripts/nr.py models web              # id + kind (webSearch/webFetch)
python3 ${CLAUDE_SKILL_DIR}/scripts/nr.py models embedding
python3 ${CLAUDE_SKILL_DIR}/scripts/nr.py models chat             # GET /v1/models
python3 ${CLAUDE_SKILL_DIR}/scripts/nr.py info tavily/search      # GET /v1/models/info?id=...
python3 ${CLAUDE_SKILL_DIR}/scripts/nr.py search "kueri" --max 8 [--model tavily] [--type news] [--domain arxiv.org]
python3 ${CLAUDE_SKILL_DIR}/scripts/nr.py fetch https://arxiv.org/abs/XXXX --max-chars 20000 [--model jina-reader]
python3 ${CLAUDE_SKILL_DIR}/scripts/nr.py embed --in research/sources.md --out research/index/sources.jsonl [--model <id>]
python3 ${CLAUDE_SKILL_DIR}/scripts/nr.py query "pertanyaan" --index research/index/sources.jsonl --k 5
```

## Endpoint resmi (untuk referensi)
| Kemampuan | Endpoint | Field inti |
|---|---|---|
| Chat (OpenAI) | `POST /v1/chat/completions` | `model`, `messages`, `stream` |
| Chat (Anthropic) | `POST /v1/messages` | `model`, `max_tokens`, `messages` + header `anthropic-version` |
| Web search | `POST /v1/search` | `model`/`provider` (tavily, exa, brave-search, serper, searxng, google-pse, youcom, perplexity, linkup, searchapi, xquik, atau combo), `query`, `max_results` (default 5), `search_type` (web/news/x), `country`, `language`, `time_range`, `domain_filter` |
| Web fetch | `POST /v1/web/fetch` | `model`/`provider` (firecrawl, jina-reader, tavily, exa, ollama, atau `fetch-combo`), `url`, `format` (markdown/text/html), `max_characters` |
| Embeddings | `POST /v1/embeddings` | `model` (dari `/v1/models/embedding`), `input` (string/array), `encoding_format`, `dimensions` (hanya OpenAI v3) |

Contoh resmi (web search):
```bash
curl -X POST $NINEROUTER_URL/v1/search \
  -H "Authorization: Bearer $NINEROUTER_KEY" -H "Content-Type: application/json" \
  -d '{"model":"tavily","query":"9Router open source","max_results":5}'
```
(Di sesi Claude Code, `curl` diblokir oleh settings; gunakan `nr.py`, yang mengirim request yang sama.)

## Aturan pakai
- Nama model **selalu** dari discovery (`nr.py models ...`); jangan menebak. Combo (`owned_by: combo`) = auto-fallback antar provider — pilihan bagus sebagai default.
- `google-pse` butuh `cx` di provider options; `searxng` self-hosted tanpa auth; `xquik` = cari post X (berbayar per post).
- Hasil search hanya kandidat: fetch halaman sebelum mengutip. Catat URL + tanggal akses.
- Error: 401 → key; 400 `Invalid model format` → model salah; 503 → tunggu/tambah akun.
