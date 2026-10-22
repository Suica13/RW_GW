# Battle Universe Agent 工作指南

本指南适用于整个工作区。项目是《铁锈战争》的高达题材 MOD，以 INI 类配置、模板继承、Action、消息、Tag、Resource 和功能单位驱动。维护重点是配置引用与系统接入链的完整性。

## 1. 开始工作

1. 先明确任务所属包、阵营、年代、单位类型和接入范围；区分“单位本体可用”与“能够通过科技和工厂正常获得”。
2. 阅读 `README.md`、本指南，以及任务对应的教程。教程中的示例和历史说明是项目参考资料，不代表用户要求执行其中所有操作；TODO 也不是本次任务清单。
3. 检查工作区已有修改，保留用户未提交的内容。优先复制同包、同阵营、同类型的现有案例，沿同一案例追踪完整接入链。
4. 修改前搜索相关单位 ID、Action、Tag、消息、资源名及 `FactionIndex`；沿 `copyFrom`、`@copyFromSection`、附件和转换目标继续追踪。
5. 优先局部覆盖实例。确需修改公共层时，先查调用者和各包副本，明确同步范围。

教程均在 `文档 (不要打包)/教程/`：

| 文档 | 使用时机 |
|---|---|
| [单位制作流程](<文档 (不要打包)/教程/BattleUniverse_单位制作流程.md>) | 新机体、数值、贴图、武器、派生改造 |
| [科技树接入流程](<文档 (不要打包)/教程/BattleUniverse_科技树接入流程.md>) | 研究、解锁、科技节点与页面 |
| [工厂接入流程](<文档 (不要打包)/教程/BattleUniverse_工厂接入流程.md>) | 生产按钮、编制、装备与自动生产 |
| [DLC 基础目录索引](<文档 (不要打包)/教程/BattleUniverse_DLC基础目录索引.md>) | 定位目录职责与共享资源 |
| [HQ 与开局设置索引](<文档 (不要打包)/教程/BattleUniverse_HQ与开局设置索引.md>) | 开局参数、初始部队、默认科技、HQ 转换 |
| [新建阵营工作流（第一版）](<文档 (不要打包)/教程/BattleUniverse_新建阵营工作流_第一版.md>) | 新阵营、场景或 DLC 的整条接入链 |
| [历史原因与不可随意简化项](<文档 (不要打包)/教程/BattleUniverse_历史原因与不可随意简化项.md>) | 修改框架、合并流程或删除“重复”内容前必读 |
| [0093 骨架接入说明](<文档 (不要打包)/教程/BattleUniverse_0093骨架接入说明.md>) | 0093 两阵营骨架、Main 联动、验证与扩展 |

教程可能包含示意字段、旧命名或作者回忆。实现时以当前文件、被继承模板和实际游戏行为交叉核实，不照抄示例数值或凭空补造字段。

## 2. 工作区地图

```text
units/
├─ GW_BattleUniverse_Main/          # 通用框架、开局与系统实体、公共占位入口
├─ GW_BattleUniverse_DLC_0079/      # UC 0079 内容
├─ GW_BattleUniverse_DLC_0087/      # UC 0087 内容
├─ GW_BattleUniverse_DLC_0093/      # UC 0093 开发骨架（空阵容/科技/生产）
├─ GW_BattleUniverse_DLC_SEED/      # SEED 内容
├─ 文档 (不要打包)/                 # 教程、TODO、代码表与编辑器插件
├─ 资源 (不要打包)/                 # 原始贴图、工程素材与压缩包
├─ README.md
└─ 当前为v159版本.txt
```

原有四个游戏包各有 `mod-info.txt`、`all-units.template`、`Resource/`、`Template/` 和 `Units/`。检查时四包元数据标题均为 V159，`minVersion` 均为 `1.15p11`；版本调整以实际发布任务为准。

