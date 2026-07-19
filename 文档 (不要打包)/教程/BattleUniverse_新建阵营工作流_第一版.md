# Battle Universe 新建阵营工作流（第一版）

> 本文依据当前项目结构、现有案例和作者回忆整理。
>
> 该流程可能存在遗漏、版本差异或个别顺序不完全准确。遇到问题时，建议：
>
> 1. 优先参考已经正常运行的同类阵营或 DLC；
> 2. 使用 AI 辅助追踪 `copyFrom`、`attachments_addNewUnits`、`convertTo`、Tag、FactionIndex 和 Action 的引用关系；
> 3. 分阶段测试，不要一次性完成全部内容后再排错；
> 4. 对于 `Mod`、模板类和公共逻辑文件，修改后应尽量同步到所有相关包中。

---

# 1. 总体结构

新建阵营通常会同时涉及：

```text
Main 包
→ 场景选择入口
→ 开局占位 HQ
→ 场景 Index 注册
→ 科技树占位符
→ 公共建筑注册
→ 据点与建筑槽公共逻辑
→ 驾驶员公共目录

DLC 包
→ 正式阵营 HQ
→ 阵营选择 Pickup
→ 科技树 Core
→ BaseTech
→ Tech/Faction
→ UnlockedListMarker
→ 工厂、据点、ACE 信标、建筑槽
→ DLC 专用 BuildingSlot
→ DLC 专用建筑与单位
```

完整流程大致可以理解为：

```text
创建场景选择按钮
→ 注册场景 Page
→ 创建 Main 占位 HQ
→ HQ_GetMode 注册场景 Index
→ 创建 DLC 正式 HQ
→ 创建阵营选择 Pickup
→ 设置 FactionIndex 和初始 Tag
→ 创建科技树占位符
→ 创建 DLC 科技树 Core
→ 创建 BaseTech 与 Tech/Faction
→ 创建 UnlockedListMarker
→ HQ 转换时挂载科技树 Core
→ 创建工厂、据点、建筑槽等基础设施
→ 配置公共建筑 Get/Send
→ 配置驾驶员与 DLC 的连携
→ 分阶段测试
```

---

# 2. FactionIndex 编码规则

示例：

```text
1020101
```

当前理解：

```text
10
→ UC

20
→ 第二个剧本，即 0087

10
→ 阵营 A

1
→ 第一种可能，目前没有其他可能
```

因此在创建新阵营时，应保持：

```text
FactionIndex
阵营 Tag
正式 HQ 名称
科技树起始 Tag
工厂阵营 Tag
建筑槽判断
据点判断
```

彼此一致。

不要只修改显示名称而遗漏 `FactionIndex`。

---

# 3. 第一阶段：在 Main 包创建场景选择入口

## 3.1 创建场景 UI 按钮

路径：

```text
GW_BattleUniverse_Main/
└─ Units/
   └─ Buildings/
      └─ HQ/
         └─ HostOption/
            └─ VS/
               └─ Marker/
                  └─ Common/
```

在这里创建新的场景 UI 按钮。

建议：

```text
复制相近场景按钮
→ 修改显示名称
→ 修改图标
→ 修改场景 Index
→ 修改 Action 名称
→ 检查可见条件
```

## 3.2 在对应 Page 中添加场景按钮

路径：

```text
GW_BattleUniverse_Main/
└─ Units/
   └─ Buildings/
      └─ HQ/
         └─ HostOption/
            └─ VS/
```

在对应 Page 中加入刚才创建的场景选择按钮。

需要检查：

- Page 是否正确加载 Marker；
- 按钮位置是否正确；
- 翻页逻辑是否包含该 Page；
- Action 是否指向正确场景；
- 场景 Index 是否与后续 `HQ_GetMode.ini` 一致。

---

# 4. 第二阶段：创建 Main 包中的占位 HQ

路径：

```text
GW_BattleUniverse_Main/
└─ Units/
   └─ Buildings/
      └─ HQ/
         └─ HQ_VS_GE/
```

在这里创建新的占位符阵营基地。

该 HQ 的作用不是最终 DLC 阵营 HQ，而是：

```text
Main 包先识别目标场景
→ 生成占位 HQ
→ DLC 包加载后
→ 转换为同名正式 HQ
```

因此必须保证：

```text
Main 中的占位 HQ 名称
=
DLC 中正式 HQ 的名称
```

命名不一致时，可能导致：

- 无法转换；
- 场景启动后仍停留在占位 HQ；
- DLC HQ 逻辑没有被加载；
- 科技树和阵营选择按钮不出现。

