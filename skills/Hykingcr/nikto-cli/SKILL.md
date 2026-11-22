---
name: nikto-cli
description: "Nikto — аудит конфигурации веб-сервера: устаревшее ПО, опасные файлы, ошибки настройки, известные CVE. Бинарный файл: /usr/bin/nikto."
allowed-tools: Bash(nikto *), Read
---

# nikto-cli

Binary: `/usr/bin/nikto`

## Key invocations

```bash
# Basic scan
nikto -h https://target.com

# With proxy (through Burp)
nikto -h https://target.com -useproxy http://127.0.0.1:8080

# Specific port
nikto -h target.com -p 8443 -ssl

# Scan multiple hosts
nikto -h hosts.txt

# Output to file
nikto -h https://target.com -o nikto_out.html -Format html

# Tuning (1=interesting, 2=misconfig, 3=info disclosure, 4=injection, 8=upload, 9=sql)
nikto -h https://target.com -Tuning 3489

# Skip specific checks
nikto -h https://target.com -Tuning x3

# With authentication
nikto -h https://target.com -id admin:password

# Mutate (append files to directory)
nikto -h https://target.com -mutate 5
```
