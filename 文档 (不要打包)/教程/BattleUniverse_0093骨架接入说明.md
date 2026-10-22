# UC0093 DLC 接入说明

0093 已接入原开局链，两阵营各有第一页科技树和一个 Base 科技，解锁基础建筑及指定的两种战斗单位。没有其他研究项目、战斗单位或开局赠送部队。

## 安装与命名

启用 `GW_BattleUniverse_Main` 和 `GW_BattleUniverse_DLC_0093`；支持与 0079、0087、SEED 混装。Main 单独加载时，0093 场景按钮受 DLC Marker 条件锁定。

| 项目 | 值 |
|---|---|
| 版本 / 最低引擎 | V159 / 1.15p11 |
| 场景 / stageIndex | `HQ_VS_GE_UC0093` / `1020` |
| 联邦阵营 / FactionIndex | `0093_EFSF` / `1030101` |
| 新吉翁阵营 / FactionIndex | `0093_NZN` / `1030201` |
| 正式 HQ | `HQ_0093_EFSF` / `HQ_0093_NZN` |
| 科技核心 / 解锁标记 | `TechTree_Core_0093` / `UnlockedListMarker_0093` |
| 建筑槽 / 据点 | `0093_BuildingSlot` / `StrategicLocation_0093` |

阵营键严格保留年代在前；不要自行改为 `EFSF_0093`，也不要沿用 `NEO_ZEON_0087`。

## 开局、建筑槽与据点

1. Main 地面/宇宙第四页（内部 Page3）提供 UC0093 场景入口。
2. 按钮发送 `VS_Stage(Index=1020)`，HostOption_Core 保存 stageIndex，经 `Setting_GameMode` 交给 GameManager_Start，随后广播到各玩家 HQ。GameManager 的通用逻辑未修改。
3. Main/0079/0087/0093 的 HQ_GetMode 副本已有 1020 路由；Main 保留模式 HQ、阵营 HQ、科技核心、解锁标记、建筑槽和据点的稳定占位。
4. 选择阵营时写入对应 FactionIndex、阵营 Tag、`Tech_<阵营>_Start`，挂载 UnlockedListMarker_0093；GameStart 后转换为正式 HQ，并挂载 TechTree_Core_0093。
5. 五包建筑槽/据点路由均能识别两个新 FactionIndex，保留旧年代转换。没有赠送战斗单位或改变地面/宇宙初始编成。
6. 正式 HQ 和 StrategicLocation_0093 均继承 `0093_MainBuildList.ini`；建筑槽保留独立的建筑附件生产 Action，二者都接收同一套 Unlock Tag。

## 第一页与 Base 科技

每阵营只有一页（`Page_00`）和一个节点：`Tech_0093_EFSF_BaseTech` / `Tech_0093_NZN_BaseTech`。节点沿用 0087 左侧起点坐标，不画通向不存在项目的连线；pageMax=0。UI、AI 打开科技页、研究 Awake/Start/Stop/Done、解锁和盟友同步链均已接入。

Base 的时间、资金、物资、科技需求均为 0。选阵营时已有 PassT0；科技核心初始化沿用 0087 的 Start_Set_Tech 分派，向当前阵营的科技 UI 发送 Unlock_Tech_<阵营>_BaseTech（byOther=1），经原有 Done → UnlockUnit → Get/Send 自动解锁基础内容，不需要手动研究或打开科技页。最初遗漏的开局分派已补齐。

| 阵营 | 战斗单位 ID | 生产位置 |
|---|---|---|
| 联邦吉姆III | `RGM_86R_0093_EFSF` | Land、Space 工厂 |
| 联邦萨拉米斯改级 | `SalamisClassKai_0093_EFSF` | Space_Mega 工厂 |
| 新吉翁卡尔斯J | `AMX_101_0093_NZN` | Land、Space 工厂 |
| 新吉翁姆塞最终生产型 | `MusaiClassFinalType_0093_NZN` | Space_Mega 工厂 |

