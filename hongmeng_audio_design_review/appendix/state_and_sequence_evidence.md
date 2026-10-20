# 状态机、时序与线程边界：技术深化核验

核验日期：2026-10-18。当前源码工作树干净；逐行读取实现，未运行设备实验。

- 新框架 `source_gitcode`：`3a2688e805df970739e3b0cebf9cc05d8cb24e9b`。
- PA 历史框架 `source_audio_5_1`：`c42a228d60b64a90d6b05cf26278a89253e5310b`，OpenHarmony-5.1.0-Release。
- 以下行号均对应上述固定提交。路径省略仓库根。普通播放路径为主；FAST、DIRECT、OFFLOAD、INTERPHONE、standby 等需单独标注，不能推广成所有播放路径。

## 1. 三套状态不能混成一张无归属的状态机

### 客户端 RendererInClientInner（API 调用者看到的状态）

文件 `services/audio_service/client/src/renderer_in_client_public.cpp`：

| 操作 | 前置状态/行为 | 完成条件 | 行号 |
|---|---|---|---|
| Start | PREPARED / STOPPED / PAUSED | IPC Start 返回成功后，CV 等待 state_ == RUNNING；超时尝试 IPC Stop，返回 false | 1398–1451 |
| Pause | 只允许 RUNNING | IPC Pause 后，CV 等待 PAUSED | 1463–1505 |
| Stop | 非 offload 且非 static，先尝试 DrainAudioStreamInner(true)；STOPPED 可直接成功；其余允许 RUNNING / PAUSED | UpdateStopState、IPC Stop、等待 STOPPED；超时置 INVALID | 1554–1603 |
| Flush | 普通流允许 RUNNING / PAUSED / STOPPED；先清 callback queue / speed buffer | 等待 FLUSH_STREAM 通知，不把状态改成另一个生命周期态 | 1681–1731 |
| Drain | 委托 DrainAudioStreamInner | 等待 DRAIN_STREAM 通知，不创建客户端 DRAINING 态 | 1734–1740 |

`renderer_in_client.cpp:1319–1360`：DrainAudioStreamInner 只允许 RUNNING；INTERPHONE 直接成功；IPC Drain 后等待通知，stopFlag 的 callback 模式还会清 cbBufferQueue。**不要画“Stop 一定先成功 Drain”**：Stop 中未以 Drain 返回值阻断后续 Stop。

### 服务端 RendererInServer（管理处理中间态）

文件 `services/audio_service/server/src/renderer_in_server.cpp`：

```text
I_STATUS_IDLE / PAUSED / STOPPED
    -- ValidateStartState --> I_STATUS_STARTING
    -- OPERATION_STARTED --> I_STATUS_STARTED

I_STATUS_STARTED -- Pause --> I_STATUS_PAUSING
    -- OPERATION_PAUSED --> I_STATUS_PAUSED

STARTED / PAUSED / DRAINING / STARTING -- Stop --> I_STATUS_STOPPING
    -- OPERATION_STOPPED --> I_STATUS_STOPPED

I_STATUS_STARTED -- Drain --> I_STATUS_DRAINING
    -- OPERATION_DRAINED 且此刻仍 DRAINING --> I_STATUS_STARTED

STARTED / PAUSED / STOPPED -- Flush --> FLUSHING_WHEN_原态
    -- OPERATION_FLUSHED --> 恢复原态
```

状态前缀在图中统一用 `I_STATUS_`，不可误写为客户端 `RUNNING`。依据：Start 校验1527–1540；共享区标志 STREAM_STARTING1543–1554；Pause1666–1712；Flush 状态1766–1774、1810–1837，恢复778–795；Drain1844–1887；Stop1889–1916；回调411–477，Pause769–775。

### 最值得讲的真实竞态：迟到的 Drain 回调

`renderer_in_server.cpp:450–454,470–477` 明确注释：客户端 Stop 先 Drain 再 Stop，Drain 超时后可能先完成 Stop，随后 Drain 回调才到。代码只在 `status_ == I_STATUS_DRAINING` 时恢复 STARTED 并通知 Drain。否则不会把已 STOPPED 的服务端错误复活。

