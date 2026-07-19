# Battle Universe 科技树接入流程

以下内容以联邦 0079 科技树为例。

主要目录：

```text
GW_BattleUniverse_DLC_0079/
└─ Units/
   └─ TechTree/
      ├─ Button/
      ├─ Core/
      ├─ Mod/
      ├─ Tech/
      └─ UnlockedListMarker/
```

制作普通新单位时，主要需要处理：

```text
单位自身 tags
→ Get / Send 注册
→ TechList 科技信息
→ Common 科技标记单位
→ UI 页面中的节点位置和连线
→ UI 主页面逻辑
```

`Mod` 一般是模板目录。除非需要修改科技树的基本运行逻辑，否则不要修改。

---

## 1.1 `Core/Faction/EFSF_0079`

```text
TechTree_EFSF_0079.gw
TechTree_UI_Main_EFSF_0079.ini
TechTree_UI_Page_EFSF_0079_00.ini
TechTree_UI_Page_EFSF_0079_01.ini
```

| 文件 | 用途 | 普通新增单位时 |
|---|---|---|
| `TechTree_EFSF_0079.gw` | 阵营科技树核心入口或底层整合 | 暂时不处理 |
| `TechTree_UI_Main_EFSF_0079.ini` | 页面切换、打开关闭和页面逻辑 | 一般复制现有段修改 |
| `TechTree_UI_Page_EFSF_0079_00.ini` | 第 0 页节点位置和连线 | 需要 |
| `TechTree_UI_Page_EFSF_0079_01.ini` | 第 1 页节点位置和连线 | 需要 |

`Page` 文件只负责面板表现：

- 科技标记单位的位置
- 节点之间的连线
- 节点与连线的显示条件
- 节点所属页面

它不负责真正注册单位，也不代表工厂已经可以生产。

---

## 1.2 单位自身的 `tags`

单位 `[core]` 中必须包含自己的 `name`：

```ini
[core]
name:NEW_UNIT
tags:NEW_UNIT,Unit,MS,EFSF,0079,UC
```

科技树注册与工厂解锁会通过单位 Tag 判断目标，因此应保证：

```text
单位 name
=
单位自身 Tag
=
科技树注册使用的 UnitID
```

例如：

```ini
name:RGM_79
tags:RGM_79,Unit,MS,EFSF,0079,UC
```

缺少自身 Tag 时，可能出现：

- 科技完成但工厂找不到目标单位
- 解锁列表中有单位 ID，但生产条件判断失败
- 派生、筛选或阵营注册无法识别该单位

---

## 1.3 `EFSF_0079_Get.ini`

路径：

```text
Units/TechTree/Tech/Faction/EFSF_0079/EFSF_0079_Get.ini
```

它负责接收解锁消息，并把对应解锁 Tag 加入阵营。

基础模板：

```ini
[template_Get_UnlockInfo]
@define UnitID=Test

autoTriggerOnEvent:newMessage(withTag="Unlock_${UnitID}")
addGlobalTeamTags:Unlock_${UnitID}
```

新单位追加：

```ini
[hiddenAction_Get_UnlockInfo_NEW_UNIT]
@copyFromSection:template_Get_UnlockInfo
@define UnitID=NEW_UNIT
```

运行关系：

```text
收到 Unlock_NEW_UNIT
→ Get 中识别 NEW_UNIT
→ 阵营获得 Unlock_NEW_UNIT
→ 工厂和其他系统可以检测该 Tag
```

可以把 `Get` 理解成：

> 把“科技完成事件”转换为“阵营解锁状态”。

---

## 1.4 `EFSF_0079_Send.ini`

路径：

```text
Units/TechTree/Tech/Faction/EFSF_0079/EFSF_0079_Send.ini
```

它负责把单位加入阵营科技树的发送或同步流程。

新增单位时，复制同类型、同层级单位的段落，再修改：

```text
段落名称
UnitID
发送消息
相关 Tag
```

它与 `Get` 是一组：

```text
Send
→ 发出或转交 Unlock_NEW_UNIT

Get
→ 接收 Unlock_NEW_UNIT
→ 添加 Unlock_NEW_UNIT 阵营 Tag
```

不要只改 `Get` 而漏掉 `Send`。

---

## 1.5 `TechList_EFSF_0079.ini`

路径：

