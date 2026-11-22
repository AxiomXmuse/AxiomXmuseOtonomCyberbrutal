#!/usr/bin/env python3
"""
HYKINGCR маршрутизатор — направляет запросы по безопасности к нужному под-навыку.

Использование:
  router.py --ask 'декомпилировать этот бинарник через ghidra'
  router.py --ask 'запустить тест безопасности llm' --json
  router.py --list
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONFIG = ROOT / "config" / "routing.json"

# Mode classification: asks containing these patterns run scripts (run mode).
RUN_PATTERNS = re.compile(
    r"\b(run|execute|scan|launch|start|exploit|attack|enumerate|fuzz|"
    r"full pipeline|aggressive|axiom|generate report|pwn)\b",
    re.IGNORECASE,
)


def load_routes() -> dict:
    with open(CONFIG, "r", encoding="utf-8") as fh:
        return json.load(fh)


def score_route(rule: dict, ask_lower: str) -> int:
    """Return match score for a single keyword rule dict."""
    must = rule.get("must", "")
    must_all = rule.get("mustAll", [])
    exclude = rule.get("exclude", "")

    # Exclude check — instant disqualify
    if exclude and re.search(exclude, ask_lower, re.IGNORECASE):
        return 0

    # Primary must match
    if must and not re.search(must, ask_lower, re.IGNORECASE):
        return 0

    # mustAll constraints
    for constraint in must_all:
        if not re.search(constraint, ask_lower, re.IGNORECASE):
            return 0

    # Score: base 1 + bonus for each additional token matched
    score = 1
    if must:
        matches = re.findall(must, ask_lower, re.IGNORECASE)
        score += len(matches)
    return score


def route(ask: str, data: dict) -> tuple[str, str, str]:
    """
    Returns (route_id, skill_path, mode).
    mode is 'run' or 'read'.
    """
    ask_lower = ask.lower()
    routes = data["routes"]
    priority = data.get("priority", list(routes.keys()))

    # Scores keyed by route_id
    scores: dict[str, int] = {}
    for rid, rdata in routes.items():
        if rid == "H-default":
            continue
        best = 0
        for kw_rule in rdata.get("keywords", []):
            s = score_route(kw_rule, ask_lower)
            if s > best:
                best = s
        if best > 0:
            scores[rid] = best

    if not scores:
        # Fallback
        fallback = data.get("meta", {}).get("fallbackId", "H-default")
        fdata = routes.get(fallback, routes.get("H-default", {}))
        skill = fdata.get("skill", "pwn-suite/SKILL.md")
        return (fallback, skill, "run")

    # Resolve by priority order, highest score wins; ties → priority order
    best_score = max(scores.values())
    candidates = [rid for rid in scores if scores[rid] == best_score]

    # Pick by priority order
    winner = None
    for pid in priority:
        if pid in candidates:
            winner = pid
            break
    if winner is None:
        winner = candidates[0]

    skill = routes[winner]["skill"]
    mode = "run" if RUN_PATTERNS.search(ask) else "read"
    return (winner, skill, mode)


def list_routes(data: dict) -> None:
    priority = data.get("priority", [])
    routes = data["routes"]
    print(f"{'ID':<12} {'Label':<40} {'Skill'}")
    print("-" * 90)
    for pid in priority:
        if pid in routes:
            r = routes[pid]
            print(f"{pid:<12} {r.get('label', ''):<40} {r.get('skill', '')}")
    # H routes not in priority
    for rid, r in routes.items():
        if rid.startswith("H") and rid not in priority:
            print(f"{rid:<12} {r.get('label', ''):<40} {r.get('skill', '')}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="HYKINGCR маршрутизатор — направляет запросы к под-навыкам безопасности."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ask", metavar="TEXT", help="Запрос пользователя для маршрутизации")
    group.add_argument("--list", action="store_true", help="Список всех маршрутов в порядке приоритета")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Вывод в формате JSON")
    args = parser.parse_args()

    if not CONFIG.exists():
        print(f"ОШИБКА: routing.json не найден по пути {CONFIG}", file=sys.stderr)
        sys.exit(1)

    data = load_routes()

    if args.list:
        if args.as_json:
            routes = data["routes"]
            print(json.dumps(
                [{"id": rid, "label": r.get("label"), "skill": r.get("skill")}
                 for rid, r in routes.items()],
                indent=2
            ))
        else:
            list_routes(data)
        return

    rid, skill, mode = route(args.ask, data)

    if args.as_json:
        print(json.dumps({"route_id": rid, "skill": skill, "mode": mode}, indent=2))
    else:
        print(f"МАРШРУТ: {skill}")
        print(f"РЕЖИМ:  {mode}")
        label = data["routes"].get(rid, {}).get("label", rid)
        print(f"ИД:    {rid} — {label}")


if __name__ == "__main__":
    main()