建议一页使用时序：Client Drain → Server DRAINING → 等待超时 → Client Stop → Server STOPPED → late OPERATION_DRAINED → guard 拦住恢复。该页讲的是并发正确性，有直接源码依据；不要宣称这一保护为新引擎独创，因为属于当前公共服务层。

## 2. Start 时序：控制确认、节点就绪、首帧出声是不同边界

1. Client `StartAudioStream`：IPC Start、等待 RUNNING（上表）。
2. Server `StartInner:1576–1606`：ValidateStartState → ValidateAndSetupBufferForStart → Policy `UpdateSessionOperation(START)` → 非 FAST `WaitForDataConnection()` → 普通 `stream_->Start()`。源码解释设备连接可能较久，等待应位于激活设备后、流真正启动前，以避免连接前后数据不连续造成 pop。
3. `hpae_renderer_stream_impl.cpp:166–188`：`IHpaeManager::Start(...)`。
4. `hpae_manager.cpp:1830–1873`：封装 request → 管理队列。管理线程处理时找到 RendererManager → 调用其 Start（再次入设备侧队列）→ 更新 manager 的 session state → `UpdateStatus(OPERATION_STARTED)`。
5. `hpae_renderer_manager.cpp:919–944`：设备侧 request 执行：SinkInput 置 HPAE_SESSION_RUNNING → ConnectInputSession → SetSessionFade(STARTED) → 可选 SessionEffectStart → 更新 session / cluster 信息。
6. Server `OnStatusUpdate:422–426` → `HandleOperationStarted:480–498` 置 I_STATUS_STARTED、共享区 STREAM_RUNNING → `OnOperationHandled(START_STREAM)` 返回客户端。

**关键图法**：管理线程分叉为“设备队列命令”和“上行 STARTED 通知”；设备执行泳道和上行回调之间不画严格的先后屏障。RendererManager::Start 返回的是入队成功路径，不是节点已经执行/首帧已经播放。RUNNING 更不能直接标成“扬声器已出声”。

额外真实设计：919–936 将 `SetSessionFade(STARTED)` 放在 Connect 后、SessionEffectStart 前，注释指出 SessionEffectStart 可耗数毫秒，预缓冲流若晚设 fade-in 会在窗口内泄露全增益帧。可用“连接 → 先布置淡入 → 再启动音效”局部时序讲为什么调用顺序本身是音质设计。

## 3. Pause / Stop：让音频淡出完成，再拆图

真实引擎状态前缀：`HPAE_SESSION_`。普通活跃播放可画：

```text
RUNNING -- Pause --> PAUSING -- Gain淡出完成 --> PAUSED
RUNNING -- Stop  --> STOPPING -- Gain淡出完成 --> STOPPED
```

但必须画条件旁路，不能只画理想直线：

- `hpae_renderer_manager.cpp:1110–1137` Pause；1218–1244 Stop：封装设备侧 request → FinalizePendingSessionEffectClose → SetSessionFade → 若无需fade则暂停 SessionEffect 并断开 input session。
- `SetSessionFade:1861–1901`：若 node 已 STOPPED/PAUSED、没有 GainNode、manager 不运行或 isStandby，则直接设置终态并 TriggerCallback，返回 false。否则 GainNode::SetFadeState；将 node/session 置 PAUSING 或 STOPPING。
- `hpae_gain_node.cpp:207–229` 设置淡入/淡出状态；234–249 无效输入也触发淡出完成；253–280 实际 ApplyFadeOut 后 OnFadeDone。
- `HpaeRendererManager::OnFadeDone:1777–1802`：再次封装 request；如果 node 已 RUNNING 则退出（防止过时的 fade-complete 拆掉恢复播放的链）；否则停止 SessionEffect、DisConnectInputSession、写 PAUSED/STOPPED、TriggerCallback。
- `hpae_manager.cpp:1910–1928` Pause 管理侧还登记 pending transition；2036之后 Stop 对应 STOPPING。
- `hpae_manager.cpp:1383–1443` 收到 PAUSED/STOPPED 时检查当前管理状态必须为 PAUSING/STOPPING，处理 pending 记录，再上行通知。
- `hpae_manager.cpp:43,1542–1589`：默认 **60ms** pending-transition 超时兜底，经 HandleUpdateStatus 完成管理侧通知。这个60ms是代码超时常量，**不是端到端时延、淡出时长或性能指标**；超时通知不意味着设备侧实际处理已经完成。

