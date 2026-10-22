# UC0093 DLC 骨架接入说明

本包是可以接入原有开局链的开发骨架，保留空科技页、空生产列表、HQ/建筑槽/据点与 Main 占位定义；没有加入战斗机体、小队、驾驶员或初始部队。

## 安装组合与命名

启用 `GW_BattleUniverse_Main` 和 `GW_BattleUniverse_DLC_0093`。可以与 0079、0087、SEED 混装。没有 0093 包时，Main 的 0093 场景按钮受 DLC Marker 条件锁定。

| 项目 | 值 |
|---|---|
| 包目录 | `GW_BattleUniverse_DLC_0093` |
| 元数据版本 | V159，最低引擎 1.15p11 |
| 场景实体 | `HQ_VS_GE_UC0093` |
| 场景 Index | `1020` |
| 联邦阵营键 | `0093_EFSF` |
| 联邦 FactionIndex | `1030101` |
| 联邦 HQ | `HQ_0093_EFSF` |
| 新吉翁阵营键 | `0093_NZN` |
| 新吉翁 FactionIndex | `1030201` |
| 新吉翁 HQ | `HQ_0093_NZN` |
| 科技核心 / 已解锁标记 | `TechTree_Core_0093` / `UnlockedListMarker_0093` |
| 建筑槽 / 据点 | `0093_BuildingSlot` / `StrategicLocation_0093` |

`0093_EFSF`、`0093_NZN` 按本次需求保留年代在前的写法；不要自行转换成 `EFSF_0093` 或沿用 `NEO_ZEON_0087`。场景编号延续 UC 0079=1001/1002、0087=1010/1011 的分组，0093 占用 1020。FactionIndex 延续 UC 第三个剧本 103 的编码。

## 已接入的开局链

1. Main 地面和宇宙的第四页（内部 Page3）提供 UC0093 场景按钮，使用现有 `UC0093_01.png` 横幅。
2. 按钮发送 `VS_Stage(Index=1020)`，HostOption_Core 将 Index 写入 stageIndex，再通过 `Setting_GameMode` 发给 GameManager_Start。
3. GameManager_Start 保存全部开局参数，逐玩家 HQ 广播。原有 GameManager 逻辑已经通用传递 stageIndex，没有增加第二套管理器，也没有修改其文件。
4. Main/0079/0087/0093 中存在的 HQ_GetMode 副本均增加 1020 路由，目标为 Main 同名占位/DLC 正式 `HQ_VS_GE_UC0093`。
5. 玩家选阵营时设置对应 FactionIndex、阵营 Tag 和 `Tech_<阵营>_Start`，沿用 ReadyOK，挂载 `UnlockedListMarker_0093`。AI 使用队伍编号奇偶作为确定性兜底，避免全 AI 开局无人首先选阵营。
6. GameManager_VS 等全员准备后设置 GameStart；0093 HQ 转换为最终阵营 HQ，并挂载 TechTree_Core_0093。地面、宇宙都不赠送战斗单位。
7. 两阵营各有一张空科技页，可打开/关闭；没有研究节点、科技费用、前置线或虚假的默认战斗单位解锁。

## 建筑槽与据点

- 旧四包的 `Template/Building/Common_Buildings_Slot.gw` 都追加 `ConvertTo_0093`；旧有场景分支保持。
- 旧四包的 `Units/Buildings/StrategicLocation/Mod/StrategicLocation.ini` 同样追加 0093 转换。
- Main 提供 `0093_BuildingSlot`、`StrategicLocation_0093` 占位定义，确保公共分支不引用只存在于可选 DLC 的 ID。
- 0093 通过同名 `overrideAndReplace` 接管，连接 `0093_MainBuildList.ini`。
- 新包自身的建筑槽和据点 Mod 以 Main 的多场景路由为基础，因此不会丢掉被旧年代阵营接管后返回对应场景的入口。
- 两个 FactionIndex 都转换到 0093 建筑槽/据点，阵营内容再用各自 Tag 筛选。没有将新的联邦或新吉翁映射到 0087。

## 空内容如何扩展

每阵营工厂均保留 `Land`、`Air`、`Aqua`、`Mega`、`Space`、`Space_Mega` 六类空壳、UnitList 文件和对应分类目录。工厂没有生产 Action，不会偷偷生产旧阵营单位。

MainBuildList、BuildingSlot Action、阵营 Get/Send 已为这些空工厂预留匹配的 `Factory_<阵营>_<分类>` 和 `Unlock_...`。默认不赠送这些解锁 Tag，因此正常面板不会出现一批无内容工厂。以后在新科技的完成事件中解锁目标工厂，即可继续填入生产定义。

建议扩展顺序：

```text
新增第一台 0093 单位并独立测试
→ 使用现有武器/盾牌模板
→ 在正确工厂分类添加 <UNIT>.gw 并纳入 UnitList
→ 在新阵营 TechList 定义科技，Get/Send 注册目标
→ 在 Common 添加研究节点，放入 Page_00 并连线
→ 接入工厂解锁，测试生产
→ 再添加驾驶员、支援技能、ACE 和初始部队
```

空 ACE 信标与支援技能目录不注册功能实体；Main 原有公共技能入口仍按原框架存在。不要把“有目录”误认为已经完成相应玩法。

