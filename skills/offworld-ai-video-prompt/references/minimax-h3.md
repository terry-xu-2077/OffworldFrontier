# MiniMax H3｜仅明确指定时启用

**本项目默认 Seedance 2.5 参考生图。用户明确指定 MiniMax H3 / H3 后才进入此模块。** 每场尚无母图时先输出一次 [核心电影静帧](core-scene-keyframe.md)，再输出独立的 `[全局资产]` 类型化制作参考清单，**两者都放在 H3 官方格式纯提示词代码块之外**；实际成图并绑定后才能作为 H3 的真实参考资产输入。全局清单使用 `<Picture 名称>`、`<Audio 名称>`、`<Video 名称>`；缺失图片用同名 `<Picture>` + `<Prompt>`，由节点提取生图内容并从视频提示词中剥离。**这些中文命名标签属于 TerryDirector 制作侧，不属于 H3 官方模型输入字段**；下方独立复制的 H3 纯提示词必须严格保持官方结构。严格采用当前 MiniMax 官方 [h3-prompt-writing Skill](https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills/h3-prompt-writing) 的文本结构；执行时按需读取：
- [官方 SKILL.md](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/SKILL.md)
- [T2VA / I2VA / FL2VA / L2VA 模式规范](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/base-en.txt)
- [Ref2VA 模式规范](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/ref-en.txt)

**官方当前时长建议：4–15秒；Seedance 30秒分批规则不能套到 H3。** 参数若因后端实现发生改变，以所用 H3 入口为准。使用 TerryDirector / ComfyUI 时，先确认实际工作流接入的是什么参考与首尾帧；导演时间线的片段重叠和尾帧参考是**编排能力**，不是 H3 提示词天然能强制保证的能力。

## 1. 选正确生成模式

| 模式 | 条件 |
|---|---|
| T2VA | 文本直接创建片段，画面与声音自行生成 |
| I2VA | 实际首帧图像锁定0.00s，动作从首帧已完成的阶段向前演化 |
| FL2VA | 实际第一与末帧均给定，写清中间动作路径；默认单镜更合适 |
| L2VA | 仅锁末帧，合理推导前序动作并最终抵达所给画面 |
| Ref2VA | 多图、视频、音频及可重用主体等**全参考关系**，要用专用六字段结构；图像用于定义角色时不等于独立首帧 |

参考生图准备清单中列了文件，不代表这些文件已接入 H3。实际同时有角色／场景／道具等多图参考，且后端提供 Ref2VA 时，按真实输入编写相应六字段；缺失的先补图。**不根据“上传过图片”一概选 I2VA。**上一镜画面若只是身份、道具或光线参考而非首帧锚定，要对应选择真正可实现的模式。若没有素材，不许杜撰`<Picture 1>` 等标签。

## 2. H3 官方基础字段，不混 Seedance 标题

**制作侧与模型侧标签必须分开：** `<Picture 特瑞>`、`<Audio 特瑞声线>`、`<Video FPV运动参考>` 是全局制作清单中的语义引用；H3 正式提示词中的 `<Picture 1>`、`<Audio 1>`、`<Video 1>` 是根据真实输入顺序生成的官方编号。两者不能直接互换，也不能把 `<Prompt>` 块送入 H3。只有在资产实际映射完成后，才为 H3 正式字段分配数字编号。

**交付结构：** 先给用户独立的 `[全局资产]` 类型化制作清单，然后以**另一个代码块**提供完整英文 H3 纯提示词，便于只复制该块到模型。若存在待生成图片，制作清单中写同名 `<Picture 名称>` + `<Prompt 名称>`；节点先提取并剥离 `<Prompt>` 块，图片导入后再绑定 `<Picture>`。官方指令必须仍然是 H3 模型提示词自己的第一行。

对于 T2VA/I2VA/FL2VA/L2VA，主体结构**英文**为：

```text
integrated_multimodal_description: [Shot 1] ... [Shot 2] At 00:03.500, the camera cuts to ...
overall_soundscape: ...
non_diegetic_music: N/A
```

字段之间空一行。**第一镜标`[Shot 1]`，不加时间码**；其后切镜`[Shot N] At MM:SS.mmm,`，严格递增，不能超出总长度。若单镜，无后续`[Shot 2]`。声源编号按声音第一次出现顺序用`(S1)`、`(S2)`，跨镜重用。中文对白原样放入`<d>[Chinese]原对白</d>`，人物身份、口气、说话动作留在标签外；不改写台词。画外配乐默认字段`non_diegetic_music: N/A`；这个`N/A`只表示**无非现场配乐**，环境声照写。

**首帧对齐在字段之前**：
- I2VA 首行精确为：`For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.`
- FL2VA 首行：`How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.`；`N`为最后镜号，`S.SS`为最终有效时长，精确两位小数。
- L2VA 首行：`How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.`
- T2VA **不需要**任何图片对齐首行。

紧接指令与三个字段之间留一个空行。镜头运动写成自然英文（动作种类 + 必要的幅度 + 速度），不是尾部参数列表。`overall_soundscape` 是1–4句英文连续环境音/拟音概要；不重复对白全文，不因默认无配乐而写`N/A`（除非用户明确要求全静音）。

## 3. Ref2VA 六字段

必须按序输出：
1. `subject_definitions`：`<Subject N>`（人物/物件/场景的可复用内容）、`<Picture N>`（真实的首/末帧或分镜构图锚）、`<Video N>`（视频结构或延长/编辑源）、`<Audio N>`（独立音频或实际启用的配音参考）分别定义；一个资产可以包含多个角色，一个角色可汇集多个资产，不能任意重编号。
2. `summary`：以`[reference generation]`、`[keyframe completion]`、`[video continuation]`等**与实际输入角色吻合的模式前缀**概括。
3. `retention_analysis`：逐资产写继承关系，图像/主体使用`fully_preserved / partially_preserved / attribute_transfer / weak_reference`，音频使用`fully_copy / partially_copy / reference / weak_reference`。
4. `detailed_description`：**英文**，全片顺序的`[Shot N]`、动作/摄影/声音/中文对白`<d>[Chinese]…</d>`。镜头1无时间戳，其余切镜时间码同基础模式。
5. `overall_soundscape`：真实环境声与Foley，别重复对白。
6. `non_diegetic_music`：默认`N/A`。

**关键区分：**`<Subject N>`是从视觉/声音资产抽象出来的可复用人物/场景，`<Picture N>`单独成行通常是**参考图本身充当帧锚或分镜布局锚**，不是所有视觉参考都强制生出`<Picture N>`独立条目。参考视频的结构性`<Video N>`标签也不自动代替可见人物`<Subject N>`。音频资产与说话人`(Sx)`各有独立编号。

## 4. 忠实转译与连续性

- 中文分镜→英文动作、空间、摄影、声学描述，但角色**已写中文台词照原样**；项目人物/装备在多批次保持稳定。
- 同一导演镜号超过15秒时做`A/B`制作批次；不自主改变机位和剧情，备注说明具体是连续首帧/延长，还是新独立构图。
- 有实际上一镜尾帧才可把它设为 I2VA 首帧；不同机位不强行帧插值。若实际输入条件不支持“上一镜仅用于状态参考”，应采用支持参考的 Ref2VA 链路或转换成**正确新机位的首帧资产**，而非写一句说明就当功能存在。
- 物理、表演、真实场面、无额外画外音乐等导演意图与 Seedance 相同，但**提示词格式绝对不同**。
