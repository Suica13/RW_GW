# Battle Universe HQ 与开局设置索引

本文结合 Main 包中的 HQ、GameManager，以及 DLC 0079 的 HQ 案例，说明：

- 开局 HQ 如何进入房主设置
- GameManager 如何保存并广播开局参数
- DLC HQ 如何选择阵营
- 默认科技树如何被挂载
- 初始科技 Tag 和初始部队在哪里设置

这部分不是普通单位注册流程。修改前应先确认游戏模式和目标 HQ 类型。

---

# 1. 主要目录

## Main 包

```text
GW_BattleUniverse_Main/
└─ Units/
   ├─ GameManager/
   │  ├─ GameManager_Start.ini
   │  ├─ GameManager_VS.ini
   │  └─ Mod/
   └─ Buildings/
      └─ HQ/
         ├─ HQ_Start.ini
         ├─ HQ_Start_Host.ini
         ├─ HQ_VS_GE/
         ├─ HostOption/
         └─ Mod/
```

## DLC 0079

```text
GW_BattleUniverse_DLC_0079/
└─ Units/
   └─ Buildings/
      └─ HQ/
         ├─ HQ_VS_GE/
         │  ├─ HQ_VS_GE_UC0079.ini
         │  ├─ HQ_VS_GE_UC0079_T2.ini
         │  └─ Faction/
         ├─ Image/
         └─ Mod/
```

---

# 2. 整体流程

```text
地图生成 HQ_Start
→ 确认房主
→ 房主 HQ 转换为 HQ_Start_Host
→ HostOption 收集开局设置
→ GameManager_Start 接收设置
→ GameManager 广播给所有玩家 HQ
→ GameManager 转换到具体游戏模式
→ DLC 模式 HQ 提供阵营选择
→ 玩家或 AI 选择阵营
→ HQ 获得阵营 Tag 与初始科技 Tag
→ 正式开局后 HQ 转换为阵营 HQ
→ 挂载 TechTree_Core
→ 根据地面或宇宙地图生成初始部队
```

---

# 3. `HQ_Start.ini`

路径：

```text
GW_BattleUniverse_Main/Units/Buildings/HQ/HQ_Start.ini
```

该文件是开局阶段的基础 HQ。

它继承：

```ini
ROOT:Units/Buildings/HQ/Mod/HQ.ini
ROOT:Units/Buildings/HQ/Mod/HQ_GetMode.ini
```

关键配置：

```ini
name:HQ_Start
overrideAndReplace:commandCenter
isPickableStartingUnit:true
```

说明：

- 替换原版 `commandCenter`
- 作为地图可选择的开局单位
- 在正式阵营 HQ 生成前充当等待和设置入口

---

# 4. 房主与非房主

`HQ_Start.ini` 监听：

```ini
newMessage(withTag="SetHost")
```

收到后：

```text
HQ_Start
→ 转换为 HQ_Start_Host
→ 挂载 HostOption_Core
```

对应逻辑：

```ini
convertTo:HQ_Start_Host
attachments_addNewUnits:HostOption_Core
attachments_onlyOnSlots:HostOptionSlot
```

未成为房主的 HQ 保留等待按钮：

```text
等待房主
```

因此 Main 包把开局设置权限集中在房主 HQ 上。

---

# 5. `HQ_Start_Host.ini`

路径：

```text
GW_BattleUniverse_Main/Units/Buildings/HQ/HQ_Start_Host.ini
```

该文件是房主的开局设置 HQ。

主要职责应从 `HostOption` 一起理解：

- 显示游戏模式设置
- 设置地图或阶段
- 设置初始资源
- 设置初始科技
- 设置资源倍率
- 设置科技倍率
- 设置是否自动研究
- 设置科技上限
- 设置科技共享
- 设置特殊单位许可
- 最终发送开局设置

普通 DLC 不应直接重写整套 Host 设置。

如果只是增加一个新阵营或年代，优先接入已有模式和 HQ 转换流程。

---

# 6. `GameManager_Start.ini`

路径：

```text
GW_BattleUniverse_Main/Units/GameManager/GameManager_Start.ini
```

它继承：

```ini
ROOT:Units/GameManager/Mod/GameManager.ini
```

并作为地图中央的中立管理单位生成：

```ini
name:GameManager_Start
onNewMapSpawn:mapCenter_asNeutral
```

可以把它理解为：

> 保存开局参数，并把房主设置同步到所有玩家 HQ 的中央控制器。

---

# 7. GameManager 接收的开局参数

`GameManager_Start` 监听：

```text
Setting_GameMode
```

并保存以下内容：

```text
gameMainMode
gameSubMode
stageIndex

resStart
mpStart
techStart

resX
mpX
techX

autoTech
techLimit
techShare

allowACEUnit
allowPMCUnit
```

大致可以分成：

## 游戏模式

```text
gameMainMode
gameSubMode
stageIndex
```

## 初始值

```text
resStart
mpStart
techStart
```

