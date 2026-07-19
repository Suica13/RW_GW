# Battle Universe 工厂接入流程

本文说明如何把一个已经完成单位本体和科技树注册的新单位，加入对应阵营的工厂生产列表。

以下以联邦 0079 陆军工厂和 `RGM_79` 为例。

---

# 1. 工厂接入结构

主要涉及三个位置：

```text
Units/Buildings/Factory/UnitList/EFSF_0079/Units/
Units/Buildings/Factory/UnitList/EFSF_0079/
Units/Buildings/Factory/Faction/EFSF_0079/
```

完整关系：

```text
单位生产定义文件
→ 阵营 UnitList 注册
→ 阵营工厂继承 UnitList
→ 工厂显示生产按钮
→ 检查科技解锁 Tag
→ 生产目标单位
```

---

# 2. 第一步：选择正确的工厂分类

先进入：

```text
GW_BattleUniverse_DLC_0079/
└─ Units/
   └─ Buildings/
      └─ Factory/
         └─ UnitList/
            └─ EFSF_0079/
               └─ Units/
```

这里按工厂类型划分单位。

普通泛用 MS 一般放入：

```text
Units/Land/
```

例如：

```text
Units/Land/RGM_79.gw
```

选择目录时，应根据单位实际用途判断：

```text
普通陆战或泛用 MS
→ Land

航空单位或空中工厂单位
→ Air

宇宙专用单位
→ 对应宇宙工厂目录

舰船、特殊兵器或其他分类
→ 参考同类型现有单位
```

不要只根据机体名字决定目录，应优先参考：

- 单位由哪个工厂生产
- 单位主要移动环境
- 同类型单位被放在哪个列表
- 阵营当前工厂分类

---

# 3. 第二步：复制单位生产定义

参考文件：

```text
GW_BattleUniverse_DLC_0079/
└─ Units/
   └─ Buildings/
      └─ Factory/
         └─ UnitList/
            └─ EFSF_0079/
               └─ Units/
                  └─ Land/
                     └─ RGM_79.gw
```

复制一份并改名：

```text
RGM_79.gw
→ NEW_UNIT.gw
```

建议优先选择生产方式最接近的新单位作为模板。

例如：

```text
普通三机小队
→ 参考 RGM_79

单机生产
→ 参考其他单机单位

多种装备小队
→ 参考带 EquipmentIndex 的单位

特殊驾驶员或固定编制
→ 参考相同生产结构的单位
```

---

# 4. `RGM_79.gw` 的主要职责

`RGM_79.gw` 并不是战斗单位本体，而是工厂中的生产列表定义。

它主要负责：

- 工厂生产面板按钮
- 自动生产
- 生产费用
- 建造时间
- 生产数量
- 驾驶员类型
- 装备索引
- 小队编制
- 解锁和显示条件

文件首先继承生产模板：

```ini
[core]
copyFrom:ROOT:Units/Buildings/Factory/UnitList/Mod/UnitTemplate.ini
```

普通新增单位不需要修改 `UnitTemplate.ini`。

---

# 5. 修改单位 ID

复制后，应先全局检查并修改：

```text
RGM_79
→ NEW_UNIT
```

主要包括：

```ini
@memory NEW_UNIT:bool
```

```ini
[hiddenAction_Pannel_Close_NEW_UNIT]
setUnitMemory:NEW_UNIT=false
```

```ini
[hiddenAction_AutoProduce_NEW_UNIT]
@define UnitID=NEW_UNIT
```

```ini
[action_Pannel_NEW_UNIT]
@define UnitID=NEW_UNIT
```

```ini
[action_Produce_NEW_UNIT]
@define UnitID=NEW_UNIT
```

以及所有：

```ini
produceUnits:NEW_UNIT*1(...)
```

必须保持以下内容一致：

```text
单位本体 name
=
单位本体自身 Tag
=
工厂 UnitID
=
produceUnits 中的单位 ID
=
科技树注册的 UnitID
```

例如：

```ini
[core]
name:NEW_UNIT
tags:NEW_UNIT,Unit,MS,EFSF,0079,UC
```