## 武器、盾牌与资源

`Units/BattleUnits/` 顶层严格只有 `Shield/`、`Weapon/`。武器保留 Beam、Cqb、Funnel、SetUp、Shell、Sp、Template 及其图片和弹体/辅助实体定义，没有实际机体、舰船、小队、Pilot 目录。

公共模板和资源参考四包合并，优先取 0087 同路径文件，再补 0079、SEED、Main 的独有路径；少数公共接口/多场景路由明确采用 Main。音乐不复制，新包没有 `[music]` 配置。

临时图片包含两阵营徽标的六张别名和八张上游缺失图片替代。清单记录在 `文档 (不要打包)/分析/0093_构建清单.json`。六张原本来自具体机体或 Pilot 目录的图片移到 `Resource/Image/Weapon/Legacy/`，不因此恢复那些战斗单位目录。

## 已执行与未执行的检查

- 自定义静态连携/回归：58 项通过，包括文件引用闭合、阵营编号链、Main 占位对应、场景按钮经 GameManager 广播的字段链、五包建筑槽/据点分支、原场景 Action 保留、旧包仅 12 个声明文件变化。
- 新阵营选择 HQ 的 MCP lint：0 错误、0 警告。
- 科技树目录 MCP lint：0 错误、21 警告；部分跨文件继承/宏在局部扫描时无法还原。
- 全包 MCP lint：1821 个配置文件，6368 个错误、2122 个警告。大量来自原样复制的宏/模板，示例为 Combo_AGE_1N 的 `${...}` 被视作多余 `}`。这不是全包无问题的证明，也没有据此批量修模板。全量保留的未接入 `.gw` 还需在具体单位引用时测试。
- 使用本机真实引擎，在项目内隔离 preferences/cache/logs 后分别验证 Main、Main+0093、五包混装；结果见分析目录 `0093_引擎加载_*.json`。只有启用状态、初始化完成和 MOD 错误检查均满足，才判定加载通过。初始化后由脚本停止无窗口进程，受控停止可能返回非零退出码；这与 MOD 解析失败分开记录。

可复现命令（从工作区根目录运行）：

```powershell
$env:PYTHONUTF8='1'
python '文档 (不要打包)/工具/验证_0093骨架.py'
python '文档 (不要打包)/工具/验证_0093引擎加载.py' --case main
python '文档 (不要打包)/工具/验证_0093引擎加载.py' --case 0093
python '文档 (不要打包)/工具/验证_0093引擎加载.py' --case mixed
```

隔离加载目录 `文档 (不要打包)/工具/0093_loadtest/` 被 Git 忽略；日志保存在本机，其中使用目录联接读取游戏资源。原游戏 preferences.ini 和 MOD 启用状态不改。

尚未进行玩家界面/联网对局的交互验收。需手动检查：两种地图模式下 Page3 场景选择，房主与非房主参数一致，玩家/AI 选阵营与准备，GameStart 后正式 HQ 与科技附件，空页面开关，以及据点和建筑槽的占领/换阵营转换。空包没有可生产部队，因此不能声称已验证 0093 的战斗或完整经济循环。

## 审阅文件

- `文档 (不要打包)/分析/BattleUniverse_四包详细对比与0093方案.md`：结构、职责、内容差异和接入方案。
- `BU_四包文件对比_0093制作前.csv`：四包 12538 个不同相对路径的逐文件内容比较。
- `BU_四包基线_0093制作前.json`：制作前的文件大小与 SHA-256，可检查旧包是否意外改动。
- `0093_公共资源来源.csv`、`0093_同路径公共副本取舍.csv`：来源和冲突取舍。
- `0093_构建清单.json`、`0093_静态连携验证.json`：新 ID、临时图片、修改范围与检查结果。

以上文档和工具都在“不要打包”目录；发布只取所需游戏包，不把分析报告、测试目录和 MCP 工具装入 MOD。


## 年代文字与标题更新（2026-10-23）

场景选择下方的 UC0093 标题现在使用新增的 `Resource/Image/Title/UC_0093.png`，已复制到 Main，并接入地面/宇宙 Page3 的 `decal_Title`；场景卡片的 Banner 图片保留原用途。

六张年代文字按原画布 130×60 重绘为透明 RGBA PNG：`Button_UC0079.png`、`Button_UC0087.png`、`Button_CE71.png`、`Button_CE73.png`、`Button_AD2308.png`、`Button_UC0093.png`。显示文字沿用 UC.0079、UC.0087、SEED.CE71、SEED.CE73、A.D.2308、UC.0093；使用 Arial Bold 白字，4 倍采样后缩小。

新素材以 0093 包为源，同步到绘制场景界面的 Main。0079/0087（含 T2）场景引用新文件名，CE71 自动使用同名重绘资源；0093 原先空白的 `decal_Text` 已接入专用按钮。CE73/AD2308 素材已准备，但不额外创建未请求的新场景。

0093 中旧的 Button_0079、Button_0087、Button_2308 已完成重命名；Main 保留旧文件供兼容。原图备份和总览在 `文档 (不要打包)/工具/年代按钮预览/`，可复现渲染脚本为 `生成_年代按钮.ps1`。本轮额外改动的图片和引用已记入构建清单，初版“原包 12 个文件变化”的统计仅对应首轮骨架制作。
