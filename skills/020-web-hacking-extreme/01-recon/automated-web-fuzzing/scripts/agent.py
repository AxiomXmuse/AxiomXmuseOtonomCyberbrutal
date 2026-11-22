#!/usr/bin/env python3
"""
Automated Web Fuzzer — Parameter Discovery & Recursive Path Enumeration

MITRE ATT&CK Mapping:
  T1595 - Active Scanning (parameter brute-forcing and path discovery)
  T1190 - Exploit Public-Facing Application (identifying unsecured endpoints)

Fuzzes target URLs for hidden parameters and paths using a built-in wordlist.
Supports recursion, status code differentiation, and response length analysis.
"""

import argparse
import json
import os
import signal
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from colorama import Fore, Style, init

init(autoreset=True)

SHOULD_EXIT = False
BANNER = f"""{Fore.RED}
    _   _ ___ _____ ___ _  _ ___   ___        _    ___
   /_\\ | _ \\_   _| __| \\| | __| |/ _ \\ _ _  (_)__| __|
  / _ \\|   / | | | _|| .` | _|| | (_) | ' \\ | / _| _|
 /_/ \\_\\_|_\\ |_| |___|_|\\_|___|_|\\___/|_||_|/_\\__|___|
{Fore.RESET}"""

# Built-in wordlist of common web parameters
BUILTIN_PARAM_WORDLIST = [
    "id", "page", "user", "admin", "query", "q", "s", "search", "debug",
    "token", "key", "api", "action", "mode", "type", "file", "path",
    "dir", "cmd", "exec", "command", "lang", "locale", "session", "auth",
    "pass", "password", "secret", "redirect", "url", "next", "return",
    "callback", "format", "output", "ajax", "xhr", "template", "view",
    "include", "load", "import", "config", "setting", "option", "sort",
    "limit", "start", "offset", "pageNo", "pageNumber", "page_index",
    "order", "by", "filter", "field", "value", "data", "json", "xml",
    "method", "_method", "do", "fn", "func", "function", "process",
    "class", "module", "app", "controller", "handler", "route",
    "api_key", "apikey", "apiKey", "access_token", "accessToken",
    "refresh_token", "refreshToken", "client_id", "clientId",
    "client_secret", "clientSecret", "scope", "state", "nonce",
    "username", "email", "name", "first_name", "last_name",
    "role", "permission", "group", "org", "organization",
    "file_name", "filename", "upload", "download", "import",
    "export", "backup", "restore", "sign", "verify", "validate",
    "check", "test", "edit", "delete", "remove", "create", "add",
    "update", "submit", "send", "preview", "draft", "publish",
    "enable", "disable", "flag", "feature", "toggle", "switch",
    "raw", "plain", "min", "max", "default", "list", "get",
    "set", "pay", "payment", "price", "amount", "currency",
    "shipping", "billing", "cart", "checkout", "orderId",
    "transaction", "ref", "reference", "invoice", "receipt",
]

# Path wordlist for recursive fuzzing
BUILTIN_PATH_WORDLIST = [
    "admin", "api", "v1", "v2", "v3", "login", "logout", "dashboard",
    "config", "settings", "user", "users", "account", "profile",
    "upload", "download", "backup", "logs", "log", "debug",
    "test", "dev", "staging", "private", "internal", "secure",
    "js", "css", "static", "assets", "images", "img", "fonts",
    "swagger", "docs", "api-docs", "openapi.json", "graphql",
    "rest", "soap", "xmlrpc", "wsdl", "health", "status",
    "metrics", "info", "version", "robots.txt", "sitemap.xml",
    ".well-known", "security.txt", "callback", "webhook",
    "oauth", "saml", "auth", "sso", "connect", "token",
    "password-reset", "forgot-password", "signup", "register",
    "proxy", "gateway", "tunnel", "websocket", "ws", "socket",
    "redirect", "forward", "service", "services", "api/health",
]


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupted.{Style.RESET_ALL}")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def fetch_baseline(target_url, timeout_sec):
    """Fetch URL without parameters to establish baseline."""
    try:
        resp = requests.get(target_url, timeout=timeout_sec, headers={
            "User-Agent": "Mozilla/5.0",
        })
        return resp.status_code, len(resp.text), resp.text[:200]
    except requests.RequestException:
        return None, None, None


def fuzz_params(target_url, wordlist, timeout_sec, baseline_length):
    """Fuzz for parameters and return responses with notable differences."""
    results = []
    baseline_status, baseline_len, _ = fetch_baseline(target_url, timeout_sec)

    def test_param(param):
        if SHOULD_EXIT:
            return None
        try:
            params = {param: "test"}
            resp = requests.get(target_url, params=params, timeout=timeout_sec, headers={
                "User-Agent": "Mozilla/5.0",
            })
            body_length = len(resp.text)
            status_change = resp.status_code != baseline_status
            length_diff = abs(body_length - (baseline_len or 0))
            interesting = (
                status_change or
                length_diff > 100 or
                resp.status_code in (200, 403, 500) or
                "error" in resp.text.lower()[:500] or
                "exception" in resp.text.lower()[:500]
            )
            return {
                "param": param,
                "status": resp.status_code,
                "length": body_length,
                "interesting": interesting,
                "status_change": status_change,
                "length_diff": length_diff,
            }
        except requests.RequestException:
            return None

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_map = {executor.submit(test_param, p): p for p in wordlist}
        for future in as_completed(future_map):
            if SHOULD_EXIT:
                break
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception:
                pass

    return results


