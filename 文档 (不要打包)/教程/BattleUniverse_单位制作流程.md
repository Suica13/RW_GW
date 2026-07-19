# Battle Universe 新单位最小制作流程

本文以 `RGM_79.ini` 为基础，并参考以下四个派生单位：

- `RGM_79_Commander`：吉姆指挥官机
- `RGM_79L`：吉姆轻装甲型
- `RGC_80`：吉姆加农
- `RGM_79D`：吉姆寒冷地带式样

目标是说明：**如何先制作一个能够正常生成、移动、攻击和死亡的最小单位，再逐步扩展为完整单位。**

---

## 1. 推荐制作顺序

```text
选择最接近的现有单位
→ 复制单位目录和 INI
→ 修改单位 ID、名称和图标
→ 保留通用 MS 框架
→ 修改基础数值
→ 替换身体贴图
→ 接入一把远程武器
→ 接入一把近战武器
→ 进游戏测试
→ 添加护盾、装备切换和特殊能力
→ 添加派生或改造入口
```

不要从空白 INI 开始。优先复制体型、阵营、移动方式和武器结构最接近的单位。

---

## 2. 最小文件结构

```text
Units/BattleUnits/NEW_UNIT/
├─ NEW_UNIT.ini
└─ Image/
   ├─ NEW_UNIT_Crotch_1.png
   ├─ NEW_UNIT_Body_1.png
   ├─ NEW_UNIT_ArmL_1.png
   ├─ NEW_UNIT_ArmR_1.png
   ├─ NEW_UNIT_ShoulderL_1.png
   ├─ NEW_UNIT_ShoulderR_1.png
   ├─ NEW_UNIT_Head_1.png
   ├─ NEW_UNIT_Head_1_Close.png
   ├─ NEW_UNIT_Foot_1.png
   ├─ NEW_UNIT_LegL_1.png
   └─ NEW_UNIT_LegR_1.png

Resource/Image/Units/Icon/
└─ NEW_UNIT.png
```

最小单位通常只需要：

- 1 个单位 INI
- 约 10～11 张身体贴图
- 1 张单位图标
- 复用现有武器、动画、特效和驾驶员

---

## 3. 修改单位身份

先修改 `[core]` 和 `[graphics]`。

```ini
[core]
tags:NEW_UNIT,Unit,MS,EFSF,0079,UC
name:NEW_UNIT
displayText:New Unit
displayText_zh:新单位

maxHp:20000
maxShield:4000

[graphics]
icon_build:ROOT:Resource/Image/Units/Icon/NEW_UNIT.png
```

必须确认：

- `name` 没有与其他单位重复
- `tags` 中包含单位自身 ID
- 图标路径存在
- 中英文名称正确
- 单位目录名、INI 文件名和内部 ID 尽量统一

---

## 4. 保留通用 MS 框架

普通人形 MS 可以先保留以下结构：

```ini
copyFrom:"""
ROOT:Template/Unit/BattleUnit_Framework_MS.ini,
ROOT:Template/Unit/BattleUnit_Graphics_MS.ini,

ROOT:Resource/Image/Fx/Unit/Common_Unit_1.gw,
ROOT:Resource/Image/Fx/Common/Common_ExhaustGas_Double_1.gw,

ROOT:Template/Unit/Animation/Stats/Common_EQPilot_A.gw,
ROOT:Template/Unit/Animation/Stats/Common_Idle_A.gw,
ROOT:Template/Unit/Animation/Stats/Common_Dodge_A.gw,
ROOT:Template/Unit/Animation/Stats/Common_OnMoving.gw,
ROOT:Template/Unit/Animation/Stats/Common_OnMovingWalk.gw,
ROOT:Template/Unit/Animation/Stats/Common_Guard_A_L.gw,
ROOT:Template/Unit/Animation/Stats/Common_Dead_A.gw,
ROOT:Template/Unit/Animation/Stats/Common_Hitrecover_A.gw
"""
```

这些内容负责：

- MS 基础战斗框架
- 身体部件与损坏
- 驾驶员
- 移动、闪避和死亡动画
- 通用推进特效
- 护盾与修理等基础逻辑

