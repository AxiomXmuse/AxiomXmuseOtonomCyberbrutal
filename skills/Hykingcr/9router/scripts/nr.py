#!/usr/bin/env python3
"""nr.py — klien kecil 9Router untuk Claude Code (search, fetch, embeddings, discovery).

Hanya memanggil ${NINEROUTER_URL} (default http://localhost:20128). Tidak ada domain lain.
Key dibaca dari env NINEROUTER_KEY (opsional jika 9Router requireApiKey=false). Tidak pernah dicetak.

Contoh:
  nr.py health
  nr.py models [chat|web|embedding|image|tts|stt|image-to-text]
  nr.py info <model-id>
  nr.py search "query" [--model tavily] [--max 5] [--type web|news|x] [--domain arxiv.org]
  nr.py fetch <url> [--model jina-reader] [--format markdown] [--max-chars 20000]
  nr.py embed "teks" ... | --in file.md --out index.jsonl [--model <id>] [--chunk 1200]
  nr.py query "pertanyaan" --index index.jsonl [--k 5] [--model <id>]
Model default diambil dari env NR_SEARCH_MODEL / NR_FETCH_MODEL / NR_EMBED_MODEL.
"""
import argparse, json, math, os, sys, urllib.error, urllib.request

BASE = os.environ.get("NINEROUTER_URL", "http://localhost:20128").rstrip("/")
KEY = os.environ.get("NINEROUTER_KEY", "")
MODEL_KIND = {"chat": "/v1/models", "web": "/v1/models/web", "embedding": "/v1/models/embedding",
              "image": "/v1/models/image", "tts": "/v1/models/tts", "stt": "/v1/models/stt",
              "image-to-text": "/v1/models/image-to-text"}


def call(path, body=None, timeout=120):
    req = urllib.request.Request(BASE + path, method="POST" if body is not None else "GET")
    if KEY:
        req.add_header("Authorization", f"Bearer {KEY}")
    data = None
    if body is not None:
        req.add_header("Content-Type", "application/json")
        data = json.dumps(body).encode()
    try:
        with urllib.request.urlopen(req, data=data, timeout=timeout) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")[:500]
        hint = {401: "set/refresh NINEROUTER_KEY (Dashboard → Keys)",
                400: "cek nama model di /v1/models/<kind> (nr.py models ...)",
                503: "semua akun provider sibuk: tunggu retry-after / tambah akun"}.get(e.code, "")
        sys.exit(f"9Router HTTP {e.code}: {msg}\n{hint}")
    except urllib.error.URLError as e:
        sys.exit(f"Tidak bisa menghubungi {BASE}: {e.reason}. Apakah 9Router jalan? (nr.py health)")


def need(model, env):
    m = model or os.environ.get(env)
    if not m:
        sys.exit(f"Model belum diset. Jalankan discovery (nr.py models web|embedding) lalu pakai --model <id> atau export {env}=<id>.")
    return m


def chunks(text, size):
    paras, buf, out = text.split("\n\n"), "", []
    for p in paras:
        if len(buf) + len(p) > size and buf:
            out.append(buf.strip()); buf = ""
        buf += p + "\n\n"
    if buf.strip():
        out.append(buf.strip())
    return out


def embed(texts, model):
    res = call("/v1/embeddings", {"model": model, "input": texts})
    return [d["embedding"] for d in sorted(res.get("data", []), key=lambda d: d.get("index", 0))]


def cos(a, b):
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb or 1.0)