单位从 0087 复制后使用独立 ID；舰船炮塔、段名、资源和动作引用一并处理，混装时不覆盖 0087 同型机体。吉姆III采用 0087 联邦涂装，保留标准/机枪/火箭筒三种小队；卡尔斯J保留标准三机小队。队列后两步的 1 秒间隔保留，不合并随机驾驶员生成。舰船保留炮塔、机库、伤害检测和补给/再入等原有能力。四种机体的基础数值、装备与生产费用沿用原型。

## 基础建筑解锁

双方 Base 均解锁以下内容：

- 各自 Land、Mega、Space、Space_Mega 工厂。Mega 目前无地面大型单位生产项；Air/Aqua 空壳保留，尚未解锁。
- `Refinery_Common_T3`、`Institute_Common_T2`、`SupplyDepot_Common_T2`、`Academy_Common_T2`。
- 地面 B 型机枪、防空、加农、黄色光束炮塔，以及 B 型雷达。
- 宇宙 B 型机枪、导弹、加农防御设施。
- `Wall_T2_A`、`Wall_T2_B` 和 `HLV_0093_Build`。

公共建筑实体与贴图由 Main 提供，不复制到 DLC。0093 自身增加 Common_Building_Get/Send、MainBuildList 和 BuildingSlot 的必要注册，使解锁同时到达 HQ、据点和建筑槽。建筑槽也补了经济建筑与工厂的 AI 建造分派；三类有内容工厂显式调用对应单位的自动生产 Action。

HLV 属于跨地面/宇宙的基础功能，新增 Main 的 `Units/Buildings/HLV_Build/Unit/HLV_0093_Build.ini` 和 `Units/BattleUnits/HLV/HLV_0093.ini`。它们复用 Main 原有模型、模板和音效，施工完成生成 0093 HLV，默认驾驶员按当前阵营选择；不额外引入其他战斗机体。

0087 Base 的实际完成动作没有解锁 ACE 信标。本轮保持这一范围，不复制其他 ACE、强化人、支援技能或额外运输舰。

## 普通驾驶员

完整定义位于 Main 的 `Units/BattleUnits/Pilot/0093/Common/`，沿用 0087 实际结构，无需 DLC 再覆盖。

| 阵营 | 普通驾驶员 | 士官 |
|---|---|---|
| `0093_EFSF` | `Pilot_0093_EFSF_N_C_A` | `Pilot_0093_EFSF_O_C_A` |
| `0093_NZN` | `Pilot_0093_NZN_N_C_A` | `Pilot_0093_NZN_O_C_A` |

普通驾驶员/士官继承 Main 原有基础模板；身体两张、头像四张从 0087 原样复制，在 Main 独立命名。分派链为总 Marker → 0093 Marker → 阵营 Marker → 实体，保留消息和 Step3 技能传递。

`PilotType=1001/1101` 选择普通驾驶员，`2001/2101` 选择士官；工厂自动配属继续使用既有 `PilotCustom=1` 流程。MS 使用 1101，舰船使用 2101，默认驾驶员也均改为 0093 对应阵营。

Main 的 T1/T2 学院有两阵营普通驾驶员生产入口，100 资金、0 物资、3 秒。当前 Base 解锁 T2 学院，实际学院可用性仍取决于科技、建造和施工完成。

## 图片与公共文件

场景下方标题使用 `Resource/Image/Title/UC_0093.png`，Main 与 0093 同步。场景横幅仍使用其原 Banner。

六张年代文字为 130×60 透明 PNG：Button_UC0079、Button_UC0087、Button_CE71、Button_CE73、Button_AD2308、Button_UC0093。运行时引用在 Main；0079/0087（含 T2）和 0093 已接入，CE73/AD2308 只准备素材。生成脚本与预览备份位于“工具”目录。

