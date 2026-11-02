# 《异星边境》创作 Skill

本项目调用三套职责清楚、按需协作的技能；AI 视频导演技能本身保持通用，项目约定由仓库入口补充：

- **[AI 视频导演](ai-video-director/SKILL.md)**：统一负责剧作与场景审查、协作式分镜设计、镜头连续性、动作与摄影编排、AI视频批次制作、Seedance 2.5 / MiniMax H3 提示词及生成结果审片。导演可提供局部画面方向或提示词反馈，AI主动补全可执行镜头与制作细节。
- **[默认生图](offworld-image-generation/SKILL.md)**：负责所有图像生成与设计性改图，自动核对云盘角色、载具、道具和环境正式资产，结合原图与反推中文文本锁定造型、结构、方向、空间和摄影。
- **[director-persona-maintainer｜Terry个人Skill](director-persona-maintainer/SKILL.md)**：负责维护 Terry 跨项目的个人导演判断、审美偏好与创作方法；在《异星边境》中必须与[项目适配文件](../创作/导演人格/项目适配.md)配合使用。

适用于 ChatGPT、Codex 或能够读取 GitHub 文件的 AI 助手。这里保存的是可按需读取的**技能文件与项目入口约定**，不表示已经安装成 ChatGPT 全局 Skill。

## 如何使用：先载入导演人格，再使用视频导演技能

**《异星边境》的创作／分镜／视频提示词任务，必须遵循以下顺序。** 不要只打开视频导演 Skill 就开始写镜头；也不要把个人导演人格的内容复制进通用视频导演技能。

1. **先载入导演人格。** 先读取 [Terry 导演人格](director-persona-maintainer/references/Terry导演人格.md)，建立人物、故事、节奏、视听取舍和审稿判断的个人基线。普通创作只读取这份人格资料即可，**不需要执行人格维护技能的更新流程**。
2. **再载入本项目的适配。** 读取 [《异星边境》项目适配](../创作/导演人格/项目适配.md) 和其中的 [项目导演人格补充](../创作/导演人格/references/异星边境导演人格补充.md)，理解本剧的专属风格、人物边界与创作判断；同时遵循仓库 [AGENTS.md](../AGENTS.md)、[创作方向](../创作/创作方向.md)。风格类比时才按需读取视觉参照，复杂改稿审查时才按需读取既有案例；人物、世界和美术事实从当下正典及正式资产核对。
3. **最后使用 AI 视频导演技能。** 读取 [ai-video-director/SKILL.md](ai-video-director/SKILL.md)，根据当前任务选择相关的 `references/` 模块，依次完成场面判断、分镜设计、空间／动作连续性、资产绑定、视频批次提示词或实际成片审查。**先用导演人格决定“拍什么、为什么值得拍”，再用视频导演技能决定“怎么拍、怎么写成可生成提示词”。**
4. **执行与验证。** 保留用户明确锁定的剧本、镜头、对白、剪点与最新意见；交付前检查场面整体、跨批连续性、画面可见性、资产引用与指定格式。若修改仓库文件，直接更新权威文件并说明改动；提示词格式校验不等于导演验收，也不等于真实视频已经生成。

> **名称说明：** 你之前使用的 `offworld-ai-video-director` 是旧目录名；为使技能本身不绑定任何作品，现已更名为 **`ai-video-director`**。在本项目里说“使用 offworld-ai-video-director”，应按上述顺序调用当前实际文件 `skills/ai-video-director/SKILL.md`；不要访问已移除的旧目录或假定它仍是一个独立技能。

### 任务路由

- **写剧本、改台词、设计／审阅分镜、直接从剧本制作视频提示词、检查镜头连续性、拆批或审片：** 按上述顺序加载导演人格与项目适配，再使用 AI 视频导演 Skill。其参考模块按当前任务选取，不要求一次性读完十四个模块。
- **生成电影静帧、角色／场景资产图或修改图片：** 仍先遵循相关人物与项目视觉设定，然后由 [默认生图 Skill](offworld-image-generation/SKILL.md) 负责实际图片流程；视频导演 Skill 只负责镜头和视觉需求，不能代替真正生图。
- **更新或校准 Terry 导演人格：** 才使用 [director-persona-maintainer Skill](director-persona-maintainer/SKILL.md) 的维护流程，配合个人导演人格和项目适配文件；不得把一次提示词修改自动当作人格更新。
- **纯仓库维护、代码修改、文件检索：** 不属于创作判断时，不必强制加载导演人格。

### 可直接交给 ChatGPT / Codex 的调用指令

```text
本次在《异星边境》仓库开展创作任务。
请先读取 skills/director-persona-maintainer/references/Terry导演人格.md，
再读取 创作/导演人格/项目适配.md 与该文件指定的项目导演人格补充，
并遵循 AGENTS.md、创作/创作方向.md 和相关现行正典。
在建立导演判断后，载入 skills/ai-video-director/SKILL.md，
按当前任务读取相关 references 模块，再开始执行我的具体要求。
不要使用已移除的 offworld-ai-video-director 旧路径；
不要运行导演人格维护或更新流程，除非我明确要求。
```

### 默认视频制作约定

默认视频模型仍为 Seedance 2.5 参考生图，批次默认按 15 秒规划但不机械填满；只有明确指定 MiniMax H3 / H3 才切换。文档级稳定 `Picture` / `Audio` / `Video` 语义别名、集中定义的待生成图片 `Prompt`、节点的跨批资产同步和现有 W 式六栏目输出格式全部保持不变。导演已确认内容优先；会改变剧情因果、人物选择或世界设定的新增内容标注为提案。

## AI 视频导演参考模块

- [故事、人物、场景、对白与观看价值](ai-video-director/references/01_story-and-viewing-value.md)
- [导演意图、镜头组织与批次规划](ai-video-director/references/02_intent-and-batch.md)
- [空间关系、构图与场面调度](ai-video-director/references/03_space-and-blocking.md)
- [动作时间轴、物理因果与生成可执行性](ai-video-director/references/04_action-timeline.md)
- [摄影机控制与特殊拍摄方式](ai-video-director/references/05_camera-control.md)
- [视觉反馈、光影、材质与声音](ai-video-director/references/06_visual-and-sound.md)
- [资产引用与连续性](ai-video-director/references/07_assets-and-continuity.md)
- [核心电影静帧](ai-video-director/references/08_core-scene-keyframe.md)
- [输出格式与模型正文边界](ai-video-director/references/09_output-contract.md)
- [Seedance 2.5](ai-video-director/references/10_seedance-2.5.md)
- [MiniMax H3](ai-video-director/references/11_minimax-h3.md)
- [质量审查与生成结果复盘](ai-video-director/references/12_quality-review.md)
- [方法来源与适用边界](ai-video-director/references/13_reference-methods.md)
- [跳跃动作物理（可选）](ai-video-director/references/14_jump-preparation.md)

按需核对当下有效的正典专题，第一季提案、灵感池和历史废弃剧情不自动成为通用规则。编写剧本不自动输出镜头表，设计分镜不自动生成素材，具体交付层级以本次任务为准。

> 注意：这是仓库里的协作约定。ChatGPT 不会因为 GitHub 存在 SKILL.md 就自动挂载为原生技能；需要对话中的助手实际读取该文件。
