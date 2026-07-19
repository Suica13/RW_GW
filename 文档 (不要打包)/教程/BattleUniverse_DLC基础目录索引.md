# Battle Universe DLC 基础目录索引

本文用于快速说明 `GW_BattleUniverse_DLC_0079` 中常用目录和文件的职责。

本文不包含：

- 单位本体制作流程
- 科技树接入流程
- 工厂接入流程
- HQ、GameManager 与开局设置逻辑

这些内容分别维护在独立文档中。

---

# 1. 根目录概览

```text
GW_BattleUniverse_DLC_0079/
├─ Resource/
├─ Template/
├─ Units/
├─ all-units.template
└─ 其他 DLC 信息文件
```

可以把它简单理解为：

```text
Units
→ 实际单位和功能实体

Template
→ 通用逻辑框架

Resource
→ 图片、声音、特效等资源

all-units.template
→ 全局变量与全局配置
```

---

# 2. `Units`

路径：

```text
GW_BattleUniverse_DLC_0079/Units
```

这是 DLC 内主要的单位索引目录。

这里不只包含玩家直接操作的战斗单位，也包含：

- 战斗单位
- 建筑
- 科技树节点
- 支援技能功能单位
- 工厂生产定义
- DLC 标记单位
- 其他系统用隐藏单位

因此这里的“Unit”应理解为游戏引擎中的实体，而不只是 MS、载具或舰船。

---

# 3. `Units/DLCMarker`

路径：

```text
GW_BattleUniverse_DLC_0079/Units/DLCMarker
```

用途：

> 标记某个 DLC 包是否已经存在或加载。

这个目录通常只存在于个别 DLC 包中。

其他系统可以通过 DLC Marker 判断：

- 某 DLC 是否安装
- 某扩展内容是否可用
- 是否显示跨 DLC 内容
- 是否允许引用该 DLC 中的单位或科技
- 是否启用兼容逻辑

普通制作单个单位时一般不需要修改。

只有以下情况才需要关注：

- 新建完整 DLC 包
- 制作跨 DLC 联动
- 需要检测另一个 DLC 是否存在
- 内容必须在特定 DLC 安装后才显示

---

# 4. `Units/BattleUnits`

路径：

```text
GW_BattleUniverse_DLC_0079/Units/BattleUnits
```

这里主要存放战斗单位。

常见内容包括：

- MS
- MA
- 战车
- 航空单位
- 舰船
- 战斗辅助单位
- 武器
- 通用盾牌

需要注意的是，目录结构不完全等于实际功能分类。

其中 `Weapon` 和 `Shield` 是比较特殊的公共资源目录。

---

# 5. `Units/BattleUnits/Weapon`

路径：

```text
GW_BattleUniverse_DLC_0079/Units/BattleUnits/Weapon
```

虽然位于 `BattleUnits` 下，但实际用途是：

> 集中存放各类可复用武器定义。

这里通常按武器类别继续划分，例如：

```text
Weapon/
├─ Beam/
├─ Cqb/
├─ Shell/
└─ Sp/
```

可能包含：

- 光束枪
- 机枪
- 火箭筒
- 加农炮
- 火神炮
- 光束军刀
- 推撞
- 特殊推进或武器技能

制作新武器时，推荐顺序：

```text
先确定武器类别
→ 找到同类型现有武器
→ 复制最接近的案例
→ 修改伤害、射程、弹药和显示
→ 在单位本体中接入
```

不要从空白文件开始写武器。

不同武器文件可能同时包含：

- 武器攻击定义
- 弹药
- 射击动作
- 使用条件
- 武器贴图
- 音效
- 特效
- 冷却或装填
- 部件损坏限制

因此应优先参考同类武器完整复制。

---

# 6. `Units/BattleUnits/Shield`

路径：

```text
GW_BattleUniverse_DLC_0079/Units/BattleUnits/Shield
```

用途：