| 路径（相对于各游戏包） | 职责 |
|---|---|
| `mod-info.txt` | 包名、引擎最低版本、缩略图和音乐配置 |
| `all-units.template` | 包级公共配置与资源定义，影响范围大 |
| `Units/BattleUnits/` | 战斗单位及其状态变体，也包含武器、盾牌和驾驶员目录 |
| `Units/BattleUnits/Weapon/{Beam,Cqb,Shell,Sp}/` | 可复用武器及特殊能力定义 |
| `Units/BattleUnits/Shield/` | 公共盾牌；专用盾牌也可能在机体 `Image/` 中 |
| `Units/BattleUnits/Pilot/` | 驾驶员定义、模板、图像及阵营/年代配置 |
| `Units/Buildings/` | HQ、工厂、建筑槽、据点等实体与模板 |
| `Units/Buildings/Factory/UnitList/` | 生产定义和阵营分类列表，并非战斗单位本体 |
| `Units/TechTree/` | `Button`、`Core`、`Mod`、`Tech`、`UnlockedListMarker` |
| `Units/SkillsUnits/` | 支援技能功能实体，需追踪生成、消息、效果及清理 |
| `Units/DLCMarker/` | DLC 加载/存在标记，当前三个 DLC 均有此目录 |
| `Template/Unit/` | 战斗框架、图形、动画、AI 和技能等公共逻辑 |
| `Template/Building/`、`Template/UI/`、`Template/Event/` | 建筑、UI 和事件模板；各包目录并不完全一致 |
| `Resource/Image/`、`Resource/Sound/`、`Resource/Music/` | 公共图片、特效、音效、语音和音乐 |

Main 还包含 `Maps/`，以及 `Units/CommonUnit`、`CVUnits`、`DelAllVanillaUnits`、`EventUnits`、`GameManager`，和 `Template/DamageChecker`、`DetectMarker` 等系统内容。没有模型或不能战斗的单位也可能是核心管理器。

2026-10-22 文件遍历快照（不含 `.git`，新增本指南前）：共 22,726 个文件，其中 PNG 14,750、GW 3,999、INI 2,593、OGG 1,240。Main 3,890、0079 7,988、0087 6,737、SEED 3,837；其余为文档、素材及根文件。此数字仅用于理解规模，不是校验基线。

## 3. 配置与资源约定

- `.ini` 是单位或配置定义；新增可复用模板按 README 使用 `.gw`。已有框架也使用 `.ini`，不要为统一扩展名批量重命名。
- 遵循原文件的段落结构、大小写、编码、换行和注释风格，中文文本应正确保存。新增文档使用 UTF-8，避免无关格式化。
- 保留 `copyFrom` 顺序、三引号多行值、逗号、`${...}` 宏、`@define`、`@global`、`@memory` 和 `@copyFromSection` 语法。
- 不要使用普通 INI 解析器直接读写整文件：项目有模板宏、多行表达式及重复段落等扩展写法。空段也可能参与继承覆盖，不能仅因内容为空就删除。
- `ROOT:` 文件路径按当前 MOD 包根目录检查；相对路径按当前文件及引擎继承规则核实。其他包有同名文件不能证明本包资源引用有效。
- 文件引用和单位 ID 引用分别检查：`copyFrom`、图片、音效指向文件；`produceUnits`、`spawnUnits`、`convertTo`、`attachments_addNewUnits` 等通常使用实体 ID。
- 图片统一用 `.png`，音效和音乐统一用真正转码后的 `.ogg`，不能仅改后缀。
- 单机专用身体、武器或盾牌图片可放机体 `Image/`；图标、UI、公共特效和声音优先复用 `Resource/`。
- 不要把同一 BGM 重复加入所有包。不要把 `文档 (不要打包)`、`资源 (不要打包)` 当运行时依赖或直接打进发布包。
- 命名尽量统一目录、文件和 `name`，但尊重已有共享目录和变体结构；`_CloseState`、`_OverLine`、`_MA`、炮塔等相关实体需一并追踪。

## 4. 单位制作与修改

基础参考位于 `GW_BattleUniverse_DLC_0079/Units/BattleUnits/`：

| 参考文件 | 适合的扩展方向 |
|---|---|
| `RGM_79/RGM_79.ini` | 标准 MS 最小战斗闭环 |
| `RGM_79/RGM_79_Commander.ini` | 复用原型图片，追加指挥技能及武器 |
| `RGM_79L/RGM_79L.ini` | 轻装高机动，重新分配耐久、续航与机动 |
| `RGC_80/RGC_80.ini` | 背包火炮、距离/随机攻击选择、部件损坏联动 |
| `RGM_79_D/RGM_79_D.ini` | 专用武器、推进和环境限制；实际 ID 含 `_D` |

