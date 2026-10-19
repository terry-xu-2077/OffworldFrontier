#!/usr/bin/env python3
"""Small repository guard against obsolete plot mandates and vague screenplay jargon.

Run: python scripts/check_canon.py
Uses only the Python standard library. This is a tripwire, not a substitute for editorial review.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
CANON_DIRS = (ROOT / "创作", ROOT / "设定")
SCREENPLAY_DIR = ROOT / "创作" / "剧本"
ALLOW = "<!-- audit-allow:"
IMAGE_LINK = re.compile(r"\[[^\]]+\]\(([^)]+?\.(?:png|jpe?g|webp))\)", re.I)

GLOBAL_RULES = (
    ("旧电影场次/顺序被写回设定", re.compile(
        r"旧稿正典|旧稿开场|旧稿第[一二三四五六七八九十0-9]+场|"
        r"电影第[一二三四五六七八九十0-9]+场|电影尾声|"
        r"开场阶段.{0,35}(?:不得|不能|必须)|"
        r"第[0-9]+[-—～][0-9]+集"
    )),
    ("旧式人力重载矿车", re.compile(
        r"手推矿车|推矿车回电梯|"
        r"矿工(?:沿轨道|双手|徒手|一路|长距离)?推着?(?:装满|满载|沉重)?矿车|"
        r"背着(?:整袋|满袋)?矿石(?:出井|升井)"
    )),
    ("机械翻字牌回归", re.compile(
        r"机械翻牌自行跳动|机械翻牌一格一格|"
        r"机械牌不停翻动"
    )),
    ("马克纸账被错误禁止", re.compile(r"马克.{0,14}不使用纸面记账")),
)

# These words may appear in glossary examples and formal documentation;
# they are hard errors only inside current episode narrative text.
EPISODE_JARGON = re.compile(
    r"交易重量|补重量|交易窗口|换货缺口|交易矿|补矿|"
    r"工分出不了账|旧权限留痕|终端唤醒|旧系统醒了|"
    r"机械翻牌|货运预留|船位担保|责任主体"
)


def main() -> int:
    documents = sorted(
        path for folder in CANON_DIRS
        for path in folder.rglob("*.md")
        if path.is_file()
    )
    errors: list[str] = []
    unresolved_images: list[str] = []
    for doc in documents:
        rel = doc.relative_to(ROOT).as_posix()
        text = doc.read_text(encoding="utf-8-sig")
        is_episode = (SCREENPLAY_DIR in doc.parents and
                      re.match(r"^(?:0[1-9]|[1-9][0-9])_", doc.name) is not None)
        for no, line in enumerate(text.splitlines(), 1):
            if ALLOW in line:
                continue
            for label, pattern in GLOBAL_RULES:
                if pattern.search(line):
                    errors.append(f"{rel}:{no}: {label}: {line.strip()[:110]}")
            if is_episode and EPISODE_JARGON.search(line):
                errors.append(f"{rel}:{no}: 具体剧情使用了含糊简称: {line.strip()[:110]}")
            for link in IMAGE_LINK.finditer(line):
                target = unquote(link.group(1).split("#", 1)[0])
                if "://" in target or target.startswith("/"):
                    continue
                if not (doc.parent / target).resolve().is_file():
                    unresolved_images.append(f"{rel}:{no}: {target}")

    if errors:
        print(f"FAIL — {len(errors)} creative-continuity issue(s) detected:")
        for message in errors:
            print("  " + message)
    else:
        print(f"PASS — scanned {len(documents)} Markdown files; no known regression patterns.")
    if unresolved_images:
        print(f"WARN — {len(unresolved_images)} relative image reference(s) do not exist in this checkout.")
        print("       Do not claim those images were inspected; use written canon or obtain the assets.")
        for message in unresolved_images[:8]:
            print("  " + message)
        if len(unresolved_images) > 8:
            print(f"  ... plus {len(unresolved_images) - 8} more")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