DLC 保留 Shield、Weapon 公共树，另有上述四种机体目录及必要炮塔、图像和一份不加载的吉姆III继承模板。未复制其他战斗单位定义，没有重复音乐。公共模板/资源的首轮来源仍参考四包合并清单；本轮具体迁移和缺图补齐记录在 `0093_Base科技接入.json`。

本轮仅改 0093 的科技、工厂和建筑入口，在 Main 新增 HLV 变体；原有驾驶员接入继续保留。没有修改 0079、0087、SEED 原文件、GameManager 或公共战斗框架。

## 验证与待验收

- Base 接入静态检查：135/135 通过（含开局自动完成链）；覆盖解锁集、Get/Send、建造入口、生产与驾驶员、文件继承和跨包 ID。
- 开局/公共链回归：86/86 通过；保留 HQ、GameManager 字段、BuildingSlot、据点转换、场景按钮与驾驶员检查。
- 上一轮整目录科技树 MCP lint：27 文件，0 错误、25 警告，包含原共享模板空段/重复键提示、局部扫描最低版本提示和多行动作误报；未自动批量修改公共层。
- 使用本机真实引擎，Main、Main＋0093、五包混装均已重新启用并完成初始化，无 MOD 加载错误。首次迁移出现的舰船炮塔段名不一致已修正，以上均为修正后的结果。
- `git diff --check` 用于检查修改格式。原工作区已有四张 Main Title 删除和新的年代标题图片，本轮保留用户修改。

上述加载不等于对局行为验证。仍需在游戏里检查：房主/非房主参数和 AI 阵营；地面/宇宙科技页打开与 Base 研究；建筑建造、施工、据点占领转换；四种单位的工厂训练、驾驶员配属、部件/炮塔显示、攻击、运输与再入；AI 生产、存档重载和联网同步。

```powershell
$env:PYTHONUTF8='1'
python '文档 (不要打包)/工具/验证_0093_Base科技.py'
python '文档 (不要打包)/工具/验证_0093骨架.py'
python '文档 (不要打包)/工具/验证_0093引擎加载.py' --case main
python '文档 (不要打包)/工具/验证_0093引擎加载.py' --case 0093
python '文档 (不要打包)/工具/验证_0093引擎加载.py' --case mixed
```

引擎校验使用项目内隔离 preferences/cache/logs，原游戏设置不改。初始化后可由脚本受控停止，非零退出码与 MOD 解析错误分别记录。

## 清单

分析目录保留 `BattleUniverse_四包详细对比与0093方案.md`、逐文件 CSV 与制作前 SHA-256 基线；它们是首轮历史快照，不是当前空包状态说明。

当前接入与结果见 `0093_构建清单.json`、`0093_Base科技接入.json`、`0093_Base科技验证.json`、`0093_普通驾驶员接入.json`、`0093_静态连携验证.json` 和 `0093_引擎加载_*.json`。

“文档 (不要打包)”、原始素材和 MCP/测试目录均不属于 MOD 发布内容。

开局 Base 修复补充：仅修改 0093 科技核心的初始化分派，按原 0087 流程完成当前阵营 Base。修复后的单文件 lint 为 0 错误、1 条多行动作误报；135 项 Base 静态检查通过，尚未实测交互对局。需要重新加载 MOD 并新开一局验证，已有存档不会重新执行 created 初始化事件。

图标更新：联邦 Base 使用 0079 EFSF 的 `Tech_EFSF_0079_1.png`，在 0093 本地命名为 `Tech_0093_EFSF_1.png`；新吉翁 Base 使用 0079 ZEON 的 `Tech_ZEON_0079_1.png`，本地命名为 `Tech_0093_NZN_1.png`。NZN 阵营图标的 1/2/3 三种规格也由 0079 ZEON 原图复制，命名为 `Faction_0093_NZN_1/2/3.png`，现有阵营选择、HQ、工厂和科技树入口引用继续使用这些 0093 名称。五张图与来源逐字节一致，尺寸保持不变。