第一次制作时不要急着删除通用引用。先确认单位能够正常运行，再逐项精简。

---

## 5. 填写基础数值

主要修改：

```ini
[hiddenAction_InitializeStats]
setUnitMemory:"""
unitLevel=1000,

enMax=750,
dpMax=1000,

baseHeight=1,
attackMode=0,
baseAttackRange=500,

baseFogOfWarSightRange=20,
baseDetectRange=memory.baseFogOfWarSightRange*18,

baseMoveSpeed=0.65,
boostMoveSpeed=1.4,
baseTurnSpeed=1.75,

baseShootLevel=120,
baseCqbLevel=115,
baseAccuracyLevel=115,
baseReactionLevel=115,

partStructuralStrength=120,
cockpitSafety=120,

groundAdaptability=100,
cliffAdaptability=100,
waterAdaptability=50,
skyAdaptability=10,
spaceAdaptability=100
"""
```

第一次测试优先确认：

1. HP 和护盾
2. EN 和 DP
3. 普通移动、推进和转向
4. 射击、格斗、命中和反应
5. 地形适应性
6. 基础射程

防御加成、建筑倍率和复杂护盾参数可以之后再调整。

---

## 6. 设置默认驾驶员

普通联邦量产机可以暂时复用：

```ini
[hiddenAction_InitializeAddPilot_Default]
addUnitsIntoTransport:Pilot_EFSF_0079_N_C_A*1
```

如果单位属于其他阵营、年代或特殊人物，再替换驾驶员。

驾驶员会影响部分能力计算，因此不建议完全删除。

---

## 7. 替换身体贴图

在各个 decal 中替换图片路径：

```ini
[decal_Crotch]
image:ROOT:\Units\BattleUnits\NEW_UNIT\Image\NEW_UNIT_Crotch_1.png

[decal_Body]
image:ROOT:\Units\BattleUnits\NEW_UNIT\Image\NEW_UNIT_Body_1.png

[decal_ArmL]
image:ROOT:\Units\BattleUnits\NEW_UNIT\Image\NEW_UNIT_ArmL_1.png

[decal_ArmR]
image:ROOT:\Units\BattleUnits\NEW_UNIT\Image\NEW_UNIT_ArmR_1.png
```

继续替换左右肩、头部、关闭状态头部、左右腿和左右脚。

第一次制作时尽量沿用原单位的画布尺寸、关节位置、部件中心点和身体比例，这样可以直接复用 `BattleUnit_Graphics_MS.ini`。

如果只是头部稍微偏移，可以局部修改：

```ini
[decal_Head]
xOffsetRelative:-0.5
```

不需要为了很小的差异重写整套图形模板。

---

## 8. 接入一把远程武器

在 `copyFrom` 中引用现有武器：

```ini
ROOT:Units/BattleUnits/Weapon/Beam/EF_BeamSprayGun.gw
```

然后设置触发条件：

```ini
[hiddenAction_EF_BeamSprayGun_Trigger]
autoTriggerOnEvent:newMessage(withTag="Attack")
requireConditional:"""
if distanceBetween(self,self.attacking)>60
and distanceBetween(self,self.attacking)<=memory.finalAttackRange
and memory.armRBreaked==false
"""
```

设置当前武器：

```ini
[hiddenAction_EF_BeamSprayGun_SetWeaponIndex]
setUnitMemory:nowWeaponIndex=0
```

设置武器显示：

```ini
[decal_EF_BeamSprayGun]
isVisible:if memory.nowWeaponIndex==0 and memory.armRBreaked==false
```

最初不要加入多个 `EquipmentIndex`。先让唯一一把远程武器正常攻击。

---

## 9. 接入一把近战武器

引用近战武器：

```ini
ROOT:Units/BattleUnits/Weapon/Cqb/EF_BeamSaber_A.gw
```

设置触发条件：

```ini
[hiddenAction_EF_BeamSaber_A_Trigger]
autoTriggerOnEvent:newMessage(withTag="Attack")
requireConditional:"""
if distanceBetween(self,self.attacking)<=60
and memory.armRBreaked==false
"""
```