这组机制适合一页“状态图 + 三个护栏”：渐变后拆图、过时回调防护、管理侧超时兜底。也可拆成正常时序与异常时序两页。

## 4. Flush 与 Drain 不可画成同一个“清空 Buffer”

- Flush 主动丢弃/重置已有缓存。Server 先 `FlushOhAudioBuffer`，再 stream Flush；设备侧 `hpae_renderer_manager.cpp:1166–1193` 清 SinkInput历史、Converter buffers，按条件 InitEffectBuffer、SessionEffectFlush。
- 管理侧 `hpae_manager.cpp:1952–1992` 调用 RendererManager::Flush（入队）后即 `UpdateStatus(OPERATION_FLUSHED)`。**不能把该回调画成“所有设备侧 buffer 均完成清空”的同步栅栏**。
- Drain 通过消费过程判断输入耗尽：`hpae_renderer_manager.cpp:1196–1215` SinkInput::Drain；非 RUNNING 则直接通知；运行中 `hpae_sink_input_node.cpp:118–148` 读数据失败/underflow且 isDrain_ 才发送 OPERATION_DRAINED 并复位标志。historyBuffer 有足够数据时仍先输出历史帧。
- 这是引擎输入侧条件，不能凭此声称扬声器或硬件 FIFO 全部播放完成。

## 5. 旧 PA 控制路径：调用 libpulse，等待异步回调

历史文件 `services/audio_service/server/src/pa_renderer_stream_impl.cpp`：

| 操作 | 旧 PA 调用 | 回调后通知 | 行号 |
|---|---|---|---|
| Start | PaLockGuard(mainloop_)；校验 PA_STREAM_READY；pa_stream_cork(...,0,StartSuccessCb)；unref operation | callback 将 streamImpl state_ 置 RUNNING，OnStatusUpdate(OPERATION_STARTED) | 159–185；835–855 |
| Pause | pa_stream_cork(...,1,PauseSuccessCb) | PAUSED、OPERATION_PAUSED | 188–240；857–879 |
| Flush | pa_stream_flush | OPERATION_FLUSHED | 243–278；881–897 |
| Drain | pa_stream_drain | OPERATION_DRAINED、isDrain_=false | 281–304；899–917 |
| Stop | pa_stream_cork(...,1,AsyncStopSuccessCb) | STOPPED、OPERATION_STOPPED | 306–340；933–950 |

回调函数名称含 Success，不等于这里先验证 success 参数再更新状态；Start 实际先赋 RUNNING，最后保存 success。讲解应说“回调路径”，不夸大为完善成功校验。异步 operation_unref 不等于取消操作。

新旧对照图可以共用 Client / Server 两条泳道，内侧分别展开：旧 PaLockGuard→libpulse cork→PA callback；新 Manager queue→Renderer queue→节点状态/接图。但不要断言“PA 所有地方都有锁”：PA 自身也有异步队列。

## 6. 调度线程与 PCM 交接：范围明确才有可信的“少一次中转”

旧框架 `frameworks/native/pulseaudio/modules/hdi/hdi_sink.c`：

