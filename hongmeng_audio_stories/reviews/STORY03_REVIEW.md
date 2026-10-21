# 故事三：路由与图修改独立审查

状态：PASS

审查对象：`scripts/03_routing_and_graph.md`。本轮实查当前框架 `3a2688e805df970739e3b0cebf9cc05d8cb24e9b`，并用 git show 实查 PA `bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca` 的 sink-input.c / sink.c / protocol-native.c 对应行。

## 技术核验

- 默认配置链、first-valid 直接返回、privacy 内部先过滤后按连接时间选择成立。稿件明确配置前提及无有效 UserSelect/Pair 条件，没有把最新连接推广为全局最高优先级。
- 非零 zone 的 PreFetch 分支与普通 Router 链区分准确。可以直接返回 zone 设备，未错误画成 ZoneService→RouterCenter 的强制串行。
- device / pipe / sink 分开，IsSamePipe 用名称或 id 判断，成立。
- DEFAULT 与 MOVE 在 ProcessOutputPipeUpdate 的相同 case 下仍会进入 MoveToNewOutputDevice/MoveStreamSink，成立。没有把 DEFAULT 当成不会调 Move API。
- HPAE 先 CheckMoveSinkInput 后同 sinkName 早退，不同 sink 才 oldRendererManager->MoveStream，成立。还保留目标已初始化、isMoveAble、产品 sink 映射前提。
- 旧侧 shared inputNode 保存、KEEP_ATTACH_STATE_FOR_MOVE、MOVE_SINK_INPUT 回调，目标 AddNodeToSink 再入队，随后 manager 映射/回调，源码顺序成立。成功回程不是目标设备首帧屏障，叙述准确。
- 目标 AddSingleNodeToSink 更新设备信息、frameLen、UPDATE_SPAN_SIZE；CreateProcessClusterAndConnect 先建簇，isConnect 且 RUNNING 才 ConnectInputSession，成立。PAUSED 预测题答案准确。
- PA 保留同一 sink_input，经 START_MOVE / FINISH_MOVE 两次同步 send，旧 I/O detach、新 I/O attach，随后 hook/subscription/协议 ACK，成立。稿件未声称旧 PA 每次重建流。
- PA 目标 latency 下按条件 drop/rewind，未承诺无声学间隙，成立。
- CreateSessionEffectNode 的重复/端点检查、CreateEffectWithInstance 失败先返回、成功才 DisConnect+两次 Connect、登记 map，成立。48kHz stereo 限制与非整图事务边界已明确。

## 教学结构与预测性

三个连续决定形成因果链：谁选目标→是否需要迁移→怎样迁移；随后以音效失败/成功分支证明节点组合的修改范围。每段有改变一个条件即可得到不同结果的预测题，听众需要用规则推演而非复述框图。尤其“新耳机较晚但 UserSelect 已返回有效设备”和“deviceId 变、sinkName 不变”有明确反直觉记忆点。

旧 PA 对照问的是同样的控制等待与 I/O 完成语义，没有以同步/异步标签直接推导性能优劣。此版本已具备内容深度；页数与分钟数仍需通过后续可视化分步呈现和试讲确定。

## 不阻塞通过的制作建议

1. 最后一句“哪两条边改变”可精确改为“删除哪一条旧边、增加哪两条新边”，避免听众以为总共只发生两次连接修改。
2. 三个决定至少分成三组视觉推进，不把 Router 条件表、跨 sink 时序与音效图全部挤同一页。默认链与 nonzero zone 用 alt 标明，不需要给每个特殊 router 展开旁支。
3. “旧 Renderer 在自己的执行上下文”在绘制时注明本故事选其已初始化、入队消费的普通路径；MoveStream 未初始化时存在同步执行分支，不能把图标题写成所有移动唯一实现。
4. PA 对照保留“同步消息 send 等待 I/O handler”与“客户端协议 ACK”两个不同终点；不要让动画把 ACK 等同于声学完成。
5. 跨 sink 只要显示假设 Sink_A→Sink_B 即足够；实际产品 USB 对应哪个 sink 未核实，不应以确定产品名称代替教学标签。

无需直接改稿即可进入分镜设计。上述五点应在切页与画图时一并保留。
