---
name: hashcat-cli
description: "Hashcat — анализ стойкости криптографических дайджестов с GPU-ускорением: словарные, перебором, комбинаторные атаки. Бинарный файл: /usr/bin/hashcat."
allowed-tools: Bash(hashcat *), Read
---

# hashcat-cli

Binary: `/usr/bin/hashcat`
Wordlists: `$SECLISTS_ROOT/Passwords/` · `/usr/share/wordlists/rockyou.txt`

## Common hash modes

| Mode | Hash type |
|---|---|
| 0 | MD5 |
| 100 | SHA1 |
| 1000 | NTLM |
| 1800 | sha512crypt (Linux shadow) |
| 2500 | WPA-PBKDF2-PMKID+EAPOL |
| 5600 | NetNTLMv2 |
| 13100 | Kerberoast (TGS-REP) |
| 18200 | AS-REP Roast |
| 22000 | WPA-PBKDF2-PMKID |

## Key invocations

```bash
# Dictionary attack (mode 0 = straight)
hashcat -m 1000 hashes.txt /usr/share/wordlists/rockyou.txt

# Rule-based
hashcat -m 1000 hashes.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule

# Brute force mask (?l=lower, ?u=upper, ?d=digit, ?s=special)
hashcat -m 1000 hashes.txt -a 3 ?u?l?l?l?d?d?d?s

# Combinator (two wordlists)
hashcat -m 1000 hashes.txt -a 1 wordlist1.txt wordlist2.txt

# Show cracked
hashcat -m 1000 hashes.txt --show

# Kerberoast tickets
hashcat -m 13100 tickets.txt /usr/share/wordlists/rockyou.txt

# AS-REP roast
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt

# NetNTLMv2 (Responder capture)
hashcat -m 5600 ntlmv2.txt /usr/share/wordlists/rockyou.txt
```