> 存放通用盾牌贴图或公共盾牌资源。

这样做的优点是：

- 多台单位可以复用同一盾牌
- 不需要重复存放相同图片
- 修改公共盾牌时可以统一更新

不过后期部分盾牌没有继续集中放在这里。

因此目前两种方式都可以：

## 通用盾牌

```text
Units/BattleUnits/Shield/
```

适合：

- 多台机体共用
- 标准制式盾牌
- 需要统一维护

## 机体专用盾牌

```text
Units/BattleUnits/单位目录/Image/
```

适合：

- 只有一台机体使用
- 盾牌外观与机体贴图紧密关联
- 不值得建立公共资源

选择原则：

```text
会被多次复用
→ 放 Shield

只属于单一机体
→ 放对应机体 Image
```

---

# 7. `Units/SkillsUnits`

路径：

```text
GW_BattleUniverse_DLC_0079/Units/SkillsUnits
```

用途：

> 存放主基地旁边生成的支援技能功能单位。

这些单位通常不是普通战斗单位，而是为了实现某个功能而生成的实体。

可能承担：

- 支援技能按钮
- 炮击或空袭调用
- 增援生成
- 特殊效果
- 临时范围功能
- 技能冷却与状态显示
- HQ 附近的交互功能

分析这类单位时，不要只看它是否能移动或攻击。

应重点追踪：

```text
谁生成它
→ 它监听什么消息
→ 它触发什么 Action
→ 它生成或影响什么单位
→ 结束后如何删除
```

制作新支援技能时，建议复制功能最接近的 `SkillsUnits` 案例。

---

# 8. `Template`

路径：

```text
GW_BattleUniverse_DLC_0079/Template
```

这是 DLC 的基础框架索引。

当前顶层通常包含：

```text
Template/
├─ Building/
├─ Event/
├─ UI/
└─ Unit/
```

这里集中存放可被多个单位复用的逻辑。

包括但不限于：

- 单位基础框架
- 建筑基础框架
- AI
- UI
- 动画状态
- 单位差异技能
- 通用事件
- 通用部件逻辑
- 修理、护盾、驾驶员等系统

简单理解：

```text
Units
→ 具体实例

Template
→ 实例共同继承的规则
```

普通新增单位时，一般只引用模板，不修改模板。

只有以下情况才考虑修改：

- 多个单位都需要同一套新逻辑
- 现有模板无法支持新单位类型
- 需要改变整个类别的基础行为
- 需要修复通用框架问题

不要为了单台机体的小差异修改公共模板。

优先顺序应为：

```text
先在单位本体局部覆盖
→ 确认多台单位都需要
→ 再抽成 Template
```

---

# 9. `all-units.template`

路径：

```text
GW_BattleUniverse_DLC_0079/all-units.template
```

可以理解为：

> DLC 范围内的全局变量和全局配置入口。

它可能影响大量单位，因此修改风险较高。

适合放置或管理：

- 全局资源定义
- 全局变量
- 所有单位共同读取的设置
- 全局倍率
- 全局兼容配置
- DLC 范围的公共引用

修改前应先搜索变量被哪些文件读取。

推荐步骤：

```text
搜索变量名
→ 确认读取范围
→ 判断是否会影响所有单位
→ 再进行修改
```

不要把只服务于单个单位的变量随意放进这里。

---

# 10. `Resource`

路径：

```text
GW_BattleUniverse_DLC_0079/Resource
```

用途：

> 集中管理 DLC 中的大部分资源文件。

常见内容包括：

- 单位图标
- 阵营图标
- UI 图片
- 特效图片
- 音效
- 语音
- 公共贴图
- 系统按钮
- 其他共享素材

推荐放入 `Resource` 的内容：

```text
多个单位共用
全局 UI 使用
阵营共同使用
系统级功能使用
需要统一管理
```

单台机体独有的身体贴图，可以继续放在机体自己的 `Image` 文件夹。

