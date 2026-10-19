# 全页技术重构审查

审查日期：2026-10-18。对象：P01–P21 的页面 JSON、讲稿、现有源码证据，以及补查的 RendererManager 暂停/淡出状态实现。状态：**旧版内容审查完成，建议所有页面进入新一轮逐页修订与独立复审**；旧 PASS 仅代表旧标准，不能用于新验收。

## 核心诊断

用户反馈成立。现版准确性边界做得较好，但主讲中 P01、P02、P03、P05、P06、P12、P13、P14、P15 多次重复“策略决策、服务协调、引擎执行、设备输出”和收益/约束。源码细节经常只藏在讲稿；画面仍是职责卡片。P16–P20 的真实机制被放到附录，导致听众听完主讲仍无法说清一次 Start、Pause 或 Move 究竟如何执行。

P19 有效的原因不是“箭头多”，而是具体操作、真实参与者、异步交接、状态回程和成功语义形成完整问题。新标准应为：每张核心技术页回答一个可复现操作；图上出现调用或状态、关键条件与执行上下文；至少解释一个设计取舍。源码函数名服务理解，不能堆满调用栈。

建议主线：**启动一次声音 → 看懂旧 PA 的执行链 → 对照新执行线程和控制队列 → 暂停为何需要中间态 → 节点怎样拉取与局部重连 → 策略触发迁移如何落实 → 用可观察事件验证收益**。保留全局策略，但用真实接口和状态显示其职责。

## 逐页审查与改法

