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
├─ GW_BattleUniverse_DLC_0093/      # UC 0093 开发包（基础单位与中排占位科技）
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
- `[ENGINE_WORKAROUND]` 引擎拼接三引号多行表达式时不会自动插入空格；`500 ` 后的空格可能是分词所必需的，禁止对配置整文件批量 `rstrip`。新增长条件优先写单行，或显式保留操作符两侧空格；格式改动必须在最终文件上重新做引擎加载检查。
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

`GW_BattleUniverse_DLC_0093` 为已接入 Main 的开发包，见 [接入说明](<文档 (不要打包)/教程/BattleUniverse_0093骨架接入说明.md>)。阵营键严格使用 `0093_EFSF`、`0093_NZN`，FactionIndex 分别为 `1030101`、`1030201`，场景 stageIndex 为 `1020`。

Main 的场景 Page3、HQ_GetMode 和占位目标已连接；GameManager 复用原有通用广播。旧四包建筑槽/据点副本均追加 0093 分支，新包自身保留多场景回转。不要只改新 DLC 而遗漏这些公共入口。

0093 每阵营第一页接入 Base 和 Mid02～Mid05 四个中排科技（02/03 已为开发计划，04/05 仍占位）；前置、研究费用和时长沿用 0087 中排节奏。展示占位定义位于 `Units/TechTree/PlaceholderUnits/`，不进工厂、不生成部队，不是新增战斗单位。BattleUnits 除 Shield、Weapon 外，仅有 `RGM_86R_0093_EFSF`、`SalamisClassKai_0093_EFSF`、`AMX_101_0093_NZN`、`MusaiClassFinalType_0093_NZN` 四种已接入生产的战斗单位及必要炮塔/继承模板，另有 `RGM_89`、`RGC_90`、`RGZ_91`、`RX_93`、`RX_93_Test`、`AMS_119`、`AMS_119H`、`MSN_03`、`MSN_04` 九种吉姆III属性空壳（八台已接入第2/3开发计划和地面／宇宙工厂，仅 RX_93_Test 待接入）；不要复制其他整条科技或未请求单位。Base 解锁 Main 共用基础建筑和 Land/Mega/Space/Space_Mega 工厂，Mega 暂无生产项，Air/Aqua 尚未解锁。HLV 的 0093 基础设施变体在 Main。资源来源、临时图片和改动前基线在 `文档 (不要打包)/分析/`，后续维护应保留这些可追踪信息。

0093 普通驾驶员和士官按 0087 结构放在 Main 的 `Units/BattleUnits/Pilot/0093/Common/`；总 Marker 已接入两个阵营，T1/T2 学院有普通驾驶员入口。复用的 0087 贴图在 Main 另存为 0093 命名，勿误判为 DLC 缺少 Pilot 目录。详情见接入说明的“普通驾驶员接入”。

## 11. 火线纵横 P1

`GW_BattleUniverse_DLC_CR_P1` 是独立主模式的第一阶段骨架，见 [接入说明](<文档 (不要打包)/教程/BattleUniverse_CR_P1骨架接入说明.md>)。菜单使用既有单位 / 附属单位系统，顺序为主模式（起源 / 火线纵横）→ 子模式（对决 / 场景 WIP）。

- `gameMainMode=1` 为起源，`2` 为火线纵横；`gameSubMode=1` 为对决。原起源仍是 `(1,1)`；火线纵横 P1 使用 `(2,1,stageIndex=2000)`。不要按照旧 `VS_GE` 文件名推断字段层级。
- 阵营为 `CR_Order` / `9010101`、`CR_Resistance` / `9010201`、`CR_Chaos` / `9010301`。阶段级实体用 `CR_P1`，阵营键不含 P1。
- Main 保留八个 CR P1 入口占位；P1 覆盖。六包的建筑槽 / 据点、现有 HQ_GetMode 副本都已接入新路由，后续保留旧分支和包间差异。
- Base 仅解锁基础建筑和四类工厂；全部生产列表为空。未接入驾驶员、HLV 或战斗单位。不能从 0093 复制生产动作后遗留自动生产和解锁引用。
- `GameManager_CR_VS` 继承 Main 的 `GameManager_VS`，专用逻辑优先在 CR 实例中覆盖。
- 只读静态检查：`python -B '文档 (不要打包)/工具/验证_CR_P1骨架.py'`。该检查不代表引擎加载或实际对局通过。