---

# 5. 第三阶段：在 `HQ_GetMode.ini` 注册场景 Index

路径：

```text
GW_BattleUniverse_Main/
└─ Units/
   └─ Buildings/
      └─ HQ/
         └─ Mod/
            └─ HQ_GetMode.ini
```

在这里填写新的场景 Index，并注册到对应 Action 中。

需要检查：

```text
场景 UI 按钮使用的 Index
=
Page 中传递的 Index
=
HQ_GetMode.ini 判断的 Index
=
转换目标 HQ 的场景
```

推荐做法：

```text
复制现有 0079 或 0087 案例
→ 修改 Index
→ 修改目标占位 HQ
→ 修改 Action 名称
→ 检查触发条件
```

---

# 6. 第四阶段：在 DLC 中创建正式 HQ

参考路径：

```text
GW_BattleUniverse_DLC_0087/
└─ Units/
   └─ Buildings/
      └─ HQ/
         └─ HQ_VS_GE/
            └─ Faction/
```

在该目录中创建新的正式 HQ。

注意：

```text
DLC 正式 HQ
=
Main 占位 HQ 同名转换目标
```

该正式 HQ 通常负责：

- 阵营基础属性；
- 建筑生产；
- 资源生成；
- 科技树挂载；
- 正式游戏中的 HQ 行为；
- 被摧毁后的处理；
- 阵营建筑和工厂入口。

---

# 7. 第五阶段：创建开局阵营 Pickup 单位

路径：

```text
GW_BattleUniverse_DLC_0087/
└─ Units/
   └─ Buildings/
      └─ HQ/
         └─ HQ_VS_GE/
```

在这里创建开局阵营选择 Pickup 单位。

需要重点修改：

```text
[action_ChoseFaction_Info_2]
```

以及具体阵营选择 Action，例如：

```ini
[action_ChoseFaction_AEUG_0087]
@copyFromSection:template_ChoseFaction
```

## 7.1 显示文本

修改：

```ini
text:AEUG[0087]
text_zh:奥古[0087]
```

并根据新阵营填写：

```ini
description:"""
...
"""

description_zh:"""
...
"""
```

建议至少包含：

- 阵营背景；
- 战术定位；
- 游戏风格；
- 上手难度；
- 特殊机制。

## 7.2 图标和语音

修改：

```ini
iconImage:ROOT:Resource/Image/Icon/Faction_AEUG_0087_1.png
```

以及：

```ini
playSoundToPlayer:ROOT:Resource/Sound/VC/AEUG_BKS/AEUG_BKS_Pick.ogg:2
```

需要确认：

- 图标路径存在；
- 语音路径存在；
- Main 与 DLC 的 Resource 是否同步；
- 发布包中没有遗漏资源。

## 7.3 阵营 Index

修改：

```ini
setResourcesWithLogic:FactionIndex=1020101
```

新阵营必须使用新的 `FactionIndex`，不要与现有阵营重复。

## 7.4 临时 Tag

修改：

```ini
temporarilyAddTags:"""
AEUG_0087,HQ_ResGen
"""
```

其中通常包含：

- 阵营 Tag；
- HQ 临时功能 Tag；
- 资源生成相关 Tag。

## 7.5 全局队伍 Tag

修改：

```ini
addGlobalTeamTags:"""
AEUG_0087,Tech_AEUG_0087_Start,PassT0,HQ_ResGenLv2,HQ_TechGenLv2
"""
```

新阵营至少要确认：

```text
阵营 Tag
起始科技 Tag
初始科技等级 Tag
HQ 资源生成等级
HQ 科技生成等级
```

这些 Tag 会与科技树、工厂、建筑、初始资源、解锁列表和 HQ 转换产生连携。

---

# 8. 第六阶段：HQ 转换时生成科技树标记

这一项之前容易遗漏，但非常关键。

示例：

```ini
[hiddenAction_ConvertToFaction_AEUG_0087]
requireConditional:"""
if self.resource().FactionIndex==1020101
"""
convertTo:HQ_AEUG_0087
attachments_addNewUnits:TechTree_Core_0087
attachments_onlyOnSlots:TechTreeMarkerSlot
```

该 Action 负责：

```text
根据 FactionIndex
→ 转换为正式阵营 HQ
→ 生成 TechTree_Core
→ 挂载到 TechTreeMarkerSlot
```

如果没有正确设置：

- 不会生成对应科技树 UI 标记；
- 科技树按钮可能不出现；
- 科技树 Core 不会挂载；
- HQ 与科技树页面无法联动。

