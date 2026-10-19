#!/usr/bin/env python3
"""Small bounded Markdown retriever for OffworldFrontier canon.

route QUERY -> a few relevant source paths
headings PATH -> section names and line numbers
read PATH SECTION -> section excerpt (default 3600 chars)
search QUERY -> short excerpts; excludes proposal scripts by default
check -> validate the index
Examples:
  python scripts/canon_lookup.py route "特瑞 矿车 失联"
  python scripts/canon_lookup.py headings "设定/世界设定/03_地下矿道与采矿流程.md"
  python scripts/canon_lookup.py read "设定/世界设定/03_地下矿道与采矿流程.md" "采矿机与下矿流程"
  python scripts/canon_lookup.py search "能量匣"
  python scripts/canon_lookup.py search "特瑞" --scope proposals
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "设定" / "速查索引.md"
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
MAX_CHARS = 9000
MAX_ROUTE_RESULTS = 8
MAX_HEADINGS = 60
MAX_SEARCH_RESULTS = 12
MAX_PER_FILE = 3
MAX_LINE_CHARS = 240


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def routes_from_index() -> list[dict]:
    result = []
    for line in INDEX.read_text(encoding="utf-8-sig").splitlines():
        if not line.startswith("|") or not line.endswith("|"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) != 3 or parts[0] in ("主题", "---"):
            continue
        match = LINK.search(parts[2])
        if not match:
            continue
        path = (INDEX.parent / unquote(match.group(2))).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError("Index contains an out-of-repository path")
        result.append({"topic": parts[0], "keys": parts[1].split(), "path": path})
    return result


def safe_path(raw: str) -> Path:
    path = (ROOT / raw).resolve()
    if not path.is_relative_to(ROOT) or path.suffix.lower() != ".md":
        raise ValueError("Read expects a Markdown path inside the repository")
    if not path.is_file():
        raise FileNotFoundError(raw)
    return path


def route_score(item: dict, phrase: str) -> tuple[int, list[str]]:
    phrase = re.sub(r"\s+", "", phrase.casefold())
    matched = [key for key in item["keys"] if key.casefold() in phrase]
    score = sum(3 + min(len(key), 4) for key in matched)
    if item["topic"].replace(" ", "").casefold() in phrase:
        score += 9
    if item["path"].stem.casefold() in phrase:
        score += 11
    return score, matched


def route_command(args, routes: list[dict]) -> int:
    matches = [(route_score(item, args.query), item) for item in routes]
    matches = [(r, item) for r, item in matches if r[0]]
    matches.sort(key=lambda x: (-x[0][0], x[1]["topic"]))
    if not matches:
        print("No indexed topic matched. Use a shorter term or the search command.")
        return 1
    for (score, found), item in matches[:max(1, min(args.limit, MAX_ROUTE_RESULTS))]:
        print(f"[{item['topic']}] {relative(item['path'])}")
        print(f"  keyword matches: {', '.join(found) or 'topic/title'}")
    print("Next: headings PATH, then read PATH SECTION; do not load every candidate.")
    return 0


def get_headings(path: Path):
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    heads = []
    for i, line in enumerate(lines):
        match = HEADING.match(line)
        if match:
            heads.append((i, len(match.group(1)), match.group(2)))
    return lines, heads


def headings_command(args) -> int:
    path = safe_path(args.path)
    _, headings = get_headings(path)
    print("FILE", relative(path))
    for no, level, title in headings[:max(1, min(args.limit, MAX_HEADINGS))]:
        print(f"L{no + 1:>4} {'  ' * (level - 1)}{title}")
    if len(headings) > max(1, min(args.limit, MAX_HEADINGS)):
        print(f"... {len(headings) - max(1, min(args.limit, MAX_HEADINGS))} more headings")
    return 0


def read_command(args) -> int:
    path = safe_path(args.path)
    lines, headings = get_headings(path)
    needle = re.sub(r"\s+", "", args.section).casefold()
    exact = [x for x in headings if re.sub(r"\s+", "", x[2]).casefold() == needle]
    matches = exact or [x for x in headings
                        if needle in re.sub(r"\s+", "", x[2]).casefold()]
    if not matches:
        print("No matching section. Call headings PATH first.")
        return 1
    if len(matches) > 1:
        print("Ambiguous section; choose a more precise heading:")
        for no, _, title in matches[:12]:
            print(f" L{no + 1} {title}")
        return 1
    start, depth, title = matches[0]
    end = next((no for no, level, _ in headings
                if no > start and level <= depth), len(lines))
    data = "\n".join(f"L{i + 1} {lines[i]}" for i in range(start, end))
    limit = min(max(args.max_chars, 300), MAX_CHARS)
    print(f"FILE {relative(path)} | SECTION {title} | L{start + 1}-L{end}")
    print(data[:limit])
    if len(data) > limit:
        print(f"... truncated {len(data) - limit} chars; choose a narrower subsection")
    return 0


def search_sources(scope: str):
    canon = sorted(p for p in (ROOT / "设定").rglob("*.md") if p != INDEX)
    canon.append(ROOT / "创作" / "创作方向.md")
    drafts = sorted((ROOT / "创作" / "剧本").rglob("*.md"))
    drafts += [ROOT / "创作" / "人物关系与冲突.md",
               ROOT / "创作" / "人物生活事件实验库.md",
               ROOT / "创作" / "灵感池.md",
               ROOT / "创作" / "灵感记录_早期原文.md"]
    return canon if scope == "canon" else drafts if scope == "proposals" else canon + drafts


def search_command(args, routes) -> int:
    needle = args.query.strip().casefold()
    if not needle:
        return 1
    map_routes = {item["path"]: item for item in routes}
    ranked = []
    for path in search_sources(args.scope):
        if not path.is_file():
            continue
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        hits = [(n + 1, line.strip()) for n, line in enumerate(lines)
                if needle in line.casefold()]
        if hits:
            route = map_routes.get(path)
            score = route_score(route, needle)[0] if route else 0
            score += 12 if needle in path.name.casefold() else 0
            ranked.append((score, len(hits), path, hits))
    ranked.sort(key=lambda x: (-x[0], -min(x[1], 15), relative(x[2])))
    count = 0
    for _, _, path, hits in ranked:
        for line_no, line in hits[:max(1, min(args.per_file, MAX_PER_FILE))]:
            if count >= max(1, min(args.limit, MAX_SEARCH_RESULTS)):
                break
            print(f"{relative(path)}:L{line_no} {line[:max(50, min(args.line_chars, MAX_LINE_CHARS))]}")
            count += 1
        if count >= max(1, min(args.limit, MAX_SEARCH_RESULTS)):
            break
    if not count:
        print("No matching excerpt in this scope; try a synonym or --scope proposals.")
        return 1
    print(f"{count} short excerpts ({args.scope}). Read only relevant source sections.")
    return 0


def check_command(routes) -> int:
    errors = []
    seen = set()
    for item in routes:
        path = item["path"]
        if path in seen:
            errors.append(f"Duplicate index source: {relative(path)}")
        seen.add(path)
        if not path.is_file():
            errors.append(f"Missing source: {relative(path)}")
    if not routes:
        errors.append("No index routes were parsed")
    if errors:
        print("\n".join("ERROR: " + issue for issue in errors))
        return 1
    print(f"PASS: {len(routes)} topic routes, all source paths exist.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("route")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=4)
    p = sub.add_parser("headings")
    p.add_argument("path")
    p.add_argument("--limit", type=int, default=45)
    p = sub.add_parser("read")
    p.add_argument("path")
    p.add_argument("section")
    p.add_argument("--max-chars", type=int, default=3600)
    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--scope", choices=("canon", "proposals", "all"), default="canon")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--per-file", type=int, default=2)
    p.add_argument("--line-chars", type=int, default=180)
    sub.add_parser("check")
    args = parser.parse_args()
    try:
        routes = routes_from_index()
        if args.action == "route":
            return route_command(args, routes)
        if args.action == "headings":
            return headings_command(args)
        if args.action == "read":
            return read_command(args)
        if args.action == "search":
            return search_command(args, routes)
        return check_command(routes)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