| 页 | 当前问题 | 建议画面与真实内容 | 与其他页的分工 / 验收点 |
|---|---|---|---|
| P01 | 场景卡片只表达体验目标，没有具体悬念 | 用“点击 Start → 收到 RUNNING → 首帧写设备”三个事件开场，明确它们不是同一事件；音乐/游戏/耳机作为操作场景 | 只提问题与路标，避免再次总结四层；不提前宣称实际耗时 |
| P02 | 职责图缺少对象、通道和边界 | 一张对象地图：AudioRenderer / RendererInClient、RendererInServer、AudioZoneService、HpaeManager / RendererManager、SinkOutput / HDI；分别标 IPC、共享音频缓冲、控制队列、函数调用 | 说明为何同时存在控制面和数据面；不可把架构层画成一层一进程 |
| P03 | “一次场景变化”仍是责任列表，且将真实调用藏入备注 | 将 P19 的 Start 时序提升到主讲：客户端检查与 IPC；服务 StartInner；策略 UpdateSessionOperation；非 FAST 的 WaitForDataConnection；管理队列与设备队列；状态回调 | 必须显示两次排队及“管理状态不是首帧完成”的边界。P19 改成异常/精细语义附录，避免重复 |
| P04 | PA 名词地图不能解释旧系统怎样真正跑 | 旧 PA Start 时序：PaRendererStreamImpl::Start → PaLockGuard/mainloop lock → pa_stream_cork → 成功回调 / 状态通知；下方补 PA daemon 在 audio_server 内、libpulse context/stream 与自定义 hdi_sink | 旧方案承担哪些职责、为什么要 mainloop 同步。旧状态回程需补查后再绘制，不能用新回程代填 |
| P05 | 三种“成本”是概念列表 | 展开旧普通输出双线程泳道：ProcessRenderUseTiming → pa_asyncmsgq_post(primary.dq, HDI_RENDER) → ThreadFuncWriteHDI → ProcessHdiRendererPrimary → RenderWrite；标 chunk 引用交接、等待点与队列位置 | 提供可定位的旧执行基线；这是结构边界，不是已测瓶颈排名。不要将引用传递画成必然 PCM 复制 |
| P06 | 目标/约束再次重复，技术密度低 | 改为新旧普通输出并列泳道：旧 render→dq→write；新 SignalProcessThread: HandleMsg→Process→OutputCluster→SinkOutput→RenderFrame。用删除边界的标记解释职责合并 | 新旧必须同一普通主输出范围；驱动内部线程不作结论。原目标/约束压缩为一句 |
| P07 | 已有实际调用，但与 P16 重复，尚未解释调度 | 专讲新线程循环：条件等待 → HandleMsg → Process → 下一轮，列出 IsRunning / IsMsgProcessing / recvSignal 等唤醒条件，并标 Notify 仍持 mutex | 回答谁消费控制、何时跑数据、何时睡眠；避免误称固定 tick、全链无锁或硬实时 |
| P08 | Buffer 功能列表没有数据库存与块长关系 | 以一次 SinkOutput 要求数据为序列：ReadPreOutputData → 上游 converter/mixer → 输出拼帧 → 达到 renderSize 才提交；旁列共享缓冲 / converter cache / sink accumulation 的职责 | 显示保留哪几处、删除哪一中转。抗抖动结果是团队结论；源码只能解释责任，不能证明等价余量 |
| P09 | 画面只说入队/消费，未呈现算法 | 生产者/请求链/消费者三泳道：取 free node→填 request→CAS 发布；原子摘批→逆向遍历恢复发布次序→逐任务执行→回收。将扩容/耗尽作为旁支 | 体现具体算法而非“无锁更快”；要标批次、并发发布顺序和慢路径锁，不能称任务执行原子 |
| P10 | 职责组过于折叠，不能看出图怎样跑 | 将 P18 的真实节点图升入主讲：Input→Converter→可选 SessionEffect→LoudnessGain→Gain→scene Mixer→可选 RenderEffect；OutputCluster 汇合。双向不同颜色分别显示 pull 请求与 PCM 返回 | 说明缓存为空才 DoProcess，类型复用与实例共享分开。P18 留作多输入/缓存命中细节 |
| P11 | 当前最接近干货，但只有静态前后图 | 改为局部重连时序＋前后两图：检查 map / converter / gain→创建并初始化 effect→成功才 Disconnect→两次 Connect→登记映射；失败返回保留既有链路 | 必须给真实初始化失败分支、48kHz 双声道适用范围；生命周期不能一句“灵活扩展”带过 |
| P12 | 全局总结高度重复，浪费主讲容量 | 改为 Pause/Stop 状态机：RUNNING→PAUSING/STOPPING→OnFadeDone→PAUSED/STOPPED；配 Gain fade、SessionEffectPause、Disconnect、状态回调顺序；旁画无需淡出分支 | 这是新引擎具体设计价值：状态切换与音频过渡协调。不能说 Pause 立即切断，也不能将一份内部状态机等同客户端状态机 |
| P13 | 收益表全是机制推断，缺少真实系统事件 | 将 P20 的 Move 时序升入主讲：策略选择目标→Manager 请求→旧 Renderer MoveStreamSync 保留 SinkInput / 断旧连接→目标 AddNodeToSink 再入队→更新身份/粒度→按 RUNNING 连接→更新映射 | 将全局策略重新落到操作；强调已有目标 sink 的可移动会话范围，管理成功不等于声学切换完成 |
| P14 | 只有测试建议，技术分享中显得虚 | 用一张真实事件观测图：应用 Start、IPC 返回、STARTED、RUNNING、SinkOutput RenderFrame、声学检测；列可从哪一层取事件、哪些时间段能解释问题；再给同负载 CPU/唤醒/欠载对照栏 | 静态代码支持埋点位置；无产品测量不要画虚假曲线。指标条件可以进入备注，主图解释如何定位时延 |
| P15 | 三项口号和前文再次重述 | 用新旧机制对照结案：旧转交队列→同调用链提交；mainloop 保护实例→原子发布/串行控制执行；专用通路函数→节点组合。各给一条已展示的函数或状态证据 | 用三件已看懂的设计回扣延迟/资源/扩展性，定性成果只一行，量化留空且说明待补 |
| P16 | 与 P07/P08 重复 | 保留作“Buffer 与线程核对表”：PA 属性 prebuf/minreq/tlength 的请求语义；当前块长/提交粒度/缓存库存不同量；列出本次已验证/仍需产品 dump 的边界 | 应提供查错工具，不重复主讲流水线。20/80ms 不得写成 E2E 时延 |
| P17 | 算法附录有用，但与增强后的 P09 可能重复 | 专讲队列容量状态图：正常→90% 扩容检查→expandMutex/分配→达到5000→无空节点时 drop/report；附 tagged head/index 与批次顺序只在源码核验后展开 | 对复杂度和故障路径给实际条件；不能将所有 Push 都称不分配 |
| P18 | 静态节点链与增强 P10 重复 | 专讲一次 Pull 的条件时序：InputPort遍历前驱→OutputPort 缓存有/无→无则 DoProcess→消费缓存；多次拉取拼满设备 frame | 让听众理解为什么不是一轮全部节点各算一次。可用示意批次但不得编造产品默认帧数 |
| P19 | 本轮标杆，但折叠设备管理队列，容易遮住关键异步关系 | 保留为精细 Start 时序：客户端、服务、策略、HpaeManager 队列、RendererManager 队列、数据执行 6 lifeline；分别标同步返回、管理回调、设备执行 | 与 P03 主讲区分：这里给超时 Stop、队列受理和实际执行不等同、无全局总序；不重复同一张简图 |
| P20 | 静态迁移卡片没有状态条件 | 做迁移“对象状态表”：SinkInput identity 保留、设备信息更新、span 更新通知、连接根据 RUNNING、session effect 按条件重建；再给旧 PA MoveSinkInput API 对照 | 与 P13 分工：P13 看时间顺序，P20 看哪些对象保持/变化。旧 PA 内部移动细节需查 PA 代码再写，不能只凭 API 推测 |
| P21 | 版本与测量口径有必要，但占画面过多 hash | 留作证据索引：3个版本短 SHA+仓库/分支，3类事实（源码、团队定性、待测），连接可点击完整来源；范围矩阵普通/DIRECT/VOIP/特殊分支 | 给讲师可复核入口，不再重新讲一遍所有收益限制；完整 SHA 放备注和证据文件 |

