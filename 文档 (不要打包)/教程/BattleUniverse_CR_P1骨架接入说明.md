# 火线纵横 P1 骨架接入说明

`GW_BattleUniverse_DLC_CR_P1` 是火线纵横第一阶段 DLC。以 0093 的完整依赖和基础设施链为参照，提供秩序、反抗、混沌三个阵营。当前仅搭建初始骨架，不提供战斗单位、驾驶员生产、开局部队或 HLV。

## 安装与范围

启用更新后的 `GW_BattleUniverse_Main` 和 `GW_BattleUniverse_DLC_CR_P1`。不依赖启用 0093、0087、0079 或 SEED；这些包可以同时安装。公共基础建筑继续由 Main 提供，P1 保存自身需要的模板、图像、声音、武器和盾牌副本。

| 项目 | 当前约定 |
|---|---|
| MOD 标题 | `GW_BattleUniverse_DLC_CR_P1_V159` |
| 最低引擎版本 | `1.15p11` |
| 加载标记 | `DLCMarker_CR_P1` |
| 主模式 | 起源 `gameMainMode=1`；火线纵横 `gameMainMode=2` |
| 子模式 | 对决 `gameSubMode=1`；场景保留 WIP，不发送开局配置 |
| 火线纵横 P1 对决阶段 | `stageIndex=2000` |
| 开局阵营选择 HQ | `HQ_VS_CR_P1` |
| 运行管理器 | `GameManager_CR_VS` |
| 科技核心 / 解锁标记 | `TechTree_Core_CR_P1` / `UnlockedListMarker_CR_P1` |
| 建筑槽 / 据点 | `CR_P1_BuildingSlot` / `StrategicLocation_CR_P1` |

`gameMainMode` / `gameSubMode` 现在分别表达主模式和玩法。原有起源对决继续使用 `(1, 1)`，年代 `stageIndex` 不变。旧文件名和消息名中的 `VS_GE` / `VS_CR` 保留为接口名称，不能据此倒推菜单层级。

## 单位与附属单位菜单

地形选择 → 主模式选择（起源 / 火线纵横）→ 子模式选择（对决 / 场景 WIP）。

- 复用 `HostOption_Main_Menu_2`、`HostOption_Main_VS` 及已预留的 `HostOption_VS_CR` 附属按钮，不引入新的 UI 实现方式。
- 起源选择对决后仍进入原地面 / 宇宙年代分页。
- 火线纵横选择对决后设定 P1 阶段，进入现有资源、科技、弹速及确认页面。初始资金和物资为 12000，战力 60，科技点 0，与 0093 起步设置一致。
- `HostOption_VS_CR` 的动作和缺 DLC 覆盖图均检查 `DLCMarker_CR_P1`，处理该消息的 HostOption Core 也检查标记。
- 两个主模式复用锁定的场景按钮，保留 `[WIP]` 文字和覆盖图；`Stage` 事件没有转换或开局操作。
- 返回按钮继续走原 `BackToMenuPage`，回到地形入口并重置模式、阶段、分页和开局设置。

## 开局与广播

HostOption Core → `Setting_GameMode` → `GameManager_Start` → 每个玩家 HQ。

房主发送字段、GameManager 保存和广播字段保持原有完整集合。火线纵横对决使用 `(2, 1, 2000)`：

1. GameManager 转换为 `GameManager_CR_VS`。
2. 各玩家 `HQ_GetMode` 转换为 `HQ_VS_CR_P1`。
3. 选择阵营后设置 FactionIndex、阵营 Tag、Start Tag、PassT0，挂载 `UnlockedListMarker_CR_P1`。
4. 准备和游戏开始沿用 VS 逻辑。
5. HQ 转为对应阵营 HQ，挂载 `TechTree_Core_CR_P1`，由原有初始化事件完成该阵营 Base。

`GameManager_CR_VS` 通过本包 `copyFrom` 继承 `GameManager_VS` 的准备、开局和天气规则，只覆盖 CR 分派和提示。后续可在该实例追加火线纵横专用规则；目前没有另造胜负机制。

## 三阵营

| 中文 | 阵营键 | FactionIndex | 正式 HQ |
|---|---|---|---|
| 秩序 | `CR_Order` | `9010101` | `HQ_CR_Order` |
| 反抗 | `CR_Resistance` | `9010201` | `HQ_CR_Resistance` |
| 混沌 | `CR_Chaos` | `9010301` | `HQ_CR_Chaos` |

AI 按 `teamID % 3` 的等价整数表达式选择一个阵营，并以 FactionIndex 为 0 作保护。即使全员 AI，也有确定的默认阵营，不依赖先观察到人类玩家的选择。这只是初始分派，没有为三阵营添加战斗定位或 AI 战术。

