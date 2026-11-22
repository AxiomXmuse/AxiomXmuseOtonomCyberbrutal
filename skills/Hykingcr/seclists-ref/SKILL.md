---
name: seclists-ref
description: "Навигатор словарей тестирования SecLists — локальная копия ~/tools/SecLists. Сопоставляет поверхность атаки с нужным словарём для фаззинга, перебора, полезных нагрузок."
allowed-tools: Bash, Read
---

# seclists-ref

Local path: `$SECLISTS_ROOT/`

## Key directories

```
SecLists/
├── Discovery/
│   ├── Web-Content/          ← dir/file fuzzing
│   │   ├── directory-list-2.3-medium.txt      (220k entries)
│   │   ├── raft-medium-words.txt              (63k, lower FP)
│   │   ├── raft-large-files.txt               (37k files)
│   │   └── api/                               ← API-specific
│   ├── DNS/
│   │   ├── subdomains-top1million-5000.txt
│   │   └── subdomains-top1million-110000.txt
│   └── Infrastructure/
├── Passwords/
│   ├── Common-Credentials/
│   │   └── 10-million-password-list-top-10000.txt
│   └── Leaked-Databases/
├── Usernames/
│   └── Names/names.txt
├── Fuzzing/
│   ├── LFI/                  ← LFI payloads
│   ├── SQLi/                 ← SQL injection
│   ├── XSS/                  ← XSS payloads
│   └── SSRF/                 ← SSRF bypass wordlists
└── Payloads/
    └── ...
```

## Usage patterns

```bash
# Web content discovery (ffuf)
ffuf -u https://target.com/FUZZ -w $SECLISTS_ROOT/Discovery/Web-Content/raft-medium-words.txt

# Subdomain (ffuf)
ffuf -u https://FUZZ.target.com -w $SECLISTS_ROOT/Discovery/DNS/subdomains-top1million-5000.txt

# Password spray (netexec)
nxc smb <target> -u users.txt -p $SECLISTS_ROOT/Passwords/Common-Credentials/10-million-password-list-top-10000.txt

# LFI fuzz
ffuf -u "https://target.com/?file=FUZZ" -w $SECLISTS_ROOT/Fuzzing/LFI/LFI-Jhaddix.txt
```
