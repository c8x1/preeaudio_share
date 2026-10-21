# 故事二：声音正在运行，控制请求怎样安全改变它？

## 讲述正文

上一段，我们沿着音频数据走到了设备。现在音乐还在播放，用户按下暂停。这个动作看似只是把一个状态改成 PAUSED，但设备处理线程可能正在遍历节点、计算增益、向设备提交数据。假如调用暂停的线程立即把输入连接拆掉，处理线程手里的通路就可能在遍历中改变。我们需要回答两个问题：谁有权修改运行中的通路；轮到它修改时，这条请求是否还符合当前情况。

先看旧方案怎样协调。5.1 框架调用 libpulse 的 Start 时，先用 PaLockGuard 获取 threaded mainloop 的锁，再检查流是否 READY，调用 pa_stream_cork 解除暂停。这里的锁保护调用者进入 libpulse 的访问边界。函数返回以后，命令还要经过协议处理；PA 控制上下文再通过 asyncmsgq_send，把状态修改同步交给 sink I/O 上下文，等处理完成后继续，最后返回协议 ACK，触发框架的回调。它已经把不同线程的职责分开，也有明确的握手。

因此，旧方案的同步成本需要按层看。asyncmsgq 的多写端包装会获取写端 mutex；send 还会等待信号量，直到消费端报告完成。post 则发布后返回，不等待业务处理。再向下看，asyncq 的槽位本身使用原子指针操作。所以“PA 都用大锁，自研才用原子”解释不了真实变化。要比较的是具体边界：哪些访问要互斥，谁等待谁，哪一刻才能继续。

自研 RendererManager 采用另一种工作交接。Pause、Start 等操作先把待做的事情封装成闭包，也就是一个保存了 sessionId 等信息、以后可以调用的小函数，再通过 SendRequest 发布。普通设备处理路径里，发布后还会 Notify，唤醒处理线程。线程在 Run 中先 HandleMsg，再 Process：先消费控制请求，再进行这一轮音频处理。这样，这条路径的控制修改进入了设备处理上下文。Notify 仍有 mutex 和条件变量；常规请求发布以 CAS 竞争取代这层写端 mutex 互斥，不能把整个执行过程理解成没有等待。

再向上补一个交接：Start 首先进入 HpaeManager 的管理队列，管理侧执行后，调用 RendererManager 的 Start，又把接图工作提交到设备队列。管理侧还会发出 STARTED 通知。这两个动作之间，没有一个等待设备闭包执行完成的同步屏障。因此，看到上层 RUNNING，不能倒推设备已经接好全部节点，更不能倒推首帧已从扬声器出来。讲清这两个队列，才能理解为什么接口返回、状态通知和执行完成需要分别观察。

### 两个人同时提交，怎样避免漏掉其中一个？

下面用 A、B 两个教学请求推演。它们只表示两个独立任务，不预设业务顺序。队列里有两条链：一条保存空闲节点，一条保存已发布请求。生产者先取得自己的空闲节点，把闭包写进去，然后尝试把节点挂到请求链表头。它没有普通环形队列的 head、tail 两端。

初始表头为空。生产者甲准备 A，乙准备 B。两人都读到了空头，各自把节点的 next 写成空。甲先执行 CAS：只有当前头仍等于我读到的空，才把它换成 A。甲成功了；轮到乙时，当前头已经是 A，乙原先的假设失效，CAS 必须失败。这不是请求失败，而是在提醒乙：重新连接到最新的链表，再提交。

停在这里想一想：乙能否只重试 CAS，继续保持 B.next 为空？不能。即使它下一次成功把头换成 B，也会形成 B 指向空，已经发布的 A 就从待处理链上消失了。实际代码把“重新读头、重写 next、再 CAS”放在同一个重试循环里。乙重新读到 A，写 B.next=A，然后成功发布，结果才是 B→A→空。原子比较替换保护的是这次表头更新；next 的重建负责保持已有链条不被截断。两者缺一不可。

源码的头值还携带索引和 flag：低三十二位定位节点，高三十二位携带版本信息。节点从空闲链取出后，返回值的高位加一，后续发布、回收携带它。这里能确认设计考虑了节点复用时的版本变化；有限位宽和并发前提仍然存在，不能仅凭这个字段就宣布得到了无条件的 ABA 安全证明。

### 消费者摘走一批，新来的请求归谁？

现在全局头是 B。消费者也执行 CAS，把全局头换为空，同时取得 B→A 这条链。这一步成功之后，链有了两个归属：全局入口接收新工作，摘下的旧链由本次消费者处理。假设 C 此刻才发布成功，它挂在新的全局头上，属于下一批；它不会悄悄接进消费者正在遍历的旧链。如果 C 在摘批之前已经成功发布，它就可能同这一批一起被取走。分界点是成功更新表头的时刻。

旧链按 B、A 排列，是否就先执行 B？实际并没有。消费者沿链遍历，把闭包 move 到临时 vector，得到 [B,A]，随后反向遍历，先调用 A，再调用 B。这样恢复的是这一批成功发布的先后次序。两个调用者在外面何时开始调用 PushRequest，并不能直接决定这个顺序；线程可能在发布之前被抢占。