## 倍率

```text
resX
mpX
techX
```

## 科技规则

```text
autoTech
techLimit
techShare
```

## 特殊单位许可

```text
allowACEUnit
allowPMCUnit
```

---

# 8. GameManager 广播设置

GameManager 保存设置后，会遍历：

```text
memory.playersHQ
```

并向每个玩家 HQ 发送：

```text
Setting_GameMode
```

连同全部开局参数。

因此：

```text
HostOption
→ GameManager
→ 所有玩家 HQ
```

GameManager 是开局设置的中转和统一状态源。

如果只在房主 HQ 中修改变量，而没有进入这条广播链，其他玩家 HQ 可能无法获得相同设置。

---

# 9. 游戏模式转换

`GameManager_Start` 根据：

```text
gameMainMode
```

转换为具体 GameManager。

当前可确认的案例：

```ini
if memory.gameMainMode==1
→ convertTo:GameManager_VS
```

因此增加新主模式时，通常需要同时考虑：

- HostOption 中的模式选择
- GameManager_Start 中的模式索引
- 对应 GameManager 实体
- HQ 的模式转换
- 模式所使用的胜负逻辑

只新增一个 DLC 阵营时，一般不需要增加全新的 GameManager 主模式。

---

# 10. DLC 0079 的模式 HQ

参考：

```text
GW_BattleUniverse_DLC_0079/
Units/Buildings/HQ/HQ_VS_GE/HQ_VS_GE_UC0079.ini
```

它继承：

```ini
ROOT:Units/Buildings/HQ/Mod/HQ.ini
```

并替换：

```ini
HQ_VS_GE_UC0079
```

这个 HQ 负责 0079 对战模式中的：

- 阵营选择
- AI 自动选择阵营
- 初始阵营 Tag
- 初始科技 Tag
- 正式阵营 HQ 转换
- 默认科技树挂载
- 地面或宇宙初始部队生成

---

# 11. AI 阵营选择

DLC HQ 会在 AI 尚未选择阵营时，根据敌方阵营判断选择联邦或吉翁。

例如：

```text
敌方存在 ZEON_0079
→ AI 选择 EFSF_0079

敌方存在 EFSF_0079
→ AI 选择 ZEON_0079
```

说明这个 HQ 不只是 UI，还承担 AI 的开局阵营匹配。

增加新阵营时，需要考虑：

- AI 如何识别敌方
- 多阵营时如何避免同时满足
- 阵营选择优先级
- 没有匹配敌人时的默认行为

---

# 12. 阵营选择时添加的内容

选择联邦 0079 时，HQ 会写入：

```text
FactionIndex=1010101
```

并临时添加：

```text
EFSF_0079
```

同时给队伍添加：

```text
EFSF_0079
Tech_EFSF_0079_Start
PassT0
```

选择吉翁时则对应：

```text
FactionIndex=1010201
ZEON_0079
Tech_ZEON_0079_Start
PassT0
```

这说明开局默认科技树并不是只靠 UI 文件决定。

关键入口是 HQ 在阵营选择时添加的全局队伍 Tag：

```text
阵营 Tag
起始科技 Tag
初始科技层级 Tag
```

---

# 13. 默认科技树绑定

联邦案例：

```text
EFSF_0079
Tech_EFSF_0079_Start
PassT0
```

可以理解为：

```text
EFSF_0079
→ 当前队伍所属阵营

Tech_EFSF_0079_Start
→ 阵营默认起始科技入口

PassT0
→ 初始科技层级状态
```

如果创建新阵营或新年代，必须确认：

- 起始科技 Tag 的名字
- TechList 是否识别该 Tag
- 默认已解锁项目
- 初始科技层级
- 工厂是否依赖该阵营 Tag
- 科技树 UI 是否依赖该阵营 Tag

仅复制科技树页面，而没有让 HQ 添加起始科技 Tag，可能导致科技树存在但没有正确初始状态。

---

# 14. `UnlockedListMarker`

阵营选择模板会在 HQ 上挂载：

```text
UnlockedListMarker_0079
```

并放入：

```text
UnlockedListMarkerSlot
```

它应与已解锁科技列表和状态记录有关。

因此开局科技链中至少包含：

```text
HQ 阵营选择
→ 添加起始科技 Tag
→ 挂载 UnlockedListMarker
→ 正式挂载 TechTree_Core
```

如果新年代使用不同的解锁列表 Marker，也需要在 HQ 选择阶段替换。

---

# 15. 正式开局转换

当：

```text
GameStart==1
```

DLC HQ 会按 `FactionIndex` 转换为正式阵营 HQ。

联邦案例：

```text
HQ_VS_GE_UC0079
→ HQ_EFSF_0079
```

同时挂载：

```text
TechTree_Core_0079
```

到：

```text
TechTreeMarkerSlot
```

因此：

> 正式科技树核心是在阵营 HQ 转换时挂载的。