工厂中则使用：

```ini
@define UnitID=NEW_UNIT
```

以及：

```ini
produceUnits:"""
NEW_UNIT*1
"""
```

---

# 6. 生产面板按钮

参考：

```ini
[action_Pannel_RGM_79]
@copyFromSection:template_Pannel

@define UnitID=RGM_79
@define FactionVisible=(memory.Pannel_EFSF_0079_DontShow==false)
```

新单位修改为：

```ini
[action_Pannel_NEW_UNIT]
@copyFromSection:template_Pannel

@define UnitID=NEW_UNIT
@define FactionVisible=(memory.Pannel_EFSF_0079_DontShow==false)
```

该段负责：

- 在工厂中显示单位面板入口
- 打开该单位的具体生产选项
- 判断当前阵营面板是否应显示

通常直接复制并修改 `UnitID` 即可。

---

# 7. 科技解锁与单位 Tag

工厂中的生产模板会根据单位 ID 和阵营科技解锁状态判断是否显示或允许生产。

因此三个部分必须一致：

```text
单位制作：
name:NEW_UNIT
tags 中包含 NEW_UNIT

科技树：
注册 NEW_UNIT
完成后获得 Unlock_NEW_UNIT

工厂：
@define UnitID=NEW_UNIT
produceUnits 使用 NEW_UNIT
```

完整链条：

```text
单位 tags 包含 NEW_UNIT
→ 科技树完成 NEW_UNIT 科技
→ 阵营获得 Unlock_NEW_UNIT
→ 工厂模板检查 NEW_UNIT
→ 显示对应生产按钮
→ 允许生产 NEW_UNIT
```

如果命名不一致，常见结果包括：

- 科技已经研究，但工厂按钮不出现
- 按钮出现但无法生产
- 工厂生产了错误单位
- 自动生产不工作
- 工厂无法正确读取装备或单位信息

---

# 8. 修改生产费用和时间

参考 RGM-79 标准小队：

```ini
[action_Produce_RGM_79_StandardSquad]
@copyFromSection:template_Produce

@define UnitID=RGM_79
@define Money=1950
@define Resource=3200
@define FactionVisible=(memory.Pannel_EFSF_0079_DontShow==false)

buildSpeed:45s
```

新单位示例：

```ini
[action_Produce_NEW_UNIT_StandardSquad]
@copyFromSection:template_Produce

@define UnitID=NEW_UNIT
@define Money=2000
@define Resource=3500
@define FactionVisible=(memory.Pannel_EFSF_0079_DontShow==false)

buildSpeed:45s
```

主要修改：

```text
UnitID
Money
Resource
buildSpeed
按钮名称
中文名称
```

价格应按照生产编制计算，而不是只看单机单位强度。

---

# 9. 修改实际生产单位

RGM-79 的标准小队会连续生成三台单位。

示例结构：

```ini
alsoQueueAction:"""
Produce_RGM_79_StandardSquad_1,
Produce_RGM_79_StandardSquad_2,
Produce_RGM_79_StandardSquad_3
"""
```

然后分别生产：

```ini
[hiddenAction_Produce_RGM_79_StandardSquad_1]
buildSpeed:0.0s
highPriorityQueue:true

produceUnits:"""
RGM_79*1(addResources=PilotType:1101|EquipmentIndex:0)
"""
```

新单位需要修改为：

```ini
[hiddenAction_Produce_NEW_UNIT_StandardSquad_1]
buildSpeed:0.0s
highPriorityQueue:true

produceUnits:"""
NEW_UNIT*1(addResources=PilotType:1101|EquipmentIndex:0)
"""
```

---

# 10. 驾驶员与装备索引

生产定义可以通过 `addResources` 为新单位写入初始资源。

常见内容：

```ini
addResources=PilotType:1101|EquipmentIndex:0
```

其中：

```text
PilotType
→ 指定初始驾驶员类型或驾驶员配置

EquipmentIndex
→ 指定单位生成时使用的装备组合
```

例如 RGM-79 的不同小队使用不同装备：