这部分与 Main 包占位 HQ 和 DLC 正式 HQ 同名转换直接相关。

---

# 9. 第七阶段：创建 Main 科技树占位符

## 9.1 创建 `UnlockedListMarker` 占位符

路径：

```text
GW_BattleUniverse_Main/
└─ Units/
   └─ TechTree/
      └─ UnlockedListMarker/
```

在这里创建对应占位符标记。

作用大致是：

```text
Main 包先持有同名占位单位
→ DLC 加载后由正式内容替换或继承
→ 避免 Main 包引用不存在的 DLC 单位
```

## 9.2 创建 `Core` 占位符

路径：

```text
GW_BattleUniverse_Main/
└─ Units/
   └─ TechTree/
      └─ Core/
```

在这里创建科技树 Core 的占位符。

该名称应与 DLC 中正式科技树 Core 对应。

需要保证：

```text
HQ attachments_addNewUnits 使用的名字
=
Main Core 占位符名字
=
DLC 正式 Core 名字
```

---

# 10. 第八阶段：创建 DLC 科技树初始模板

参考：

```text
GW_BattleUniverse_DLC_0087/
└─ Units/
   └─ TechTree/
      └─ Core/
```

创建新阵营或新剧本的科技树初始模板。

第一版可以先只做：

```text
1 页科技树
+ 空科技
+ 最基础的 TechTree Core
```

推荐先保证：

- HQ 能挂载 Core；
- 科技树 UI 能打开；
- Page 能显示；
- 空科技节点能正常出现；
- 页面不会报错。

不要一开始就填满完整科技树。

---

# 11. 第九阶段：创建基础 BaseTech

参考已有科技树创建文档，创建基础 `BaseTech`。

BaseTech 通常是后续科技的基础入口。

建议先实现：

```text
Start Tech
→ BaseTech
→ 第一层可研究科技
```

需要检查：

- 起始科技 Tag；
- `PassT0`；
- 前置科技；
- 科技费用；
- 科技时间；
- 完成后发送的解锁 Tag；
- 是否与阵营 Tag 对应。

---

# 12. 第十阶段：配置 `Tech/Faction`

路径：

```text
GW_BattleUniverse_DLC_0087/
└─ Units/
   └─ TechTree/
      └─ Tech/
         └─ Faction/
```

需要配置：

- 阵营 `Get`；
- 阵营 `Send`；
- `TechList`；
- `Common` 科技标记单位；
- 基础科技；
- 起始科技；
- 单位科技；
- 建筑科技。

至少要保证：

```text
阵营选择时添加的 Tech_阵营_Start
→ 能被 Tech/Faction 识别
→ 能正确进入基础科技
→ 能生成对应科技节点
```

---

# 13. 第十一阶段：创建 DLC 的 `UnlockedListMarker`

路径：

```text
GW_BattleUniverse_DLC_0087/
└─ Units/
   └─ TechTree/
      └─ UnlockedListMarker/
```

创建与 Main 占位符同名的正式 `UnlockedListMarker`，并修改内部逻辑。

需要确认：

- 名称一致；
- 场景或年代一致；
- 阵营识别正确；
- 已解锁列表能读取对应科技；
- 不会误读其他 DLC 的解锁状态。

---

# 14. 第十二阶段：创建基础设施

接下来通常需要依次创建：

```text
工厂
据点
ACE 信标
建筑格子
其他阵营建筑
```

建议顺序：

```text
建筑槽
→ 据点
→ 基础工厂
→ 资源建筑
→ 科技建筑
→ ACE 信标
→ 特殊建筑
```

原因是：

- 工厂和其他建筑通常依赖建筑槽；
- 据点可能转换建筑槽；
- ACE 信标可能依赖阵营 Tag；
- 工厂又依赖科技树和 UnitList。

---

# 15. `Common_Buildings_Slot.gw` 的场景转换

路径：

```text
GW_BattleUniverse_DLC_0087/
└─ Template/
   └─ Building/
      └─ Common_Buildings_Slot.gw
```

需要根据每个 DLC 的场景修改场景 Index 或阵营判断。

示例：

```ini
[hiddenAction_ConvertToFaction]
autoTrigger:"""
if self.attachment(slot='Building').hp<=0 and self.resource().GameStart==1
"""
alsoTriggerAction:"""
ConvertTo_0087
"""
```

以及：

```ini
[hiddenAction_ConvertTo_0087]
requireConditional:"""
if 
(
    (self.resource().FactionIndex==1020101 or self.resource().FactionIndex==1020201 or self.resource().FactionIndex==1020301) 
) 
and not self.tags(includes='0087') 
"""
convertTo:0087_BuildingSlot
```

