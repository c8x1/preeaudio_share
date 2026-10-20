# 三个可以逐步推演的真实设计例子

核验日期：2026-10-20。源码基线：`multimedia_audio_framework`，SHA `3a2688e805df970739e3b0cebf9cc05d8cb24e9b`。下面的 A/B/C 请求、时序交错、采样格式和时长是**教学假设**；实现动作、字段含义和条件分支是该提交的**源码事实**。这些推演未经板端实验，不代表性能测量。

固定源码链接前缀：`https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/`。

## 1. 两个生产者争一个表头：为什么 CAS 失败后必须重写 next

### 先把数据结构画清楚

`HpaeNoLockQueue` 使用两个原子表头：`freeRequestHeadIndex_` 管理空闲节点，`requestHeadIndex_` 管理已发布请求。每个节点含 `request` 和原子的 `nextRequestIndex`。节点以索引定位；64 位头值的低 32 位为节点索引，高 32 位为 flag。不能把它画成一个拥有 head/tail 的普通环形 FIFO。

源码位置：`services/audio_engine/utils/hpae_no_lock_queue.h` 28–42、70–78；对应 cpp `InitQueue` 42–55、`GetRequestIndex`/`GetRequestFlag` 147–155。

### 教学假设

两个生产者 P、Q，各从空闲链取得独占节点 `nA`、`nB`。请求 A、B 的业务含义可以是两个互不依赖的控制请求；这里不假定 Start/Pause 等特定操作，也不借此推断业务全局顺序。初始待处理头为 `∅`。图中 A/B/C 仅标节点身份，省略实际 flag 数值。

| 步骤 | 生产者 P | 生产者 Q | 待处理链 |
|---|---|---|---|
| 1 | 在 nA 中写入闭包 A | 在 nB 中写入闭包 B | ∅ |
| 2 | load 头=∅，写 nA.next=∅ | load 头=∅，写 nB.next=∅ | ∅ |
| 3 | CAS(期望∅，新头A)成功 | 尚未 CAS | A→∅ |
| 4 | 已完成发布 | CAS(期望∅，新头B)失败；当前头已是 A | A→∅ |
| 5 | — | 重试循环：重新 load 头=A，**重新写 nB.next=A** | A→∅ |
| 6 | — | CAS(期望A，新头B)成功 | B→A→∅ |

`PushRequestNode` 173–187 实际在每轮循环重新读取头并写 `nextRequestIndex`，再执行 `atomic_compare_exchange_strong`。**如果只重试 CAS 却保留旧 next，B 成功发布后会把 A 从链上漏掉。** 这就是此处值得讲清楚的算法约束。`PushRequest` 57–78 则负责先取空闲节点、写闭包、再发布。

### 消费者一次摘走一批，后来发布的 C 怎么办

| 步骤 | 消费者 R | 生产者 | 全局待处理链 / R 的私有批次 |
|---|---|---|---|
| 7 | load 当前头 B，CAS 把全局头改为空索引；成功 | — | 全局∅；R 持有 B→A |
| 8 | 开始处理已经摘下的 B→A | 发布 C 到当前全局空头 | 全局 C→∅；R 仍持有 B→A |
| 9 | 遍历 B、A，把闭包 move 到临时 vector，按节点逐个回收到空闲链 | 其他生产者可继续入队 | vector=[B,A]；全局 C 不变 |
| 10 | 逆向遍历 vector，调用 A、再调用 B | — | 当前批执行 A、B |
| 11 | 下次调用 HandleRequests 再摘下 C | — | C 属于后续批次 |

摘批代码：`HandleRequests` 80–89。它保留读到的高位 flag，把低位替换为 `INVALID_REQUEST_ID`，CAS 失败则重读重试。步骤 8 的结论以“C 的成功发布发生在步骤 7 的成功摘批之后”为前提；若 C 在摘批前发布成功，它可能被本批摘下。

回收与执行代码：`ProcessRequests` 227–262。**节点先回到空闲链，闭包已经移入 vector；闭包随后逆序调用。** 应画出两类对象：节点存储可先复用，当前批闭包仍由临时 vector 持有。该例的 A→B 顺序来自成功发布的先后，不是两个生产者从外部开始调用函数的先后。整个批次被原子摘取，业务函数本身逐个执行，不能说“原子执行一批业务”。

### flag 与慢路径的准确边界

- `GetRequestNode` 206–225 从空闲链摘节点后，通过 `IncRequestIndex` 142–145 把返回值的高位 flag 加一；后续发布和回收携带该值。可以据此讲“节点复用时带版本信息”，不要据静态阅读给出无条件、无界的 ABA 消除证明，尤其不要忽略有限位宽回绕和并发使用前提。
- `TryExpandQueue` 103–139 存在 `expandMutex_` 和动态分配；`ProcessRequests` 229–231 可能 reserve 临时 vector；最大容量耗尽后 `PushRequest` 64–68 报告并丢弃请求。应把常规链表 CAS 与扩容/耗尽路径分开讲。
- `IsFinishProcess` 264–267 只检查全局待处理头的索引是否为空。已经摘下的闭包仍可能执行，不能把该条件讲成“所有业务均已执行完”。

