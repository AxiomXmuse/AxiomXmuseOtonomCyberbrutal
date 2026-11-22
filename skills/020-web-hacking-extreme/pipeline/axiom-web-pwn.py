#!/usr/bin/env python3
"""
AXIOM WEB PWN — Automated Web Hacking Pipeline
================================================
Scan → Detect → Exploit → Pivot → PWN

MITRE ATT&CK:
  T1595  - Active Scanning
  T1190  - Exploit Public-Facing Application
  T1059  - Command and Scripting Interpreter
  T1210  - Exploitation of Remote Services
  T1068  - Exploitation for Privilege Escalation
  T1574  - Hijack Execution Flow (chain)

Usage:
  python axiom-web-pwn.py -t https://target.com
  python axiom-web-pwn.py -t https://target.com --aggressive --output /tmp/report
  python axiom-web-pwn.py -t https://target.com --cookie "session=abc123" --proxy http://127.0.0.1:8080
"""

import os, sys, json, time, argparse, signal, logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Add pipeline to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.recon import ReconEngine
from modules.detector import DetectionEngine
from modules.exploiter import ExploitEngine
from modules.reporter import ReportEngine

VERSION = "2.0.0"
BANNER = f"""
╔══════════════════════════════════════════════════════╗
║             AXIOM WEB PWN v{VERSION}                    ║
║     Automated Web Hacking Pipeline — SCAN → PWN      ║
╚══════════════════════════════════════════════════════╝
"""

class WebPwnPipeline:
    """Orchestrates the full web hacking pipeline."""

    PHASES = [
        "recon",
        "detection",
        "waf-bypass",
        "exploitation",
        "chain",
        "pivot",
        "report"
    ]

    def __init__(self, target: str, output_dir: str = None,
                 aggressive: bool = False, cookie: str = None,
                 proxy: str = None, wordlist: str = None,
                 threads: int = 10, timeout: int = 10):
        self.target = target.rstrip("/")
        self.aggressive = aggressive
        self.cookie = cookie
        self.proxy = proxy
        self.wordlist = wordlist or os.path.join(
            os.path.dirname(__file__), "..", "01-recon",
            "automated-web-fuzzing", "wordlists", "common.txt"
        )
        self.threads = threads
        self.timeout = timeout
        self.start_time = time.time()

        # Output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = target.replace("https://", "").replace("http://", "").replace("/", "_")
        self.output_dir = output_dir or f"reports/{safe_name}_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/evidence", exist_ok=True)

        # State
        self.findings = {}
        self.vulnerabilities = []
        self.exploits = []
        self.breach_level = 0
        self.running = True

        # Signal handler
        signal.signal(signal.SIGINT, self._handle_interrupt)

        # Logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler(f"{self.output_dir}/pipeline.log"),
                logging.StreamHandler()
            ]
        )
        self.log = logging.getLogger("WebPwn")

    def _handle_interrupt(self, sig, frame):
        self.log.warning("\n[!] Interrupt received — saving state and exiting...")
        self.running = False
        self._save_checkpoint()

    def _save_checkpoint(self):
        checkpoint = {
            "target": self.target,
            "phase": self.current_phase if hasattr(self, 'current_phase') else "unknown",
            "breach_level": self.breach_level,
            "vulns_found": len(self.vulnerabilities),
            "exploits_run": len(self.exploits),
            "elapsed": round(time.time() - self.start_time, 2)
        }
        with open(f"{self.output_dir}/checkpoint.json", "w") as f:
            json.dump(checkpoint, f, indent=2)

    def run(self):
        """Execute the full pipeline."""
        print(BANNER)
        self.log.info(f"Target: {self.target}")
        self.log.info(f"Output: {self.output_dir}")
        self.log.info(f"Aggressive: {self.aggressive}")
        self.log.info("-" * 50)

        # Phase 1: Reconnaissance
        if self.running:
            self.current_phase = "recon"
            self.log.info("[PHASE 1/7] RECONNAISSANCE")
            recon = ReconEngine(self.target, self.output_dir,
                                self.cookie, self.proxy, self.threads, self.timeout)
            self.findings = recon.run()
            self._save_checkpoint()

        # Phase 2: Vulnerability Detection
        if self.running and self.findings.get("alive"):
            self.current_phase = "detection"
            self.log.info("[PHASE 2/7] VULNERABILITY DETECTION")
            detector = DetectionEngine(self.target, self.output_dir,
                                       self.findings, self.aggressive,
                                       self.cookie, self.proxy, self.timeout)
            self.vulnerabilities = detector.run()
            self._save_checkpoint()

        # Phase 3: WAF Bypass (if WAF detected)
        if self.running and self._check_waf():
            self.current_phase = "waf-bypass"
            self.log.info("[PHASE 3/7] WAF BYPASS")
            self._run_waf_bypass()

        # Phase 4: Exploitation
        if self.running and self.vulnerabilities:
            self.current_phase = "exploitation"
            self.log.info("[PHASE 4/7] EXPLOITATION")
            exploiter = ExploitEngine(self.target, self.output_dir,
                                      self.vulnerabilities, self.cookie,
                                      self.proxy, self.timeout)
            self.exploits = exploiter.run()
            self.breach_level = max([e.get("level", 0) for e in self.exploits], default=0)
            self._save_checkpoint()

        # Phase 5: Exploit Chaining
        if self.running and self.breach_level >= 2 and self.aggressive:
            self.current_phase = "chain"
            self.log.info("[PHASE 5/7] EXPLOIT CHAINING")
            self._run_chain()

        # Phase 6: Pivot deeper
        if self.running and self.breach_level >= 3 and self.aggressive:
            self.current_phase = "pivot"
            self.log.info("[PHASE 6/7] PIVOT & PERSIST")
            self._run_pivot()

        # Phase 7: Report
        self.current_phase = "report"
        self.log.info("[PHASE 7/7] REPORT")
        reporter = ReportEngine(self.target, self.output_dir,
                                self.findings, self.vulnerabilities,
                                self.exploits, self.breach_level)
        report_path = reporter.run()
        self._save_checkpoint()

        elapsed = round(time.time() - self.start_time, 2)
        self.log.info("=" * 50)
        self.log.info(f"PIPELINE COMPLETE in {elapsed}s")
        self.log.info(f"Target: {self.target}")
        self.log.info(f"Vulnerabilities: {len(self.vulnerabilities)}")
        self.log.info(f"Exploits executed: {len(self.exploits)}")
        self.log.info(f"Breach level: {self.breach_level}/5")
        self.log.info(f"Report: {report_path}")
        self.log.info("=" * 50)

        return {
            "target": self.target,
            "elapsed": elapsed,
            "vulns": len(self.vulnerabilities),
            "exploits": len(self.exploits),
            "breach_level": self.breach_level,
            "report": report_path
        }

    def _check_waf(self) -> bool:
        """Check if a WAF was detected during recon."""
        for f in self.findings.get("technologies", []):
            name = f.get("name", "").lower()
            if any(w in name for w in ["waf", "cloudflare", "akamai",
                                         "aws waf", "imperva", "modsecurity",
                                         "barracuda", "f5", "fortinet"]):
                self.log.info(f"WAF detected: {name}")
                return True
        return False

    def _run_waf_bypass(self):
        """Attempt WAF bypass techniques."""
        waf_skills = os.path.join(os.path.dirname(__file__), "..", "02-waf-bypass")
        for skill in ["cloudflare-waf-bypass", "akamai-waf-bypass", "aws-waf-bypass"]:
            script = os.path.join(waf_skills, skill, "scripts", "agent.py")
            if os.path.exists(script):
                cmd = f"python \"{script}\" -t \"{self.target}\" -o \"{self.output_dir}/waf-bypass-{skill}.json\""
                if self.cookie:
                    cmd += f" --cookie \"{self.cookie}\""
                self.log.info(f"  → Running {skill}...")
                os.system(cmd)

    def _run_chain(self):
        """Chain multiple exploits for deeper compromise."""
        chain_script = os.path.join(
            os.path.dirname(__file__), "..", "06-automation",
            "exploit-chain-automation", "scripts", "agent.py"
        )
        if os.path.exists(chain_script):
            vulns_json = json.dumps([v.get("type") for v in self.vulnerabilities])
            cmd = (
                f"python \"{chain_script}\" -t \"{self.target}\" "
                f"--vulns '{vulns_json}' -o \"{self.output_dir}/chain-results.json\""
            )
            if self.cookie:
                cmd += f" --cookie \"{self.cookie}\""
            self.log.info("  → Running exploit chain...")
            os.system(cmd)

    def _run_pivot(self):
        """Pivot deeper into the target infrastructure."""
        ssrf_script = os.path.join(
            os.path.dirname(__file__), "..", "03-exploit",
            "ssrf-tunnel", "scripts", "agent.py"
        )
        if os.path.exists(ssrf_script):
            cmd = (
                f"python \"{ssrf_script}\" -t \"{self.target}\" "
                f"-o \"{self.output_dir}/pivot-ssrf.json\" --deep"
            )
            self.log.info("  → Running SSRF pivot...")
            os.system(cmd)

    def status(self) -> Dict:
        """Return current pipeline status."""
        return {
            "target": self.target,
            "phase": getattr(self, 'current_phase', 'not_started'),
            "vulns": len(self.vulnerabilities),
            "exploits": len(self.exploits),
            "breach_level": self.breach_level,
            "elapsed": round(time.time() - self.start_time, 2),
            "running": self.running
        }