1. 复制最相近案例，修改 `[core] name`、自身 Tag、中英文名称/说明、图标及混选条件。新实体 ID 应检查冲突；Main/DLC 有意设计的占位覆盖除外。
2. 普通人形 MS 先保留 `BattleUnit_Framework_MS.ini`、`BattleUnit_Graphics_MS.ini` 和必要动画、驾驶员、特效引用。其他类型应选择对应现有框架。
3. 在 `[core]` 配置 HP/护盾，在 `[hiddenAction_InitializeStats]` 的 `setUnitMemory` 中调整 EN、DP、机动、射程、能力、部件强度和地形适应性。不要只改显示值或跳过初始化链。
4. 替换身体 decal 与图标路径，尽量沿用画布、关节中心和部件比例；小偏移优先局部覆盖 decal，不改全局图形模板。
5. 先接通一把远程、一把近战武器及必要的损坏降级行为；保持 `Attack` 消息、距离条件、`nowWeaponIndex` 和武器可见性一致。
6. 检查近远距离边界、随机分支覆盖、部件完好条件，避免空白区或多武器错误同时触发。`EquipmentIndex` 表示装备组合，不等同于当前武器索引。
7. 最小闭环通过后，逐项增加护盾、多装备、特殊推进、随机武器、驾驶员条件和主动技能，每加一个系统单独验证。
8. 派生改造沿用 `CustomUnit.gw` 与 `template_CustomUnit`，核对目标 `UnitID`、`Unlock_...`、费用和装备重置；目标单位必须具备自身初始化，不能依赖改造入口补齐。

教程称驾驶员统一在 Main，但实际 Main 与三个 DLC 均有 `Units/BattleUnits/Pilot/`。新增或修改时应追踪当前 `PilotType`、默认驾驶员、正式定义/占位及覆盖关系，不能推断其他包没有驾驶员内容。

## 5. 科技与工厂接入

始终核对这条命名链：

```text
单位 name = 单位自身 Tag = 科技注册 UnitID = 工厂 UnitID = 实际生产目标
研究完成消息 Unlock_<ID> → Get 接收 → 队伍 Unlock_<ID> Tag → 生产条件
```

科技不一定与单位一对一；同一研究项目可以解锁多个单位。不要假设每台机体都必有一个 `Tech_<单位ID>` 节点。

以联邦 0079 为例，以下路径相对于 `GW_BattleUniverse_DLC_0079/`：

| 接入位置 | 检查内容 |
|---|---|
| `Units/TechTree/Tech/Faction/EFSF_0079/EFSF_0079_Get.ini` | 接收解锁事件并添加队伍 Tag |
| 同目录 `EFSF_0079_Send.ini` | 对应发送/同步注册 |
| 同目录 `TechList_EFSF_0079.ini` | 科技生命周期、费用、时间、前置和完成解锁 |
| 同目录 `Common/` | 科技标记实体、图标、名称和研究条件 |
| `Units/TechTree/Core/Faction/EFSF_0079/` | `TechTree_UI_Page_...` 的节点/连线，必要时更新 `UI_Main` |
| `Units/Buildings/Factory/UnitList/EFSF_0079/Units/Land/<ID>.gw` | 面板、费用、时间、编制、驾驶员、装备及自动生产 |
| `Units/Buildings/Factory/UnitList/EFSF_0079/EFSF_0079_UnitList_Land.ini` | 在 `copyFrom` 中纳入生产定义 |
| `Units/Buildings/Factory/Faction/EFSF_0079/Factory_EFSF_0079_Land.ini` | 继承列表、阵营筛选和 AI 选择调用 |

- 先让单位本体可加载，再接科技，再接生产；通常无需修改科技树 `Mod`、核心 `.gw`、`Factory.ini` 或 `UnitTemplate.ini`。
- 教程里的 `[tech_NEW_UNIT]` 属示意；实际 `TechList` 使用多段 `hiddenAction` 与模板组合，复制真实研究项目的完整生命周期。
- 科技页面只负责 UI 表现，创建节点不等于注册解锁，更不等于加入工厂。
- 生产定义不仅要改 `UnitID`，还要改 `@memory`、面板关闭、Action、队列、自动生产及 `produceUnits` 中残留的参考 ID。
- 按实际生产用途选择 Land、Air 或其他现有分类；小队费用按整队计算，并核对 `PilotType` 和 `EquipmentIndex`。
- 工厂可同时继承多个阵营列表，依靠 `FactionVisible` 和解锁条件筛选，不能据此删除“别的阵营”列表。
- AI 可能还有工厂内显式的 `AutoProduce_...` 调用列表；仅新增生产定义中的自动 Action 不足以证明 AI 已接入。
- 是否修改 `UnlockedListMarker` 应搜索同类参考项和实际同步链，不能只凭目录名增加注册。