**课堂问题：**“消费者已经摘批，为什么 C 不会丢失，也不会悄悄加入正在遍历的旧链？”让听众指认全局头与消费者私有链的分离，再用步骤 7–10 回答。可支撑约 4–5 分钟的算法讲解。

## 2. 上游 20 ms，设备 10 ms：逐字节看剩余量怎样保留

### 教学假设与适用范围

假设 SinkOutput 节点设备提交粒度为 10 ms，上游每次提供 20 ms PCM；两边均为 48 kHz、2 声道，最终输出 S16（每样本 2 字节），不变格式、不切路由，数据有效，RenderFrame 成功且完整写入。本例是为解释拼帧分支选择的数值，**并非声称全部实际设备均采用这些粒度，也不是 30 ms 的端到端延迟测量**。

源输入内部是 float，`ConvertFromFloat` 转到设备格式后才写入 `renderFrameData_`；下面的库存单位都是该输出格式的字节，不能拿 float 的每样本 4 字节来算库存。

```
每毫秒字节数 = 48000 / 1000 × 2 × 2 = 192 B
renderSize_ = 10 × 192 = 1920 B       （每次 RenderFrame 的请求长度）
outputSize_ = 20 × 192 = 3840 B       （一次上游 Pull 转换后追加的长度）
```

`HpaeSinkOutputNode` 构造函数 62–69 由 nodeInfo.frameLen × channels × format 字节数设置 `renderSize_`，并初始 `outputSize_=renderSize_`。`ReadDataAndConvertFormat` 680–707 在发现输入输出时长不同且缓冲尚未扩展时，用输入帧长重设 `outputSize_`，把缓冲扩到 `outputSize_+renderSize_`，本例为 5760 B。**扩容到 5760 B 是存储容量，不能说每轮实际缓存 5760 B。**

### 四轮逐步计算

| DoProcess 轮次 | 进入时 currentSize | while currentSize < 1920？ | 本轮 Pull / 转换追加 | 提交前 currentSize | RenderFrame 请求 | 尾部搬移后 currentSize |
|---|---:|---|---:|---:|---:|---:|
| 1 | 0 B | 是 | 第 1 块 20 ms，3840 B | 3840 B | 首 1920 B，即第 0–10 ms | 1920 B，即第 10–20 ms |
| 2 | 1920 B | 否 | **0 次 Pull** | 1920 B | 剩余 1920 B，即第 10–20 ms | 0 B |
| 3 | 0 B | 是 | 第 2 块 20 ms，3840 B | 3840 B | 第 20–30 ms | 1920 B，即第 30–40 ms |
| 4 | 1920 B | 否 | **0 次 Pull** | 1920 B | 第 30–40 ms | 0 B |

实际执行顺序：`DoProcess` 132 先调用 ReadDataAndConvertFormat；143 以固定 `renderSize_` 请求写设备；160–162 把 `[renderSize_, currentSize_)` 的余量移动到缓冲起始，并减去本轮提交长度。因此第二轮 while 不进，仍能正常输出，**剩余数据不会为了凑下一轮而被清零，也不必重复拉上游**。

可并排补一个反向小例：若设备每次 20 ms（3840 B）、上游每次 10 ms（1920 B），初始 0→1920 仍不足→再次 Pull 到3840→一次提交后0。它说明同一个 while 同时处理“上游块更小”和“上游块更大”。两种教学假设都应明确为固定格式/固定粒度的合法输入情形，不据此推断中途改变块长的全部实现。

### 这个例子说明什么设计问题

1. 节点拉取次数由库存决定，不能把“一个 Process 等于每个上游节点恰好执行一次”写死。
2. 线程减少后，**粒度适配的缓存职责依然需要存在**；此处缓冲承担大小适配，和跨线程队列的等待成本不是同一概念。
3. 要优化 Buffer，先区分容量、已用字节、持有时长、提交粒度。看见一个 vector 的容量不能直接换算端到端时延。
4. 此处只演示正常完整写路径。143–154 处理 RenderFrame 错误/短写并记录失败，160–162 仍扣除整段 renderSize；不要把本例叙述成“任意短写均自动保留未写字节重试”。

**课堂问题：**“为什么第二轮不再 Pull？如果把 currentSize 每轮清零，会漏掉哪 10 ms？”逐行算表可以支撑约 3–4 分钟。

## 3. Pause 还在淡出，Start 已恢复：迟到的 OnFadeDone 为什么不能断流

### 真实职责分工

暂停要协调两个进度：控制请求希望暂停；音频处理要完成淡出后再断开输入。`Pause` 返回 SUCCESS 表示已提交控制请求，不能据此断言节点已经断开或硬件声学输出已经停止。

