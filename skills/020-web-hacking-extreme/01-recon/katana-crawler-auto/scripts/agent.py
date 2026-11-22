#!/usr/bin/env python3
"""
katana-crawler-auto agent.py
MITRE ATT&CK: T1595 (Active Scanning)
Automates katana headless crawler with JS parsing and smart crawling logic.
"""
import argparse
import json
import os
import re
import signal
import subprocess
from urllib.parse import urlparse, urljoin
import requests
from colorama import Fore, Style, init
init(autoreset=True)
SHOULD_EXIT = False

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
SKIP_EXTS = {".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2", ".ttf", ".eot"}


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupt received. Shutting down...{Style.RESET_ALL}")


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def build_katana_command(target, options=None):
    cmd = ["katana", "-u", target, "-jsonl"]
    if not options:
        return cmd
    if options.get("headless"):
        cmd.append("-headless")
    if options.get("depth"):
        cmd.extend(["-depth", str(options["depth"])])
    if options.get("js_crawl"):
        cmd.append("-jc")
    if options.get("known_files"):
        cmd.append("-kf")
    if options.get("scope"):
        cmd.extend(["-scope", options["scope"]])
    if options.get("delay"):
        cmd.extend(["-delay", str(options["delay"])])
    if options.get("rate_limit"):
        cmd.extend(["-rl", str(options["rate_limit"])])
    if options.get("timeout"):
        cmd.extend(["-timeout", str(options["timeout"])])
    if options.get("proxy"):
        cmd.extend(["-proxy", options["proxy"]])
    if options.get("concurrency"):
        cmd.extend(["-c", str(options["concurrency"])])
    if options.get("passive"):
        cmd.append("-passive")
    if options.get("no_subdomains"):
        cmd.append("-nfs")
    return cmd


def extract_js_endpoints(body, base_url):
    endpoints = set()
    patterns = [
        r'["\'](/[a-zA-Z0-9_\-./?&=]+)["\']',
        r'fetch\(["\'](/[a-zA-Z0-9_\-./?&=]+)["\']',
        r'axios\.(?:get|post|put|delete)\(["\'](/[a-zA-Z0-9_\-./?&=]+)["\']',
        r'apiUrl\s*[+:=]\s*["\'](/[a-zA-Z0-9_\-./?&=]+)["\']',
        r'endpoint\s*:\s*["\'](/[a-zA-Z0-9_\-./?&=]+)["\']',
        r'route\s*:\s*["\'](/[a-zA-Z0-9_\-./?&=]+)["\']',
    ]
    for pat in patterns:
        for m in re.finditer(pat, body):
            path = m.group(1)
            if not any(path.endswith(e) for e in SKIP_EXTS):
                endpoints.add(urljoin(base_url, path))
    return endpoints


