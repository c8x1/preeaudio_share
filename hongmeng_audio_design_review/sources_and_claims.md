# 页面与证据

当前框架3a2688e805df970739e3b0cebf9cc05d8cb24e9b；5.1框架c42a228d60b64a90d6b05cf26278a89253e5310b；5.1PA bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca。源码说明限定实现。时延/性能/功耗及抗抖动定性结论由用户团队提供，未补造幅度。

## P01 一次 Start，什么时候才算开始播放？

状态确认、数据消费与实际出声，需要分别理解

边界：RUNNING、RenderFrame 返回、声学出声是不同语义。

- StartAudioStream / 等待RUNNING L1398–1454：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/client/src/renderer_in_client_public.cpp#L1398
- HpaeManager::Start L1830–1875：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1830
- STARTED 状态回程 L411–428：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L411
- SinkOutput::DoProcess / RenderFrame L121–165：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L121

## P02 音频底座的对象与通信通道

控制经过 IPC 和请求队列，音频数据从共享缓冲进入处理图

边界：普通 HPAE 播放路径，图不表示进程划分。

- WriteData L1122–1161：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L1122
- StartInner L1576–1606：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L1576
- HpaeManager::Start L1830–1875：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1830
- RendererManager::Start L919–945：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919
- SinkOutput::DoProcess / RenderFrame L121–165：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L121
- ActivateAudioInterrupt L818–853：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L818
- FetchOutputDevices L966–978：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L966

## P03 Start 如何穿过策略、服务与两级队列

管理状态回程与设备级执行分叉，不能合并成一次成功

边界：普通 HPAE 路径；非 FAST 的连接等待有条件；无跨线程全局总序。

- StartAudioStream / 等待RUNNING L1398–1454：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/client/src/renderer_in_client_public.cpp#L1398
- StartInner L1576–1606：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L1576
- HpaeManager::Start L1830–1875：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1830
- RendererManager::Start L919–945：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919
- STARTED 状态回程 L411–428：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L411

## P04 5.1 方案：PA Start 的同步返回与操作回调

pa_stream_cork 提交后函数返回，状态在操作回调中更新

边界：旧版5.1普通PA路径；操作回调不等于声学出声；回调未检查success参数。

- paDaemonThread / ohos_pa_main L261–273：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/audio_server.cpp#L261
- Start / pa_stream_cork L154–182：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/pa_renderer_stream_impl.cpp#L154
- PaLockGuard L25–63：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/include/pa_adapter_tools.h#L25
- pa_stream_write / PAStreamWriteCb L699–755：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/pa_renderer_stream_impl.cpp#L699
- SinkRenderPrimaryProcess L2315–2354：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2315
- PAStreamStartSuccessCb L835–855：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/pa_renderer_stream_impl.cpp#L835

## P05 5.1 普通主输出：渲染与 HDI 写分属两线程

primary.dq 承接 chunk，写线程再调用 RenderWrite

边界：旧方案具体路径；不能推广到所有PA设备、DIRECT或offload路径。

- ProcessRenderUseTiming L2449–2477：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2449
- ProcessHdiRendererPrimary / ThreadFuncWriteHDI L3821–3887：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L3821

## P06 同一普通输出路径：跨线程交接在哪里收拢

旧 render 到写线程的队列交接，变为当前处理线程内连续调用

边界：两个版本的实现对照，不是相同设备上的实测数值。

- ProcessRenderUseTiming L2449–2477：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2449
- ProcessHdiRendererPrimary / ThreadFuncWriteHDI L3821–3887：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L3821
- Notify / Run L75–125：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_signal_process_thread.cpp#L75
- Process L1640–1664：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1640
- OutputCluster::DoProcess L79–84：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_output_cluster.cpp#L79
- SinkOutput::DoProcess / RenderFrame L121–165：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L121

## P07 新处理线程：消息与音频怎样共用执行循环

条件变量唤醒后先处理控制请求，再执行节点图

边界：处理顺序来自Run；不声明固定调度周期或系统硬实时。

- Notify / Run L75–125：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_signal_process_thread.cpp#L75
- SendRequest L1755–1770：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1755
- Process L1640–1664：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1640

## P08 Buffer 减在哪，仍保留在哪

