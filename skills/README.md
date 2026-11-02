# 《异星边境》创作 Skill

本项目保留三套职责清楚、按需协作的技能：

- **[AI 视频导演](offworld-ai-video-director/SKILL.md)**：统一负责剧作与场景审查、导演分镜设计、镜头连续性、动作与摄影编排、AI视频批次制作、Seedance 2.5 / MiniMax H3 提示词及生成结果审片。默认尊重导演逐镜创作，不擅自续写正式分镜。
- **[默认生图](offworld-image-generation/SKILL.md)**：负责所有图像生成与设计性改图，自动核对云盘角色、载具、道具和环境正式资产，结合原图与反推中文文本锁定造型、结构、方向、空间和摄影。
- **[director-persona-maintainer｜Terry个人Skill](director-persona-maintainer/SKILL.md)**：负责维护 Terry 跨项目的个人导演判断、审美偏好与创作方法；在《异星边境》中必须与[项目适配文件](../创作/导演人格/项目适配.md)配合使用。

适用于 ChatGPT、Codex 或能够读取 GitHub 文件的 AI 助手。这里保存的是可按需读取的**项目级技能文件**，不表示已经安装成 ChatGPT 全局 Skill。

## ChatGPT 对话调用约定

在本《异星边境》项目里：

- 用户要求写剧本、讨论人物或场景、改台词、设计或审阅分镜、检查镜头连续性、转译视频提示词、拆分生成批次、匹配视频参考素材或审片时，统一进入 [AI 视频导演 Skill](offworld-ai-video-director/SKILL.md)，按任务读取必要的 1–3 个参考模块。剧作、正式分镜、图像生成和视频制作仍然分层，不强制铺开全部流程。
- 用户明确要求生图、生成电影静帧、概念图或设计性修改图片时，直接执行 [默认生图 Skill](offworld-image-generation/SKILL.md)，无需导演重复提醒云盘读取、图像参考、反推文本和结果验收。
- 用户要求更新导演人格、补充喜欢的电影／剧集／游戏、总结导演风格或从纠错中改进时，同时使用 [Terry个人维护Skill](director-persona-maintainer/SKILL.md) 和[《异星边境》项目适配文件](../创作/导演人格/项目适配.md)。

默认视频模型为 Seedance 2.5 参考生图；只有导演明确指定 MiniMax H3 / H3 才切换。用户已经写出正式逐镜分镜时，忠实转译，不主动补写后续镜头。只有导演明确要求从现行剧本直出视频制作稿时，才允许提出 AI 拟议镜头，并明确标记为制作层提案，不得冒充正式分镜。

## AI 视频导演参考模块

- [故事、人物、场景、对白与观看价值](offworld-ai-video-director/references/01_story-and-viewing-value.md)
- [导演意图、镜头组织与批次规划](offworld-ai-video-director/references/02_intent-and-batch.md)
- [空间关系、构图与场面调度](offworld-ai-video-director/references/03_space-and-blocking.md)
- [动作时间轴、物理因果与生成可执行性](offworld-ai-video-director/references/04_action-timeline.md)
- [摄影机控制与特殊拍摄方式](offworld-ai-video-director/references/05_camera-control.md)
- [视觉反馈、光影、材质与声音](offworld-ai-video-director/references/06_visual-and-sound.md)
- [资产引用与连续性](offworld-ai-video-director/references/07_assets-and-continuity.md)
- [核心电影静帧](offworld-ai-video-director/references/08_core-scene-keyframe.md)
- [输出格式与模型正文边界](offworld-ai-video-director/references/09_output-contract.md)
- [Seedance 2.5](offworld-ai-video-director/references/10_seedance-2.5.md)
- [MiniMax H3](offworld-ai-video-director/references/11_minimax-h3.md)
- [质量审查与生成结果复盘](offworld-ai-video-director/references/12_quality-review.md)
- [方法来源与案例](offworld-ai-video-director/references/13_reference-methods.md)

同时遵循仓库根目录 AGENTS.md、创作/创作方向.md，按需核对 1–3 份权威正典专题。Terry 的个人基线保留在 skills/director-persona-maintainer/；《异星边境》的项目适配、项目人格补充、视觉参照和改稿案例独立位于 创作/导演人格/，不在技能内复制一份会漂移的设定副本。

用户最新决定与仓库正典优先；第一季提案、灵感池和旧电影版限制不得自动上升为通用规则。正式分镜仍由导演主导；写剧本不自动输出镜头表，写分镜不自动执行媒体生成。

> 注意：这是仓库里的协作约定。ChatGPT 不会因为 GitHub 存在 SKILL.md 就自动挂载为原生技能；需要对话中的助手实际读取该文件。