```text
EquipmentIndex:0
→ 标准装备

EquipmentIndex:1
→ 机枪装备

EquipmentIndex:2
→ 火箭筒装备
```

新单位如果只有一种装备，可以统一使用：

```ini
EquipmentIndex:0
```

如果单位本体没有使用 `EquipmentIndex`，则不要无意义地复制多套生产按钮。

---

# 11. 自动生产

RGM-79 包含自动生产定义：

```ini
[hiddenAction_AutoProduce_RGM_79]
@copyFromSection:template_AutoProduce

@define UnitID=RGM_79

alsoTriggerAction:AutoProduce_RGM_79_Step2
```

第二阶段处理自动生产费用：

```ini
[hiddenAction_AutoProduce_RGM_79_Step2]
@copyFromSection:template_AutoProduce_Step2

@define Money=1500
@define Resource=2050
```

之后通过随机值选择：

```text
标准小队
机枪小队
火箭筒小队
```

新单位复制后需要同步修改：

- Action 名称
- `UnitID`
- 自动生产费用
- 随机分支
- 最终队列 Action
- `produceUnits`

如果新单位只有一种生产方式，可以简化自动生产逻辑，不必保留三个随机分支。

---

# 12. 第三步：在阵营 UnitList 中注册

编辑：

```text
GW_BattleUniverse_DLC_0079/
└─ Units/
   └─ Buildings/
      └─ Factory/
         └─ UnitList/
            └─ EFSF_0079/
               └─ EFSF_0079_UnitList_Land.ini
```

该文件负责整合联邦 0079 陆军工厂的单位生产定义。

其中会依次引用：

```ini
ROOT:Units/Buildings/Factory/UnitList/EFSF_0079/Units/Land/RGM_79.gw,
ROOT:Units/Buildings/Factory/UnitList/EFSF_0079/Units/Land/RGM_79_Commander.gw,
ROOT:Units/Buildings/Factory/UnitList/EFSF_0079/Units/Land/RGM_79L.gw,
ROOT:Units/Buildings/Factory/UnitList/EFSF_0079/Units/Land/RGC_80.gw,
```

新增单位时追加：

```ini
ROOT:Units/Buildings/Factory/UnitList/EFSF_0079/Units/Land/NEW_UNIT.gw,
```

建议放在同系列或同类型单位附近。

注意：

```text
创建 NEW_UNIT.gw
≠ 已经加入工厂

必须在 EFSF_0079_UnitList_Land.ini 中注册
```

---

# 13. 第四步：确认工厂继承 UnitList

目标工厂：

```text
GW_BattleUniverse_DLC_0079/
└─ Units/
   └─ Buildings/
      └─ Factory/
         └─ Faction/
            └─ EFSF_0079/
               └─ Factory_EFSF_0079_Land.ini
```

其 `[core]` 中继承：

```ini
[core]
copyFrom:"""
ROOT:Units/Buildings/Factory/Mod/Factory.ini,
ROOT:Units/Buildings/Factory/UnitList/ZEON_0079/ZEON_0079_UnitList_Land.ini,
ROOT:Units/Buildings/Factory/UnitList/EFSF_0079/EFSF_0079_UnitList_Land.ini,
ROOT:Template/Building/Skill/Upgrade.gw
"""
```

因为工厂已经继承：

```ini
ROOT:Units/Buildings/Factory/UnitList/EFSF_0079/EFSF_0079_UnitList_Land.ini
```

所以只要新单位已经注册进这个 UnitList，继承该列表的工厂就可以加载它。

普通新增陆军单位时，一般不需要修改：

```text
Factory_EFSF_0079_Land.ini
```

只需要确认目标工厂确实继承了对应 UnitList。

---

# 14. 多阵营列表与显示条件

当前陆军工厂同时继承：

```ini
ZEON_0079_UnitList_Land.ini
EFSF_0079_UnitList_Land.ini
```

但生产按钮还会通过阵营显示条件与解锁条件进行筛选。

例如：

```ini
@define FactionVisible=(memory.Pannel_EFSF_0079_DontShow==false)
```

因此：