- `ProcessRenderUseTiming:2449–2477` 渲染 chunk，然后 `pa_asyncmsgq_post(u->primary.dq, ..., HDI_RENDER, ..., &chunk, ...)`（2475）。
- `ThreadFuncWriteHDI:3841–3887` 从 primary.dq 取 chunk（3856），HDI_RENDER 分支调用写端处理；线程创建4714。
- 因而可画“PA sink render线程 → primary.dq/chunk → 独立HDI写线程 → RenderFrame”。这里 chunk 跨线程引用传递，不自动等于逐级复制PCM。

新：

- `hpae_signal_process_thread.cpp:76–107` Notify 仍用 mutex/CV；Run 先 `HandleMsg()`，再 `Process()`。111–121还有可被命令唤醒的 SleepUntilNotify。不得画恒定10ms无锁循环。
- `hpae_renderer_manager.cpp:1640–1664` Process 根据 IsRunning、空流/suspend、underrun 条件决定调用 OutputCluster::DoProcess。
- `hpae_output_cluster.cpp:79–84` → SinkOutput::DoProcess；`hpae_sink_output_node.cpp:121–165` 最终 RenderFrame。限定此路径，可画“同一设备处理线程内调用链：HandleMsg → Process → OutputCluster → SinkOutput → RenderFrame”。
- 管理队列仍独立：`hpae_manager.cpp:1529–1540` PushRequest+managerThread.Notify；设备队列 `hpae_renderer_manager.cpp:1755–1770` PushRequest+Notify，INTERPHONE有特殊路径。

结论：公共普通播放路径中减少了这段跨线程中转；未由此证明全系统只剩一个线程、零复制、固定减少N个buffer或固定节能百分比。下游 HDI/驱动自身调度需要单独核验。

## 7. 推荐转换为主讲页的讲法

1. **Start 的两个异步队列**：调用者为何等待回调；RUNNING 到首帧还差什么。
2. **PAUSE 的真正终点**：一条 PAUSING 状态链串起音质淡出、节点断连、回调、防过时与超时兜底。
3. **Stop 与迟到 Drain**：一张很短的竞态时序，解释公共服务层如何守住一致性。
4. **Flush vs Drain**：同一个缓存，不同操作语义；列出真实清理对象/耗尽条件。
5. **PA 与自研同尺度时序**：同样从 stream Start 到内核执行，比较 cork/callback 与 request/节点状态；同样从 mix 到 HDI，比较 dq 边界是否存在。

以上机制不应全部声称是自研独创。共享框架状态管理体现整个底座的工程复杂度；自研重点落到可验证的调度重组、request queue、节点生命周期以及可组合的处理图上。

## 8. PA 第三方库本体补核验（2026-10-19）

仓库 `third_party_pulseaudio`，固定 SHA `bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca`。所有内容通过 `git show SHA:path` 读取，未依赖 Windows 不完整工作树。以下路径相对该第三方仓库。

### P20 可直接绘制：旧 PA 移动通路的五步

| 步骤/泳道 | 真实动作 | 固定源码行号 |
|---|---|---|
| 1. libpulse 客户端 | `pa_context_move_sink_input_by_index` 校验 context READY / index，创建 operation，打包 `PA_COMMAND_MOVE_SINK_INPUT`（input index、目标sink index），发送并注册 ACK callback | `src/pulse/introspect.c:2033–2056` |
| 2. PA 主控制上下文 | `command_move_stream` 找到 sink_input 与目标 sink，调用 `pa_sink_input_move_to(si,sink,true)`；失败返回协议错误，正常最后 ACK | `src/pulsecore/protocol-native.c:4483–4499,4521` |
| 3. 从旧 sink 摘除 | `start_move` 执行 move-start hook、移出旧 sink inputs、同步 `pa_asyncmsgq_send(START_MOVE)` 至旧 sink I/O 上下文；I/O detach、移出 thread_info.inputs、请求 rewind；返回控制侧后 `i->sink=NULL` | `src/pulsecore/sink-input.c:1867–1930`；`src/pulsecore/sink.c:2748–2790` |
| 4. 接入新 sink | `finish_move` 验证兼容性、必要时尝试 reconfigure，调用 moving 回调；令 `i->sink=dest`、加入 dest inputs、重配 resampler/音量，再同步 `pa_asyncmsgq_send(FINISH_MOVE)` 至目标 I/O 上下文 | `src/pulsecore/sink-input.c:2159–2232` |
| 5. 目标 I/O attach 与通知 | 目标 thread_info.inputs 加入同一个 input，attach；非 CORKED 时考虑新 sink latency、按条件 drop 并请求 rewind；更新 max rewind/request；控制侧随后 move-finish hook、subscription，再协议 ACK | `src/pulsecore/sink.c:2793–2866`；`src/pulsecore/sink-input.c:2234–2243`；`src/pulsecore/protocol-native.c:4521` |

