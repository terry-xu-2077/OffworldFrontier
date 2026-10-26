# 《异星边境》创作 Skill

项目有三套分工清楚的技能：**[编剧 × 导演分镜](offworld-storyboard-director/SKILL.md)** 负责剧本、分镜与审稿；**[AI 视频提示词制作](offworld-ai-video-prompt/SKILL.md)** 负责把导演已写分镜转译为视频生成任务（**默认 Seedance 2.5，明确指定时切换 MiniMax H3**）；**[导演人格维护](director-persona-maintainer/SKILL.md)** 负责将导演反馈转为长期判断和审美坐标。

适用于 ChatGPT、Codex 或能够读取 GitHub 文件的 AI 助手。这里保存的是可按需读取的 **项目级技能文件**，不表示已经安装成 ChatGPT 全局 Skill。

## ChatGPT 对话调用约定

在本《异星边境》项目里，用户提出“写剧本／分镜、设计构图、改台词、审片／改稿”时，**先读 [编剧分镜 Skill](offworld-storyboard-director/SKILL.md)** 及其必要参考，并按指引加载 [唯一导演人格](director-persona-maintainer/references/导演代理人格.md)；具体参考风格时读 [审美坐标及作品偏好](director-persona-maintainer/references/导演审美印象与作品偏好.md)。用户提出“把现有分镜转为视频生成提示词／拆生成批次／匹配参考素材／检查生成连续性”时，**进入 [AI 视频提示词 Skill](offworld-ai-video-prompt/SKILL.md)，默认 Seedance 2.5，只有明确说 H3 才切换**。用户提出“更新导演人格、补充喜欢的电影／剧集／游戏、总结导演风格或从纠错中改进”时，使用 [导演人格维护 Skill](director-persona-maintainer/SKILL.md)。同时遵循 `AGENTS.md`、`创作/创作方向.md`，按需只读1–3份正典专题。

无须用户每次重复提供第三方技能链接。只有当任务需要第三方更深的专项方法时，再根据 `references/sources.md` 的来源定位读取上游内容，不把上游模板当成本项目正典。

- 剧本、角色、对白：`references/dramaturgy.md`
- 分镜、构图、机位：`references/cinematography.md`
- 多镜头动作与道具状态：`references/continuity.md`
- AI 视频制作通用规则：`references/production.md`；**按模型生成可复制提示词**：[`offworld-ai-video-prompt/SKILL.md`](offworld-ai-video-prompt/SKILL.md)（[Seedance 2.5](offworld-ai-video-prompt/references/seedance-2.5.md)／[MiniMax H3](offworld-ai-video-prompt/references/minimax-h3.md)）
- 原始资料与授权：`references/sources.md`

导演人格维护的参考文件位于 `director-persona-maintainer/references/`：[人格正文](director-persona-maintainer/references/导演代理人格.md)维护长期价值取舍，[创作与迭代方法论](director-persona-maintainer/references/影视叙事创作与迭代方法论.md)维护案例驱动的场景诊断、方案比较及五步验证，[审美文件](director-persona-maintainer/references/导演审美印象与作品偏好.md)用于摄影风格与作品偏好。按需加载，不复制正式剧本和设定。

用户的最新创作决定与仓库正典优先；第一季提案、灵感池和旧电影版限制不得自动上升为通用规则。写剧本时不提前强塞导演镜头表；写分镜时才使用逐镜控制卡。

> 注意：这是仓库里的协作约定。ChatGPT 并不会因为 GitHub 存在 `SKILL.md` 就自动挂载为原生技能；需要对话中的助手实际读取该文件。 