def main():
    parser = argparse.ArgumentParser(
        description="AXIOM WEB PWN — Automated Web Hacking Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -t https://target.com
  %(prog)s -t https://target.com --aggressive --output /tmp/audit
  %(prog)s -t https://target.com --cookie "session=abc" --proxy http://127.0.0.1:8080
        """
    )
    parser.add_argument("-t", "--target", required=True, help="Target URL")
    parser.add_argument("-o", "--output", help="Output directory")
    parser.add_argument("--aggressive", action="store_true",
                       help="Enable aggressive mode (chaining, pivot)")
    parser.add_argument("--cookie", help="Session cookie")
    parser.add_argument("--proxy", help="Proxy (e.g. http://127.0.0.1:8080)")
    parser.add_argument("--wordlist", help="Custom wordlist path")
    parser.add_argument("--threads", type=int, default=10, help="Thread count")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout")
    parser.add_argument("--version", action="version", version=f"AXIOM Web Pwn v{VERSION}")

    args = parser.parse_args()

    pipeline = WebPwnPipeline(
        target=args.target,
        output_dir=args.output,
        aggressive=args.aggressive,
        cookie=args.cookie,
        proxy=args.proxy,
        wordlist=args.wordlist,
        threads=args.threads,
        timeout=args.timeout
    )

    result = pipeline.run()

    # Exit code based on breach level
    if result["breach_level"] >= 3:
        sys.exit(0)  # PWNED
    elif result["breach_level"] >= 1:
        sys.exit(1)  # Partial
    else:
        sys.exit(2)  # No breach


if __name__ == "__main__":
    main()
