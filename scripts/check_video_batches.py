#!/usr/bin/env python3
"""Structural validator for Offworld Frontier video-prompt Markdown.

Run from the repository root:
  python scripts/check_video_batches.py
  python scripts/check_video_batches.py "创作/视频提示词/第一季/01_异星拾荒_Seedance2.5.md"
  python scripts/check_video_batches.py --format html --output report.html

This checks explicit production-document contracts, not creative quality or shot style.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIR = ROOT / "创作" / "视频提示词"

BATCH_RE = re.compile(r"^\s{0,3}#{1,6}\s*\[?批次\s*0*(\d+)\]?(.*)$")
BRACKET_BATCH_RE = re.compile(r"^\s*\[批次\s*0*(\d+)\]\s*$")
SECTION_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")
FENCE_RE = re.compile(r"^\s*(\x60{3,}|~{3,})")
PROMPT_RE = re.compile(r"^\s*<Prompt\s+([^<>]+)>([:：])(.*)$")
ASSET_RE = re.compile(r"^\s*<(Picture|Audio|Video)\s+([^<>]+)>([:：])(.*)$")
SHOT_RE = re.compile(
    r"^\s*镜头\s*([0-9A-Za-z]+)\s*[｜|]\s*"
    r"\[\s*(\d+(?:\.\d+)?)\s*(?:–|—|-|~|～|至)\s*"
    r"(\d+(?:\.\d+)?)\s*s\s*\]"
)
DURATION_RE = re.compile(r"建议(?:生成时长)?\s*[:：]?\s*(\d+(?:\.\d+)?)\s*(?:秒|s)", re.I)
ASSET_COLUMNS = {"全局参考", "全局资产"}
W_COLUMNS = ("导演说明", "全局参考", "连续性状态", "视觉基调", "色彩光影", "分镜脚本")
SHOT_FIELDS = {
    "景别 / 焦段": re.compile(r"^\s*(?:\*\*)?景别\s*/\s*焦段\s*[:：]\s*(.*)$"),
    "运镜 / 视角": re.compile(r"^\s*(?:\*\*)?运镜\s*/\s*视角\s*[:：]\s*(.*)$"),
    "画面描述": re.compile(r"^\s*(?:\*\*)?画面描述\s*[:：]\s*(.*)$"),
    "声音 / Foley": re.compile(r"^\s*(?:\*\*)?声音\s*/\s*Foley\s*[:：]\s*(.*)$", re.I),
}
H3_BASE = ("integrated_multimodal_description", "overall_soundscape", "non_diegetic_music")
H3_REF2VA = ("subject_definitions", "summary", "retention_analysis", "detailed_description",
             "overall_soundscape", "non_diegetic_music")
H3_FIELD_RE = re.compile(
    r"^\s*(subject_definitions|summary|retention_analysis|detailed_description|"
    r"integrated_multimodal_description|overall_soundscape|non_diegetic_music)\s*:", re.M)
H3_SHOT_RE = re.compile(r"\[Shot\s+(\d+)\](?:\s+At\s+(\d{2}:\d{2}\.\d{3}),)?")


@dataclass
class Issue:
    level: str
    code: str
    file: str
    line: int
    message: str
    batch: str = ""

    def as_dict(self):
        return asdict(self)


@dataclass
class Batch:
    number: int
    title: str
    start: int
    end: int
    sections: list[tuple[str, int, int]]


def add(issues, level, code, file, index, message, batch=""):
    issues.append(Issue(level, code, file, index + 1, message, batch))


def mask_fences(lines):
    """Hide fenced examples from Markdown structure parsing; preserve line numbers."""
    result, marker, size = [], "", 0
    for line in lines:
        match = FENCE_RE.match(line)
        if not marker and match:
            marker, size = match.group(1)[0], len(match.group(1))
            result.append("")
        elif marker:
            if line.lstrip().startswith(marker * size):
                marker, size = "", 0
            result.append("")
        else:
            result.append(line)
    return result


def code_blocks(lines, start, end):
    blocks, marker, size, opening, current = [], "", 0, 0, []
    for i in range(start, end):
        match = FENCE_RE.match(lines[i])
        if not marker:
            if match:
                marker, size, opening, current = match.group(1)[0], len(match.group(1)), i, []
        elif lines[i].lstrip().startswith(marker * size):
            blocks.append((opening, current))
            marker, size, current = "", 0, []
        else:
            current.append(lines[i])
    if marker:
        blocks.append((opening, current))
    return blocks


def parse_batches(masked):
    starts = []
    for i, line in enumerate(masked):
        match = BATCH_RE.match(line)
        bracket = BRACKET_BATCH_RE.match(line)
        if match:
            starts.append((i, int(match.group(1)), match.group(2).strip()))
        elif bracket:
            starts.append((i, int(bracket.group(1)), ""))
    batches = []
    for pos, (start, number, title) in enumerate(starts):
        end = starts[pos + 1][0] if pos + 1 < len(starts) else len(masked)
        headers = [(m.group(1).strip(), i) for i in range(start + 1, end)
                   if (m := SECTION_RE.match(masked[i]))]
        sections = []
        for n, (name, sec_start) in enumerate(headers):
            sec_end = headers[n + 1][1] if n + 1 < len(headers) else end
            sections.append((name, sec_start, sec_end))
        batches.append(Batch(number, title, start, end, sections))
    return batches


def sections(batch, name):
    return [(a, b) for n, a, b in batch.sections if n == name]


def expected_duration(title):
    match = DURATION_RE.search(title)
    return float(match.group(1)) if match else None


def validate_assets(masked, batch, file, issues):
    seen = set()
    label = f"批次{batch.number:02d}"
    pictures = set()
    for name in ASSET_COLUMNS:
        for start, end in sections(batch, name):
            for i in range(start + 1, end):
                line = masked[i]
                if not line.strip():
                    continue
                if "<Prompt" in line:
                    add(issues, "error", "prompt-in-batch", file, i,
                        "<Prompt> 只能放在文档开头唯一的 [待生成资产] 区域。", label)
                if not re.match(r"^\s*<(?:Picture|Audio|Video)\b", line):
                    continue
                match = ASSET_RE.match(line)
                if not match:
                    add(issues, "error", "asset-tag-syntax", file, i,
                        "资产标签格式错误；应为 <Picture 名称>：用途描述（Audio / Video 同理）。", label)
                    continue
                kind, raw_name, colon, description = match.groups()
                alias = raw_name.strip()
                if not alias:
                    add(issues, "error", "empty-asset-alias", file, i, "资产别名不能为空。", label)
                if colon != "：":
                    add(issues, "error", "asset-colon", file, i, "资产标签必须使用中文冒号“：”。", label)
                if not description.strip():
                    add(issues, "error", "empty-asset-description", file, i,
                        f"<{kind} {alias}> 缺少用途描述。", label)
                if alias.isdigit():
                    add(issues, "error", "numeric-asset-alias", file, i,
                        f"资产别名“{alias}”不能是纯数字；纯数字标签保留给 H3 官方编号。", label)
                if "/" in alias or "\\" in alias or re.search(r"\.(png|jpe?g|webp|mp4|mov|wav|mp3)$", alias, re.I):
                    add(issues, "error", "path-like-asset-alias", file, i,
                        f"资产别名“{alias}”看起来像文件名或路径，应使用稳定语义名称。", label)
                key = (kind, alias)
                if key in seen:
                    add(issues, "warning", "duplicate-asset-reference", file, i,
                        f"同一批次重复声明 <{kind} {alias}>；确认是否有意重复。", label)
                seen.add(key)
                if kind == "Picture":
                    pictures.add(alias)
    return pictures


def validate_shots(lines, section, batch, file, issues):
    start, end = section
    shots = []
    for i in range(start + 1, end):
        match = SHOT_RE.match(lines[i])
        if match:
            shots.append((i, match.group(1), float(match.group(2)), float(match.group(3))))
    label = f"批次{batch.number:02d}"
    if not shots:
        add(issues, "error", "no-shots", file, start,
            "[分镜脚本] 中没有识别到“镜头编号｜[起止秒]”格式。", label)
        return

    seen, previous_end = set(), None
    tolerance = 0.011
    if abs(shots[0][2]) > tolerance:
        add(issues, "error", "timecode-not-zero", file, shots[0][0],
            f"批次内时码应从 0 秒开始，当前第一镜从 {shots[0][2]:g}s 开始。", label)

    for pos, (i, shot_id, begin, finish) in enumerate(shots):
        if shot_id in seen:
            add(issues, "error", "duplicate-shot-id", file, i, f"镜头编号 {shot_id} 在本批次重复。", label)
        seen.add(shot_id)
        if finish <= begin:
            add(issues, "error", "invalid-shot-duration", file, i, f"镜头{shot_id} 的结束时码必须大于开始时码。", label)
        if previous_end is not None:
            delta = begin - previous_end
            if delta > tolerance:
                add(issues, "error", "timecode-gap", file, i,
                    f"镜头{shot_id} 与上一镜之间有 {delta:.3f}s 空档。", label)
            elif delta < -tolerance:
                add(issues, "error", "timecode-overlap", file, i,
                    f"镜头{shot_id} 与上一镜重叠 {-delta:.3f}s。", label)
        previous_end = finish

        next_i = shots[pos + 1][0] if pos + 1 < len(shots) else end
        block = lines[i + 1:next_i]
        if not lines[i].endswith("  "):
            add(issues, "warning", "missing-hard-break", file, i,
                f"镜头{shot_id} 标题行末尾缺少 Markdown 硬换行的两个空格。", label)
        for field, pattern in SHOT_FIELDS.items():
            matches = [(line, match) for line in block if (match := pattern.match(line))]
            if not matches:
                add(issues, "error", "missing-shot-field", file, i,
                    f"镜头{shot_id} 缺少“{field}”字段。", label)
                continue
            if not any(match.group(1).strip() for _, match in matches):
                add(issues, "error", "empty-shot-field", file, i,
                    f"镜头{shot_id} 的“{field}”内容为空。", label)
            for line, _ in matches:
                if not line.endswith("  "):
                    add(issues, "warning", "missing-hard-break", file, i,
                        f"镜头{shot_id} 的“{field}”行末尾缺少 Markdown 硬换行的两个空格。", label)

    target = expected_duration(batch.title)
    if target is not None and abs(shots[-1][3] - target) > tolerance:
        add(issues, "error", "batch-duration-mismatch", file, shots[-1][0],
            f"批次标题建议时长为 {target:g}s，但分镜时码结束于 {shots[-1][3]:g}s；请同步标题或时码。", label)


def validate_h3(lines, batch, file, issues):
    label = f"批次{batch.number:02d}"
    for opening, block in code_blocks(lines, batch.start, batch.end):
        content = "\n".join(block)
        names = [m.group(1) for m in H3_FIELD_RE.finditer(content)]
        if not names:
            continue
        ref2va = any(n in H3_REF2VA[:4] for n in names)
        required = H3_REF2VA if ref2va else H3_BASE
        for field in required:
            if names.count(field) == 0:
                add(issues, "error", "h3-missing-field", file, opening, f"H3 官方提示词缺少字段“{field}”。", label)
            elif names.count(field) > 1:
                add(issues, "error", "h3-duplicate-field", file, opening, f"H3 官方提示词字段“{field}”重复。", label)
        order = [required.index(n) for n in names if n in required]
        if order != sorted(order):
            add(issues, "error", "h3-field-order", file, opening, "H3 官方字段顺序不正确。", label)

        description_field = "detailed_description" if ref2va else "integrated_multimodal_description"
        field_start = re.search(rf"(?m)^\s*{description_field}\s*:\s*", content)
        if not field_start:
            continue
        next_field = H3_FIELD_RE.search(content, field_start.end())
        description = content[field_start.end():next_field.start() if next_field else len(content)]
        shot_marks = list(H3_SHOT_RE.finditer(description))
        if not shot_marks:
            add(issues, "error", "h3-no-shots", file, opening,
                f"H3 的 {description_field} 中没有识别到 [Shot 1]。", label)
            continue
        previous_time, expected_number = None, 1
        target = expected_duration(batch.title)
        for mark in shot_marks:
            number, stamp = int(mark.group(1)), mark.group(2)
            if number != expected_number:
                add(issues, "error", "h3-shot-sequence", file, opening,
                    f"H3 镜头编号应连续；预期 Shot {expected_number}，实际为 Shot {number}。", label)
            if expected_number == 1 and stamp:
                add(issues, "error", "h3-first-shot-timecode", file, opening,
                    "H3 第一镜 [Shot 1] 不应添加切点时间码。", label)
            if expected_number > 1 and not stamp:
                add(issues, "error", "h3-missing-cut-timecode", file, opening,
                    f"H3 [Shot {number}] 缺少 At MM:SS.mmm 切点时间码。", label)
            if stamp:
                minute, second = stamp.split(":")
                current = int(minute) * 60 + float(second)
                if previous_time is not None and current <= previous_time:
                    add(issues, "error", "h3-timecode-order", file, opening,
                        f"H3 [Shot {number}] 的切点时间码没有严格递增。", label)
                if target is not None and current >= target:
                    add(issues, "error", "h3-timecode-out-of-range", file, opening,
                        f"H3 [Shot {number}] 的切点时间码 {stamp} 已到达或超过批次建议时长 {target:g}s。", label)
                previous_time = current
            expected_number += 1


def validate_document(text, file="<memory>"):
    lines = text.splitlines()
    masked = mask_fences(lines)
    issues = []
    batches = parse_batches(masked)
    prompt_sections = [i for i, line in enumerate(masked)
                       if (m := SECTION_RE.match(line)) and m.group(1).strip() == "待生成资产"]
    if len(prompt_sections) > 1:
        add(issues, "error", "duplicate-prompt-section", file, prompt_sections[1],
            "整份 MD 只能有一个 [待生成资产] 区域。")

    prompts, picture_names = {}, set()
    first_batch = batches[0].start if batches else len(lines)
    if prompt_sections:
        start = prompt_sections[0]
        if start > first_batch:
            add(issues, "error", "prompt-section-position", file, start,
                "[待生成资产] 必须位于第一批次之前。")
        end = next((i for i in range(start + 1, len(masked))
                    if SECTION_RE.match(masked[i]) or BATCH_RE.match(masked[i]) or BRACKET_BATCH_RE.match(masked[i])),
                   len(masked))
        current, body = None, []
        def finish():
            nonlocal current, body
            if current is None:
                return
            name, source = current
            if not any(x.strip() for x in body):
                add(issues, "error", "empty-prompt", file, source, f"<Prompt {name}> 缺少生图提示词正文。")
            if name in prompts:
                add(issues, "error", "duplicate-prompt-name", file, source, f"<Prompt {name}> 在文档中重复定义。")
            else:
                prompts[name] = source
            current, body = None, []
        for i in range(start + 1, end):
            line = masked[i]
            if not line.strip():
                if current:
                    body.append(line)
                continue
            if "<Prompt" in line:
                finish()
                match = PROMPT_RE.match(line)
                if not match:
                    add(issues, "error", "prompt-tag-syntax", file, i,
                        "Prompt 定义格式错误；应为 <Prompt 名称>：完整生图提示词。")
                    continue
                name, colon, first_text = match.groups()
                name = name.strip()
                if colon != "：":
                    add(issues, "error", "prompt-colon", file, i, f"<Prompt {name}> 后必须使用中文冒号“：”。")
                if not name or name.isdigit():
                    add(issues, "error", "invalid-prompt-name", file, i, "Prompt 别名不能为空或纯数字。")
                current, body = (name, i), ([first_text] if first_text.strip() else [])
            elif current:
                body.append(line)
        finish()

    allowed = set()
    if prompt_sections:
        start = prompt_sections[0]
        end = next((i for i in range(start + 1, len(masked))
                    if SECTION_RE.match(masked[i]) or BATCH_RE.match(masked[i]) or BRACKET_BATCH_RE.match(masked[i])),
                   len(masked))
        allowed.update(range(start, end))
    for i, line in enumerate(masked):
        if "<Prompt" in line and i not in allowed:
            add(issues, "error", "prompt-outside-section", file, i,
                "<Prompt> 只能出现在文档开头唯一的 [待生成资产] 区域。")

    seen_numbers, previous_number = set(), None
    for batch in batches:
        label = f"批次{batch.number:02d}"
        if batch.number in seen_numbers:
            add(issues, "error", "duplicate-batch-number", file, batch.start, f"{label} 编号重复。", label)
        seen_numbers.add(batch.number)
        if previous_number is not None and batch.number <= previous_number:
            add(issues, "error", "batch-order", file, batch.start, "批次编号没有按递增顺序排列。", label)
        elif previous_number is not None and batch.number > previous_number + 1:
            add(issues, "warning", "batch-number-gap", file, batch.start,
                f"批次编号从 {previous_number:02d} 跳到 {batch.number:02d}。", label)
        previous_number = batch.number

        names = [name for name, _, _ in batch.sections]
        for name in set(names):
            found = [(a, b) for n, a, b in batch.sections if n == name]
            if len(found) > 1 and (name in W_COLUMNS or name in ASSET_COLUMNS):
                add(issues, "error", "duplicate-section", file, found[1][0],
                    f"批次内栏目 [{name}] 重复出现。", label)

        w_mode = "导演说明" in names or ("全局参考" in names and "分镜脚本" in names)
        if w_mode:
            for name in W_COLUMNS:
                if name not in names:
                    add(issues, "error", "missing-section", file, batch.start,
                        f"W式批次缺少必需栏目 [{name}]。", label)
            order = [names.index(n) for n in W_COLUMNS if n in names]
            if order != sorted(order):
                add(issues, "error", "section-order", file, batch.start,
                    "W式六栏目顺序不正确；应为：" + " → ".join(f"[{n}]" for n in W_COLUMNS) + "。", label)

        for pic in validate_assets(masked, batch, file, issues):
            picture_names.add(pic)
        if "分镜脚本" in names:
            sec = next((a, b) for n, a, b in batch.sections if n == "分镜脚本")
            validate_shots(lines, sec, batch, file, issues)
        validate_h3(lines, batch, file, issues)

    for name, index in prompts.items():
        if name not in picture_names:
            add(issues, "error", "orphan-prompt", file, index,
                f"<Prompt {name}> 没有被任何批次的同名 <Picture {name}> 引用。")

    if not batches and (prompt_sections or "[批次" in "\n".join(masked)):
        add(issues, "warning", "no-batches", file, 0, "文档包含制作标记，但没有识别到批次标题。")
    return issues


def summary(results):
    issues = [issue for _, items in results for issue in items]
    return {
        "files": len(results),
        "errors": sum(x.level == "error" for x in issues),
        "warnings": sum(x.level == "warning" for x in issues),
    }


def scan(paths):
    results = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError) as exc:
            results.append((str(path), [Issue("error", "read", str(path), 1, f"无法读取文件：{exc}")]))
            continue
        try:
            name = path.resolve().relative_to(ROOT).as_posix()
        except ValueError:
            name = path.as_posix()
        results.append((name, validate_document(text, name)))
    return results


def render_text(results):
    stats = summary(results)
    out = [f"《异星边境》视频批次检查：{stats['files']} 个文件 · {stats['errors']} 个错误 · {stats['warnings']} 个警告"]
    for name, items in results:
        out.append(f"\n{name}")
        if not items:
            out.append("  PASS")
        for x in items:
            level = "ERROR" if x.level == "error" else "WARN"
            batch = f" [{x.batch}]" if x.batch else ""
            out.append(f"  {level} {x.code}{batch} · L{x.line}: {x.message}")
    out.append("\n结果：" + ("FAIL" if stats["errors"] else "PASS"))
    return "\n".join(out)


def render_html(results):
    stats = summary(results)
    rows = []
    for name, items in results:
        if not items:
            rows.append(f'<tr><td>{html.escape(name)}</td><td colspan="4" class="ok">PASS · 未发现结构问题</td></tr>')
        for x in items:
            cls = "error" if x.level == "error" else "warning"
            rows.append(
                f"<tr><td>{html.escape(name)}</td><td>{x.line}</td>"
                f'<td class="{cls}">{x.level.upper()}</td><td>{html.escape(x.batch or x.code)}</td>'
                f"<td>{html.escape(x.message)}</td></tr>"
            )
    status = "FAIL" if stats["errors"] else "PASS"
    color = "#f08080" if stats["errors"] else "#73c99a"
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>异星边境 · 视频批次检查</title>
<style>
:root{{color-scheme:dark;--bg:#111318;--panel:#191d24;--line:#303743;--text:#e7eaf0;--muted:#9ba5b3}}
*{{box-sizing:border-box}}body{{margin:0;padding:28px;background:var(--bg);color:var(--text);font:14px/1.6 system-ui,"Microsoft YaHei",sans-serif}}
main{{max-width:1200px;margin:auto}}h1{{font-size:22px}}.muted{{color:var(--muted)}}.stats{{display:flex;gap:10px;margin:20px 0}}
.stat{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 16px;min-width:120px}}.stat b{{display:block;font-size:22px}}
.wrap{{overflow:auto;border:1px solid var(--line);border-radius:10px}}table{{width:100%;border-collapse:collapse;min-width:760px}}
th,td{{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}}th{{background:var(--panel);color:var(--muted)}}
td:first-child{{min-width:250px;overflow-wrap:anywhere}}.error{{color:#f08080;font-weight:700}}.warning{{color:#e9bd70;font-weight:700}}.ok{{color:#73c99a;font-weight:700}}
</style></head><body><main><h1>《异星边境》视频批次检查</h1>
<p class="muted">结构与引用自动检查 · 不评价创作质量、镜头风格或表演效果</p>
<div class="stats"><div class="stat"><b>{stats['files']}</b><span>检查文件</span></div>
<div class="stat"><b>{stats['errors']}</b><span>错误</span></div><div class="stat"><b>{stats['warnings']}</b><span>警告</span></div>
<div class="stat"><b style="color:{color}">{status}</b><span>检查结果</span></div></div>
<div class="wrap"><table><thead><tr><th>文件</th><th>行</th><th>级别</th><th>批次 / 规则</th><th>问题与建议</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<p class="muted">提示：警告需要人工判断；检查通过不代表生成画面已通过审片。</p></main></body></html>"""