设置武器索引：

```ini
[hiddenAction_EF_BeamSaber_A_SetWeaponIndex]
setUnitMemory:nowWeaponIndex=1
```

设置显示条件：

```ini
[decal_EF_BeamSaber_A]
isVisible:if memory.nowWeaponIndex==1 and memory.armRBreaked==false
```

可以保留右臂损坏后的推撞：

```ini
ROOT:Units/BattleUnits/Weapon/Cqb/Common_Push_A.gw

[hiddenAction_Common_Push_A_Trigger]
autoTriggerOnEvent:newMessage(withTag="Attack")
requireConditional:"""
if distanceBetween(self,self.attacking)<=60
and memory.armRBreaked==true
"""
```

---

## 10. 最小测试项目

第一次进入游戏只检查：

```text
单位能够加载
→ 能够生成
→ 身体部件正常显示
→ 能够移动和转向
→ 能够发现敌人
→ 远距离使用远程武器
→ 近距离使用近战武器
→ 能够受到伤害
→ 部件损坏不会报错
→ 能够正常死亡
```

此时不要同时制作三套装备切换、派生单位、专用武器、自定义动画或复杂随机武器。

---

# 11. 四种派生单位扩展案例

## 11.1 RGM-79 Commander：在原型上追加能力

指挥官机与普通吉姆整体结构非常接近，适合说明：

> **保留原单位结构，只增加少量性能、武器和特殊功能。**

主要变化：

- `unitLevel`、HP、护盾和机动略微提高
- 光束喷枪替换为光束枪
- 追加指挥通信模板 `CmdCom.gw`
- 追加双光束军刀攻击
- 双刀攻击受驾驶员格斗能力限制
- 大部分身体贴图继续复用普通吉姆
- 只为差异较大的胯部、身体等位置制作新贴图

```ini
ROOT:Template/Unit/Skill/CmdCom.gw
ROOT:Units/BattleUnits/Weapon/Beam/EF_BeamGun.gw
ROOT:Units/BattleUnits/Weapon/Cqb/EF_BeamSaber_Double_AALDF.gw
```

双刀攻击条件示例：

```ini
requireConditional:"""
if distanceBetween(self,self.attacking)<=60
and not (memory.armRBreaked==true and memory.armLBreaked==true)
and eventData("RandomWeapon",type="float")<50
and memory.pilotUnit.readUnitMemory(
    "pilotCqbSkillFinal",
    type="float"
)>145
"""
```

适合参考：

- 指挥官型
- 精英型
- 改良型
- 同一机体的高性能版本
- 只有少量外观区别的派生机

推荐流程：

```text
复制原单位
→ 保留大部分身体贴图
→ 修改少量专用贴图
→ 小幅提高数值
→ 替换或追加武器
→ 引用一个新技能模板
→ 添加技能使用条件
```

---

## 11.2 RGM-79L：通过数值重做单位定位

轻装甲型仍使用标准 MS 框架，但战斗定位与普通吉姆明显不同。

主要变化：

- HP 和护盾下降
- 普通移动、推进和转向明显提高
- 反应速度和闪避推进提高
- EN、部件强度下降
- 对建筑伤害下降
- 追加 `Common_FullBoost.gw`
- 武器数量减少
- 使用专用光束枪和专用光束军刀
- 使用较小护盾

```ini
ROOT:Units/BattleUnits/Weapon/Sp/Common_FullBoost.gw
ROOT:Units/BattleUnits/Weapon/Beam/EF_BOWA_BeamGun.gw
ROOT:Units/BattleUnits/Weapon/Cqb/EF_BeamSaber_BF.gw
```

关键数值方向：

```ini
maxHp:17000
maxShield:3250

baseMoveSpeed=0.75
boostMoveSpeed=1.65
baseTurnSpeed=2.5
baseReactionLevel=140
onDodgeBoostSpeed=1.35

partStructuralStrength=100
extraBuildingDef=0.65
extraBuildingAtk=0.75
```

适合参考：

