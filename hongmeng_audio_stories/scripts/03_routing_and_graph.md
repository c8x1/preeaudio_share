# 故事三：设备变了，哪些必须改变，哪些可以复用？

状态：完整讲述初稿，待独立审查。当前框架固定`3a2688e805df970739e3b0cebf9cc05d8cb24e9b`；旧PA固定`bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca`。正文中的会话S42、连接时间先后和sink名称是教学标签，不是产品运行日志。设备选择的配置前提必须随图保留。

## 完整讲述稿

音乐还在播放，我们把输出切到耳机。前面已经知道，音频通路会被控制消息改变。现在先问一个更早的问题：到底谁决定了“去耳机”，引擎是不是看到耳机插入就把所有流搬过去？

如果直接回答“策略选设备，引擎搬节点”，我们仍然没解释什么。因为策略不只看设备有没有连接，引擎也不只看设备名称。我们先选一个可核验的小场景：普通音乐会话，属于zone零，采用仓库中的默认路由配置，没有通话或车机优先规则，也没有后续refiner改写结果。设备已经成功连接，不处于禁用、异常或排除状态。接下来所有选择都在这些前提下推演，不把它当成每个产品的通用规则。

### 第一个决定：新耳机为什么可能获胜，也可能根本轮不到它？

默认配置先把MUSIC映射到媒体输出策略。媒体策略里是一条有顺序的Router链：用户选择、配对设备、隐私优先、公共优先、流过滤、默认。遍历不是让每个Router投票再统计票数，而是前面的Router一旦返回有效设备，就直接返回，不再问后面的Router。

现在假设用户没有有效的显式输出选择，配对路由也没有结果，执行才轮到PrivacyPriority。它从适合媒体输出的隐私设备里取候选，排除不能使用的设备，再从合格列表中选最新连接的一个。默认隐私设备配置包含有线耳机与若干USB耳机类别。因此，当这次新耳机是合格候选中最新连接的设备时，它可以成为音乐的目标。

请先预测一个变化：音乐原来在扬声器上，用户选择Router此刻仍返回一个有效的扬声器；后面插入了更晚连接的耳机，会因为“更新”而覆盖前面的结果吗？在这条配置链里不会。第一个Router已经返回了有效结果，PrivacyPriority没有获得决策机会。“最新连接”是某个Router内部的候选选择规则，不是整个系统对所有偏好的最高规则。

再变一次条件：没有有效用户选择，Privacy里最新的设备却被禁用了。它能因为时间最新而获胜吗？不能，过滤先于时间选择。最新的前提是仍在合格列表里。听到这里，我们已经可以解释两种看似相同的插入动作为什么有不同结果：它们可能进入了不同Router，或者候选在过滤阶段已经不同。

如果前面的Router都没有结果，还会进入Default。这里也先查询媒体默认输出上下文，不是无条件写死扬声器；只有该上下文没有结果时，才使用渲染默认设备。因此“最后回扬声器”也需要给出条件。

还有一条不要混进主图的分支：如果这个会话属于非零zone，预取阶段可以向zone查询设备，得到结果后直接返回。普通zone零的Router链和非零zone选择不是两站连续的流水线。主图先标分支，再走本次场景，听众才知道我们为什么只展开这条策略。

### 第二个决定：选中了耳机，是否就必须迁移输入节点？

设备连接事件会触发输出重选。服务拿到当前输出流，按会话覆盖后的usage等信息批量求取新目标，更新每流的设备描述，然后选择和执行pipe计划。注意这里已经出现三个不同名字：物理设备、执行pipe、引擎里的sink。它们不是同一把编号尺。

两个物理设备可能映射到同一条primary通路。Pipe选择判断是否同pipe时比较pipe的名称或标识，并不等于比较两个deviceId。于是耳机成为目标，不代表pipe一定换了；pipe没有换，也不能仅凭一个DEFAULT动作就断言后面没有Move接口调用。

实际代码把DEFAULT和MOVE放在同一组处理分支，普通运行流仍可能进入MoveToNewOutputDevice，再把目标pipe的模块名称作为sinkName传到引擎。HPAE收到后先验证会话、目标和可移动性，再比较目标sinkName与当前名称。相同就成功返回，不向旧Renderer发起拆图；不同才请求跨Renderer迁移。

现在可以给出一个完整反例。教学假设中，扬声器和这副耳机在产品配置里都映射到同一个primary sink。设备目标改变，策略可能仍调用Move方法，但引擎验证后发现sink相同，直接返回。运行流还可能按条件更新设备route，物理输出位置在设备适配侧发生变化。此时若我们画出旧SinkInput被搬到另一个Renderer，就是把并不存在的跨sink迁移加进了故事。

所以看见一条Move日志，还需要追问它最终走到了哪个分支；看见设备切换成功，也不能立刻把它算成节点迁移优化的成果。这个区别能帮助定位问题：路由选错、pipe计划不同、实际节点迁移失败，是三类不同的排查入口。

