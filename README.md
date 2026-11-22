# AxiomXmuseOtonomCyberbrutal

**AXIOM — bangkit dari kekalahan. We are legend.**

Arsenal red-team otonom untuk Muse: skill, router, dan agent loop dalam satu repo. Siap tempur.

## Yang ada di dalam

| Area | Lokasi | Isi |
|---|---|---|
| Aturan operasi agent | `AGENTS.md` | Cara Axiom bekerja di repo ini |
| Skill Hykingcr | `skills/Hykingcr/` | CLI + MCP: nmap, gobuster, hashcat, hydra, metasploit, netexec, nikto, responder, evil-winrm, certipy, chisel, ghidra, ida, re-tools, llm-redteam, killchain-engine, pentest-agents, pwn-suite, api-recon, binary-recon, geo-osint, browser-act, dan banyak lagi. Router di `skills/Hykingcr/scripts/router.py`, tabel routing di `skills/Hykingcr/config/routing.json`. |
| Web hacking extreme | `skills/020-web-hacking-extreme/` | 15 kategori: 01-recon, 02-waf-bypass, 03-exploit, 04-client-side, 05-auth-oauth, 06-automation, 07-web-security, 08-cloud-web, 09-ai-llm-web, 10-adv-recon, 11-network-web, 12-red-team-web, 13-log-siem-web, 14-exploit-arsenal, 15-threat-intel, plus `pipeline/`. |
| HackinMode | `skills/HackinMode/` | Titik masuk mode web-pwn (`skill.md`). |
| Indeks skill | `SKILLS_INDEX.md` | Semua 302 dokumen skill, lengkap dengan path. |

Angka terverifikasi 2026-11-22: **301 `SKILL.md` + 1 `skill.md`, 300 `agent.py`**, 1.391 file, ~27 MB.

## Install

```bash
git clone https://github.com/AxiomXmuse/AxiomXmuseOtonomCyberbrutal.git
cd AxiomXmuseOtonomCyberbrutal
python3 --version   # 3.12+
# Install hanya tool yang dibutuhkan targetmu:
# nmap, gobuster, ffuf, nuclei, sqlmap, hydra, hashcat — lihat SKILL.md tiap skill
```

Tidak ada kredensial di repo ini. Tidak ada file `.env`. Kalau skill butuh token, export di shell-mu sendiri, jangan pernah commit.

## Pakai

1. Tulis targetmu dulu: host, IP range, atau URL.
2. Pilih skill dari `SKILLS_INDEX.md`, baca `SKILL.md`-nya dulu.
3. Jalankan script skill dengan target sebagai argumen.
4. Simpan bukti: command, output, dan apa yang berubah. Tanpa bukti = belum selesai.

Contoh (recon saja):

```bash
python3 skills/Hykingcr/scripts/router.py "recon web target"
```

## Router

Tanya dengan kata biasa, router mengarahkan ke skill yang tepat:

```bash
python3 skills/Hykingcr/scripts/router.py --ask "bypass waf dan exploit sql injection di website" --json
# -> W02 020 WAF Bypass
```

Route: H01–H14 + R0–R45 (Hykingcr + reverse-skill), W01–W15 (020-web-hacking-extreme), W16 (HackinMode). Tidak ada yang cocok → H-default (pwn-suite).

## Di dalam

- `skills/Hykingcr/scripts/router.py` + `config/routing.json` — route tugas dengan kata biasa ke skill yang tepat.
- `skills/020-web-hacking-extreme/pipeline/` — pipeline web end-to-end (recon → deteksi → WAF bypass → exploit → chain → report).
- `SKILLS_INDEX.md` — indeks satu baris tiap skill, supaya Muse menemukan skill yang tepat tanpa membaca 302 dokumen.

## Aturan repo

- Secret scan hukumnya wajib: `gitleaks dir .` dari root repo harus bersih sebelum push. Token contoh di dokumentasi skill terdaftar di `.gitleaksignore` berdasarkan fingerprint — tidak ada kredensial asli yang diabaikan, dan secret baru tetap ketahuan.
- `__pycache__` dan `*.pyc` dikecualikan (lihat `.gitignore`).

## License

MIT — lihat `LICENSE`.
