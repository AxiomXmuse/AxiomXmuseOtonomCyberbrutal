---
name: hydra-cli
description: "Hydra — параллельная верификация учётных данных для SSH, FTP, HTTP, SMB, RDP, SMTP, MySQL и 50+ протоколов. Бинарный файл: /usr/bin/hydra."
allowed-tools: Bash(hydra *), Read
---

# hydra-cli

Binary: `/usr/bin/hydra`
Wordlists: `$SECLISTS_ROOT/Passwords/` · `/usr/share/wordlists/rockyou.txt`
User lists: `$SECLISTS_ROOT/Usernames/`

## Key invocations

```bash
# SSH brute force (single user)
hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://<target>

# SSH user list + password list
hydra -L users.txt -P passwords.txt ssh://<target>

# FTP
hydra -l user -P pass.txt ftp://<target>

# HTTP POST form
hydra -l admin -P pass.txt <target> http-post-form "/login:user=^USER^&pass=^PASS^:Invalid"

# HTTP Basic auth
hydra -l admin -P pass.txt http-get://<target>/admin

# SMB
hydra -l admin -P pass.txt smb://<target>

# RDP
hydra -l admin -P pass.txt rdp://<target>

# MySQL
hydra -l root -P pass.txt mysql://<target>

# Throttle (avoid lockout)
hydra -l admin -P pass.txt -t 4 -W 3 ssh://<target>

# Stop on first valid
hydra -l admin -P pass.txt -f ssh://<target>
```