### 第三个决定：确实需要换sink时，如何迁移？

为了继续看引擎，我们另选一个明确的合法子场景：产品配置把新目标映射到不同sink，目标Renderer已经打开并初始化，会话允许移动，不走重建等特殊路径。不能只因为耳机是USB就宣布它必然满足这些前提，要先核对部署配置。

HpaeManager把移动请求放进管理队列。消费时检查目标与会话，记录移动中的状态，再请求旧Renderer。旧Renderer在自己的执行上下文里，取得现有SinkInput的共享引用；需要时先通知会话音效准备移动，然后删掉旧图上的输入连接，保留用于移动的音效attach信息，通过回调把输入对象交回管理侧。

这里有两种不同的“保留”。保留输入对象，意味着会话的输入身份没有因为换sink就被销毁重建。保留一份音效attach信息，也不等于整个旧处理簇可以原封不动搬过去。目标设备有自己的格式、帧粒度、输出配置和簇；还需要根据当前绑定关系决定音效是否重建。

管理侧找到目标Renderer后，调用AddNodeToSink，又形成一个设备级请求。随后管理映射会更新为目标sink，并向服务报告结果；设备侧接入请求还需要实际执行。这个回程不是“新设备已经播出第一帧”的同步屏障。

目标侧真正接入时，更新输入对象里的设备类别、网络与地址等信息，按目标帧粒度调整frameLen，通知UPDATE_SPAN_SIZE，建立所需的过程簇。然后还有一个关键条件：只有允许连接，而且这个session的当前内部状态为RUNNING，才把它接入正在工作的图。

请预测：一个PAUSED会话移到新设备，目标侧完成登记后，是否也应该立即Connect并开始被输出端拉取？不应该。它的设备归属可以先更新，但暂停状态没有因此失效。源码按状态决定是否连接，避免把“改变输出归属”悄悄变成“恢复播放”。如果会话在迁移中释放，管理侧也有处理路径；本课不把所有并发移动都压成一次无条件成功。

### 旧PA怎样做同一件事？

PA已经支持移动同一个sink_input对象，并不是每切一次设备就重建整条流。控制上下文处理MOVE命令后，先进入start_move，通过同步消息START_MOVE交给旧sink的I/O上下文，让其摘除输入并处理rewind。再进入finish_move，更新目标sink、重采样与音量相关信息，通过同步FINISH_MOVE让目标I/O接入。控制侧继续hook、订阅通知，最后协议ACK返回。

对照时用同样三个问题：控制侧何时等待，I/O侧何时摘除和接入，什么事件报告完成。旧PA两次send会等待对应I/O处理；当前HPAE是管理和设备请求的交接，再由节点与簇恢复连接。异步不自动等于更快：发布容易，不代表后面没有队列等待或设备准备。同步也不是没有价值：它给控制侧一个特定的处理完成边界。我们比较的是组织方式和完成语义，而不是给“同步”“异步”贴好坏标签。

两边都要处理目标格式与状态，旧PA还会按目标latency条件考虑drop或rewind；新侧按设备信息调整帧粒度、span与簇连接。不能把这些不同职责画成一条笼统的“平滑迁移”，更不能从返回成功推导无声学间隙。

### 节点化是否真能缩小修改范围？用一次音效接入验证

现在不换设备，给当前会话接入一项可选音效。原来的局部数据方向是Converter到LoudnessGain，后面还有Gain、场景混音和设备输出。问题是：新功能要不要另写一条从输入到设备的通路？

当前CreateSessionEffectNode先查重复绑定，再找Converter和LoudnessGain。如果两端不在，直接返回。如果节点创建后音效初始化失败，也在断开旧连接之前返回。请停在这个失败点看图：旧Converter到LoudnessGain的边还在，函数没有先拆旧路再尝试一条未必能用的新路。

成功时才执行三个连接动作：LoudnessGain断开Converter，SessionEffect连接Converter，LoudnessGain连接SessionEffect，最后登记映射。按数据方向看，新局部图是Converter、SessionEffect、LoudnessGain。原有增益、混音与设备提交职责继续使用。

这就是一个可检查的扩展收益：修改集中在已经定义好的职责边界与局部连接，失败返回也没有先破坏旧边。它不等于任意格式、任意音效都能即时插入。当前这项AISS接入有48kHz双声道输入约束，转换节点需要提供适合的格式；节点的创建、运行、关闭和迁移仍有生命周期工作。我们只是证明这段局部操作如何组织，没有把它升级成整图事务。

回到选择耳机的动作，系统实际做了几层不同的事：策略选择设备，pipe选择计划，sink判断是否真的需要迁移，输入对象保持身份而目标连接按设备和状态建立。再看音效接入，扩展价值来自这些职责可以局部组合。**节点化的价值，需要通过一次具体的通路修改来证明。** 听众能指出哪些对象保留、哪两条边改变、失败时停在哪里，这个设计才真正讲清了。

