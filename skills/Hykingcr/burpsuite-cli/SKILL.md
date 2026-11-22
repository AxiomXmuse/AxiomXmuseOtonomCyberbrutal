---
name: burpsuite-cli
description: "Burp Suite Community — прокси-перехватчик веб-трафика, сканер, repeater, intruder для ручного тестирования веб-приложений. Расположен: $BURP_ROOT."
allowed-tools: Bash(java *), Read
---

# burpsuite-cli

Install: `$BURP_ROOT/`

## Launch

```bash
# Standard GUI launch
$BURP_ROOT/BurpSuiteCommunity &

# With custom JVM heap
java -Xmx4g -jar $BURP_ROOT/burpsuite_community.jar &
```

## Proxy setup

- Proxy listener: `127.0.0.1:8080` (default)
- CA cert: navigate to `http://burpsuite` in browser while proxy running → download CA cert → install in browser
- CLI tool proxy: `--proxy http://127.0.0.1:8080` for curl, httpx, nuclei, sqlmap, etc.

## Key workflows

```bash
# Pipe any tool through Burp for inspection
curl -x http://127.0.0.1:8080 -k https://target.com/api/endpoint

# sqlmap through Burp
sqlmap -u USER:PASS --proxy http://127.0.0.1:8080

# nuclei through Burp
nuclei -u https://target.com -proxy http://127.0.0.1:8080

# httpx through Burp
httpx -u https://target.com -http-proxy http://127.0.0.1:8080
```

## Intruder (manual)

- Sniper: single injection point, one payload list
- Battering Ram: same payload everywhere
- Pitchfork: parallel payload lists (credential stuffing)
- Cluster Bomb: all combinations of multiple lists

## Bambda filters (Proxy history)

```java
// Flag requests with interesting params
return requestResponse.request().hasParameter("redirect", HttpParameterType.URL)
    || requestResponse.request().hasParameter("url", HttpParameterType.URL)
    || requestResponse.request().hasParameter("next", HttpParameterType.URL);
```