源码：`services/audio_engine/manager/src/hpae_renderer_manager.cpp`，`Pause` 1110–1138、`Start` 919–945、`SetSessionFade` 1868–1902、`OnFadeDone` 1777–1803。`services/audio_engine/node/src/hpae_gain_node.cpp` `ApplyFadeOut` 253–281，在淡出后调用回调；无有效输入时 `DoFading` 232–240 也能结束淡出并通知。

### 教学场景：选择一条允许淡出的正常路径

假设同一 session，输入、场景 Gain 节点存在，sink 正在运行，`isStandby=false`，Pause 的 SetSessionFade 返回 true。时间从上到下；竖线是职责泳道，箭头不代表固定耗时。

| 步骤 | 调用侧 | RendererManager 的已执行请求 | Gain / 输入连接 |
|---|---|---|---|
| 1 | 调用 Pause | Pause 闭包进入队列，尚待执行 | 初态 RUNNING，输入相连 |
| 2 | — | 执行 Pause：SetSessionFade(PAUSED) 设置 Gain 淡出，输入节点及 session 状态置 PAUSING | 输入保持连接，以便后续处理完成淡出 |
| 3 | — | — | Gain 执行淡出；发出 OnFadeDone(sessionId)，其处理闭包等待执行 |
| 4 | 此前已提交的 Start 请求在此先执行 | Start 首先把输入节点置 RUNNING，重新 ConnectInputSession，设置淡入，再把 session 置 RUNNING | 链路继续为恢复播放服务 |
| 5 | — | 执行迟到的 OnFadeDone 闭包：读取当前输入节点状态=RUNNING；条件保护直接 return | **不执行 DisConnectInputSession，不把恢复的会话改回 PAUSED** |

这是一个**教学选择的请求交错**：只要求 Start 闭包先于该 OnFadeDone 闭包被执行，不声称每次调用都会产生这种先后。OnFadeDone 从事件发生到闭包执行存在排队窗口；守卫在“闭包真正执行时”检查最新状态，因此能挡住该交错中的过期淡出完成通知。

关键代码可直接放页上：

```cpp
// OnFadeDone 中提交的 request 闭包，1781–1783
CHECK_AND_RETURN_LOG(SafeGetMap(sinkInputNodeMap_, sessionId), ...);
CHECK_AND_RETURN_LOG(sinkInputNodeMap_[sessionId]->GetState() != HPAE_SESSION_RUNNING,
    "no need disconnect renderer input session, %{public}u is running", sessionId);
```

条件要求“当前状态不是 RUNNING”才继续；当前是 RUNNING 则返回。应把这个反向判断讲清楚，避免误读为 RUNNING 才断开。

### 没有恢复 Start 时，正常暂停怎样收尾

若步骤 5 当前输入仍为 PAUSING，守卫通过：OnFadeDone 1784–1800 先收尾待关闭的 session effect，暂停相关 effect，断开输入，再设置 PAUSED 并 TriggerCallback。若当前是 STOPPING，则选择 STOPPED。不是所有 Pause 都要等 FadeDone：SetSessionFade 1878–1888 对已暂停/已停止、无 Gain、sink 未运行、standby 等分支直接设置终态并回调，Pause 1122–1127 随即断开输入。

```text
正常淡出路径： RUNNING --Pause--> PAUSING --FadeDone--> PAUSED
恢复交错路径： PAUSING --Start执行--> RUNNING --旧FadeDone--> RUNNING（守卫退出）
直接完成路径： RUNNING --Pause(无Gain/未运行/standby等)--> PAUSED，并断开
```

### 边界和课堂问题

- 此处使用**当前状态检查**，源码未给该回调附带一个在这里核验的 pause 代次令牌。不能把这个守卫扩大成“任何旧事件、任何重新 Pause 的交错都能被唯一识别”。
- sessionInput 的状态、Manager session 状态、上层 Renderer 状态和设备实际发声进度不应压成一条完全同步的单状态机。此例只画与断开守卫直接相关的两种节点/session 状态。
- Start 927 先恢复输入节点为 RUNNING；933 在连接后尽快设置淡入，源码注释明确提到 effect 启动可能耗时，预缓存数据会在未及时设置淡入时泄漏全增益帧。可以追加这一处“连接—淡入—EffectStart”的顺序约束作为第二个设计点，但不能据注释声称测得了具体延迟值。

**课堂问题：**“如果删掉 RUNNING 守卫，步骤 5 会对刚恢复的 session 做什么？”让听众依次指出 pause effect、断开输入、回写 PAUSED、通知回调四个后果。这比只画 RUNNING→PAUSED 的两节点状态机更能说明实际设计。可支撑约 4–5 分钟。

## 使用建议

每例按“设定输入→停在临界点提问→逐步推演→展示源码守卫→讨论边界”组织。上述时长包含提问和指图讲解，只是备课预算，正式时长应通过试讲确定。不要用一般性口号填满原定分钟数，也不要只把函数名加到原来概念图上。