新阵营或新场景需要修改：

- `ConvertTo_0087` 的 Action 名称；
- 所有属于该场景的 `FactionIndex`；
- 场景 Tag；
- 转换目标 `0087_BuildingSlot`。

---

# 16. 据点逻辑同步

路径：

```text
GW_BattleUniverse_Main/
└─ Units/
   └─ Buildings/
      └─ StrategicLocation/
         └─ Mod/
            └─ StrategicLocation.ini
```

据点部分也需要做类似处理。

需要特别注意：

> 据点公共逻辑应同步到其他包中。

原因是未来可能存在：

```text
不同 DLC 混装
跨年代阵营对战
Main 与多个 DLC 同时加载
```

如果只在单个 DLC 中修改据点逻辑，混装时可能出现：

- 据点无法识别新阵营；
- 据点转换为错误年代；
- 新阵营不能占领；
- 旧 DLC 无法与新 DLC 混合运行。

---

# 17. 通用建筑的 Get/Send 注册

路径：

```text
GW_BattleUniverse_Main/
└─ Units/
   └─ TechTree/
      └─ Tech/
         └─ Faction/
            └─ Common/
```

其他建筑部分可以参考现有内容制作。

但通用建筑应先在 Main 包中写好：

```text
Get 注册事件
Send 注册事件
```

然后：

```text
同步到 BuildSlot 中的列表
→ 再根据单独 DLC 调整
```

推荐关系：

```text
Main Common
→ 定义通用建筑科技事件

DLC Tech/Faction
→ 决定阵营是否能解锁

BuildSlot
→ 决定建筑槽是否能建造

具体建筑
→ 实现建筑本体
```

---

# 18. DLC 专用 BuildingSlot

路径：

```text
GW_BattleUniverse_DLC_0087/
└─ Units/
   └─ Buildings/
      └─ BuildingSlot/
         └─ Faction/
```

这里可以按 DLC 单独调整。

适合处理：

- 该年代专用建筑列表；
- 阵营专用建筑；
- 建筑升级；
- 工厂差异；
- 资源建筑差异；
- 建筑图标和生产按钮；
- 场景专用限制。

但如果修改的是公共转换或公共判断逻辑，应回到 Main 或公共模板中同步，而不是只改 DLC 实例。

---

# 19. 驾驶员目录

路径：

```text
GW_BattleUniverse_Main/
└─ Units/
   └─ BattleUnits/
      └─ Pilot/
```

驾驶员统一保存在 Main 包中。

新阵营驾驶员的接入方式，可以先参考：

```text
其他 DLC 包
Main 包 Pilot
具体单位生产定义
驾驶员选择逻辑
```

整体逻辑类似层次嵌套：

```text
Main Pilot 公共定义
→ DLC 或阵营引用
→ 工厂生产时写入 PilotType
→ 单位读取 PilotType
→ 生成对应驾驶员效果
```

需要检查：

- `PilotType`；
- 驾驶员 ID；
- 阵营限制；
- ACE 驾驶员；
- 普通驾驶员；
- 工厂生产参数；
- 单位本体读取逻辑。

---

# 20. Mod 与模板同步原则

再次强调：

> 所有 `Mod` 类和模板类文件，如果有调整，最好同步到所有相关包中。

包括但不限于：

```text
Main/Units/.../Mod
DLC/Units/.../Mod
Template
all-units.template
Common
公共 BuildingSlot
公共 StrategicLocation
公共 TechTree 模板
公共工厂模板
```

原因：

- 多 DLC 混装；
- 不同年代共用基础逻辑；
- Main 包与 DLC 包相互覆盖；
- 占位符和正式文件需要同名；
- 某个 DLC 使用旧模板会出现兼容问题。

推荐提交方式：

```text
公共模板改动
→ 单独提交

DLC 专用内容
→ 单独提交

新阵营单位和建筑
→ 分模块提交
```

---

# 21. 推荐制作顺序

## 阶段 A：只打通场景

```text
1. 创建场景 UI Marker
2. Page 中添加按钮
3. 创建 Main 占位 HQ
4. HQ_GetMode 注册 Index
5. 创建 DLC 同名正式 HQ
6. 确认场景能进入
```

## 阶段 B：只打通阵营选择

```text
7. 创建阵营 Pickup
8. 设置 FactionIndex
9. 设置阵营 Tag
10. 设置起始科技 Tag
11. 设置图标和语音
12. 确认 HQ 能转换
```