## 6. HQ、场景、阵营与建筑链

普通新增单位通常止于本体、科技、工厂。只有涉及开局赠送、初始科技、新阵营/年代/模式等内容时才扩展到 HQ。

```text
Main HQ_Start → 房主 HQ_Start_Host / HostOption
→ GameManager_Start 保存并广播 Setting_GameMode
→ 各玩家模式 HQ → 阵营选择与 FactionIndex、起始 Tag
→ GameStart → 正式阵营 HQ + TechTree_Core 附件 + 地面/宇宙初始部队
```

- 修改初始参数应追踪 HostOption、GameManager、所有玩家 HQ，不能只修改房主局部变量。
- 默认科技依赖起始 Tag、`UnlockedListMarker`、`TechTree_Core` 挂载及 TechList 对 Tag 的响应。核对附件 ID 和槽名，例如 `TechTreeMarkerSlot`。
- 初始部队应查 `ConvertToFaction_..._Ground/Space` 和 `tileMode`，不一定来自工厂。
- 新建阵营按“场景入口 → 阵营选择 → 一页空科技树 → 基础科技与建筑 → 完整内容”分阶段接入。
- 新场景需核对 HostOption Marker/Page、场景 Index、`HQ_GetMode.ini`、Main 占位与 DLC 模式 HQ；随后核对阵营选择到正式阵营 HQ 的独立转换。
- `FactionIndex` 带有系列/场景/阵营编码含义，新增前搜索完整值与范围判断，不能随意重排编号。教程的位数解释只是现有案例，不能当作所有扩展的固定规范。
- 建筑接入需同时检查公共建筑 Get/Send、`Common_Buildings_Slot.gw`、DLC BuildingSlot、StrategicLocation、工厂/建筑列表和阵营 Tag。
- 新建阵营教程为第一版。遇到表述不清，分别确认模式选择 HQ、阵营选择 Action 和最终阵营 HQ，不把它们视为同一个实体。

## 7. 公共副本与不可随意简化项

引擎不能跨 MOD 直接读取资源文件，各包保留公共文件副本。单位 ID 的占位、替换和转换机制与跨包文件读取是两回事。

修改共享内容的步骤：搜索各包同路径/同职责文件 → 比较现有差异 → 确认公共接口与场景专用条件 → 同步应一致的改动 → 检查相关组合。

本次抽样中，四包 `all-units.template` 与 `BattleUnit_Framework_MS.ini` 分别具有相同哈希，但 `Common_Buildings_Slot.gw` 四包哈希不同。因此不能把某一包的 `Template/`、`Mod/` 或 `Resource/` 整目录无差别覆盖到其他包，也不能默认 Main 的任意副本都是唯一最新实现。

以下结构在理解目的并完成等价验证前保留：

- Main 同名占位单位、DLC `overrideAndReplace` 与 `convertTo`：支持可选 DLC、稳定入口和混装。
- 隐藏单位、附件和 Marker：可能承担管理器、状态存储与消息路由。
- Tag、全局队伍 Tag、Resource、memory 的多种状态表示：各系统可读取的作用域不同，不能视为同义变量合并。
- 多层 Get/Send、Tech、UnitList、BuildSlot 注册：分别负责事件、权限、筛选和 UI，不能改成静态 `canBuild` 绕过。
- `Step1/Step2/Step3`、队列和延时：历史文档记录同 tick 随机值重复问题；现有吉姆小队后两步有 `1.0s` 间隔。不要合并成一次 `*3` 生产而改变随机驾驶员行为。
- 多层 Action：可能等待 Tag 更新、附件、转换或新实体初始化，不能只因语句少就合并。

新增相关注释可沿用 `[ENGINE_WORKAROUND]`、`[DO_NOT_SIMPLIFY]`、`[CROSS_DLC]`、`[ORDER_DEPENDENT]`、`[TICK_DEPENDENT]`、`[RANDOM_DEPENDENT]`、`[PLACEHOLDER]`、`[HIDDEN_DEPENDENCY]`、`[LEGACY_REASON]`，并说明具体依赖。

## 8. 查找、验证与交付

优先用 `rg --files` 定位文件，再在相关包的 `.ini`、`.gw`、`.template` 中搜索。避免将全仓二万余条路径或媒体内容直接输出。