```text
列表被工厂加载
≠ 所有阵营都能看到并生产
```

是否显示仍由以下内容共同决定：

- 阵营面板状态
- 科技解锁 Tag
- 单位 Tag
- 生产模板条件

---

# 15. 最小接入顺序

```text
1. 确认单位本体 name 与自身 Tag
2. 确认科技树能够产生 Unlock_NEW_UNIT
3. 判断单位属于哪个工厂分类
4. 复制相近单位的生产定义文件
5. 修改所有 UnitID 和 Action 名称
6. 修改生产费用和时间
7. 修改生产数量
8. 修改 PilotType
9. 修改 EquipmentIndex
10. 修改自动生产逻辑
11. 在对应 UnitList 中注册 NEW_UNIT.gw
12. 确认目标工厂继承该 UnitList
13. 进入游戏测试
```

---

# 16. 测试顺序

## 文件加载

```text
NEW_UNIT.gw 路径正确
→ UnitList 中路径正确
→ 路径末尾逗号正确
→ 工厂继承正确 UnitList
→ 无重复 Action 名称
```

## 面板显示

```text
未解锁时按钮是否隐藏
→ 完成科技后按钮是否出现
→ 是否出现在正确阵营面板
→ 是否出现在正确工厂
```

## 生产

```text
费用是否正确扣除
→ 建造时间是否正确
→ 生产数量是否正确
→ 驾驶员类型是否正确
→ EquipmentIndex 是否正确
```

## 自动生产

```text
AI 是否会选择该单位
→ 自动生产是否检查解锁状态
→ 自动费用是否合理
→ 随机装备分支是否正确
```

---

# 17. 常见错误

## 工厂中完全不显示

检查：

```text
NEW_UNIT.gw 是否注册进 UnitList
工厂是否继承正确 UnitList
单位 name、Tag、UnitID 是否一致
科技树是否真正获得 Unlock_NEW_UNIT
阵营显示条件是否正确
```

## 按钮出现但生产错误单位

检查：

```text
produceUnits 是否仍写着参考单位
Action 名称是否重复
UnitID 是否修改完整
EquipmentIndex 是否对应单位本体
```

## 只能手动生产，AI 不生产

检查：

```text
AutoProduce 是否复制
自动生产 UnitID 是否正确
自动生产费用是否设置
最终是否进入有效 Produce Action
```

## 科技研究完成但仍无法生产

检查命名链：

```text
单位 name
单位自身 Tag
TechList UnitID
Send UnitID
Get UnitID
Unlock_NEW_UNIT
工厂 UnitID
produceUnits 单位 ID
```

---

# 18. 完整连携关系

```text
单位本体 NEW_UNIT.ini
└─ name:NEW_UNIT
└─ tags 包含 NEW_UNIT
      ↓
科技树
└─ 研究完成
└─ 添加 Unlock_NEW_UNIT
      ↓
Units/Land/NEW_UNIT.gw
└─ 定义面板、费用、时间和生产编制
      ↓
EFSF_0079_UnitList_Land.ini
└─ 注册 NEW_UNIT.gw
      ↓
Factory_EFSF_0079_Land.ini
└─ 继承 EFSF_0079_UnitList_Land.ini
      ↓
陆军工厂
└─ 检查阵营和解锁条件
└─ 显示生产按钮
└─ 生产 NEW_UNIT
```

---

# 19. 最简操作清单

```text
1. 在正确分类目录复制参考单位的 .gw
2. 将参考单位 ID 全部替换为新单位 ID
3. 修改生产费用、时间和数量
4. 修改 PilotType 与 EquipmentIndex
5. 按需要修改自动生产
6. 在对应 EFSF_0079_UnitList_XXX.ini 中注册
7. 确认目标工厂继承该 UnitList
8. 检查单位 name、Tag、Unlock Tag 和 UnitID 一致
9. 测试手动生产
10. 测试 AI 自动生产
```

普通新增单位一般不需要修改：

```text
Factory.ini
UnitTemplate.ini
其他 Mod 模板
```

只有需要改变整个工厂或生产列表的基础逻辑时，才考虑修改模板层。
