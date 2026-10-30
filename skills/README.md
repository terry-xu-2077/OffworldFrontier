# 《异星边境》创作 Skill

项目有四套分工清楚的技能：**[编剧 × 导演分镜](offworld-storyboard-director/SKILL.md)** 负责剧本、分镜与审稿；**[默认生图](offworld-image-generation/SKILL.md)** 负责所有图像生成与改图，自动从云盘读取角色、载具、道具正式资产图，结合反推中文文本锁定造型、方向和摄影，环境从正式图提炼色彩材质与空间；**[AI 视频提示词制作](offworld-ai-video-prompt/SKILL.md)** 负责把导演已写分镜转译为视频生成任务（**默认 Seedance 2.5 参考生图**，在输出开头列 `[全局资产]`，已有云盘素材只写文件名，缺失关键素材提供中文生图提示词；明确指定时切换 MiniMax H3）；**[director-persona-maintainer｜Terry个人Skill](director-persona-maintainer/SKILL.md)** 负责维护 Terry 跨项目的个人导演判断、审美偏好与创作方法；在《异星边境》中必须与[项目适配文件](../创作/导演人格/项目适配.md)配合使用。

适用于 ChatGPT、Codex 或能够读取 GitHub 文件的 AI 助手。这里保存的是可按需读取的 **项目级技能文件**，不表示已经安装成 ChatGPT 全局 Skill。

## ChatGPT 对话调用约定

在本《异星边境》项目里，用户明确要求生图、生成电影静帧、概念图或设计性修改图片时，**默认直接执行 [生图 Skill](offworld-image-generation/SKILL.md)**，无需导演重复提醒云盘读取、图像参考和反推文本。用户提出“写剧本／分镜、设计构图、改台词、审片／改稿”时，**先读 [编剧分镜 Skill](offworld-storyboard-director/SKILL.md)** 及其必要参考，并按指引加载[Terry个人导演人格](director-persona-maintainer/references/Terry导演人格.md)及[异星边境导演人格补充](../创作/导演人格/references/异星边境导演人格补充.md)；具体参考风格时读[Terry个人审美坐标](director-persona-maintainer/references/Terry审美坐标与作品偏好.md)和[异星边境视觉与叙事参照](../创作/导演人格/references/异星边境视觉与叙事参照.md)。用户提出“把现有分镜转为视频生成提示词／拆生成批次／匹配参考素材／检查生成连续性”时，**进入 [AI 视频提示词 Skill](offworld-ai-video-prompt/SKILL.md)，默认 Seedance 2.5 参考生图：先按 Google Drive 文件名输出 `[全局资产]`，缺图附 Nano Banana／GPT 中文生图提示词；只有明确说 H3 才切换**。用户提出“更新导演人格、补充喜欢的电影／剧集／游戏、总结导演风格或从纠错中改进”时，同时使用[Terry个人维护Skill](director-persona-maintainer/SKILL.md)和[《异星边境》项目适配文件](../创作/导演人格/项目适配.md)。同时遵循 `AGENTS.md`、`创作/创作方向.md`，按需只读1–3份正典专题。

无须用户每次重复提供第三方技能链接。只有当任务需要第三方更深的专项方法时，再根据 `references/sources.md` 的来源定位读取上游内容，不把上游模板当成本项目正典。

- 剧本、角色、对白：`references/dramaturgy.md`
- 分镜、构图、机位：`references/cinematography.md`
- 多镜头动作与道具状态：`references/continuity.md`
- AI 视频制作通用规则：`references/production.md`；**场景先制作一张核心电影静帧，再进行模型提示词转译**；**模型提示词 Skill**：[`offworld-ai-video-prompt/SKILL.md`](offworld-ai-video-prompt/SKILL.md)（[核心电影静帧](offworld-ai-video-prompt/references/core-scene-keyframe.md)／[全局资产与补图](offworld-ai-video-prompt/references/asset-preparation.md)／[Seedance 2.5](offworld-ai-video-prompt/references/seedance-2.5.md)／[MiniMax H3](offworld-ai-video-prompt/references/minimax-h3.md)）
- 原始资料与授权：`references/sources.md`

Terry的个人基线保留在 `skills/director-persona-maintainer/`：个人导演判断、个人审美与作品偏好、跨项目创作方法；《异星边境》的专属资料独立位于 `创作/导演人格/`：[项目适配文件](../创作/导演人格/项目适配.md)规定两层如何配合，[项目人格补充](../创作/导演人格/references/异星边境导演人格补充.md)维护本项目叙事和协作边界，[视觉与叙事参照](../创作/导演人格/references/异星边境视觉与叙事参照.md)维护项目内的风格映射，[改稿案例](../创作/导演人格/references/异星边境改稿案例.md)维护本项目真实案例。按需加载，不复制正式剧本和设定。

用户的最新创作决定与仓库正典优先；第一季提案、灵感池和旧电影版限制不得自动上升为通用规则。写剧本时不提前强塞导演镜头表；写分镜时才使用逐镜控制卡。

> 注意：这是仓库里的协作约定。ChatGPT 并不会因为 GitHub 存在 `SKILL.md` 就自动挂载为原生技能；需要对话中的助手实际读取该文件。 