```powershell
# 从工作区根目录执行；ID 换成本次目标
rg --files GW_BattleUniverse_DLC_0079 | rg 'RGM_79|TechList|UnitList'
rg -n -F 'RGM_79' GW_BattleUniverse_DLC_0079 -g '*.ini' -g '*.gw' -g '*.template'
rg -n 'FactionIndex|convertTo:|attachments_addNewUnits:' GW_BattleUniverse_Main/Units/Buildings/HQ
git status --short
git diff --check
```

若受当前运行身份影响出现 Git `dubious ownership`，可针对本仓库使用命令级 `git -c safe.directory=E:/RustedWarfare_Reunion/mods/units ...` 检查，不为读取状态修改全局 Git 配置。

静态检查至少覆盖：

- 文件路径存在且属于正确包，继承与段落引用有效；图片、音效和图标无遗漏。
- 新 ID、Action、Tag、消息和资源名匹配，复制范围内无意外残留；有意复用的原型贴图和技能名保留。
- 单位名冲突区分意外重复与显式占位覆盖；不能把跨包所有同名项统一报告为错误。
- 武器条件、索引、部件损坏和显示一致；科技前置、解锁、页面节点/连线及生产队列完整。
- 公共改动列出同步过的副本及保留的场景差异；检查差异中没有无关文件。

初次项目梳理时未发现 MOD 自动构建或测试脚本；后续部署的 MCP 工具自检见第 9 节。`文档 (不要打包)/工具/` 的 XLSX 代码表与 VSIX 编辑器插件属于辅助资料。不要编造构建命令，也不要声称静态文本检查证明游戏行为正确。

按改动范围安排游戏内验证：

| 范围 | 必要行为验证 |
|---|---|
| 单位本体 | 加载/生成、部件显示、移动转向、索敌、远近攻击、受伤、部件损坏、死亡 |
| 装备与技能 | 装备索引、收纳/持用贴图、损坏降级、驾驶员条件、冷却/消耗、改造初始化 |
| 科技与生产 | 未解锁限制、前置/费用/时间、完成解锁、正确阵营/工厂、生产数量与驾驶员、AI 自动生产、存档重载 |
| HQ 与公共层 | 房主/非房主同步、AI 阵营选择、HQ 转换、附件、默认科技、地面/宇宙初始部队 |
| DLC 兼容 | 根据影响检查 Main 单独加载、Main + 目标 DLC、多 DLC 混装及旧阵营回归 |

无法启动游戏时，完成可做的静态检查，并明确列出尚未执行的游戏内测试。最终交付说明修改了什么、影响哪些包、同步了哪些公共文件、已验证什么及剩余限制。不要把“文件存在”“单位能生成”“整条玩法链可用”混为一谈。

## 9. 本地 MCP 工具

已部署 `rw-modding-mcp`，Codex 项目配置在 `.codex/config.toml`。操作和恢复方式见 [部署说明](<文档 (不要打包)/工具/rw-modding-mcp_部署说明.md>)。

- 优先用 `lookup_key` 查字段，用 `get_ref` 查配对规则，用 `search_source` 核对本机引擎实现，用 `lint` 检查改动文件或相关包。
- 工具为只读；本地增加了目录扫描 `.gw` 支持，更新上游后需要检查适配是否保留。
- `lint` 结果须结合模板继承、扫描范围、跨包占位和教程约束人工判断；不能代替游戏内验证，也不能作为自动批量修复依据。
- 工具仓库、虚拟环境、下载器和反编译产物被 Git 忽略，不属于 MOD 发布内容。源码索引绑定当前游戏版本，游戏更新后重新生成。
- 配置变更需要重启会话加载。缺少 MCP 连接时，可用部署说明中的命令行方式，不要声称当前会话已自动获得工具。


## 10. UC0093 骨架

`GW_BattleUniverse_DLC_0093` 为已接入 Main 的空内容骨架，见 [接入说明](<文档 (不要打包)/教程/BattleUniverse_0093骨架接入说明.md>)。阵营键严格使用 `0093_EFSF`、`0093_NZN`，FactionIndex 分别为 `1030101`、`1030201`，场景 stageIndex 为 `1020`。

Main 的场景 Page3、HQ_GetMode 和占位目标已连接；GameManager 复用原有通用广播。旧四包建筑槽/据点副本均追加 0093 分支，新包自身保留多场景回转。不要只改新 DLC 而遗漏这些公共入口。

BattleUnits 只保留 Shield、Weapon；科技节点与生产列表为空，不要为了补齐报错而把 0087 的整台机体或整条科技复制回来。资源来源、临时图片和改动前基线在 `文档 (不要打包)/分析/`，后续维护应保留这些可追踪信息。
