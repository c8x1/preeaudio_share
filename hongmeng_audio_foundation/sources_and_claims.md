# 页面与证据

当前框架3a2688e805df970739e3b0cebf9cc05d8cb24e9b；5.1框架c42a228d60b64a90d6b05cf26278a89253e5310b；5.1PA bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca。源码说明限定实现。时延/性能/功耗及抗抖动定性结论由用户团队提供，未补造幅度。

## P01 我们要交付怎样的声音体验

应用、场景和设备不断变化，用户仍期待一个连贯的体验

边界：焦点、并发、duck和设备路由结果依具体策略；音频素材为教学合成。

- 用户已确认的分享定位与体验目标。
- 当前源码音频焦点入口：services/audio_policy/server/domain/zone/src/audio_zone_service.cpp L818–853；具体实现下页展开。

## P02 鸿蒙音频底座：谁决策，谁管理，谁执行

策略组织系统行为，流服务管理状态，引擎处理数据，设备兑现输出

边界：接口控制路径有折叠；焦点通知可回到应用，不能假定引擎单独完成全部策略行为。

- ActivateAudioInterrupt L818–853：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L818
- FetchOutputDevices L966–978：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L966
- SetSystemVolumeLevel L720–734：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L720
- StartInner L1576–1606：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L1576
- CreateRendererStream L273–307：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/hpae_adapter_manager.cpp#L273
- SinkOutput::DoProcess / RenderFrame L121–165：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L121

## P03 一次场景变化，怎样传遍整个系统

策略决定行为，服务协调状态，引擎与设备共同落实变化

边界：不固定游戏/提醒的焦点结果；引擎迁移仅指存在目标sink的可移动会话。

- ActivateAudioInterrupt L818–853：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L818
- FetchOutputDevices L966–978：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L966
- StartInner L1576–1606：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L1576
- MoveSinkInputByIndexOrName L1065–1095：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1065
- MoveStreamSync L872–916：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L872
- AddSingleNodeToSink L106–179：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L106

## P04 PulseAudio时代，整个底座怎样协同

鸿蒙策略与流服务之下，PA流模型连接自定义音效和HDI适配

边界：PA版本声明17.0另见附录；图不表示独立进程边界，旧方案能力不等于全部由PA上游实现。

- GetPlaybackManager L22–39：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/i_stream_manager.cpp#L22
- paDaemonThread / ohos_pa_main L261–273：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/audio_server.cpp#L261
- pa_stream_write / PAStreamWriteCb L699–755：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/pa_renderer_stream_impl.cpp#L699
- MoveSinkInputByIndexOrName L447–473：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/audioadapter/src/pulse_audio_service_adapter_impl.cpp#L447
- SinkRenderPrimaryProcess L2315–2354：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2315
- ProcessRenderUseTiming L2449–2477：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2449
- ProcessHdiRendererPrimary / ThreadFuncWriteHDI L3821–3887：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L3821

## P05 业务要求提高后，成本出现在哪里

更及时的响应、更低开销和更快需求迭代，要求重新审视执行边界

边界：不虚构业务规模/测试成绩；线程边界不等于固定时延，同步实例不代表所有PA操作。

- ProcessRenderUseTiming L2449–2477：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2449
- ProcessHdiRendererPrimary / ThreadFuncWriteHDI L3821–3887：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L3821
- PaLockGuard L25–63：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/include/pa_adapter_tools.h#L25
- Start / pa_stream_cork L154–182：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/pa_renderer_stream_impl.cpp#L154
- MultiChannel processing L3409–3491：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L3409

## P06 自研要改变什么，又必须守住什么

降低时延与开销，提高扩展性，同时承接完整系统约束

边界：用户团队定性结论含抗抖动保持，不从结构静态证明量化收益。

- GetPlaybackManager L29–64：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/i_stream_manager.cpp#L29
- ActivateAudioInterrupt L818–853：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L818
- FetchOutputDevices L966–978：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L966
- Notify / Run L75–125：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_signal_process_thread.cpp#L75
- PushRequest / HandleRequests / TryExpandQueue L57–145：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L57
- ProcessCluster::Connect L206–232：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L206

## P07 线程精简：减少执行环节之间的交接

旧渲染侧把数据交给写线程，当前处理线程拉图后直接提交

边界：同一调用链仅指引擎到RenderFrame调用；没有测量固定耗时或全局线程数。

