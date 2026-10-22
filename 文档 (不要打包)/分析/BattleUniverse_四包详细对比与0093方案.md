# Battle Universe 四包详细对比（0093 制作前）

比较范围：Main、0079、0087、SEED 四包全部文件，按相对路径、字节数和 SHA-256 对比。未以文件时间推断版本新旧。

完整逐文件结果见 `BU_四包文件对比_0093制作前.csv`，原始哈希基线见 `BU_四包基线_0093制作前.json`。本报告保存的是改动前状态。

## 文件与体积

| 包 | 文件数 | INI | GW | PNG | OGG | MiB |
|---|---:|---:|---:|---:|---:|---:|
| Main | 3890 | 721 | 440 | 2339 | 350 | 87.8 |
| DLC_0079 | 7988 | 918 | 1414 | 5302 | 340 | 83.54 |
| DLC_0087 | 6737 | 623 | 1274 | 4495 | 327 | 72.92 |
| DLC_SEED | 3837 | 331 | 871 | 2394 | 223 | 50.3 |

## 两两比较

相同/不同只比较双方都有的同路径文件。

| A | B | 同路径同内容 | 同路径不同内容 | 仅 A | 仅 B |
|---|---|---:|---:|---:|---:|
| Main | DLC_0079 | 2848 | 82 | 960 | 5058 |
| Main | DLC_0087 | 2751 | 43 | 1096 | 3943 |
| Main | DLC_SEED | 2478 | 43 | 1369 | 1316 |
| DLC_0079 | DLC_0087 | 3952 | 94 | 3942 | 2691 |
| DLC_0079 | DLC_SEED | 2747 | 69 | 5172 | 1021 |
| DLC_0087 | DLC_SEED | 2615 | 25 | 4097 | 1197 |

## 各系统目录

| 目录 | Main | 0079 | 0087 | SEED |
|---|---:|---:|---:|---:|
| `Template/` | 288 | 248 | 250 | 240 |
| `Resource/Image/` | 1588 | 1846 | 1917 | 1410 |
| `Resource/Sound/` | 322 | 317 | 317 | 209 |
| `Resource/Music/` | 28 | 23 | 10 | 14 |
| `Units/BattleUnits/Weapon/` | 751 | 1293 | 1271 | 737 |
| `Units/BattleUnits/Shield/` | 191 | 191 | 194 | 191 |
| `Units/BattleUnits/Pilot/` | 167 | 161 | 141 | 142 |
| `Units/Buildings/HQ/` | 64 | 18 | 17 | 14 |
| `Units/Buildings/Factory/` | 38 | 341 | 229 | 116 |
| `Units/Buildings/BuildingSlot/` | 10 | 5 | 5 | 5 |
| `Units/Buildings/StrategicLocation/` | 8 | 6 | 6 | 6 |
| `Units/Buildings/Beacon_ACE/` | 4 | 44 | 11 | 9 |
| `Units/TechTree/` | 18 | 68 | 82 | 44 |
| `Units/SkillsUnits/` | 24 | 13 | 9 | 6 |
| `Units/DLCMarker/` | 0 | 2 | 2 | 2 |
| `Units/GameManager/` | 3 | 0 | 0 | 0 |
| `Units/CommonUnit/` | 48 | 0 | 0 | 0 |
| `Units/EventUnits/` | 54 | 0 | 0 | 0 |
| `Units/CVUnits/` | 4 | 0 | 0 | 0 |
| `Maps/` | 45 | 0 | 0 | 0 |

## 四包共有但内容不同的配置

这里只列 INI/GW/template。完整图片、声音和其他差异见 CSV。差异可能是场景专用逻辑或公共副本漂移，不能据此判断哪份更新。

- `Resource/Image/Fx/Common/Common_Explosion_1.gw`
- `Template/Building/Common_Buildings.gw`
- `Template/Building/Common_Buildings_Slot.gw`
- `Template/Unit/BattleUnit_Framework_Ships_Aircraft.ini`
- `Template/Unit/BattleUnit_Graphics.ini`
- `Template/Unit/Skill/Exam_Off.gw`
- `Template/Unit/Skill/Exam_On.gw`
- `Template/Unit/Skill/HADES_Off.gw`
- `Template/Unit/Skill/HADES_On.gw`
- `Template/Unit/Skill/HADES_PR2_Off.gw`
- `Template/Unit/Skill/HADES_PR2_On.gw`
- `Template/Unit/Skill/Transform_LandFly.gw`
- `Units/BattleUnits/Weapon/Sp/Common_ReEntry_HLV.gw`
- `Units/BattleUnits/Weapon/Sp/Common_ReEntry_HLV_FromSpace.gw`
- `Units/BattleUnits/Weapon/Sp/Common_ThunderStrike.gw`
- `Units/Buildings/HQ/Mod/HQ.ini`
- `Units/Buildings/HQ/Mod/HQ_Faction.ini`
- `Units/Buildings/StrategicLocation/Mod/StrategicLocation.ini`
- `Units/TechTree/Mod/TechList.gw`
- `Units/TechTree/Tech/Faction/Common/Common_Building_Get.ini`
- `Units/TechTree/Tech/Faction/Common/Common_Building_Send.ini`