删除旧线程中转，保留转换缓存与设备提交拼帧

边界：未给默认帧数或毫秒值，因设备/配置可变。

- WriteData L1122–1161：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L1122
- ExtractOutputFromProcessedBuffer L815–840：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_audio_format_converter_node.cpp#L815
- InputPort::ReadPreOutputData L315–325：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/include/hpae_node.h#L315
- ReadDataAndConvertFormat L680–707：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L680
- SinkOutput::DoProcess / RenderFrame L121–165：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L121
- ProcessRenderUseTiming L2449–2477：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2449
- OutputPort::PullOutputData L389–404：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/include/hpae_node.h#L389

## P09 无锁消息队列：CAS 发布与批次消费

常规链表头用 CAS；消费者摘批后反向遍历执行

边界：不保证所有请求必达或所有操作无锁。

- SendRequest L1755–1770：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1755
- PushRequest / HandleRequests / TryExpandQueue L57–145：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L57
- PushRequestNode 原子发布 L172–191：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L172
- ProcessRequests 批量执行 L227–262：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L227
- 队列容量与扩容阈值 L28–38：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.h#L28

## P10 节点图：输出端拉取，处理结果正向返回

节点负责处理；簇连接职责；Manager按会话和设备管理图

边界：当前源码配置路径；不声称每个产品都启用所有音效。

- ProcessCluster::Connect L206–232：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L206
- OutputCluster::Connect L110–135：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_output_cluster.cpp#L110
- CreateProcessClusterInner L179–240：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L179
- InputPort::ReadPreOutputData L315–325：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/include/hpae_node.h#L315
- OutputPort::PullOutputData L389–404：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/include/hpae_node.h#L389
- SinkOutput::DoProcess / RenderFrame L121–165：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L121

## P11 接入会话音效：成功创建后才重连

先验证与初始化，再修改 Converter 到 LoudnessGain 的局部连接

边界：局部函数失败保持旧边；不夸大为整图事务。

- CreateSessionEffectNode L547–582：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L547
- SessionEffect 输入格式约束 L351–365：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L351
- ProcessCluster::Connect L206–232：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L206

## P12 Pause / Stop：淡出完成后再断开节点

中间态把 Gain 渐变、音效暂停和断图衔接起来

边界：管理状态回程/超时与真实设备完成分开；旧PA也有淡出。

- SetSessionFade L1861–1904：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1861
- OnFadeDone L1777–1804：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1777
- Pause L1110–1141：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1110

## P13 切换设备：迁移输入对象，重建目标连接

路由选择落实为跨 Manager 的拆连、接入与状态衔接

边界：MOVE成功是管理语义；声学连续性需实机测量。

- FetchOutputDevices L966–978：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L966
- MoveSinkInputByIndexOrName L1065–1095：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1065
- MoveStreamSync L872–916：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L872
- 目标Manager接入与映射更新 L1181–1227：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1181
- AddSingleNodeToSink L106–179：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L106
- UPDATE_SPANSIZE 状态处理 L1157–1183：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/hpae_renderer_stream_impl.cpp#L1157

## P14 性能观测：分别记录控制确认和数据执行

用真实事件定位排队、供数与设备开销，再讨论整机收益

边界：跨时钟域需对齐；CPU降低不能直接换算功耗百分比。

- StartAudioStream / 等待RUNNING L1398–1454：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/client/src/renderer_in_client_public.cpp#L1398
- STARTED 状态回程 L411–428：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L411
- PushRequest / HandleRequests / TryExpandQueue L57–145：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L57
- ProcessRenderUseTiming L2449–2477：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2449
- ProcessHdiRendererPrimary / ThreadFuncWriteHDI L3821–3887：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L3821
- SinkOutput::DoProcess / RenderFrame L121–165：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L121
- WriteData L1122–1161：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L1122

## P15 自研的技术价值，落在可验证的执行设计上

线程、消息和节点生命周期共同支撑底座演进

边界：旧PA具有模块化与异步队列；不把本页当成全部功能差异表。

