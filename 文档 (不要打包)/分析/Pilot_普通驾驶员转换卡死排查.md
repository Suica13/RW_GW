
# 普通驾驶员转换卡死排查（2026-11-09）

用户确认故障发生在普通驾驶员：偶尔停留在没有贴图、没有有效数值、无法正常击杀的中间实体。

## 当前配置与引擎证据

入口为Main的Pilot_CustomMarker_Common.ini，按全局阵营Tag依次转换到年代标记、阵营标记和正式驾驶员。中间标记使用空白身体图片，并继承死亡/伤害交由战斗核心管理的框架；停在这里会出现用户描述的外观。

旧入口只监听created；后续阶段只监听PilotCustomChange消息。每次中间转换立即通过PilotCustomChange.gw给BattleUnitCore发送消息，再由BattleUnitCore_Pilot回传给父单位。没有跨帧续接、无消息丢失重试。

本机引擎反编译源码：
- units/custom/ag.java:2870-2902：事件递归上限来自autoTriggerOnEventRecursionLimit；newMessage在本机实现中默认4（不要简单照资料中的通用默认1推断）。
- units/custom/j.java:4025：待处理事件所属类型与当前转换后类型不一致时直接跳过。
- units/custom/j.java:4042、4054：超出本轮事件递归深度的待处理事件被过滤。
这些代码证明旧转换链存在消息被截断的路径；尚未在实际游戏中捕获该偶发故障的完整事件序列。

## 修复

- PilotCustomChange.gw的Step2设置0.1秒后的待续标记，实际由后续autoTrigger轮询发送原有“核心→驾驶员”消息。没有改成队列延时，因为TryClearQueued会清掉队列。
- 给中间标记增加每秒一次的重试。已创建核心的引用以实际attachment重新取得，确实缺失核心时才重新生成并初始化。
- 普通入口同时接受created和重试消息，要求核心附件及customTarget1来源就绪。
- 最终实际驾驶员不继承PilotCustomChange.gw，完成转换后不会继续触发标记重试。
- 原有PilotType分流、技能随机与转移、changePilotSkillsBool和正式驾驶员初始化保留。
- 六包PilotCustomChange.gw修改前哈希相同，已同步相同修正。只有Main普通入口修改，ACE入口保留。

## 边界

这次没有将未知PilotType或未实现ACE路由偷偷降级为普通驾驶员。0087三阵营ACE派发列表为空是另一个内容未实现问题，用户已确认本次不是ACE故障。未进行游戏加载或大规模生产复现，仍需验证连续生产、驾驶员落地/入载具、各年代阵营以及旧存档中已卡住的标记。