```text
Units/TechTree/Tech/Faction/EFSF_0079/TechList_EFSF_0079.ini
```

该文件处理每项科技的信息，通常包括：

- 科技 ID
- 对应单位 ID
- 科技名称
- 科技说明
- 研究费用
- 研究时间
- 前置科技
- 解锁条件
- 完成后发送的解锁消息
- 科技层级或分类

新增时，应复制位置、层级和用途最接近的现有科技。

示意：

```ini
[tech_NEW_UNIT]
@copyFromSection:某个同类科技模板

@define UnitID=NEW_UNIT
@define TechID=Tech_NEW_UNIT
@define PreTech=Tech_OLD_UNIT
```

具体字段以被复制的现有科技段为准，不要凭空新建另一套命名规则。

---

## 1.6 `Tech/Faction/EFSF_0079/Common`

路径：

```text
Units/TechTree/Tech/Faction/EFSF_0079/Common/
```

这里存放与 `TechList_EFSF_0079.ini` 中科技项目对应的科技树标记单位。

科技标记单位不是最终可生产的战斗单位，而是科技树 UI 使用的节点实体。

通常负责：

- 科技节点图标
- 节点名称
- 节点说明
- 点击或研究行为
- 已解锁、可研究、未满足条件状态
- 与 `TechList` 中科技 ID 对应

新增单位时：

```text
复制相近科技标记
→ 修改科技 ID
→ 修改目标 UnitID
→ 修改图标和名称
→ 确认与 TechList 对应
```

关系如下：

```text
TechList 中的科技信息
↕
Common 中的科技标记单位
↕
UI Page 中的节点位置
```

三者缺一不可。

---

# 2. 加入科技树的最小顺序

## 第 1 步：确认单位本体

先保证新单位可以独立生成和战斗。

检查：

```text
name 正确
tags 包含自己的 name
图标存在
单位本体可正常加载
```

科技树不能修复单位本体错误。

---

## 第 2 步：选择参考科技

选择一个满足以下条件的现有单位：

- 同阵营
- 同页面
- 同科技层级
- 相似前置关系
- 相似解锁方式

后续所有文件尽量沿用同一个参考科技，避免混用不同案例。

---

## 第 3 步：在 `Get` 中注册接收

编辑：

```text
EFSF_0079_Get.ini
```

追加：

```ini
[hiddenAction_Get_UnlockInfo_NEW_UNIT]
@copyFromSection:template_Get_UnlockInfo
@define UnitID=NEW_UNIT
```

---

## 第 4 步：在 `Send` 中注册发送

编辑：

```text
EFSF_0079_Send.ini
```

复制参考单位对应段落，将单位 ID 改为：

```text
NEW_UNIT
```

确认最终发送：

```text
Unlock_NEW_UNIT
```

---

## 第 5 步：在 `TechList` 中定义科技

编辑：

```text
TechList_EFSF_0079.ini
```

复制参考科技并修改：

```text
科技段落 ID
目标 UnitID
科技名称
说明
费用
时间
前置科技
解锁消息
```

先保证命名链一致：

```text
NEW_UNIT
Tech_NEW_UNIT
Unlock_NEW_UNIT
```

---

## 第 6 步：制作科技标记单位

进入：

```text
Tech/Faction/EFSF_0079/Common/
```

复制参考科技标记单位并修改：

```text
文件名
单位 name
科技 ID
目标 UnitID
显示名称
显示说明
图标
研究条件
```

重点检查：

```text
标记单位引用的科技 ID
=
TechList 中新增的科技 ID
```

---

## 第 7 步：放入科技树页面

根据目标位置编辑：

```text
TechTree_UI_Page_EFSF_0079_00.ini
```

或：

```text
TechTree_UI_Page_EFSF_0079_01.ini
```

复制参考节点并修改：

- 科技标记单位 ID
- X、Y 位置
- 显示条件
- 前置连线
- 后续连线

建议先放在空白位置确认显示，再调整排版。

---

## 第 8 步：必要时修改主页面逻辑

编辑：

```text
TechTree_UI_Main_EFSF_0079.ini
```

普通情况下通常只是复制已有调用并改 ID。

只有以下情况才需要较大改动：

- 新增第三页
- 改变翻页规则
- 增加新科技分类
- 修改页面加载方式
- 改变科技树打开关闭逻辑

---