批次化还有一个直接后果：A 的闭包如果执行很久，B 就要继续等，下一批 C 也不会因为发布很快就自动抢在前面。CAS 让发布者不必围着同一个写端 mutex 轮流进入，但它不会让闭包里的音效启动、节点操作或其他工作瞬间完成。分析控制响应时，既要看发布重试和唤醒，也要看消费者眼前已有多少工作、每个工作执行多久。这正是把同步开销与业务执行开销分开的意义。

这里还有一个容易画错的生命周期：遍历时，闭包先移到 vector，节点就逐个回到空闲链；业务闭包随后才被执行。节点存储可以重新利用，是因为当前批的工作已经由 vector 持有。我们不能把“回收节点”画成“任务完成”。同理，IsFinishProcess 只检查全局请求头是否为空。当消费者刚摘下 A、B，全局头已经为空，但 A、B 可能一个都没执行。判断队列入口为空，不能替代等待业务完成。

常规发布减少了写端锁争用，但它需要处理容量。当前实现初始一千节点，达到百分之九十阈值时尝试扩容，每次增加一千，上限五千。扩容存在 mutex 和动态分配，消费侧临时 vector 也可能 reserve。到达上限又拿不到节点时，会报告异常并丢弃本次请求。控制正确性不能只靠“入队了”三个字；还要知道容量耗尽的行为，以及哪一种回调才代表目标操作完成。

### 排到了执行侧，是否就一定应该执行？

再回到暂停。选一条确实需要淡出的正常路径：会话输入和 Gain 节点存在，设备在运行，也不是 standby。Pause 闭包被执行后，让 Gain 开始淡出，并把输入和会话状态置为 PAUSING。连接暂时保留，后续音频处理才能完成增益渐变。Gain 完成淡出时调用 OnFadeDone；OnFadeDone 再提交一个闭包，等待设备处理侧收尾。正常情况下，它暂停相关音效、断开输入、写入 PAUSED，并触发回调。PAUSING 的价值就在这里：表达“暂停已经开始，拆图尚未完成”。

现在插入一次恢复，按照真实循环把交错接起来。第 N 轮 HandleMsg 已经执行 Pause，随后进入 Process。还没走到 Gain 的淡出回调时，另一个线程把恢复 Start 成功发布到设备请求链。Start 赶不上本轮已摘走的批次，只能等待。设备线程继续本轮 Process，Gain 完成淡出，OnFadeDone 再把收尾闭包 F 发布到同一条请求链。发布顺序是 Start、F，头插形成的链却是 F→Start。

第 N+1 轮 HandleMsg 摘下这批请求，反向执行，先 Start、再 F。Start 把输入置为 RUNNING，接回通路，设置淡入，再更新会话。随后旧 F 才轮到执行。它若无条件完成旧任务，会把刚恢复的通路再次拆掉。请求链完整、执行顺序符合发布先后，仍然不能保证业务操作此刻有效。

这条交错依赖明确条件：Start 在 F 之前成功发布，又没有在本轮 Process 之前就被执行。如果 Pause 和 Start 已在同一批依次执行，Start 会重置 Gain 的淡出状态，接下来的 Process 未必产生旧 FadeDone。因此不能把它画成每次暂停后恢复都一定出现的现象；要看请求在哪一批、何时执行。

实际守卫放在 OnFadeDone 提交的闭包内部：先确认输入还存在，再读取当前输入状态；当前是 RUNNING 就直接返回。于是这个教学交错里，旧完成事件不会暂停音效、断开输入或回写 PAUSED。为什么一定在闭包执行时检查？因为从事件发出到请求消费之间还有排队窗口，窗口内状态可能已经改变。提前检查只能证明过去某一刻允许收尾，不能授权未来的拆图。

若执行时仍是 PAUSING，正常收尾继续；若是 STOPPING，则收尾到 STOPPED。若没有 Gain、设备未运行或属于 standby 等情况，Pause 也存在直接完成的分支，不需要等待淡出。这是一组带条件的状态转换，而不是无论什么情况都强制经过三步。

这个保护同样有明确范围：它检查当前是否 RUNNING，并没有在这里核验一个暂停代次令牌。假如又出现另一轮 Pause，不能把这一条判断夸大成能识别所有旧事件。我们学到的是把条件放在真正改变状态的位置，并逐个验证所关心的交错。

公共服务层也有一个短例子。客户端 Stop 会先尝试 Drain；Drain 等待超时后，Stop 可能已经完成，迟到的 DRAINED 才到达服务端。如果回调无条件恢复 STARTED，就会把已经停止的服务端“复活”。当前 RendererInServer 只在状态仍为 I_STATUS_DRAINING 时恢复 I_STATUS_STARTED，否则跳过这一步。这里保护的是服务状态；刚才保护的是引擎输入连接。它们是不同层次的状态，也不能当作同一条瞬时变化的状态机，或都归为自研引擎独创。