- 轻装型
- 高机动型
- 强袭型
- 防御换速度的单位
- 需要重新定义战斗定位的派生机

推荐流程：

```text
复制原单位
→ 先确定新定位
→ 同时修改优点和缺点
→ 调整机动、防御、续航和适应性
→ 删除不符合定位的武器
→ 添加与定位匹配的特殊能力
→ 制作完整的新身体贴图
```

重点不是单纯提高数值，而是形成明确交换：

```text
速度提高
↔ 耐久和续航下降
```

---

## 11.3 RGC-80：改变战斗逻辑和部件功能

吉姆加农不只是数值不同，而是增加背包火炮，并改变攻击距离和攻击选择。

主要变化：

- 基础射程从 500 提高到 750
- 射击能力提高
- 推进、转向和反应下降
- 对建筑伤害提高
- 追加背部加农炮贴图
- 引用 `Common_Cannon.gw` 和 `Common_Mortar.gw`
- 根据距离和随机数选择手持武器或火炮
- 火炮依赖背包未损坏
- 近战能力明显弱化

新增炮身：

```ini
[decal_RGC_80_Cannon]
layer:beforeBody
order:7
isVisible:true
image:ROOT:\Units\BattleUnits\RGC_80\Image\RGC_80_Cannon_1.png
basePositionFromLegEnd:arm2
xOffsetRelative:7.5
yOffsetRelative:0
dirOffset:0
onlyWhileAlive:true
```

火炮触发：

```ini
[hiddenAction_Common_Cannon_Trigger]
autoTriggerOnEvent:newMessage(withTag="Attack")
requireConditional:"""
if distanceBetween(self,self.attacking)>120
and distanceBetween(self,self.attacking)<=memory.finalAttackRange
and memory.attackMode==0
and eventData("RandomWeapon",type="float")<=25
and memory.backpackBreaked==false
"""
```

适合参考：

- 炮击型
- 狙击型
- 背包武器单位
- 肩炮单位
- 武器与部件损坏联动的单位
- 根据距离随机选择攻击方式的单位

推荐流程：

```text
复制原单位
→ 增加特殊部件贴图
→ 引用特殊武器模板
→ 修改基础射程
→ 为不同武器划分距离
→ 用随机数控制攻击比例
→ 添加部件完好条件
→ 添加部件损坏后的降级行为
```

这类单位应单独测试火炮贴图、火炮触发、背包损坏、近距离行为和多武器重复触发。

---

## 11.4 RGM-79D：专用武器、特殊推进和环境限制

寒冷地带型保留标准吉姆结构，但围绕专用用途重新配置。

主要变化：

- 追加全力推进 `Common_FullBoost.gw`
- 使用强化推撞、强化火箭筒和强化光束军刀
- 使用专用穿甲 90mm 机枪
- 推进速度、反应和射击提高
- EN 大幅下降
- 宇宙适应性明显降低
- 使用后期型护盾
- 武器切换减少为机枪和火箭筒两套
- 制作完整的新身体贴图

```ini
ROOT:Units/BattleUnits/Weapon/Sp/Common_FullBoost.gw
ROOT:Units/BattleUnits/Weapon/Cqb/Common_Push_A_Lv2.gw
ROOT:Units/BattleUnits/Weapon/Shell/EF_HypeBazooka_Lv2.gw
ROOT:Units/BattleUnits/Weapon/Shell/EF_90mmMG_79D.gw
ROOT:Units/BattleUnits/Weapon/Cqb/EF_BeamSaber_A_Lv2.gw
```

关键数值方向：

```ini
enMax=400
boostMoveSpeed=1.60
baseShootLevel=130
baseReactionLevel=130
spaceAdaptability=25
```

适合参考：

- 环境专用型
- 寒冷地、沙漠或水中型
- 使用专用弹药的单位
- 武器强化版
- 高爆发、低续航单位

推荐流程：

```text
复制原单位
→ 确定专用环境
→ 修改地形适应性
→ 增加专用武器
→ 使用强化版通用武器
→ 加入特殊推进能力
→ 用续航或环境限制平衡性能
```

环境专用机不应只增加对应环境数值，还应通过其他地形适应性、续航、武器或成本表现出限制。