## 第 9 步：测试解锁和生产

测试顺序：

```text
未研究时节点是否显示
→ 前置条件是否正确
→ 资源不足时是否不能研究
→ 完成后是否发出 Unlock_NEW_UNIT
→ 阵营是否获得 Unlock_NEW_UNIT
→ 工厂是否识别 NEW_UNIT Tag
→ 单位是否出现在正确工厂
→ 是否可以正常生产
→ 重新读取存档后是否仍然解锁
```

---

# 3. `TechTree` 下其他目录的用途

## `Button`

```text
TechTree_UI_Close.ini
TechTree_UI_LastPage.ini
TechTree_UI_NextPage.ini
```

负责：

- 关闭科技树 UI
- 上一页
- 下一页

普通新增单位不需要修改。  
只有新增页面或改变翻页逻辑时才需要处理。

---

## `Core`

包含：

```text
Core/0079/
Core/Faction/
```

### `Core/0079`

负责 0079 年代共用的科技树核心或入口。

普通新增联邦单位通常不需要修改。

### `Core/Faction`

负责阵营各自的科技树：

```text
Faction/EFSF_0079/
Faction/ZEON_0079/
```

主要内容：

- 阵营科技树核心入口
- 主页面
- 各科技树页面
- UI 节点与连线

新增单位主要修改 `UI_Main` 和 `UI_Page`，不要随意改核心 `.gw`。

---

## `Tech`

包含：

```text
Tech/Faction/Common/
Tech/Faction/EFSF_0079/
Tech/Faction/ZEON_0079/
```

主要负责：

- 阵营单位注册
- 科技信息
- 解锁消息
- 科技标记单位
- 阵营科技清单

这是新增科技单位最主要的逻辑目录。

---

## `UnlockedListMarker`

包含：

```text
UnlockedListMarker_0079.ini
UnlockedListMarker/Mod/
```

从结构上看，它负责记录或显示 0079 科技树已解锁项目。

可能承担：

- 已解锁单位标记
- 解锁状态同步
- 已解锁列表判断
- UI 或其他系统读取的中间状态

是否需要修改，应先搜索参考单位 ID：

```text
参考单位存在
→ 新单位复制对应段落

参考单位不存在
→ 暂时不修改
```

不要只看目录名就直接添加。

---

## `Mod`

包含通用模板：

```text
TechList.gw
TechMarker.gw
TechTree_Core.gw
TechTree_UI_Main.gw
TechTree_UI_Page.gw
```

普通新增单位时：

```text
不修改
不复制到阵营目录
不重写底层逻辑
```

只有需要改变整个科技树系统行为时才考虑。

---

# 4. 完整连携关系

```text
NEW_UNIT.ini
└─ name:NEW_UNIT
   └─ tags 中包含 NEW_UNIT
      ↓
TechList_EFSF_0079.ini
└─ 定义科技费用、前置和目标
      ↓
Common/科技标记单位
└─ 提供可点击科技节点
      ↓
TechTree_UI_Page_EFSF_0079_XX.ini
└─ 决定节点位置和连线
      ↓
TechTree_UI_Main_EFSF_0079.ini
└─ 负责页面逻辑
      ↓
EFSF_0079_Send.ini
└─ 发送 Unlock_NEW_UNIT
      ↓
EFSF_0079_Get.ini
└─ 添加 Unlock_NEW_UNIT 阵营 Tag
      ↓
工厂
└─ 检查 Unlock_NEW_UNIT 与 NEW_UNIT Tag
      ↓
允许生产 NEW_UNIT
```

最容易遗漏：

```text
单位自身 Tag
Get 注册
Send 注册
TechList
科技标记单位
UI 节点
UI 连线
```

---

# 5. 最简操作清单

```text
1. 单位 tags 加入自己的 name
2. EFSF_0079_Get.ini 注册 UnitID
3. EFSF_0079_Send.ini 注册 UnitID
4. TechList_EFSF_0079.ini 复制并修改科技信息
5. Common 中复制科技标记单位
6. Page_00 或 Page_01 中添加节点
7. Page 文件中添加前置和后续连线
8. 必要时在 UI_Main 中复制页面逻辑
9. 测试 Unlock Tag
10. 测试工厂生产
```

`TechTree_EFSF_0079.gw` 与 `Mod` 模板层暂时不处理。
