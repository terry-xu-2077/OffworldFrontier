# MiniMax H3｜仅明确指定时启用

**本项目默认 Seedance 2.5。只有导演明确指定 MiniMax H3 / H3 后才进入本模块。** H3时长、字段和模式以当前官方规范及实际后端为准，不能套用Seedance的30秒上限或W式六栏目。

## 一、官方资料

执行时按需读取当前官方文档：
- 官方 Skill：https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills/h3-prompt-writing
- 基础模式：https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/base-en.txt
- Ref2VA：https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/ref-en.txt

规范可能更新，使用时核对当前版本，不把历史工作流当作永久接口。

## 二、选择正确模式

| 模式 | 使用条件 |
|---|---|
| T2VA | 文本直接创建视频，画面与声音自行生成 |
| I2VA | 实际首帧在0.00秒锁定，动作从该帧已有状态向前演化 |
| FL2VA | 实际首帧与末帧均给定，描述中间动作路径；通常适合单镜 |
| L2VA | 仅锁定末帧，合理推导前序动作并抵达目标画面 |
| Ref2VA | 多图、视频、音频和可重用主体等全参考关系，使用专用六字段结构 |

不要因为“上传过图片”就一概选择 I2VA。上一镜图像若只用于身份、道具、伤痕或光线参考，而非首帧锚定，应选择真正匹配的模式。没有真实素材时，不得杜撰 Picture 编号。

## 三、制作侧与模型侧标签分开

制作侧语义标签：Picture 特瑞、Audio 特瑞声线、Video 运镜参考。同一实际资产跨批次保持相同媒体类型和别名，便于节点匹配。

H3正式提示词中的 Picture 1、Audio 1、Video 1 是当前批次按真实输入顺序生成的官方编号。两者不能直接互换。只有实际素材映射完成后，才能分配数字编号。中文命名标签和文档级 Prompt 不得放进 H3 正式字段。

## 四、基础模式字段

T2VA / I2VA / FL2VA / L2VA 使用英文主体描述：

~~~text
integrated_multimodal_description: [Shot 1] ... [Shot 2] At 00:03.500, the camera cuts to ...
overall_soundscape: ...
non_diegetic_music: N/A
~~~

字段之间空一行。第一镜写 [Shot 1]，不加时间码；后续切镜使用 [Shot N] At MM:SS.mmm，时间严格递增且不超出总时长。单镜没有后续 [Shot 2]。声源编号按首次出现顺序使用 (S1)、(S2)，跨镜复用。

中文对白原样保留，使用 <d>[Chinese]原对白</d>。不翻译、不改写、不吞句。人物身份、口气、说话动作在标签外说明。

non_diegetic_music: N/A 表示无画外配乐，不代表无环境声。overall_soundscape 用1–4句英文概括连续环境声与Foley，不重复对白全文。

## 五、首帧对齐行

首帧对齐指令位于字段之前：

- I2VA：For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
- FL2VA：How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video. 最后一镜编号和最终有效时长必须对应真实输入。
- L2VA：How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.
- T2VA：不需要图片对齐首行。

指令与字段之间留空行。具体拼写以当前官方文档为准。

## 六、Ref2VA 六字段

严格按当前官方顺序：

1. subject_definitions：定义可复用主体、参考图片、视频和音频；区分 Subject、Picture、Video、Audio 的实际作用。
2. summary：用与实际输入相符的模式前缀概括任务。
3. retention_analysis：逐资产说明继承关系。图像/主体按官方支持的 fully_preserved、partially_preserved、attribute_transfer、weak_reference 等级；音频按 fully_copy、partially_copy、reference、weak_reference 等级。
4. detailed_description：英文逐镜描述，包含动作、摄影、声音和中文对白标签；镜头1无时间戳，后续切镜标注时间。
5. overall_soundscape：真实环境声与Foley，不重复对白。
6. non_diegetic_music：默认 N/A。

Subject 是可复用人物、物件或场景定义；Picture 通常是实际参考帧或分镜构图锚点，不意味着每张身份参考图都必须单独作为帧锚。参考视频的 Video 结构标签也不自动代替可见人物的 Subject 定义。音频资产与说话人声源编号各自独立。

## 七、忠实转译与连续性

中文分镜可以转译为英文动作、空间、摄影和声学描述，但角色中文台词原样保留。导演镜头超过当前后端单次时长时，可按自然动作阶段做A/B制作批次，沿用原镜号，不自主改变机位和剧情；备注说明是连续首帧/延长，还是新独立构图。

真实上一镜尾帧才能作为 I2VA 首帧。不同机位不能强行做帧插值。若当前后端不支持“上一镜只作状态参考”，应选择支持参考的模式或准备正确新机位首帧，不要只写一句说明就假定功能存在。

H3 提示词格式与 Seedance 完全不同；资产清单在模型正文外，官方指令必须是正式提示词块的首行。