---

# 12. 四种扩展方式总结

| 案例 | 核心扩展方式 | 适合制作 |
|---|---|---|
| RGM-79 Commander | 原型基础上追加技能和少量武器 | 指挥官机、精英机、改良机 |
| RGM-79L | 重新分配性能，形成明确优缺点 | 轻装型、高机动型、强袭型 |
| RGC-80 | 增加特殊部件并改变攻击逻辑 | 炮击型、狙击型、背包武器型 |
| RGM-79D | 加入专用武器、推进和环境限制 | 环境专用型、低续航高爆发型 |

选择模板时，不要只看外观是否相似，也要看单位的扩展方式：

```text
只是增强原型
→ 参考 Commander

主要修改性能定位
→ 参考 RGM-79L

增加特殊部件和攻击规则
→ 参考 RGC-80

增加专用武器和环境限制
→ 参考 RGM-79D
```

---

# 13. 完整单位的后续扩展顺序

最小单位测试通过后，建议按照以下顺序扩展：

```text
护盾
→ 第二把远程武器
→ 装备切换
→ 头部或背包武器
→ 特殊推进
→ 随机武器选择
→ 部件损坏联动
→ 驾驶员能力条件
→ 主动技能
→ 改造或派生入口
```

每加入一个系统就进游戏测试一次，不要一次加入全部内容。

---

# 14. 派生入口写法

RGM-79 通过 `CustomUnit.gw` 提供派生改造入口：

```ini
ROOT:Template/Unit/Skill/CustomUnit.gw
```

示例：

```ini
[action_CustomUnit_NEW_VARIANT]
@copyFromSection:template_CustomUnit

@define UnitID=NEW_VARIANT
@define CustomRule=(self.globalTeamTags(includes='Unlock_NEW_VARIANT'))

@define Money=500
@define Resource=500

setResourcesWithLogic:"""
EquipmentIndex=0
"""
```

需要确认：

- `UnitID` 与目标单位 `name` 一致
- 解锁 Tag 正确
- 金钱与资源消耗正确
- 改造前需要清理或重置的资源已经处理
- 目标单位可以独立正常生成

派生单位本身仍应拥有完整、可独立运行的 INI，不要依赖改造入口替代初始化。

---

# 15. 最终检查清单

## 文件

- [ ] 单位目录存在
- [ ] INI 文件名正确
- [ ] 所有图片路径存在
- [ ] 图标存在
- [ ] 所有 `copyFrom` 路径存在
- [ ] 单位 `name` 唯一

## 显示

- [ ] 身体部件位置正确
- [ ] 武器显示条件正确
- [ ] 不使用武器时的收纳贴图正确
- [ ] 护盾位置正确
- [ ] 特殊部件层级正确
- [ ] 死亡后贴图不会继续错误显示

## 战斗

- [ ] 远程武器正常触发
- [ ] 近战武器正常触发
- [ ] 武器距离没有空白区
- [ ] 多个武器不会同时错误触发
- [ ] 右臂损坏后行为正常
- [ ] 左臂损坏后护盾失效
- [ ] 背包损坏后背包武器失效
- [ ] 武器索引与贴图显示一致

## 数值

- [ ] HP、护盾、EN 和 DP 正确
- [ ] 移动与推进符合定位
- [ ] 射程符合武器用途
- [ ] 地形适应性正确
- [ ] 优点与缺点同时存在
- [ ] 派生机不是单纯全面强化原型

---

# 16. 最简结论

制作新单位时，先完成：

```text
单位 INI
+ 身体贴图
+ 图标
+ 一把远程武器
+ 一把近战武器
```

确认最小战斗闭环后，再根据目标选择扩展方向：

```text
增强原型
→ Commander 型

改变性能定位
→ Light Armor 型

增加特殊部件和攻击逻辑
→ Cannon 型

增加专用武器和环境限制
→ Cold Type 型
```

这样能够把报错范围控制在单个步骤内，也更容易判断问题来自文件路径、decal、武器模板、触发条件、部件损坏、数值初始化还是特殊技能。

