#!/usr/bin/env python3
"""
httpx-smart-recon agent.py
MITRE ATT&CK: T1595 (Active Scanning)
Smart reconnaissance tool probing URLs with httpx for tech detection and probing.
"""
import argparse
import json
import os
import re
import signal
import subprocess
import tempfile
from urllib.parse import urlparse
import requests
from colorama import Fore, Style, init
init(autoreset=True)
SHOULD_EXIT = False

TECH_PATTERNS = {
    "nginx": ["Server: nginx"],
    "apache": ["Server: Apache"],
    "cloudflare": ["CF-RAY", "Server: cloudflare"],
    "iis": ["Server: Microsoft-IIS"],
    "express": ["X-Powered-By: Express"],
    "python": ["Server: Python", "Server: gunicorn"],
    "ruby": ["Server: Phusion", "X-Runtime"],
    "java": ["Server: Apache-Coyote"],
    "wordpress": ["wp-content", "wp-admin"],
    "drupal": ["Drupal"],
    "react": ["react", "react-dom"],
    "vue": ["vue.js"],
    "angular": ["ng-app"],
    "laravel": ["laravel_session"],
}


def signal_handler(sig, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print(f"\n{Fore.YELLOW}[!] Interrupt received. Shutting down...{Style.RESET_ALL}")


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def build_httpx_command(targets, options=None):
    cmd = ["httpx", "-json"]
    if len(targets) == 1:
        cmd.extend(["-u", targets[0]])
    else:
        fd, tmp_path = tempfile.mkstemp(suffix=".txt", prefix="httpx_")
        with os.fdopen(fd, "w") as f:
            f.write("\n".join(targets))
        cmd.extend(["-l", tmp_path])
    if options:
        if options.get("status_code"):
            cmd.append("-sc")
        if options.get("title"):
            cmd.append("-title")
        if options.get("tech_detect"):
            cmd.append("-td")
        if options.get("follow_redirect"):
            cmd.append("-fr")
        if options.get("method"):
            cmd.extend(["-x", options["method"]])
        if options.get("threads"):
            cmd.extend(["-t", str(options["threads"])])
        if options.get("rate_limit"):
            cmd.extend(["-rl", str(options["rate_limit"])])
        if options.get("timeout"):
            cmd.extend(["-timeout", str(options["timeout"])])
        if options.get("proxy"):
            cmd.extend(["-proxy", options["proxy"]])
        if options.get("response_time"):
            cmd.append("-rt")
        if options.get("cdn"):
            cmd.append("-cdn")
        if options.get("ip"):
            cmd.append("-ip")
    return cmd


def detect_technologies(headers, body):
    detected = []
    for name, indicators in TECH_PATTERNS.items():
        for indicator in indicators:
            if ":" in indicator:
                key, val = indicator.split(":", 1)
                header_val = headers.get(key.strip().lower(), "").lower()
                if val.strip().lower() in header_val:
                    detected.append(name)
                    break
            else:
                if indicator.lower() in body.lower():
                    detected.append(name)
                    break
    return sorted(set(detected))


def run_httpx(cmd):
    results = []
    try:
        print(f"{Fore.CYAN}[*] Running httpx probe{Style.RESET_ALL}")
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        output = proc.stdout + proc.stderr
        for line in output.strip().splitlines():
            if not line.strip():
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        if proc.returncode != 0 and not results:
            for line in output.splitlines():
                if "error" in line.lower():
                    print(f"{Fore.YELLOW}[!] {line}{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.YELLOW}[!] httpx not found. Simulating.{Style.RESET_ALL}")
        results = simulate_httpx(cmd)
    except subprocess.TimeoutExpired:
        print(f"{Fore.RED}[!] httpx timed out after 180s{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
    return results


def simulate_httpx(cmd):
    results = []
    try:
        targets = [cmd[i+1] for i, a in enumerate(cmd) if a == "-u" and i + 1 < len(cmd)]
        for t in targets:
            if SHOULD_EXIT:
                break
            t = t if t.startswith("http") else f"https://{t}"
            print(f"{Fore.YELLOW}[*] Probing {t}{Style.RESET_ALL}")
            try:
                resp = requests.get(t, timeout=10, verify=False, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
                headers_lower = {k.lower(): v for k, v in resp.headers.items()}
                techs = detect_technologies(headers_lower, resp.text)
                title_match = re.search(r'<title[^>]*>([^<]+)</title>', resp.text, re.I)
                title = title_match.group(1).strip()[:80] if title_match else ""
                result = {"url": t, "host": urlparse(t).netloc, "scheme": urlparse(t).scheme, "status_code": resp.status_code, "content_length": len(resp.text), "content_type": resp.headers.get("Content-Type", ""), "title": title, "technologies": techs, "response_time": round(resp.elapsed.total_seconds() * 1000, 2)}
                results.append(result)
                print(f"  {Fore.GREEN}[{resp.status_code}]{Style.RESET_ALL} {len(resp.text)}b {Fore.CYAN}{title[:50]}{Style.RESET_ALL}")
                if techs:
                    print(f"    Tech: {', '.join(techs)}")
            except requests.exceptions.RequestException as e:
                print(f"  {Fore.RED}[!] {e}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Simulation error: {e}{Style.RESET_ALL}")
    return results


def display_results(results):
    if not results:
        print(f"\n{Fore.YELLOW}[*] No results{Style.RESET_ALL}")
        return
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   HTTPX RECON RESULTS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    tech_counts = {}
    for r in results:
        for t in r.get("technologies", []):
            tech_counts[t] = tech_counts.get(t, 0) + 1
    for r in results:
        sc = Fore.GREEN if r.get("status_code", 0) < 400 else (Fore.YELLOW if r.get("status_code", 0) < 500 else Fore.RED)
        print(f"  {r.get('url', '')[:38]:<40} {sc}{r.get('status_code', 0):<8}{Style.RESET_ALL} {r.get('content_length', 0):<10} {Fore.CYAN}{r.get('title', '')[:28]:<30}{Style.RESET_ALL}")
    if tech_counts:
        print(f"\n{Fore.CYAN}Technology Distribution:{Style.RESET_ALL}")
        for tech, count in sorted(tech_counts.items(), key=lambda x: -x[1]):
            print(f"  {Fore.WHITE}{tech}{Style.RESET_ALL}: {count} hosts")
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[+] Total hosts: {len(results)} | Technologies: {len(tech_counts)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description="httpx-smart-recon -- tech detection and probing")
    parser.add_argument("-u", "--url", help="Target URL")
    parser.add_argument("-l", "--list", help="File containing URLs")
    parser.add_argument("--method", help="HTTP method override (e.g. HEAD, POST)")
    parser.add_argument("--follow-redirect", action="store_true", help="Follow redirects")
    parser.add_argument("--threads", type=int, default=10, help="Concurrency threads")
    parser.add_argument("--rate-limit", type=int, default=150, help="Rate limit per minute")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout")
    parser.add_argument("--proxy", help="Proxy URL")
    parser.add_argument("--cdn", action="store_true", help="Check if behind CDN")
    parser.add_argument("--ip", action="store_true", help="Show IP address")
    args = parser.parse_args()
    if not args.url and not args.list:
        parser.print_help()
        return
    targets = []
    if args.url:
        targets.append(args.url if args.url.startswith("http") else f"https://{args.url}")
    if args.list:
        try:
            with open(args.list, "r") as f:
                targets.extend([l.strip() for l in f if l.strip()])
        except FileNotFoundError:
            print(f"{Fore.RED}[!] File not found: {args.list}{Style.RESET_ALL}")
            return
    opts = {"status_code": True, "title": True, "tech_detect": True, "method": args.method, "follow_redirect": args.follow_redirect, "threads": args.threads, "rate_limit": args.rate_limit, "timeout": args.timeout, "proxy": args.proxy, "cdn": args.cdn, "ip": args.ip}
    cmd = build_httpx_command(targets, opts)
    print(f"{Fore.CYAN}[*] Recon on {len(targets)} target(s){Style.RESET_ALL}")
    results = run_httpx(cmd)
    display_results(results)


if __name__ == "__main__":
    main()