## 推演表：同一个“选耳机”，不同条件怎样改变结果

| 条件变化 | 本课配置下的结果 | 解释能力 |
|---|---|---|
| UserSelect先返回有效扬声器 | 该Router链直接返回，不靠后续最新耳机覆盖 | Router间顺序与候选内部排序不同 |
| 上游Router无结果，新耳机是最新合格privacy候选 | 新耳机成为目标设备 | 过滤先于连接时间选择 |
| 目标设备不同，但sink相同且验证通过 | Move入口可被调用，引擎同sink早退 | API调用不等于节点迁移 |
| 目标sink不同，已初始化，会话可移动 | 旧侧拆连接、传输入对象、目标队列接入 | 需追踪队列消费与实际连接 |
| 同上但会话PAUSED | 更新归属与过程簇，不按RUNNING分支Connect | 迁移不等于恢复播放 |
| 新音效初始化失败 | 此函数尚未DisConnect，旧局部边保留 | 先准备后改边的错误处理 |

## 短代码：局部图修改的边界

以下省略日志、类型和错误枚举，保留源码顺序，是教学摘写而非可直接编译的补丁。

```cpp
if (alreadyBound || !converter || !loudnessGain) return error;
effect = createNode();
ret = effect->CreateEffectWithInstance(...);
if (ret != 0) return ret;  // 此时旧边尚未断开
loudnessGain->DisConnect(converter);
effect->Connect(converter);
loudnessGain->Connect(effect);
effectMap[sessionId] = effect;
```

## 固定源码依据

完整策略核验、配置前提与26段短摘录见`../research/policy_device_case.md`。当前N=`3a2688e805df970739e3b0cebf9cc05d8cb24e9b`；PA P=`bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca`。

| 机制 | 固定源码位置 |
|---|---|
| MUSIC与MEDIA、Router顺序、privacy设备分类 | N `services/audio_policy/server/infra/config/file/audio_usage_strategy.xml:16–21`；`audio_strategy_router.xml:16–22`；`audio_device_privacy.xml:16–25` |
| 第一个有效Router返回 | N `services/audio_policy/server/domain/router/audio_router_center.cpp:43–60` |
| 非零zone预取分支 | N 同上 `:384–405`；`services/audio_policy/server/domain/zone/src/audio_zone_service.cpp:966–978` |
| 用户偏好与privacy/最新合格候选 | N `services/audio_policy/server/domain/router/user_select_router.cpp:28–56`；`privacy_priority_router.cpp:27–38`；`router_base.h:72–101` |
| Default先查询上下文 | N `services/audio_policy/server/domain/router/default_router.cpp:26–36` |
| 连接事件与FetchOutputDeviceAndRoute | N `services/audio_policy/server/domain/device/src/audio_device_status.cpp:147–167`；`services/audio_policy/server/service/service_main/src/audio_core_service.cpp:2795–2806` |
| 批量选择、pipe执行、DEFAULT/MOVE共分支 | N `services/audio_policy/server/service/service_main/src/audio_core_service_private.cpp:3534–3551,3571–3579,1087–1097` |
| 同pipe判断与目标sinkName | N `services/audio_policy/server/domain/pipe/src/audio_pipe_selector.cpp:2217–2226`；`audio_pipe_manager.cpp:349–356`；`audio_core_service_private.cpp:2361–2375` |
| 本地设备route条件更新 | N `services/audio_policy/server/service/service_main/src/audio_core_service_private.cpp:1696–1713,2074–2099` |
| HPAE验证、同sink早退与不同sink发起移动 | N `services/audio_engine/manager/src/hpae_manager.cpp:1030–1091` |
| 旧侧保存输入与回调 | N `services/audio_engine/manager/src/hpae_renderer_manager.cpp:872–916` |
| 目标入队、映射更新、会话音效条件重建 | N `services/audio_engine/manager/src/hpae_manager.cpp:1157–1227` |
| 目标更新设备/span、按RUNNING连接 | N `services/audio_engine/manager/src/hpae_renderer_manager.cpp:107–176` |
| PA移动的入口与两次同步I/O握手 | P `src/pulsecore/sink-input.c:1867–1930,2159–2243,2272–2302`；`src/pulsecore/sink.c:2748–2866`；`protocol-native.c:4483–4521` |
| 会话音效局部创建及插边 | N `services/audio_engine/node/src/hpae_process_cluster.cpp:547–582` |
| 当前AISS预期输入48kHz双声道 | N 同上 `:351–365` |

产品XML映射、目标sink是否已初始化、会话可移动性和声学切换结果未做产品实测。部署配置支持按产品覆盖，不能将仓内默认链推广到所有设备。