## 关键文件内容分组

同组表示字节完全相同。

- `all-units.template`：Main/DLC_0079/DLC_0087/DLC_SEED
- `Template/Building/Common_Buildings_Slot.gw`：Main；DLC_0079；DLC_0087；DLC_SEED
- `Template/Unit/BattleUnit_Framework_MS.ini`：Main/DLC_0079/DLC_0087/DLC_SEED
- `Units/Buildings/HQ/Mod/HQ.ini`：Main；DLC_0079/DLC_0087/DLC_SEED
- `Units/Buildings/HQ/Mod/HQ_Faction.ini`：Main/DLC_0079/DLC_0087；DLC_SEED
- `Units/Buildings/HQ/Mod/HQ_GetMode.ini`：Main；DLC_0079；DLC_0087；DLC_SEED（不存在）
- `Units/Buildings/StrategicLocation/Mod/StrategicLocation.ini`：Main；DLC_0079；DLC_0087；DLC_SEED
- `Units/Buildings/Factory/Mod/Factory.ini`：Main/DLC_0079/DLC_0087/DLC_SEED
- `Units/TechTree/Mod/TechTree_Core.gw`：Main/DLC_0079/DLC_0087/DLC_SEED
- `Units/BattleUnits/Weapon/Template/Cqb_BaseProjectile.ini`：Main/DLC_0079/DLC_0087/DLC_SEED


## 职责与内容差异

| 系统 | Main | 0079 | 0087 | SEED |
|---|---|---|---|---|
| 世界观/场景 | 公共管理器、场景选择和占位定义 | UC 0079，一年战争；含 T2 变体 | UC 0087，格里普斯及后续扩展；含 T2 变体 | CE71 |
| 阵营键 | 提供各阵营 HQ 占位 | EFSF_0079、ZEON_0079 | AEUG_0087、TITANS_0087、NEO_ZEON_0087 | OMNI_CE71、ZAFT_CE71 |
| 正式开局 | HQ_Start/HostOption、GameManager_Start/VS | 年代 HQ 接管、选阵营、发初始部队 | 同一开局链，但三阵营、不同部队和阶段 | 同一接口，CE 场景与两阵营 |
| 科技 | 核心与已解锁列表占位、公共建筑事件 | 两阵营研究、页面和单位解锁 | 三阵营研究、更多页和单位解锁 | 两阵营研究、CE 单位解锁 |
| 工厂 | 通用框架与基础设施 | 陆/空/水/大型/宇宙等生产列表 | 以陆/大型/宇宙等分类为主，按现有阵营细分 | 复用同一生产框架，生产 CE 内容 |
| 建筑槽与据点 | 通用实体和覆盖所有旧场景的转换入口 | 本包副本偏向 0079 转换 | 本包副本偏向 0087 转换 | 本包副本偏向 CE71 转换 |
| 战斗目录 | 少量系统/通用实体、驾驶员、武器底层 | 大量 0079 单位及 UC 武器实现 | 0087 单位及新增武器、三张额外盾牌资源 | CE 单位及对应武器；仍含公共 UC 资源 |
| 音乐 | 公共曲库，已有 0093 曲目 | 另有 23 个音乐文件 | 另有 10 个音乐文件 | 另有 14 个音乐文件 |

这些包是同一套脚本接口的不同内容实现，不是能够完全互相替换的目录副本。尤其不能将 DLC 的单场景 BuildingSlot/StrategicLocation 模板覆盖到 Main 的多场景版本。

### 实际差异案例

- 四包 `all-units.template` 和 `BattleUnit_Framework_MS.ini` 完全相同，可复用其接口。
- `Common_Buildings.gw`：Main 比 0087 多声明 `finalBeamDefPlus/finalShellDefPlus/finalCqbDefPlus`。0093 采用 Main 版本保留这些公共字段。
- `BattleUnit_Graphics.ini`：0087 的推进显示支持 `skillRules` 条件，而 Main 的表达式不同。0093 优先采用 0087 版本，没有用 Main 整体覆盖。
- `Common_Buildings_Slot.gw` 和据点 `StrategicLocation.ini`：Main 有旧 UC/CE 的多场景分派，DLC 各有自己的分派。0093 自身采用 Main 的完整分派并追加 0093；旧四包只追加 0093，不移除原分支。
- Main 的武器目录主要是底层/通用定义，而 0079/0087 含大量具体可继承 `.gw`。仅复制 Main 会漏掉这些模板；仅复制 0087 又会遗漏其他包独有资源。
- 驾驶员不只在 Main；四包均有 Pilot 树。此次按要求不将任何 Pilot 目录或实际机体带入 0093。
- 0079/0087 有 `HQ_GetMode.ini` 副本，SEED 没有该文件；没有为了目录一致而向 SEED 添加不被引用的副本。

