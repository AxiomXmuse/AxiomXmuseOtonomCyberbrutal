---
name: nmap-cli
description: "Сканер сетевой топологии — обнаружение узлов, анализ открытых портов, идентификация сервисов и ОС, NSE-скрипты. Бинарный файл: /usr/bin/nmap."
allowed-tools: Bash(nmap *), Read
---

# nmap-cli

Binary: `/usr/bin/nmap`

## Key invocations

```bash
# Fast TCP scan all ports
nmap -T4 -p- <target>

# Service + version + OS detection
nmap -sV -O -T4 <target>

# Full with NSE default scripts
nmap -sC -sV -T4 <target>

# UDP top 100
nmap -sU --top-ports 100 <target>

# Output to all formats
nmap -sC -sV -oA nmap_out <target>

# Stealth SYN scan
nmap -sS -T2 <target>

# NSE vuln scripts
nmap --script vuln <target>

# Script category: auth, brute, discovery, dos, exploit, external, fuzzer, intrusive, malware, safe, version
nmap --script=<category> <target>
```

## Common NSE scripts (offensive)

| Script | Use |
|---|---|
| `http-shellshock` | Shellshock detection |
| `smb-vuln-ms17-010` | EternalBlue check |
| `smb-vuln-ms08-067` | MS08-067 |
| `ftp-anon` | Anonymous FTP |
| `ssh-brute` | SSH brute force |
| `http-sql-injection` | SQLi scan |
| `ssl-heartbleed` | Heartbleed |
| `rdp-vuln-ms12-020` | RDP vuln |

## Engagement rules

- Always have explicit written scope authorisation before scanning
- `-T2` or `-T1` for stealthy/rate-limited environments
- `-oA` every scan; save output under `work/<case>/nmap/`