---

# 11. `Units` 与 `Resource` 的区别

## 放入单位目录

```text
Units/BattleUnits/NEW_UNIT/Image/
```

适合：

- 单位身体部件
- 单位专用武器贴图
- 单位专用盾牌
- 不会被其他单位使用的图片

## 放入 Resource

```text
Resource/Image/...
Resource/Sound/...
```

适合：

- 单位图标
- 阵营图标
- 多单位共用特效
- 公共武器资源
- UI
- 音效与语音
- 系统按钮

核心原则：

```text
实例专用
→ 单位目录

公共复用
→ Resource
```

---

# 12. 与 GitHub 根目录保持同步

资源文件与模板文件最好与 GitHub 根目录中的正式结构随时同步。

重点是：

```text
Resource
Template
all-units.template
```

这些内容经常被多个 DLC 或 Main 包交叉引用。

如果本地与 GitHub 版本不同步，可能出现：

- 路径存在但文件版本不一致
- 模板字段发生变化
- 新单位在本地正常、发布后报错
- DLC 引用了旧版公共资源
- Main 与 DLC 的逻辑接口不一致
- 合作者复制了错误版本模板

推荐做法：

```text
开始制作前同步
→ 制作过程中避免同时改多份公共模板
→ 提交前再次同步
→ 检查引用路径
→ 将公共改动与单位改动分开提交
```

尤其是修改模板时，应明确：

- 修改的是 Main 版本还是 DLC 版本
- 其他 DLC 是否也有副本
- 是否需要同步多个包
- 是否会改变现有单位行为

---

# 13. 普通制作时的查找顺序

## 想找一个单位

```text
Units/BattleUnits/
```

## 想找建筑

```text
Units/Buildings/
```

## 想找武器

```text
Units/BattleUnits/Weapon/
```

## 想找公共盾牌

```text
Units/BattleUnits/Shield/
```

## 想找支援技能功能单位

```text
Units/SkillsUnits/
```

## 想找通用 AI、动画或技能框架

```text
Template/Unit/
```

## 想找建筑框架

```text
Template/Building/
```

## 想找共享图片和声音

```text
Resource/
```

## 想找全局变量

```text
all-units.template
```

## 想确认 DLC 是否存在

```text
Units/DLCMarker/
```

---

# 14. 修改范围原则

## 优先修改实例

例如：

```text
单台机体特殊技能
→ 写在机体目录或引用专用文件

单台机体专用图片
→ 放机体 Image

单台武器变化
→ 复制现有武器制作专用版
```

## 多处复用后再抽公共层

例如：

```text
多台单位都使用同一技能
→ Template

多台单位共用同一武器
→ Weapon

多台单位共用同一盾牌
→ Shield

多个系统共用图片或声音
→ Resource
```

## 谨慎修改全局层

```text
all-units.template
Template
Main 包公共资源
```

这些文件的影响范围最大。

---

# 15. 最简目录索引

```text
Units
→ 实际单位与功能实体

Units/DLCMarker
→ DLC 存在标记

Units/BattleUnits/Weapon
→ 公共武器定义

Units/BattleUnits/Shield
→ 公共盾牌贴图

Units/SkillsUnits
→ HQ 附近支援技能功能单位

Template
→ AI、动画、单位差异技能和基础框架

all-units.template
→ 全局变量和全局配置

Resource
→ 公共图片、声音、特效和 UI 资源
```

---

# 16. 本文不处理的 HQ 部分

```text
Units/Buildings/HQ
```

HQ 与以下系统存在连携：

- 开局设置
- 房主设置
- 阵营选择
- 游戏模式
- 初始资源
- 默认科技树
- 初始科技等级
- 初始单位
- GameManager

这部分需要结合 Main 包的 HQ、GameManager 和科技树模板分析，因此另见：

```text
BattleUniverse_HQ与开局设置索引.md
```