def main():
    ap = argparse.ArgumentParser(description="Klien 9Router")
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("health")
    m = sp.add_parser("models"); m.add_argument("kind", nargs="?", default="chat", choices=MODEL_KIND)
    i = sp.add_parser("info"); i.add_argument("id")
    s = sp.add_parser("search"); s.add_argument("query"); s.add_argument("--model"); s.add_argument("--max", type=int, default=5)
    s.add_argument("--type", default=None); s.add_argument("--domain", action="append"); s.add_argument("--raw", action="store_true")
    f = sp.add_parser("fetch"); f.add_argument("url"); f.add_argument("--model"); f.add_argument("--format", default="markdown")
    f.add_argument("--max-chars", type=int, default=20000)
    e = sp.add_parser("embed"); e.add_argument("texts", nargs="*"); e.add_argument("--model"); e.add_argument("--in", dest="inp")
    e.add_argument("--out"); e.add_argument("--chunk", type=int, default=1200)
    q = sp.add_parser("query"); q.add_argument("text"); q.add_argument("--index", required=True); q.add_argument("--k", type=int, default=5); q.add_argument("--model")
    a = ap.parse_args()

    if a.cmd == "health":
        print(json.dumps(call("/api/health")))
    elif a.cmd == "models":
        res = call(MODEL_KIND[a.kind])
        for d in res.get("data", []):
            print("\t".join(str(x) for x in (d.get("id"), d.get("kind", ""), d.get("owned_by", ""))))
    elif a.cmd == "info":
        print(json.dumps(call("/v1/models/info?id=" + urllib.request.quote(a.id, safe="/")), indent=1)[:4000])
    elif a.cmd == "search":
        body = {
            "model": need(a.model, "NR_SEARCH_MODEL"),
            "query": a.query,
            "search_type": a.type or "web",
            "max_results": a.max
        }
        if a.domain: body["domain_filter"] = a.domain
        res = call("/v1/search", body)
        if a.raw:
            print(json.dumps(res, indent=1)); return
        ans = res.get("answer")
        if isinstance(ans, dict) and ans.get("text"):
            print(f"=== Ringkasan ({ans.get('source', '')} / {ans.get('model', '')}) ===")
            print(ans.get("text").strip())
            print("\n=== Sumber / Hasil Pencarian ===")
        for r in res.get("results", []):
            print(f"[{r.get('position')}] {r.get('title')}\n    {r.get('url')}  ({r.get('published_at') or '-'})\n    {(r.get('snippet') or r.get('content') or '')[:300]}")
        if res.get("errors"): print("errors:", res["errors"], file=sys.stderr)
    elif a.cmd == "fetch":
        body = {"model": need(a.model, "NR_FETCH_MODEL"), "url": a.url, "format": a.format, "max_characters": a.max_chars}
        res = call("/v1/web/fetch", body)
        res = res.get("data", res)  # bentuk respons bisa dibungkus "data" (lihat contoh JS di SKILL.md resmi)
        c = res.get("content")
        text = c.get("text", "") if isinstance(c, dict) else (c or "")
        print(f"# {res.get('title') or ''}\nsumber: {res.get('url', a.url)} via {res.get('provider', '?')}\n\n{text}")
    elif a.cmd == "embed":
        model = need(a.model, "NR_EMBED_MODEL")
        texts = chunks(open(a.inp, encoding="utf-8").read(), a.chunk) if a.inp else a.texts
        if not texts: sys.exit("Tidak ada teks.")
        vecs = []
        for j in range(0, len(texts), 32):
            vecs += embed(texts[j:j + 32], model)
        if a.out:
            os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
            with open(a.out, "w", encoding="utf-8") as fh:
                for t, v in zip(texts, vecs):
                    fh.write(json.dumps({"model": model, "source": a.inp, "text": t, "embedding": v}) + "\n")
            print(f"{len(vecs)} chunk ditulis ke {a.out} (dim={len(vecs[0]) if vecs else 0}, model={model})")
        else:
            print(json.dumps([{"text": t[:80], "dim": len(v)} for t, v in zip(texts, vecs)], indent=1))
    elif a.cmd == "query":
        rows = [json.loads(l) for l in open(a.index, encoding="utf-8") if l.strip()]
        model = a.model or (rows[0]["model"] if rows else need(None, "NR_EMBED_MODEL"))
        qv = embed([a.text], model)[0]
        for sc, r in sorted(((cos(qv, r["embedding"]), r) for r in rows), key=lambda x: -x[0])[: a.k]:
            print(f"{sc:.3f}\t{r['text'][:400]!r}")


if __name__ == "__main__":
    main()