所以这段故事最后带走一句话：**入队解决工作交接，执行时是否仍应生效由状态设计回答。** 本例中，CAS 重试时重建 next，让成功发布的请求链保持连接；容量耗尽仍可能丢弃未取得节点的请求。批次消费确定当前处理范围；中间态和执行时守卫，才能让迟到工作不破坏已经发生的新决定。

## 逐步推演用表

以下 A/B/C、甲乙和请求交错均为教学假设；链表更新、消费行为和状态分支来自固定源码。表用于指图，不计入正文长度。

| 停顿位置 | 请听众预测 | 展开后的答案 |
|---|---|---|
| A 发布成功，B 的 CAS 失败 | B 只重试 CAS 够不够？ | 不够；每轮须重写 next，否则可能截断 A |
| 消费者已摘下 B→A，C 才成功发布 | C 会加入旧链吗？ | 不会；C 挂在新的全局头，留待后批 |
| vector=[B,A]，节点已经回收 | A、B 完成了吗？ | 尚未；vector 反向调用 A、B 后才执行了本批工作 |
| N轮Pause已执行；Process中先发布Start，随后发布F；N+1轮摘F→Start | 先执行哪个，旧F会再次断流吗？ | 反向执行Start再F；F读到RUNNING，守卫退出，保留恢复的连接 |
| Server 已 STOPPED，迟到 DRAINED | 会回 STARTED 吗？ | 不会；只有仍 DRAINING 才恢复 STARTED |

## 固定源码与逐项依据

- 新框架基线 N：`multimedia_audio_framework@3a2688e805df970739e3b0cebf9cc05d8cb24e9b`，本地 `source_gitcode/`。
- 旧框架基线 O：`multimedia_audio_framework@c42a228d60b64a90d6b05cf26278a89253e5310b`，OpenHarmony-5.1.0-Release，本地 `source_audio_5_1/`。
- PA 基线 P：`third_party_pulseaudio@bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca`，通过 `git show` 读取对象，非依赖不完整 Windows 工作树。

| 正文主张 | 基线、文件与行号 |
|---|---|
| threaded mainloop guard、cork、框架回调 | O `services/audio_service/server/include/pa_adapter_tools.h:25–63`；O `services/audio_service/server/src/pa_renderer_stream_impl.cpp:159–185,835–855` |
| cork 协议与 PA I/O 同步状态修改 | P `src/pulse/stream.c:2334–2370`；`src/pulsecore/protocol-native.c:3856–3883`；`src/pulsecore/sink-input.c:702–732,1732–1741,2305–2345,2390–2401` |
| asyncmsgq 多写端 mutex；post / send / done 差异 | P `src/pulsecore/asyncmsgq.c:124–196,239–246` |
| 底层 asyncq 使用原子操作 | P `src/pulsecore/asyncq.c:140–159,231–255` |
| 闭包提交、Notify 与特殊路径 | N `services/audio_engine/manager/src/hpae_renderer_manager.cpp:1755–1770`（普通路径为主，INTERPHONE 可立即消费） |
| 管理侧 Start 请求、设备侧再入队与上行通知 | N `services/audio_engine/manager/src/hpae_manager.cpp:1830–1873`；N `services/audio_engine/manager/src/hpae_renderer_manager.cpp:919–945` |
| Run 先 HandleMsg 再 Process；唤醒仍有锁 | N `services/audio_engine/manager/src/hpae_signal_process_thread.cpp:76–125` |
| HandleMsg 一次调用仅摘一批 | N `services/audio_engine/manager/src/hpae_renderer_manager.cpp:1311–1314` |
| 空闲链、请求链、闭包与索引结构、容量常量 | N `services/audio_engine/utils/hpae_no_lock_queue.h:28–42,70–78` |
| 获取节点、写入闭包、容量耗尽丢弃 | N `services/audio_engine/utils/hpae_no_lock_queue.cpp:57–78,206–225` |
| 每轮 load、重写 next、CAS 重试 | N 同上 `:173–187` |
| 高低位解释、复用 flag 增加 | N 同上 `:142–155,206–225` |
| 消费者原子摘批 | N 同上 `:80–89` |
| 闭包移入 vector、回收节点、逆序执行 | N 同上 `:227–262` |
| 扩容锁、分配、上限 | N 同上 `:103–139`；容量常量见 header `:28–33` |
| IsFinishProcess 仅看全局头 | N 同上 `:264–267` |
| Pause 排队、正常/直接完成分支 | N `services/audio_engine/manager/src/hpae_renderer_manager.cpp:1110–1138,1868–1902` |
| Gain 淡出与完成回调 | N `services/audio_engine/node/src/hpae_gain_node.cpp:207–281` |
| Start 恢复输入、连接、淡入顺序 | N `services/audio_engine/manager/src/hpae_renderer_manager.cpp:919–945` |
| OnFadeDone 再入队，执行闭包检查 RUNNING，随后拆图与回调 | N 同上 `:1777–1803` |
| 公共 Server 防迟到 Drain 复活 STOPPED | N `services/audio_service/server/src/renderer_in_server.cpp:450–454,470–477` |

核验范围：静态源码与合法执行交错推演；没有板端时延、节能或竞争重试次数测量。正文未把队列空、请求返回、状态通知解释成声学输出完成。
