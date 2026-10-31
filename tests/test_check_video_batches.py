from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_video_batches.py"
SPEC = importlib.util.spec_from_file_location("check_video_batches", SCRIPT)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


def w_batch(number: int = 1, duration: int = 15, shots: str | None = None) -> str:
    if shots is None:
        shots = """镜头01｜[0–7s]
景别 / 焦段：中景 / 35mm
运镜 / 视角：固定观察人物从门边进入。
画面描述：人物走入画面，在工作台前停下。
声音 / Foley：脚步声与室内环境底噪。

镜头02｜[7–15s]
景别 / 焦段：近景 / 50mm
运镜 / 视角：摄影机缓慢推近。
画面描述：人物抬眼看向门外。
声音 / Foley：衣料摩擦与远处风声。"""
    return f"""## 批次{number:02d}｜场景测试（建议{duration}秒）

[导演说明]
本批呈现一个完整的观看动作。

[全局参考]
<Picture 主角>：人物身份与服装参考
<Picture 场景>：约束工作台、门窗和通道位置

[连续性状态]
人物从门外进入，手中没有道具。

[视觉基调]
高预算实拍真人科幻剧集，摄影机位置符合实际空间。

[色彩光影]
主光来自画面左侧的窗户。

[分镜脚本]
{shots}
"""