阵营选择阶段负责确定默认 Tag，正式开局阶段负责生成正式 HQ 并挂载科技树核心。

---

# 16. 初始部队生成

正式转换后，HQ 会根据：

```text
tileMode
```

区分地面和宇宙地图。

## 地面

例如联邦会生成：

- `Type74`
- `Type61`

并设置相对 HQ 的生成位置。

## 宇宙

例如联邦会生成：

- `SalamisClass`
- `FF_S3`
- `FF_4`

因此初始部队不一定来自科技树或工厂。

它们可以直接写在 HQ 的阵营转换 Action 中：

```text
ConvertToFaction_阵营_Ground
ConvertToFaction_阵营_Space
```

修改默认初始单位时，应检查这里。

---

# 17. HQ 与科技树的完整关系

```text
HQ_Start
→ 等待房主或进入 Host 设置
      ↓
HQ_Start_Host / HostOption
→ 选择开局参数
      ↓
GameManager_Start
→ 保存并广播设置
      ↓
DLC 模式 HQ
→ 玩家或 AI 选择阵营
      ↓
添加：
阵营 Tag
Tech_阵营_Start
PassT0
UnlockedListMarker
      ↓
GameStart
      ↓
转换为正式阵营 HQ
      ↓
挂载 TechTree_Core
      ↓
生成地面或宇宙初始部队
```

---

# 18. 新增阵营或年代时需要检查

## Main 开局层

```text
HQ_Start
HQ_Start_Host
HostOption
GameManager_Start
具体 GameManager
```

只有增加新游戏模式时才可能需要修改。

## DLC 模式 HQ

```text
阵营选择按钮
FactionIndex
阵营 Tag
起始科技 Tag
PassT0
正式 HQ ID
TechTree_Core
UnlockedListMarker
地面初始部队
宇宙初始部队
AI 选阵营条件
```

新阵营主要修改这一层。

---

# 19. 普通新增单位时是否需要修改 HQ

通常不需要。

普通新单位只要完成：

```text
单位本体
→ 科技树注册
→ 工厂注册
```

HQ 只在以下情况需要修改：

- 新单位开局默认赠送
- 新单位属于默认初始科技
- 新增阵营
- 新增年代
- 新增游戏模式
- 修改初始科技等级
- 修改初始部队
- 修改开局资源或科技规则
- 更换默认科技树核心

---

# 20. 修改开局内容的查找顺序

## 修改初始资源或科技倍率

```text
HostOption
→ GameManager_Start
→ HQ_GetMode
```

## 修改初始科技等级

```text
techStart
PassT0
科技树模板中的层级判断
```

## 修改默认已解锁科技

```text
Tech_阵营_Start
TechList
UnlockedListMarker
```

## 修改科技树核心

```text
HQ 阵营转换
→ attachments_addNewUnits:TechTree_Core_xxx
```

## 修改初始单位

```text
HQ 的 ConvertToFaction_Ground
HQ 的 ConvertToFaction_Space
```

## 修改阵营

```text
FactionIndex
临时阵营 Tag
全局阵营 Tag
正式 HQ convertTo
```

---

# 21. 风险提示

HQ 和 GameManager 都属于高影响范围文件。

常见风险：

- 房主与非房主设置不同步
- 玩家 HQ 未收到 GameMode 数据
- 阵营 Tag 与工厂、科技树不一致
- 起始科技 Tag 缺失
- TechTree_Core 未挂载
- UnlockedListMarker 使用错误年代
- 正式 HQ ID 不存在
- 地面地图生成了宇宙单位
- AI 无法选择阵营
- 新模式没有对应 GameManager

修改时应一次只改一条链，并逐步测试。

---

# 22. 推荐测试顺序

```text
1. 地图能否生成 HQ_Start
2. 房主是否转换为 HQ_Start_Host
3. 非房主是否保持等待状态
4. Host 设置是否到达 GameManager
5. 所有玩家 HQ 是否收到相同设置
6. GameManager 是否转换到正确模式
7. DLC HQ 是否出现正确阵营按钮
8. AI 是否能选择阵营
9. 阵营选择后 Tag 是否正确
10. GameStart 后是否转换正式 HQ
11. TechTree_Core 是否挂载
12. 默认科技是否正确
13. 地面初始单位是否正确
14. 宇宙初始单位是否正确
15. 工厂和科技树是否识别阵营 Tag
```

---

# 23. 最简结论

```text
HQ_Start
→ 房主与开局设置入口

GameManager_Start
→ 保存并广播开局参数

DLC 模式 HQ
→ 阵营选择与初始 Tag

正式阵营 HQ
→ 挂载科技树并进入正式游戏

ConvertToFaction_Ground / Space
→ 生成初始部队
```

默认科技树绑定的关键不是单一文件，而是：

```text
HQ 添加起始科技 Tag
+ UnlockedListMarker
+ 正式 HQ 挂载 TechTree_Core
+ TechList 对起始 Tag 的响应
```

修改默认科技树时，应同时追踪这四部分。