## 补查到的可直接使用状态机制

当前固定 SHA `3a2688e805df970739e3b0cebf9cc05d8cb24e9b`，工作树 clean。

`services/audio_engine/manager/src/hpae_renderer_manager.cpp`：
- `Pause` L1110–1141：请求入队；FinalizePendingSessionEffectClose；调用 SetSessionFade；无渐变路径会 SessionEffectPause / Disconnect；另有通知与特殊设备处理。
- `OnFadeDone` L1777–1804：再次入队；若已 RUNNING 则不拆连接；根据 STOPPING 选择 STOPPED，否则 PAUSED；暂停音效；Disconnect；更新会话和输入节点状态；TriggerCallback。
- `SetSessionFade` L1868–1904：STOPPED/PAUSED、无 gain node、sink 未运行或 standby 分支直接到终态并回调；普通分支设置 Gain fade，非 STARTED 进入 STOPPING/PAUSING。
- `Start` L919–945：置 RUNNING→ConnectInputSession→SetSessionFade(STARTED)→可选 SessionEffectStart；源码明确将 fade-in 设置放在可能耗时的音效 Start 之前，避免预缓冲音频在连接到淡入设置之间以全增益漏出。这是很好的“为什么顺序不能随便改”的工程细节，可以放 P03 或 P12 备注。

注意：这些是当前分支的具体机制，不能把它们说成相较旧 PA 首次具备淡入淡出。应再核查旧 PaRendererStreamImpl Pause/Stop、hdi_sink 增益或 fade 逻辑，给出准确的职责组织对比。

## 新版每页审查门槛

1. 图面本身包含证据，不靠讲稿补全所有关键步骤。
2. 对时序图明确同步调用、异步排队、回调、线程/对象边界；仅有一个简单横向流程不自动算时序图。
3. 状态机标明状态属于哪个对象、进入条件、动作与异步完成事件；不混淆内部和 API 状态。
4. 每张技术页至少一个非显然机制：条件分支、缓存命中、批次反序、延迟断连、二次排队、失败保持旧连接等。
5. 新旧比较限定同路径同职责，不用“旧全锁、新全无锁”“旧无抽象、新任意拼装”等叙述。
6. 一页只解决一个技术问题；邻页不得重复同一职责清单。主讲必须承载核心细节，附录只留更细分支。
7. 评审同时看 JSON、源代码/行号和渲染 PNG；旧 PASS 不沿用，逐页新写审查结论。