Main 保留模式 HQ、三个正式 HQ、科技核心、解锁标记、建筑槽和据点共八个同名占位；P1 使用 `overrideAndReplace` 接管。不要删除这些占位。

## Base 科技与基础建筑

三个阵营分别有独立的一页科技树、Base 节点、TechList、Get / Send 和 UI 附件。Base 的四项费用和时间均为 0，通过当前阵营 Start Tag + PassT0 自动完成，再经原有 Done → UnlockUnit → Get / Send 解锁建筑。

每个阵营的 Base 解锁 18 项建筑：

- 本阵营 Land、Mega、Space、Space_Mega 工厂。
- `Refinery_Common_T3`、`Institute_Common_T2`、`SupplyDepot_Common_T2`、`Academy_Common_T2`。
- 地面 B 型机枪、防空、加农、黄色光束炮塔和雷达。
- 宇宙 B 型机枪、导弹、加农防御设施。
- `Wall_T2_A`、`Wall_T2_B`。

Air / Aqua 工厂实体和建造入口保留，但 Base 暂不解锁。六类工厂均保留有效的空生产列表，不注册 `produceUnits` 或单位自动生产动作。学院本体可建造，但当前三个阵营没有驾驶员生产按钮。

HQ、据点、建筑槽都接入同一套建筑解锁。建筑槽保留经济建筑和工厂的 AI 建造分派，包含三个阵营。HLV 会引入运输单位和驾驶员链，因此本阶段不解锁、不新增 CR HLV。

## 公共路由与资源

- Main、0079、0087、0093、SEED、P1 六包的建筑槽和据点副本追加三个 CR FactionIndex 的转换分支，保留各包原有路线和差异。
- 所有现存 `HQ_GetMode.ini` 副本更新主 / 子模式判断并接入 P1；SEED 原本没有该副本，不额外创建无调用者文件。
- 新包复用完整的包内公共资源，保留 Weapon / Shield 功能树，不复制 0093 的四个战斗单位目录和生产定义，也不复制 BGM。
- 秩序临时图标取自 0093 联邦，混沌取自 0093 新吉翁，反抗取自 0087 奥古。均以新阵营键独立命名，之后可以替换图片而不修改配置接口。
- 菜单沿用已预留的火线纵横按钮图像；缩略图及其他通用美术暂时复用已有素材。
- 新包内具体 `ROOT:` 路径已按实际文件名匹配大小写；未批量修改旧包资源引用。

## 验证

运行只读验证：

```sh
python -B '文档 (不要打包)/工具/验证_CR_P1骨架.py'
```

259 项检查通过：包内路径、文件继承、最终配置中的动作 / 段落 / 实体引用，主菜单与子菜单附属按钮、WIP 锁定、缺 DLC 门禁、地面 / 宇宙菜单分派、返回重置、广播字段、Main 占位、公共副本路由、三阵营 Base 和建造入口、空生产列表、20 个玩家编号的 AI 分派。

原 `验证_0093_Base科技.py` 的 135 项检查也通过。检查时没有覆写其历史报告。

上述为静态检查和有限的配置分派模拟，不是游戏引擎执行。当前环境没有项目本机的 Windows 游戏与 MCP 源码索引，尚未执行游戏加载、附属单位 UI 显示、实际初始化时序、施工、多人联机和存档回归。

已有引擎加载工具增加了 `cr_p1` 和 `mixed_cr_p1` 两种组合，原 `main` / `0093` / `mixed` 组合保持原样。在项目原有 Windows 游戏目录中可以执行：

```powershell
python '文档 (不要打包)/工具/验证_0093引擎加载.py' --case cr_p1
python '文档 (不要打包)/工具/验证_0093引擎加载.py' --case mixed_cr_p1
```

建议游戏内验收：Main 单独加载时 CR 锁定；Main + P1 地面 / 宇宙开局；分别选择三个阵营及全 AI 开局；Base 自动解锁、科技页、HQ / 据点 / 建筑槽施工、工厂空列表；六包混装和原起源 0093 开局；返回重选、房主 / 非房主一致性。

## 后续扩充

增加单位时从对应 `CR_Order`、`CR_Resistance`、`CR_Chaos` 的生产列表、科技 Get / Send / TechList 和页面接入，先补齐驾驶员链。不要沿用旧 0093 阵营 Tag 或借用其单位 ID 作为 CR 新单位身份。第二阶段的包名、合装方式和公共阵营覆盖策略另行设计；本阶段仅建立 P1。