- ProcessRenderUseTiming L2449–2477：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2449
- ProcessHdiRendererPrimary / ThreadFuncWriteHDI L3821–3887：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L3821
- Start / pa_stream_cork L154–182：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/pa_renderer_stream_impl.cpp#L154
- PaLockGuard L25–63：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/include/pa_adapter_tools.h#L25
- PushRequestNode 原子发布 L172–191：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L172
- ProcessCluster::Connect L206–232：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L206
- CreateSessionEffectNode L547–582：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L547
- RendererManager::Start L919–945：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919

## P16 A1  Buffer 参数怎样避免比错

旧 PA 请求值与新引擎的帧粒度、字节提交块不能直接相减

边界：20/80ms不是实测时延；新配置按设备变化。

- ConnectRendererStreamToPA L673–702：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/pa_adapter_manager.cpp#L673
- ReadDataAndConvertFormat L680–707：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L680
- AddSingleNodeToSink L106–179：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L106
- UPDATE_SPANSIZE 状态处理 L1157–1183：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/hpae_renderer_stream_impl.cpp#L1157

## P17 A2  队列容量与耗尽路径

常规原子操作之外，扩容和容量耗尽必须纳入设计

边界：达到上限不等于立即丢请求；仅无空闲节点且扩容后仍失败才丢弃。

- PushRequest / HandleRequests / TryExpandQueue L57–145：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L57
- 队列容量与扩容阈值 L28–38：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.h#L28
- PushRequestNode 原子发布 L172–191：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L172

## P18 A3  一次 Pull：有结果就取，空队列才计算

OutputPort 的队列条件决定是否触发前驱节点处理

边界：端口结果队列与Converter内部缓存是不同对象。

- InputPort::ReadPreOutputData L315–325：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/include/hpae_node.h#L315
- OutputPort::PullOutputData L389–404：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/include/hpae_node.h#L389
- ExtractOutputFromProcessedBuffer L815–840：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_audio_format_converter_node.cpp#L815
- ReadDataAndConvertFormat L680–707：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L680

## P19 A4  迟到的 Drain 回调，怎样避免复活已停流

服务状态检查挡住过时完成事件，体现跨层异步正确性

边界：公共服务层状态保护；不宣称自研新增或所有Stop都会Drain成功。

- Drain迟到回调的状态保护 L450–477：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L450
- StopAudioStream L1554–1603：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/client/src/renderer_in_client_public.cpp#L1554
- Stop设置STOPPING L1889–1916、OPERATION_STOPPED处理 L437–443：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L437

## P20 A5  设备迁移：PA 与 HPAE 的真实设计对照

旧方案已有输入对象复用，自研用 Manager 与节点图组织迁移

边界：旧PA固定bc6e4fe5；不把对象复用作为自研独有创新。

- MoveSinkInputByIndexOrName L447–473：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/audioadapter/src/pulse_audio_service_adapter_impl.cpp#L447
- MoveSinkInputByIndexOrName L1065–1095：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1065
- MoveStreamSync L872–916：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L872
- 目标Manager接入与映射更新 L1181–1227：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1181
- AddSingleNodeToSink L106–179：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L106
- UPDATE_SPANSIZE 状态处理 L1157–1183：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/hpae_renderer_stream_impl.cpp#L1157
- PA move协议：https://gitcode.com/openharmony/third_party_pulseaudio/blob/bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca/src/pulsecore/protocol-native.c#L4483
- PA start_move / finish_move / move_to：https://gitcode.com/openharmony/third_party_pulseaudio/blob/bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca/src/pulsecore/sink-input.c#L1867
- PA finish_move：https://gitcode.com/openharmony/third_party_pulseaudio/blob/bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca/src/pulsecore/sink-input.c#L2159
- PA sink I/O START_MOVE / FINISH_MOVE：https://gitcode.com/openharmony/third_party_pulseaudio/blob/bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca/src/pulsecore/sink.c#L2748

## P21 A6  版本、路径与证据范围

固定提交解释实现，按路径限制结论

边界：OpenHarmony公开源码实现不自动等于所有内部产品配置。

- GetPlaybackManager L29–64：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/i_stream_manager.cpp#L29
- GetPlaybackManager L22–39：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/i_stream_manager.cpp#L22
- paDaemonThread / ohos_pa_main L261–273：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/audio_server.cpp#L261
- PushRequestNode 原子发布 L172–191：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L172
- ProcessCluster::Connect L206–232：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L206