## 阶段 C：只打通空科技树

```text
13. Main 创建 Core 占位符
14. Main 创建 UnlockedListMarker 占位符
15. DLC 创建 1 页 Core
16. DLC 创建空科技
17. 创建正式 UnlockedListMarker
18. HQ 转换时挂载 TechTree_Core
19. 确认科技树 UI 能打开
```

## 阶段 D：基础科技与建筑

```text
20. 创建 BaseTech
21. 配置 Tech/Faction
22. 创建 BuildingSlot
23. 创建据点
24. 创建基础工厂
25. 创建通用建筑 Get/Send
26. 同步 BuildSlot 列表
```

## 阶段 E：完整阵营内容

```text
27. 创建单位
28. 创建武器
29. 创建工厂 UnitList
30. 创建 ACE 信标
31. 创建驾驶员
32. 创建特殊建筑
33. 填充完整科技树
34. 测试 AI
35. 测试混装 DLC
```

---

# 22. 推荐测试顺序

## 场景层

```text
场景按钮是否显示
→ Page 是否正确
→ Index 是否正确
→ HQ_GetMode 是否触发
→ Main 占位 HQ 是否生成
→ DLC 正式 HQ 是否转换
```

## 阵营层

```text
Pickup 是否显示
→ 介绍和图标是否正确
→ FactionIndex 是否写入
→ 阵营 Tag 是否添加
→ 起始科技 Tag 是否添加
→ 正式 HQ 是否正确
```

## 科技树层

```text
TechTree_Core 是否挂载
→ TechTreeMarkerSlot 是否正确
→ Page 是否显示
→ UnlockedListMarker 是否生成
→ BaseTech 是否存在
→ 起始科技是否生效
```

## 建筑层

```text
BuildingSlot 是否按场景转换
→ 据点是否识别新阵营
→ 通用建筑 Get/Send 是否注册
→ 工厂是否能打开
→ 建筑列表是否同步
```

## 单位层

```text
工厂能否生产
→ 科技能否解锁
→ PilotType 是否正确
→ ACE 信标是否工作
→ 单位 Tag 是否一致
```

## 兼容层

```text
只加载 Main
→ 加载 Main + 新 DLC
→ 加载 Main + 多个 DLC
→ 混装不同年代
→ 旧阵营是否仍正常
```

---

# 23. 常见错误

## 场景按钮出现但无法进入

检查：

```text
Page
场景 Index
HQ_GetMode
目标占位 HQ
Action 名称
```

## 进入场景但 HQ 不转换

检查：

```text
Main 占位 HQ 名称
DLC 正式 HQ 名称
overrideAndReplace
convertTo
DLC 是否加载
```

## 选择阵营后没有科技树

检查：

```text
FactionIndex
hiddenAction_ConvertToFaction
attachments_addNewUnits
TechTree_Core 名称
TechTreeMarkerSlot
Main Core 占位符
DLC 正式 Core
```

## 科技树打开但为空

检查：

```text
Page
TechList
Common 科技标记单位
BaseTech
Tech_阵营_Start
UnlockedListMarker
```

## 建筑槽不转换

检查：

```text
FactionIndex 列表
场景 Tag
ConvertTo_场景
目标 BuildingSlot
GameStart
Building attachment
```

## 据点无法识别新阵营

检查：

```text
StrategicLocation.ini
Main 公共逻辑
其他 DLC 是否同步
阵营 Tag
FactionIndex
```

## 工厂和建筑无法解锁

检查：

```text
Main Common Get/Send
DLC Tech/Faction
BuildSlot 列表
Unlock Tag
建筑自身 Tag
```

---

# 24. 第一版总结

新建阵营最核心的四条链是：

## 场景链

```text
HostOption Marker
→ Page
→ HQ_GetMode
→ Main 占位 HQ
→ DLC 正式 HQ
```

## 阵营链

```text
Pickup
→ FactionIndex
→ 阵营 Tag
→ 起始科技 Tag
→ 正式 HQ
```

## 科技树链

```text
Main Core 占位符
→ DLC TechTree_Core
→ BaseTech
→ Tech/Faction
→ UnlockedListMarker
→ HQ 挂载
```

## 建筑链

```text
Common Building Get/Send
→ BuildingSlot
→ StrategicLocation
→ 工厂
→ 据点
→ ACE 信标
→ 其他建筑
```

当前版本应视作：

> 可用于定位文件和安排工作顺序的第一版工作流，而不是绝对完整的最终规范。

后续发现遗漏时，应继续补充并以现有可运行阵营作为最终参考。