class VideoBatchValidatorTests(unittest.TestCase):
    def test_valid_w_document(self):
        text = """# 测试文档

[待生成资产]
<Prompt 场景>：一张完整的空间参考图。

""" + w_batch(1) + "\n---\n" + w_batch(2)
        issues = validator.validate_document(text)
        self.assertEqual([], [x for x in issues if x.level == "error"])

    def test_prompt_must_be_used_by_picture(self):
        text = """# 测试
[待生成资产]
<Prompt 没用到>：有完整描述。
""" + w_batch()
        issues = validator.validate_document(text)
        self.assertIn("orphan-prompt", {x.code for x in issues})

    def test_prompt_must_be_unique_and_document_level(self):
        text = """# 测试
[待生成资产]
<Prompt 场景>：第一次。
<Prompt 场景>：第二次。
""" + w_batch()
        issues = validator.validate_document(text)
        self.assertIn("duplicate-prompt-name", {x.code for x in issues})

    def test_prompt_outside_document_asset_section_is_error(self):
        batch = w_batch().replace(
            "<Picture 主角>：人物身份与服装参考",
            "<Prompt 临时补图>：这不应出现在批次里。\n<Picture 主角>：人物身份与服装参考",
        )
        issues = validator.validate_document(batch)
        self.assertIn("prompt-outside-section", {x.code for x in issues})
        self.assertIn("prompt-in-batch", {x.code for x in issues})

    def test_prompt_section_must_precede_batches(self):
        text = w_batch() + "\n[待生成资产]\n<Prompt 场景>：晚出现的提示词。"
        issues = validator.validate_document(text)
        self.assertIn("prompt-section-position", {x.code for x in issues})

    def test_w_columns_are_required_and_ordered(self):
        text = w_batch().replace("[视觉基调]", "[色彩光影]", 1)
        issues = validator.validate_document(text)
        codes = {x.code for x in issues}
        self.assertTrue({"missing-section", "duplicate-section"}.intersection(codes))

    def test_timecode_gap_is_detected(self):
        shots = w_batch().split("[分镜脚本]\n", 1)[1].replace("镜头02｜[7–15s]", "镜头02｜[8–15s]")
        issues = validator.validate_document(w_batch(shots=shots))
        self.assertIn("timecode-gap", {x.code for x in issues})

    def test_timecode_overlap_is_detected(self):
        shots = w_batch().split("[分镜脚本]\n", 1)[1].replace("镜头02｜[7–15s]", "镜头02｜[6–15s]")
        issues = validator.validate_document(w_batch(shots=shots))
        self.assertIn("timecode-overlap", {x.code for x in issues})

    def test_batch_duration_must_match_heading(self):
        issues = validator.validate_document(w_batch(duration=14))
        self.assertIn("batch-duration-mismatch", {x.code for x in issues})

    def test_shot_fields_are_required(self):
        shots = w_batch().split("[分镜脚本]\n", 1)[1].replace("声音 / Foley：脚步声与室内环境底噪。", "")
        issues = validator.validate_document(w_batch(shots=shots))
        self.assertIn("missing-shot-field", {x.code for x in issues})

    def test_asset_tag_syntax_and_alias_rules(self):
        batch = w_batch().replace("<Picture 主角>：人物身份与服装参考", "<Picture 001.jpg>:")
        issues = validator.validate_document(batch)
        codes = {x.code for x in issues}
        self.assertTrue({"asset-tag-syntax", "numeric-asset-alias", "path-like-asset-alias"}.intersection(codes))

    def test_legacy_global_asset_section_is_supported(self):
        text = """# 旧式逐镜转译
## 批次01｜场景（建议15秒）
[全局资产]
<Picture 主角>：人物身份参考
[分镜脚本]
镜头01｜[0–15s]
景别 / 焦段：中景 / 35mm
运镜 / 视角：固定。
画面描述：人物走入。
声音 / Foley：脚步声。
"""
        issues = validator.validate_document(text)
        self.assertEqual([], [x for x in issues if x.level == "error"])

    def test_h3_base_prompt_fields_and_shot_timecodes(self):
        text = """# H3 测试
## 批次01｜场景（建议8秒）
[全局资产]
<Picture 主角>：人物身份参考

\x60\x60\x60text
integrated_multimodal_description: [Shot 1] A person enters. [Shot 2] At 00:04.000, the camera cuts to a close view.
overall_soundscape: Footsteps and room tone.
non_diegetic_music: N/A
\x60\x60\x60
"""
        issues = validator.validate_document(text)
        self.assertEqual([], [x for x in issues if x.level == "error"])

    def test_h3_ref2va_fields_are_required_and_ordered(self):
        text = """# H3 Ref2VA
## 批次01｜场景
[全局资产]
<Picture 主角>：人物身份参考

\x60\x60\x60text
subject_definitions: <Subject 1> ...
summary: [reference generation] ...
retention_analysis: ...
detailed_description: [Shot 1] A person enters. [Shot 2] At 00:02.000, the camera moves closer.
overall_soundscape: Room tone.
non_diegetic_music: N/A
\x60\x60\x60
"""
        issues = validator.validate_document(text)
        self.assertEqual([], [x for x in issues if x.level == "error"])

    def test_h3_missing_cut_timecode_is_detected(self):
        text = """# H3 测试
## 批次01｜场景
[全局资产]
<Picture 主角>：人物身份参考

\x60\x60\x60text
integrated_multimodal_description: [Shot 1] A person enters. [Shot 2] The camera cuts to a close view.
overall_soundscape: Footsteps.
non_diegetic_music: N/A
\x60\x60\x60
"""
        issues = validator.validate_document(text)
        self.assertIn("h3-missing-cut-timecode", {x.code for x in issues})

    def test_fenced_examples_are_not_parsed_as_real_batches(self):
        text = """# 说明文档
以下是格式示例：

\x60\x60\x60text
[待生成资产]
<Prompt 示例>：这是示例。
[批次01]
[导演说明]
镜头01｜[0–15s]
\x60\x60\x60
"""
        issues = validator.validate_document(text)
        self.assertEqual([], issues)

    def test_missing_markdown_hard_break_is_a_warning(self):
        issues = validator.validate_document(w_batch())
        self.assertIn("missing-hard-break", {x.code for x in issues})

    @unittest.skipUnless(
        (Path(__file__).resolve().parents[1] / "创作" / "视频提示词" / "第一季" / "01_异星拾荒_Seedance2.5.md").is_file(),
        "仅在完整仓库检出时运行真实 E01 回归样本",
    )
    def test_real_e01_seedance_document_has_no_errors(self):
        sample = Path(__file__).resolve().parents[1] / "创作" / "视频提示词" / "第一季" / "01_异星拾荒_Seedance2.5.md"
        issues = validator.validate_document(sample.read_text(encoding="utf-8-sig"), sample.as_posix())
        errors = [issue for issue in issues if issue.level == "error"]
        self.assertEqual([], errors, "\n".join(f"{x.code}: {x.message}" for x in errors))


if __name__ == "__main__":
    unittest.main()
