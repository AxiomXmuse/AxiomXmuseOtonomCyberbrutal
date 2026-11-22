---
name: gobuster-cli
description: "Gobuster — разведка веб-ресурсов: перебор каталогов/файлов, DNS-поддоменов, виртуальных хостов. Расположен: /usr/local/bin/gobuster."
allowed-tools: Bash(gobuster *), Read
---

# gobuster-cli

Binary: `/usr/local/bin/gobuster`
Wordlists: `$SECLISTS_ROOT/` · `/usr/share/wordlists/dirb/`

## Key invocations

```bash
# Directory bruteforce
gobuster dir -u https://target.com -w $SECLISTS_ROOT/Discovery/Web-Content/directory-list-2.3-medium.txt -t 50

# With extensions
gobuster dir -u https://target.com \
  -w $SECLISTS_ROOT/Discovery/Web-Content/raft-medium-words.txt \
  -x php,html,txt,bak,js,json -t 50

# DNS subdomain enumeration
gobuster dns -d target.com -w $SECLISTS_ROOT/Discovery/DNS/subdomains-top1million-5000.txt -t 50

# Vhost discovery
gobuster vhost -u https://target.com \
  -w $SECLISTS_ROOT/Discovery/DNS/subdomains-top1million-5000.txt \
  --append-domain -t 50

# API path enumeration
gobuster dir -u https://target.com/api \
  -w $SECLISTS_ROOT/Discovery/Web-Content/api/objects.txt \
  -t 50

# Follow redirects + ignore TLS errors
gobuster dir -u https://target.com -w wordlist.txt -t 50 -r -k

# Output to file
gobuster dir -u https://target.com -w wordlist.txt -o gobuster_out.txt
```

## SecLists paths

```
$SECLISTS_ROOT/Discovery/Web-Content/directory-list-2.3-medium.txt
$SECLISTS_ROOT/Discovery/Web-Content/raft-medium-words.txt
$SECLISTS_ROOT/Discovery/DNS/subdomains-top1million-5000.txt
$SECLISTS_ROOT/Passwords/Common-Credentials/10-million-password-list-top-10000.txt
$SECLISTS_ROOT/Usernames/Names/names.txt
```