def run_katana(cmd):
    results = []
    try:
        print(f"{Fore.CYAN}[*] Running katana{Style.RESET_ALL}")
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        target = cmd[2] if len(cmd) > 2 else "unknown"
        for line in (proc.stdout + proc.stderr).strip().splitlines():
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                entry["_target"] = target
                results.append(entry)
            except json.JSONDecodeError:
                results.append({"url": line.strip(), "_target": target, "_raw": True})
        if proc.returncode != 0 and not results:
            for line in (proc.stdout + proc.stderr).splitlines():
                if "error" in line.lower():
                    print(f"{Fore.YELLOW}[!] {line}{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.YELLOW}[!] katana not found. Simulating crawl.{Style.RESET_ALL}")
        target = cmd[2] if len(cmd) > 2 else "http://localhost/"
        results = simulate_crawl(target, cmd)
    except subprocess.TimeoutExpired:
        print(f"{Fore.RED}[!] katana timed out after 300s{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
    return results


def simulate_crawl(target, cmd):
    results = []
    try:
        depth = 3
        for i, a in enumerate(cmd):
            if a == "-depth" and i + 1 < len(cmd):
                depth = int(cmd[i + 1])
        print(f"{Fore.YELLOW}[*] Simulating crawl (depth={depth}){Style.RESET_ALL}")
        visited = set()
        to_visit = {target}
        curr_depth = 0
        while to_visit and curr_depth <= depth and not SHOULD_EXIT:
            next_batch = set()
            for url in to_visit:
                if SHOULD_EXIT or url in visited:
                    continue
                visited.add(url)
                try:
                    resp = requests.get(url, timeout=10, verify=False, headers={"User-Agent": USER_AGENT})
                    results.append({"url": url, "status": resp.status_code, "content-length": len(resp.text), "content-type": resp.headers.get("Content-Type", ""), "_target": target})
                    if resp.status_code == 200 and curr_depth < depth:
                        links = re.findall(r'href=["\']([^"\']+)["\']', resp.text)
                        js_eps = extract_js_endpoints(resp.text, url)
                        for link in list(links) + list(js_eps):
                            absolute = urljoin(url, link)
                            if target.rstrip("/") in absolute:
                                next_batch.add(absolute.split("#")[0])
                except requests.exceptions.RequestException:
                    continue
            to_visit = next_batch
            curr_depth += 1
        print(f"{Fore.GREEN}[+] Crawled {len(visited)} URLs at depth {curr_depth - 1}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Simulation error: {e}{Style.RESET_ALL}")
    return results


def display_results(results, target):
    if not results:
        print(f"\n{Fore.YELLOW}[*] No crawl results for {target}{Style.RESET_ALL}")
        return
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   KATANA CRAWL RESULTS -- {target}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    status_count = {}
    api_endpoints = []
    for r in results:
        url = r.get("url", "")
        status = r.get("status", 0)
        status_count[status] = status_count.get(status, 0) + 1
        parsed = urlparse(url)
        if "/api/" in parsed.path or "/v1/" in parsed.path or "/graphql" in parsed.path:
            api_endpoints.append(url)
    print(f"\n{Fore.GREEN}[+] Total URLs found: {len(results)}{Style.RESET_ALL}")
    for code in sorted(status_count.keys()):
        color = Fore.GREEN if code < 400 else (Fore.YELLOW if code < 500 else Fore.RED)
        print(f"  {color}{code}{Style.RESET_ALL}: {status_count[code]}")
    if api_endpoints:
        print(f"\n{Fore.MAGENTA}[!] API Endpoints ({len(api_endpoints)}):{Style.RESET_ALL}")
        for ep in api_endpoints[:10]:
            print(f"  {Fore.MAGENTA}{ep}{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description="katana-crawler-auto -- headless crawler automation")
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("--headless", action="store_true", help="Headless browser mode")
    parser.add_argument("--depth", type=int, default=3, help="Crawl depth")
    parser.add_argument("--js-crawl", action="store_true", help="Enable JS file crawling")
    parser.add_argument("--known-files", action="store_true", help="Check known files")
    parser.add_argument("--scope", choices=["strict", "subdomain", "fp"], default="subdomain", help="Crawl scope")
    parser.add_argument("--delay", type=int, default=0, help="Delay between requests (ms)")
    parser.add_argument("--rate-limit", type=int, default=100, help="Rate limit per minute")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout (s)")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent requests")
    parser.add_argument("--passive", action="store_true", help="Passive mode")
    parser.add_argument("--no-subdomains", action="store_true", help="Filter out subdomains")
    parser.add_argument("--proxy", help="Proxy URL")
    args = parser.parse_args()
    target = args.url if args.url.startswith("http") else f"https://{args.url}"
    opts = {"headless": args.headless, "depth": args.depth, "js_crawl": args.js_crawl, "known_files": args.known_files, "scope": args.scope, "delay": args.delay, "rate_limit": args.rate_limit, "timeout": args.timeout, "concurrency": args.concurrency, "passive": args.passive, "no_subdomains": args.no_subdomains, "proxy": args.proxy}
    cmd = build_katana_command(target, opts)
    print(f"{Fore.CYAN}[*] Starting crawl of {target}{Style.RESET_ALL}")
    results = run_katana(cmd)
    display_results(results, target)


if __name__ == "__main__":
    main()