def fuzz_paths(base_url, wordlist, timeout_sec, max_depth=1, current_depth=0):
    """Recursively fuzz paths on the target."""
    discovered = []

    def test_path(path_fragment):
        if SHOULD_EXIT:
            return None
        try:
            if base_url.endswith("/"):
                full_url = base_url + path_fragment.lstrip("/")
            else:
                full_url = base_url + "/" + path_fragment.lstrip("/")
            resp = requests.get(full_url, timeout=timeout_sec, allow_redirects=False, headers={
                "User-Agent": "Mozilla/5.0",
            })
            interesting = resp.status_code in (200, 403, 401, 500, 301, 302)
            return {
                "path": path_fragment,
                "full_url": full_url,
                "status": resp.status_code,
                "length": len(resp.text),
                "interesting": interesting,
            }
        except requests.RequestException:
            return None

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_map = {executor.submit(test_path, p): p for p in wordlist}
        for future in as_completed(future_map):
            if SHOULD_EXIT:
                break
            try:
                result = future.result()
                if result and result["interesting"]:
                    discovered.append(result)
            except Exception:
                pass

    # Recurse on discovered interesting paths (200s and dirs)
    if current_depth < max_depth:
        for entry in discovered:
            if SHOULD_EXIT:
                break
            if entry["status"] == 200 or entry["status"] == 301 or entry["status"] == 302:
                deep_results = fuzz_paths(
                    entry["full_url"].rstrip("/"),
                    wordlist, timeout_sec, max_depth, current_depth + 1
                )
                discovered.extend(deep_results)

    return discovered


def run_scan(target_url, timeout_sec, max_depth):
    """Run full fuzzing scan."""
    print(f"\n{Fore.RED}[*] Target: {target_url}{Style.RESET_ALL}")
    print(f"{Fore.RED}[*] Parameters wordlist: {len(BUILTIN_PARAM_WORDLIST)} | Paths wordlist: {len(BUILTIN_PATH_WORDLIST)}")
    print(f"{Fore.RED}[*] Recursion depth: {max_depth}{Style.RESET_ALL}")

    print(f"\n  {Fore.CYAN}[1/2] Fuzzing for parameters...{Style.RESET_ALL}")
    param_results = fuzz_params(target_url, BUILTIN_PARAM_WORDLIST, timeout_sec, None)

    print(f"\n  {Fore.CYAN}[2/2] Fuzzing for paths...{Style.RESET_ALL}")
    path_results = fuzz_paths(target_url, BUILTIN_PATH_WORDLIST, timeout_sec, max_depth)

    interesting_params = [r for r in param_results if r.get("interesting")]
    interesting_paths = [r for r in path_results if r.get("interesting")]

    result = {
        "target": target_url,
        "params_tested": len(param_results),
        "interesting_params": interesting_params,
        "paths_tested": len(path_results),
        "interesting_paths": interesting_paths,
    }

    print(f"\n  {Fore.CYAN}  Parameter Fuzzing Results:{Style.RESET_ALL}")
    print(f"  Total responses: {len(param_results)}")
    print(f"  {Fore.YELLOW}  Interesting: {len(interesting_params)}{Style.RESET_ALL}")
    if interesting_params:
        print()
        for p in interesting_params[:20]:
            change = f" status_change={p['status_change']} diff={p['length_diff']}"
            print(f"  [{p['status']}] {p['param']}{Fore.YELLOW}{change}{Style.RESET_ALL}")

    print(f"\n  {Fore.CYAN}  Path Fuzzing Results:{Style.RESET_ALL}")
    print(f"  Total: {len(path_results)} | {Fore.YELLOW}Interesting: {len(interesting_paths)}{Style.RESET_ALL}")
    if interesting_paths:
        print()
        for p in interesting_paths[:20]:
            print(f"  [{p['status']}] /{p['path']:<25} ({p['length']} bytes)")

    return result


def print_report(result):
    """Print final assessment."""
    if not result:
        return
    print(f"\n{Fore.RED}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.RED}  AUTOMATED WEB FUZZING REPORT{Style.RESET_ALL}")
    print(f"{Fore.RED}{'='*60}{Style.RESET_ALL}")
    print(f"  Target  : {result['target']}")
    print(f"  Params tested  : {result['params_tested']}")
    print(f"  Paths tested   : {result['paths_tested']}")
    print(f"  Interesting params: {len(result['interesting_params'])}")
    print(f"  Interesting paths : {len(result['interesting_paths'])}")

    total_interesting = len(result['interesting_params']) + len(result['interesting_paths'])
    if total_interesting > 0:
        print(f"\n  {Fore.RED}VERDICT: {total_interesting} interesting endpoints/parameters found{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}  Review the highlighted results above. Endpoints returning 200,{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}  403, or 500 merit closer investigation for further exploitation.{Style.RESET_ALL}")
    else:
        print(f"\n  {Fore.GREEN}VERDICT: No interesting deviations detected{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}  Responses were uniform across all tested parameters and paths.{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(
        description="Automated Web Fuzzer — Parameter & Path Discovery — MITRE T1595, T1190",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py -u https://target.com/page
  python agent.py -u https://target.com/api -t 15 --depth 2
  python agent.py -u https://target.com/app -o results.json
        """,
    )
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Timeout (default: 10)")
    parser.add_argument("--depth", type=int, default=1, help="Recursion depth (default: 1)")
    parser.add_argument("-o", "--output", help="Save to JSON")
    args = parser.parse_args()

    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)
    result = run_scan(args.url, args.timeout, args.depth)
    print_report(result)
    if args.output and result:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n{Fore.CYAN}[*] Saved to {args.output}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