`pa_sink_input_move_to` 总入口 `src/pulsecore/sink-input.c:2272–2302`：同一个 sink 直接成功；校验 may_move_to；持有 input 引用；start_move 后 finish_move；finish 失败走 fail_move。图上不要画“销毁旧流并重建新流”：旧 PA 已复用同一个 sink_input 对象。新引擎对照点应是 **HpaeSinkInputNode + manager/cluster 的迁移与节点连接管理**，不是“旧引擎不支持移动或对象复用”。

P20 推荐五泳道：`Policy/libpulse → PA control → old sink I/O → PA control → new sink I/O`。两次 asyncmsgq_send 是同步跨线程握手；返回 ACK 也不等于新扬声器声学输出已经稳定。图上旧 sink 和新 sink 的 I/O 上下文应分开。

需保留的边界：

- 可移动性/目标格式检查可能拒绝迁移，passthrough 不兼容会发送 FORMAT_LOST（2159–2180），不能承诺任意流都无损迁移。
- 此 OH 分支 `sink-input.c:2223` 把 `restore_render_memblockq(i)` 注释为无需恢复；`sink.c:2768–2769` 注释掉 move_start_time 设置。不能照搬上游注释，声称该分支完整执行了其所有恢复算法。
- `sink.c:2828–2847` 实际计算目标 latency 对应字节、条件 drop、请求 rewind；这是移动时序的真实复杂度，不能据此给出通用切换丢样量或 gap 时长。

### P04 / 消息页可用：PA 队列本身也分层

`src/pulsecore/asyncmsgq.c:124–153`：post 从 freelist 取消息（不足则分配），memchunk 只复制描述符并 memblock_ref；写端 mutex 保证 multiple-writer safe，然后 pa_asyncq_post。没有这里逐帧 memcpy 的证据。

`asyncmsgq.c:156–196`：send 在写端 mutex 内 push，解锁后 semaphore_wait 等消费端完成；`239–246` 的 done 写返回值并 semaphore_post。因此“post异步 / send等待处理完成”可以明确画在时序箭头上。

底层 `src/pulsecore/asyncq.c:140–159,231–255` 使用 atomic pointer CAS/load 维护槽位。准确对照是：**PA asyncmsgq 多写端包装有 mutex，HPAE 常规请求发布使用原子操作；不是 PA 从不用原子或所有队列都只有大锁。**

### cork 命令最短真实链（可选）

1. `src/pulse/stream.c:2334–2370` 打包 CORK_PLAYBACK_STREAM（channel、bool）、发协议、注册 ACK callback。
2. `src/pulsecore/protocol-native.c:3856–3883` 校验并找到 playback_stream，调用 pa_sink_input_cork，再发 ACK。
3. `src/pulsecore/sink-input.c:1732–1741` 映射 `CORKED/RUNNING`；`702–732` 控制上下文通过 asyncmsgq_send(SET_STATE) 同步交给 sink I/O，再更新控制侧 state。
4. `sink-input.c:2390–2401` I/O 调用 set_state_within_thread；`2305–2345` cork 时先请求 rewind 再写 CORKED，uncork 时先写 RUNNING 再请求 remix/rewind。

此时 cork ACK 位于该跨线程状态处理之后，但仍不是声学首帧完成；和新 HPAE 管理侧发 STARTED 的边界不同，值得如实讲清。