def main(argv=None):
    parser = argparse.ArgumentParser(description="检查《异星边境》AI 视频提示词 Markdown。")
    parser.add_argument("paths", nargs="*", help="Markdown 文件或目录；省略时扫描创作/视频提示词")
    parser.add_argument("--format", choices=("text", "json", "html"), default="text")
    parser.add_argument("--output", help="报告输出路径")
    parser.add_argument("--fail-on-warn", action="store_true", help="警告也返回失败，供 CI 使用")
    args = parser.parse_args(argv)
    inputs = [Path(p) if Path(p).is_absolute() else ROOT / p for p in args.paths] or [SCAN_DIR]
    paths = []
    for path in inputs:
        if path.is_dir():
            paths.extend(path.rglob("*.md"))
        elif path.is_file():
            paths.append(path)
        else:
            print(f"路径不存在：{path}", file=sys.stderr)
            return 2
    paths = sorted({p.resolve() for p in paths if p.suffix.lower() == ".md"})
    if not paths:
        print("没有找到可检查的 Markdown 文件。", file=sys.stderr)
        return 2
    results, stats = scan(paths), None
    stats = summary(results)
    if args.format == "json":
        output = json.dumps({"summary": stats, "files": [
            {"path": name, "issues": [x.as_dict() for x in items]} for name, items in results
        ]}, ensure_ascii=False, indent=2)
    elif args.format == "html":
        output = render_html(results)
    else:
        output = render_text(results)
    if args.output:
        dest = Path(args.output)
        if not dest.is_absolute():
            dest = Path.cwd() / dest
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(output, encoding="utf-8")
        print(f"报告已写入：{dest}")
        if args.format == "html":
            print(render_text(results))
    else:
        print(output)
    return 1 if stats["errors"] or (args.fail_on_warn and stats["warnings"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())