0093 吉姆III已切换为 0087 AEUG 身体贴图和图标，名称与数值保留。九种空壳在各自 INI 显式复制初始化数值，临时继承本包吉姆III Base 模板及模型/武器；阵营 Tag 和默认驾驶员已各自覆盖，勿把这些开发空壳视为已完成对应机型。

0093 第2/3科技：联邦杰刚计划解锁 RGM_89/RGC_90，新高达计划解锁 RGZ_91/RX_93；新吉翁基拉德卡计划解锁 AMS_119/AMS_119H，沙扎比计划解锁 MSN_03/MSN_04。内部 Tech_0093_<阵营>_Mid02/Mid03 ID 保持，03→04 的前置不改；费用沿用0087，生产临时沿用吉姆III三种装备小队，不赠送部队。

RGM_89、RGZ_91、RX_93 已移植 BattleUnits.zip 的本机身体素材，分别通过 `<ID>_Graphics.gw` 局部覆盖；其余空壳仍用吉姆III临时模型。不要恢复这三台的旧吉姆装饰层，也不要从外部INI引入武器/数值；灵格斯采用人形，牛高达浮游炮背包仅为静态外观。源包缺公共图形模板，骨架锚点和动画沿用本项目。

0093 灵格斯形态：人形 `RGZ_91`、飞机 `RGZ_91_MA`、地图适配 `RGZ_91_MA_OverLine`。科技/工厂入口保持 RGZ_91，实际生产 MA；只允许按原生 ExitUnit 消息链单向脱出，人形必须显式重置 flyUnit=0。飞机暂时无武装，不导入 GM III 武器模板；人形保留现有临时武器。详见 0093 接入说明与 `验证_0093_灵格斯BWS.py`。

0093 灵格斯武装已接入：MA 使用专用 BWS 双联光束炮／导弹，人形使用专用步枪、腕部／腰部榴弹、火神炮、伪装气球和黄色军刀。此状态取代此前“飞机无武装、人形临时吉姆III武器”的说明。RGZ_91 不再继承吉姆III Base.gw；工厂旧装备索引兼容同一武装，MG/BZ 入口隐藏并保留旧队列 ID，AI 均进入标准编制。飞机米加粒子炮与人形蓄力格斗仍未接入。回归使用 `验证_0093_灵格斯武装.py` 与 BWS、Base 科技检查。

0093 单位遵循单INI布局，临时 Base.gw／Graphics.gw 已合入本体并移除。单位内不额外声明武器 Fire_Step；开火必需条件尽可能集中到专用武器模板，单位负责距离／随机选择、索引与贴图。灵格斯腕部榴弹、黄色军刀分别使用 EF_RGZ_91_ArmGL_L.gw、EF_RGZ_91_BeamSaber_AF_Yellow.gw。MCP 已更新至 17c658d，保留 .gw 补丁，新增 explain_actions；新版工具列表需重启会话加载。

0093 的 RGM_89／AMS_119 已接入专用武装，勿恢复吉姆III临时武器。杰刚装备0=BR、1=BZ、旧2兼容BZ；基拉多加固定光束机枪＋下挂榴弹、光束斧、左手红色海蛇和双发铁拳。海蛇使用独立实体／回调及外部原图 NZN_AMS_119_SeaSerpent_Red.png；开火条件及Step均在专用武器内，单位只保留选择与显示。旧工厂队列ID保留，实际界面／AI仅使用真实装备；基拉多加现已移植外部AMS-119身体及单眼贴图，基础属性仍为临时蓝本。验证脚本为 验证_0093_杰刚基拉多加武装.py。

基拉多加身体贴图补齐（2026-10-24）：已从外部 AMS-119 复制13张身体图片，在 AMS_119.ini 内替换躯干、头、四肢和单眼，移除吉姆III身体引用。单眼保留原配置偏移2.5、缩放1.5；闭合头部复用本机普通头部图。Body_2仅保留素材，与外部原单位一样暂不启用。武器、驾驶员、属性、科技和生产不变。
