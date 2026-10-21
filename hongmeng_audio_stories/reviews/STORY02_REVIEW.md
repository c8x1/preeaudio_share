# 故事二独立审查

状态：PASS

## 修订复审（2026-10-20）

已重新阅读修订后的完整讲述。原必修缺口已解决：正文明确第 N 轮已摘批并执行 Pause；Process 内管理线程先发布 Start，Gain 后发布 F；第 N+1 轮摘取 F→Start 并逆向执行 Start、F。此例的发布、执行和回调线程边界能够对应实际代码，具有可达的设备队列交错。正文也补上反例：Pause、Start 同批执行时，Start 复位淡出状态，后续 Process 未必产生旧 F，避免把条件性场景说成必然现象。

同步机制对比已调整；结语已保留容量耗尽丢弃条件。回收早于执行、全局入口空不代表已摘闭包完成两点仍清楚准确。听众能逐步预测 CAS 竞争、批次边界、恢复后迟到回调三类结果，达到进入图稿阶段的内容深度要求。

范围：本例证明的是引擎设备队列可以出现的请求交错，未声称普通应用在同步 Pause 尚未返回时一定能成功调用 Start；成页时继续使用管理线程/设备队列泳道，不增加未经核验的应用 API 成功路径。

下面保留初审记录，说明修订原因。

审查对象：`scripts/02_control_and_lifecycle.md`。审查日期：2026-10-20。审查方式：阅读完整讲述，直接核对固定新框架 SHA `3a2688e805df970739e3b0cebf9cc05d8cb24e9b` 的 Run、HandleMsg、HandleRequests、ProcessRequests、Gain 和 OnFadeDone；旧方案与既有固定源码核验索引交叉检查。未进行板端实验。

## 结论

主体已经是可讲述的技术故事。CAS 失败后重建 next、消费者摘批与新请求的归属、vector 保留闭包而节点先回收、全局表头空不等于业务完成，均与实际实现一致。旧 PA 的 mainloop 访问锁、asyncmsgq 包装层 mutex、send 同步等待和底层原子槽位分开叙述，没有把 PA 概括为“处处大锁”。新 Start 两队列与上行通知不构成设备完成屏障，也表述准确。

本次保留一个必须补足的教学缺口：Pause/Start/FadeDone 交错**真实可达**，但正文仍用“假设 Start 闭包先于 FadeDone 执行”跳过了证明这件事的关键批次时序。这个例子恰好要教人看懂真实并发，必须把入队时刻、Process 内回调与下一轮 HandleMsg 接上。

## 必须修改：把可达交错写完整

现稿位置：“现在插入一次恢复。假设 Start 闭包先于这条 OnFadeDone 闭包被执行。”

建议用以下合法时序替换这一跳步，不要求虚构任何毫秒数：

1. 设备线程在第 N 轮 `HandleMsg` 摘到 Pause 并执行，使输入 PAUSING、Gain DO_FADEOUT。该轮处理完已摘批次，进入 `Process`。
2. 第 N 轮的 `Process` 尚未运行到 Gain 淡出回调时，管理线程已经把恢复 Start 发布到设备全局请求链。因为本轮 HandleMsg 已经摘批，这个 Start 不会在当前 Process 中执行。
3. 同一设备线程继续 Process，Gain 完成淡出，调用 OnFadeDone；OnFadeDone 把收尾闭包 F 再发布到设备队列。此时成功发布先后是 Start→F，全局头插链为 F→Start。
4. Process 返回；第 N+1 轮 HandleMsg 摘下 F→Start；ProcessRequests 先 move、回收，再逆向调用，所以先执行 Start，再执行 F。
5. Start 把输入恢复 RUNNING。F 随后读取最新状态，被 RUNNING 守卫挡住；不拆恢复后的图。

这个交错的前提是：Start 成功发布在 F 前，并且没有在本轮淡出之前被同一个已摘批次执行。反例也值得加一句：如果 Pause 和 Start 已被第 N 轮同一批依次执行，Start 会把 Gain 的 fadeOutState 重置为 NO_FADEOUT，随后 Process 未必产生本例中的旧 FadeDone。因此不能画成“任意一次 Pause 后 Start 都一定伴随迟到淡出通知”。

核验依据：

- `manager/src/hpae_signal_process_thread.cpp:99–107`：每轮先 HandleMsg，再 Process；两者同一线程串行。
- `manager/src/hpae_renderer_manager.cpp:1311–1314`：HandleMsg 只调用一次 HandleRequests，不反复消费到全局头空。
- `utils/hpae_no_lock_queue.cpp:80–89`：一次摘下当前批；`:227–262` 逆向调用闭包。
- `node/src/hpae_gain_node.cpp:207–229`：Start 设置淡入并复位 fadeOutState；`:234–281`：Process 中的淡出完成回调。
- `manager/src/hpae_renderer_manager.cpp:1777–1803`：OnFadeDone 只封装并 SendRequest；守卫在未来闭包执行时读取最新状态。

## 已通过的关键点

| 核查项 | 结论 |
|---|---|
| CAS 失败后重新 load、重写 next | 正确，并通过丢失 A 的反例讲清必要性 |
| 摘批后的 C 不接入旧链 | 正确，明确成功摘批为边界 |
| 头插与反向执行恢复批内发布次序 | 正确，未承诺外部调用起始次序 |
| 节点回收先于业务执行 | 正确，闭包 move 到 vector 后所有节点先回收，随后逐个执行 |
| IsFinishProcess 只检查全局头 | 正确，已明确已摘闭包仍可能尚未执行 |
| PA 的 post/send 差别与锁所在层 | 正确，边界具体 |
| 自研仍有 Notify mutex、扩容分配与丢弃路径 | 正确，未声称全引擎无锁或永不丢请求 |
| OnFadeDone RUNNING 保护 | 条件方向正确；未夸大为带代次令牌的全交错证明 |
| 公共服务 Drain 回调保护的归属 | 正确，未称为自研独创 |

## 建议而非阻断

- 正文“节省的是常规请求链表发布中的锁竞争”可改为“常规发布以 CAS 竞争取代这层写端 mutex 互斥”。当前措辞略像已经量化证明净收益，而这里展示的是同步机制变化。
- 结尾“原子发布让线程之间不漏接工作”建议加“容量正常、发布成功时”。正文已讲容量耗尽丢弃，结语应延续这个条件。
- 当前稿约三千余字的信息密度较高，拆页应按 CAS 竞争、摘批生命周期、Pause 恢复交错三次停顿展开，不能重新挤成一页算法图后声称讲完。

验收条件：补清上述真实批次时序，并对照 Start 的重置淡出分支说明假设后，可以转为 PASS。
