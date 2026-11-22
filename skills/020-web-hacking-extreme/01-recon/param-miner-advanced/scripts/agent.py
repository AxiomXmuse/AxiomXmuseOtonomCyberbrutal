#!/usr/bin/env python3
"""
param-miner-advanced agent.py
MITRE ATT&CK: T1595 (Active Scanning), T1190 (Exploit Public-Facing Application)
Advanced parameter mining tool replicating Burp Param Miner logic for hidden parameter discovery.
"""
import argparse
import concurrent.futures
import json
import os
import signal
from datetime import datetime
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
import requests
from colorama import Fore, Style, init
init(autoreset=True)
SHOULD_EXIT = False

COMMON_PARAMS = [
    "id", "page", "file", "path", "doc", "debug", "test", "cmd", "exec",
    "action", "token", "session", "auth", "key", "api_key", "secret",
    "redirect", "return", "next", "url", "link", "user_id",
    "cat", "category", "type", "mode", "lang", "locale", "format",
    "callback", "jsonp", "include", "template", "view", "layout",
    "sort", "order", "limit", "offset", "q", "query", "search", "term",
    "name", "title", "desc", "description", "content", "body", "text",
    "email", "phone", "address", "uid", "gid", "ref",
    "source", "src", "host", "port", "server", "domain",
    "method", "_method", "do", "func", "f", "cmd", "command",
    "data", "input", "output", "upload", "download",
    "admin", "root", "sudo", "config", "setting", "option",
    "r", "route", "class", "func", "function", "module",
    "error", "err", "msg", "message", "status", "state", "step",
]

POLLUTION_PARAMS = ["__proto__", "constructor[prototype]", "prototype"]


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupt received. Shutting down gracefully...{Style.RESET_ALL}")


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def test_parameter(base_url, param, value="x"):
    parsed = urlparse(base_url)
    params = parse_qs(parsed.query)
    new_params = params.copy()
    new_params[param] = [value]
    url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(new_params, doseq=True), parsed.fragment))
    result = {"param": param, "url": url, "status": None, "length": 0, "reflected": False, "param_reflected": False}
    try:
        resp = requests.get(url, timeout=8, verify=False, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
        result["status"] = resp.status_code
        result["length"] = len(resp.text)
        if value.lower() in resp.text.lower():
            result["reflected"] = True
        if param.lower() in resp.text.lower():
            result["param_reflected"] = True
    except requests.exceptions.RequestException:
        result["error"] = "request_failed"
    return result


def mine_parameters(target, threads=10):
    print(f"{Fore.CYAN}[*] Mining {len(COMMON_PARAMS)} parameters against {target}{Style.RESET_ALL}")
    found = []
    completed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(test_parameter, target, p): p for p in COMMON_PARAMS}
        for future in concurrent.futures.as_completed(futures):
            if SHOULD_EXIT:
                break
            completed += 1
            param = futures[future]
            try:
                result = future.result()
                if result.get("reflected") or result.get("param_reflected"):
                    found.append(result)
                    flags = []
                    if result.get("reflected"):
                        flags.append(f"{Fore.MAGENTA}REFLECTED{Style.RESET_ALL}")
                    if result.get("param_reflected"):
                        flags.append(f"{Fore.CYAN}PARAM{Style.RESET_ALL}")
                    flag_str = " [" + " | ".join(flags) + "]" if flags else ""
                    print(f"  [{completed}/{len(COMMON_PARAMS)}] {Fore.GREEN}[+]{Style.RESET_ALL} {param}{flag_str}")
                elif completed % 30 == 0:
                    print(f"  [{completed}/{len(COMMON_PARAMS)}] scanning...")
            except Exception:
                continue
    return found


def test_pollution(target):
    results = []
    print(f"{Fore.YELLOW}[*] Testing parameter pollution...{Style.RESET_ALL}")
    parsed = urlparse(target)
    params = parse_qs(parsed.query)
    for pp in POLLUTION_PARAMS:
        if SHOULD_EXIT:
            break
        test_params = params.copy()
        test_params[pp] = ["test"]
        url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(test_params, doseq=True), parsed.fragment))
        try:
            resp = requests.get(url, timeout=8, verify=False, headers={"User-Agent": "Mozilla/5.0"})
            if "test" in resp.text.lower() or pp.lower() in resp.text.lower():
                results.append({"param": pp, "type": "prototype_pollution", "reflected": True})
                print(f"  {Fore.MAGENTA}[!] Prototype pollution candidate: {pp}{Style.RESET_ALL}")
        except requests.exceptions.RequestException:
            continue
    print(f"{Fore.YELLOW}[*] Testing HTTP parameter pollution (duplicate params)...{Style.RESET_ALL}")
    existing_params = list(params.keys())
    for pn in existing_params[:10]:
        if SHOULD_EXIT:
            break
        test_params = params.copy()
        test_params[pn] = ["legit", "polluted"]
        url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(test_params, doseq=True), parsed.fragment))
        try:
            resp = requests.get(url, timeout=8, verify=False, headers={"User-Agent": "Mozilla/5.0"})
            if "polluted" in resp.text.lower():
                results.append({"param": pn, "type": "hpp", "reflected": True})
                print(f"  {Fore.YELLOW}[!] HPP on {pn}: duplicate value reflected{Style.RESET_ALL}")
        except requests.exceptions.RequestException:
            continue
    return results


def display_results(found, pollution):
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   PARAM MINER RESULTS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    if found:
        print(f"\n{Fore.GREEN}[+] Discovered {len(found)} hidden parameter(s):{Style.RESET_ALL}")
        for f in sorted(found, key=lambda x: x["param"]):
            param = f["param"]
            flags = []
            if f.get("reflected"):
                flags.append("REFLECTED")
            if f.get("param_reflected"):
                flags.append("PARAM-REFLECTED")
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} {param:<25} [{f.get('status', '?')}]{flag_str}")
    else:
        print(f"\n{Fore.YELLOW}[*] No hidden parameters found{Style.RESET_ALL}")
    if pollution:
        print(f"\n{Fore.YELLOW}[!] Pollution findings ({len(pollution)}):{Style.RESET_ALL}")
        for p in pollution:
            print(f"  {Fore.YELLOW}[!]{Style.RESET_ALL} {p['param']} ({p['type']})")
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[+] Hidden params: {len(found)}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[!] Pollution candidates: {len(pollution)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description="param-miner-advanced -- hidden parameter discovery tool")
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Thread count")
    parser.add_argument("--no-pollution", action="store_true", help="Skip pollution tests")
    parser.add_argument("--timeout", type=int, default=8, help="Request timeout")
    parser.add_argument("-o", "--output", help="Output results to JSON file")
    args = parser.parse_args()
    target = args.url if args.url.startswith("http") else f"https://{args.url}"
    requests.DEFAULT_TIMEOUT = (args.timeout, args.timeout)
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   PARAM MINER ADVANCED -- {target}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    found = mine_parameters(target, args.threads)
    if SHOULD_EXIT:
        return
    pollution = []
    if not args.no_pollution:
        pollution = test_pollution(target)
    display_results(found, pollution)
    if args.output:
        with open(args.output, "w") as f:
            json.dump({"target": target, "ts": datetime.now().isoformat(), "params_found": found, "pollution": pollution}, f, indent=2)
        print(f"{Fore.GREEN}[+] Results saved to {args.output}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