- ProcessRenderUseTiming L2449–2477：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2449
- ProcessHdiRendererPrimary / ThreadFuncWriteHDI L3821–3887：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L3821
- Notify / Run L75–125：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_signal_process_thread.cpp#L75
- Process L1640–1664：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1640
- OutputCluster::DoProcess L79–84：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_output_cluster.cpp#L79
- SinkOutput::DoProcess / RenderFrame L121–165：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L121

## P08 Buffer精简，怎样同时守住抗抖动

减少中转环节，同时保留供数、格式适配与设备提交所需的缓存

边界：缓冲职责存在不证明尺寸或抗抖动等价；音频为模拟，不代表真实欠载测量。

- ProcessRenderUseTiming L2449–2477：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2449
- WriteData L1122–1161：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L1122
- ExtractOutputFromProcessedBuffer L815–840：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_audio_format_converter_node.cpp#L815
- ReadDataAndConvertFormat L680–707：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L680

## P09 无锁队列：控制请求怎样进入执行侧

以启动流为例：原子发布请求，由管理器处理线程消费并更新状态

边界：无锁限定常规队列发布与摘取；非全链无锁或硬实时保证，Start不等于首帧已出声。

- Start / pa_stream_cork L154–182：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/pa_renderer_stream_impl.cpp#L154
- PaLockGuard L25–63：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/include/pa_adapter_tools.h#L25
- RendererManager::Start L919–945：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919
- SendRequest L1755–1770：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1755
- PushRequest / HandleRequests / TryExpandQueue L57–145：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L57
- PushRequestNode 原子发布 L172–191：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L172
- ProcessRequests 批量执行 L227–262：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L227
- Notify / Run L75–125：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_signal_process_thread.cpp#L75

## P10 节点化：处理职责怎样复用

节点做处理，簇组合节点，Manager管理连接和状态

边界：Manager控制职责与拉图调用不同；复用类型不等于任意共享有状态实例。

- ProcessCluster::Connect L206–232：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L206
- OutputCluster::Connect L110–135：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_output_cluster.cpp#L110
- CreateProcessClusterInner L179–240：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L179
- InputPort::ReadPreOutputData L315–325：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/include/hpae_node.h#L315

## P11 一个会话接入音效，哪些逻辑能复用

在局部连接中插入SessionEffect，复用已有转换、增益与混音

边界：SessionEffect有格式和状态条件；不提供未经核实的旧新代码量或交付周期对比。

- CreateSessionEffectNode L547–582：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L547
- SessionEffect 输入格式约束 L351–365：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L351
- ProcessCluster::Connect L206–232：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L206
- SinkRenderPrimaryProcess L2315–2354：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2315

## P12 回到全局：策略驱动，执行侧协同落实

三项创新服务于系统行为，最终仍要在应用与设备变化中兑现

边界：不把策略的直接影响理解为全都同步直调引擎，设备迁移限定可移动路径。

- ActivateAudioInterrupt L818–853：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L818
- FetchOutputDevices L966–978：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L966
- SetSystemVolumeLevel L720–734：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L720
- StartInner L1576–1606：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L1576
- SendRequest L1755–1770：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1755
- ProcessCluster::Connect L206–232：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L206
- MoveSinkInputByIndexOrName L1065–1095：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1065
- AddSingleNodeToSink L106–179：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L106
- SinkOutput::DoProcess / RenderFrame L121–165：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L121

## P13 收益怎样在整条音频链路上体现

机制提供改善路径，系统收益需要在一致的场景和测量边界下观察

边界：上屏为机制与评价维度对应，不是测量结果；局部与端到端不能自动同比。

- ProcessRenderUseTiming L2449–2477：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2449
- ProcessHdiRendererPrimary / ThreadFuncWriteHDI L3821–3887：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L3821
- SinkOutput::DoProcess / RenderFrame L121–165：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L121
- PushRequest / HandleRequests / TryExpandQueue L57–145：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L57
- CreateProcessClusterInner L179–240：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L179
- CreateSessionEffectNode L547–582：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L547

## P14 用同一个完整场景验证改进

固定业务语义与环境，记录配置差异，同时观察效率和连续性

边界：拟议测量方案，不展示伪造数据；5.1与master的结构对照不等同受控性能对比。



## P15 鸿蒙音频底座的协同与演进