## 0093 的来源选择与范围

可复用文件按“0087 → 0079 → SEED → Main”的顺序取同路径首份，补齐各包独有路径；`Common_Buildings.gw`、0093 的建筑槽/据点分派单独选用 Main。不同来源并不意味着更新或正确性高低，这只是本次明确的合并策略。

逐文件来源见 `0093_公共资源来源.csv`；存在不同内容的同路径取舍见 `0093_同路径公共副本取舍.csv`；新建键、图片别名、移位资源和原文件改动清单见 `0093_构建清单.json`。

- 保留 Weapon 的 Beam、Cqb、Funnel、SetUp、Shell、Sp、Template 分类，含弹体、浮游炮辅助实体与图片。这些辅助 INI 是武器机制，不是机体阵容。
- BattleUnits 顶层仅 Shield、Weapon；没有继承 0079/0087/CE 的机体、舰船、小队或驾驶员目录。
- 公共 Template、图片、特效和音效在包内保持文件引用闭合；不复制任何 BGM。Resource 中的旧图标/CG 是供后续复用的素材，不代表注册了旧战斗单位。
- 原本借用机体/Pilot 目录的六张图片移到 `Resource/Image/Weapon/Legacy/`，引用随之调整，不为几张图恢复整台机体目录。
- 为缺失图片和两阵营临时徽标建立别名，清单记录原图来源；没有伪造专用贴图。
- 只在新包中修正两处遗留武器模板引用：Mortar Lv2 的目录和 NoAqua 的旧 Dash 名称；原包武器定义不改。
- 新包不含战斗阵容、研究节点、默认工厂解锁或初始部队。工厂分为两阵营各六类，生产列表为空；Get/Send 与建造列表仅预接入这些空壳。

## 与 Main 的完整接入链

```text
地面/宇宙的场景 Page3 → HostOption_VS_GE_Common_UC0093
→ VS_Stage(Index=1020) → HostOption_Core.stageIndex
→ Setting_GameMode → GameManager_Start 保存并逐 HQ 广播
→ HQ_GetMode(stageIndex==1020) → HQ_VS_GE_UC0093
→ 选择 0093_EFSF / 0093_NZN，FactionIndex=1030101 / 1030201
→ ReadyOK → GameManager_VS 等待全员准备 → GameStart
→ HQ_0093_EFSF / HQ_0093_NZN + TechTree_Core_0093
→ 两阵营各一张空科技页，UnlockedListMarker_0093 已挂载

两种 FactionIndex → 0093_BuildingSlot
两种 FactionIndex → StrategicLocation_0093 → 0093_MainBuildList
未来研究 Unlock_Factory_... → Get/Send → 建造列表/建筑槽 → 空工厂 → 待填 UnitList
```

GameManager 原有广播已经通用传递 `stageIndex`，本次未修改它的三个文件；字节哈希回归检查确认不变。没有创建一个与其脱节的 0093 管理器。场景按钮受 `DLCMarker_0093` 限制，无 DLC 时不可选；Main 同时提供全部被公共转换引用的 0093 占位目标。

原有 12 个文件发生局部修改：Main 的 HostOption_Core，Main/0079/0087 的 HQ_GetMode，以及旧四包各自的建筑槽与据点转换模板。0093 自己还保留完整多场景转换，支持被其他年代阵营接管后的回转。旧场景的 Action 与原值由回归脚本逐段核对。

## 验证边界

静态结果保存在 `0093_静态连携验证.json`，隔离引擎结果保存在 `0093_引擎加载_*.json`。测试脚本和人工验收步骤见教程目录的《0093 骨架接入说明》。引擎解析通过不等于实际联网对局中的 HQ 选择、占领、附件和科技页面已完成交互验收。


## 本次验收结果

- 新 DLC：5023 个文件，约 77.74 MiB；BattleUnits 仅 Shield/Weapon，12 个空工厂，0 个研究节点，不含 BGM。
- 静态连携/旧场景回归：58/58 通过。
- 真实引擎启用加载：Main 单包、Main+0093、五包混装均完成初始化，无 MOD 加载错误。五包混装耗时约 74 秒。
- Main 的 GameManager 文件字节不变；新场景复用其原有参数广播与 ReadyOK/GameStart 流程。
- 玩家界面、联机和占领行为尚需按接入说明中的清单人工验收；未接入具体机体的武器模板没有宣称逐一实战验证。