从同一个场景出发，理解系统分工、执行创新和最终体验

边界：收束归纳，不新增产品性能保证或统一策略规则。

- ActivateAudioInterrupt L818–853：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L818
- FetchOutputDevices L966–978：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L966
- StartInner L1576–1606：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L1576
- Notify / Run L75–125：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_signal_process_thread.cpp#L75
- ProcessCluster::Connect L206–232：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L206
- SinkOutput::DoProcess / RenderFrame L121–165：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L121

## P16 A1  线程与Buffer边界对照

定位已移除的交接，同时区分仍保留的缓存与下游执行

边界：不从请求缓冲属性推导产品时延或线程总数。

- paDaemonThread / ohos_pa_main L261–273：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/audio_server.cpp#L261
- pa_stream_write / PAStreamWriteCb L699–755：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/pa_renderer_stream_impl.cpp#L699
- ConnectRendererStreamToPA L673–702：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/pa_adapter_manager.cpp#L673
- ProcessRenderUseTiming L2449–2477：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2449
- ProcessHdiRendererPrimary / ThreadFuncWriteHDI L3821–3887：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L3821
- WriteData L1122–1161：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L1122
- ExtractOutputFromProcessedBuffer L815–840：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_audio_format_converter_node.cpp#L815
- ReadDataAndConvertFormat L680–707：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L680
- SinkOutput::DoProcess / RenderFrame L121–165：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L121

## P17 A2  无锁队列的常规路径与慢路径

原子发布和批次摘取，不等于扩容、通知与任务执行都无锁

边界：不作全链无锁、无分配、硬实时或必不丢请求的保证。

- 队列容量与扩容阈值 L28–38：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.h#L28
- PushRequest / HandleRequests / TryExpandQueue L57–145：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L57
- PushRequestNode 原子发布 L172–191：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L172
- ProcessRequests 批量执行 L227–262：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L227
- Notify / Run L75–125：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_signal_process_thread.cpp#L75

## P18 A3  真实节点连接与拉取执行

PCM结果正向返回，输出端通过端口向前驱索取计算结果

边界：可选音效和limiter受分支条件限制；Connect代码方向与数据方向不同。

- ProcessCluster::Connect L206–232：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L206
- OutputCluster::Connect L110–135：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_output_cluster.cpp#L110
- OutputCluster 构造与limiter条件 L32–47：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_output_cluster.cpp#L32
- InputPort::ReadPreOutputData L315–325：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/include/hpae_node.h#L315
- OutputPort::PullOutputData L389–404：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/include/hpae_node.h#L389
- ReadDataAndConvertFormat L680–707：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L680

## P19 A4  策略、服务与引擎的启动协作

请求接受、RUNNING状态和首帧消费需要分别观察

边界：不声明RUNNING与真实首帧消费的固定总序；限定普通HPAE路径，其他类型有分支。

- StartAudioStream / 等待RUNNING L1398–1454：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/client/src/renderer_in_client_public.cpp#L1398
- StartInner L1576–1606：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L1576
- HpaeManager::Start L1830–1875：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1830
- RendererManager::Start L919–945：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919
- STARTED 状态回程 L411–428：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L411

## P20 A5  设备切换中的节点与状态衔接

引擎迁移已有输入节点，并按目标设备更新格式、标识与连接

边界：迁移与设备可用性是不同层次；回报成功不等于声学切换结束。

- FetchOutputDevices L966–978：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L966
- MoveSinkInputByIndexOrName L1065–1095：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1065
- MoveStreamSync L872–916：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L872
- 目标Manager接入与映射更新 L1181–1227：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1181
- AddSingleNodeToSink L106–179：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L106
- UPDATE_SPANSIZE 状态处理 L1157–1183：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/hpae_renderer_stream_impl.cpp#L1157

## P21 A6  源码版本与测量口径

固定版本解释实现，明确起止点与条件后再讨论指标

边界：不确认商业产品部署或未披露量化数据，PA版本声明不代表原封不动上游实现。

- GetPlaybackManager L29–64：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/i_stream_manager.cpp#L29
- GetPlaybackManager L22–39：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/i_stream_manager.cpp#L22
- ConnectRendererStreamToPA L673–702：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/pa_adapter_manager.cpp#L673
- PA版本声明：https://gitcode.com/openharmony/third_party_pulseaudio/blob/bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca/README.OpenSource
