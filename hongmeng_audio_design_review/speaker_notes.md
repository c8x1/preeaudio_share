# 一段声音的旅程：鸿蒙音频底座的协同与自研演进

15页主讲55分钟，另5分钟答疑。A1–A6按需。分钟数含试听、互动和停顿。

## 01 一次 Start，什么时候才算开始播放？

时间：3分钟

音乐播放、游戏加入、切耳机这些场景，都依赖一次次具体操作。先看最简单的Start。客户端调用StartAudioStream，经IPC发起请求，并等待管理状态回程。图中第三个观察点是设备侧处理线程通过节点图取得数据，再调用RenderFrame。扬声器真实出声是更下游的额外观察点。这里并排展示观察点，不画固定的时间先后：跨线程下RUNNING与首帧消费没有本图可证明的全局总序。
为什么有这么多层？因为策略要先组织会话与路由，服务要验证状态和缓冲，引擎要把请求送入自己的执行上下文，硬件还要兑现输出。今天不复习PCM，而是沿Start、Pause、Move三种真实操作，看旧PA与自研分别怎样组织工作。线程交接、缓冲库存、队列算法和节点连接会直接画在正文。

演示 cue：无
讲述安排：建议3分钟，包含逐步读图、停顿与互动。请听众先判断：客户端收到RUNNING是否足以断言扬声器已经出声？暂不要求答案。
转场：先定位这些事件属于哪些对象、经过哪些通道。
技术边界：RUNNING、RenderFrame 返回、声学出声是不同语义。

依据：
- StartAudioStream / 等待RUNNING L1398–1454：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/client/src/renderer_in_client_public.cpp#L1398
- HpaeManager::Start L1830–1875：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1830
- STARTED 状态回程 L411–428：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L411
- SinkOutput::DoProcess / RenderFrame L121–165：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L121

---

## 02 音频底座的对象与通信通道

时间：4分钟

这张图标对象和通信方式，不把每个框当成一个进程。RendererInClient负责客户端流操作；RendererInServer在服务端验证状态、缓冲并协调策略会话。服务通过具体流实现进入HpaeManager，再转到设备RendererManager。管理层和设备层各有自己的请求队列，下一页展开两次排队。
数据走另一条路：应用把音频写入共享缓冲，服务WriteData负责读数据、复制和推进指针，HPAE输入节点经回调取得这些数据。这里为避免拥挤折叠了流适配与输入节点，绿色线明确连接共享缓冲、服务读取、SinkInput与输出节点图，不经过管理队列。蓝色线表示Manager组织处理图与状态。SinkOutput从图中拉取处理结果，再调用设备RenderFrame。策略负责会话与路由，它不执行这条PCM处理链。共享内存也不意味着服务内零复制。

演示 cue：无
讲述安排：建议4分钟，包含逐步读图、停顿与互动。沿蓝色控制轨与绿色数据轨各走一次，指出数据没有进入管理请求队列。
转场：一次Start为何会出现两次排队？
技术边界：普通 HPAE 播放路径，图不表示进程划分。

依据：
- WriteData L1122–1161：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L1122
- StartInner L1576–1606：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L1576
- HpaeManager::Start L1830–1875：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1830
- RendererManager::Start L919–945：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919
- SinkOutput::DoProcess / RenderFrame L121–165：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L121
- ActivateAudioInterrupt L818–853：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L818
- FetchOutputDevices L966–978：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L966

---

## 03 Start 如何穿过策略、服务与两级队列

时间：3分钟

客户端先经IPC向RendererInServer请求Start。服务端验证状态和共享缓冲，调用策略UpdateSessionOperation；普通非FAST路径在设备激活后WaitForDataConnection，目的是避免蓝牙连接前后数据不连续造成爆音，之后调用流Start。HpaeManager先把Start封成管理请求。管理线程消费时找到RendererManager，再调用它的Start，而RendererManager只是把具体连接、淡入、音效工作放入设备级队列。随后管理状态STARTED可以回传服务端和客户端，客户端等待RUNNING。
图上第二次入队与上行状态是两条分叉，不用从设备级队列向STARTED画完成箭头。RendererManager的请求实际执行时才置HPAE_SESSION_RUNNING、ConnectInputSession、SetSessionFade、启动可选SessionEffect。这里的RUNNING是管理状态，不是设备或声学首帧的同步屏障。策略先被调用是系统协同的一部分，具体声音并发规则和目标设备依业务策略而定。

演示 cue：无
讲述安排：建议3分钟，包含逐步读图、停顿与互动。请听众指出第二次入队的位置，以及STARTED回程为什么不等待首帧。
转场：旧5.1方案的Start怎样经PA主循环和回调？
技术边界：普通 HPAE 路径；非 FAST 的连接等待有条件；无跨线程全局总序。

依据：
- StartAudioStream / 等待RUNNING L1398–1454：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/client/src/renderer_in_client_public.cpp#L1398
- StartInner L1576–1606：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L1576
- HpaeManager::Start L1830–1875：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1830
- RendererManager::Start L919–945：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919
- STARTED 状态回程 L411–428：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L411

---

## 04 5.1 方案：PA Start 的同步返回与操作回调

时间：4分钟

在OpenHarmony 5.1中，AudioServer通过paDaemonThread运行ohos_pa_main，PA不是一个与鸿蒙音频底座隔离的外部黑盒。策略、RendererInServer仍在鸿蒙框架里。流实现PaRendererStreamImpl的Start持PaLockGuard保护mainloop，检查PA stream为READY，随后pa_stream_cork(stream,0,PAStreamStartSuccessCb)提交解除cork操作。Start函数成功返回只说明这一调用路径完成，后续PAStreamStartSuccessCb操作回调置RUNNING并调用statusCallback的OPERATION_STARTED。这个5.1回调收到success参数，但当前实现未检查它便更新状态，因此图和讲述只称“操作回调”，不据此声称底层实际输出成功。
图中的PA异步操作是一条折叠泳道，不展开第三方库内部处理顺序。Start同步返回SUCCESS与后续操作回调分开画。5.1还在hdi_sink中承担混音/场景音效和HDI适配，下一页展示普通主输出真正把数据交给写线程的位置。这里对照的是控制请求进入旧执行模型的方式。PA本身包含异步消息机制，所以后文不会把旧方案概括为“所有队列都靠一把锁”。

演示 cue：无
讲述安排：建议4分钟，包含逐步读图、停顿与互动。请区分同步返回、操作回调及声学出声；不要只依据函数名中的Success作判断。
转场：再从控制转到数据，定位旧主输出的线程交接。
技术边界：旧版5.1普通PA路径；操作回调不等于声学出声；回调未检查success参数。

依据：
- paDaemonThread / ohos_pa_main L261–273：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/audio_server.cpp#L261
- Start / pa_stream_cork L154–182：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/pa_renderer_stream_impl.cpp#L154
- PaLockGuard L25–63：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/include/pa_adapter_tools.h#L25
- pa_stream_write / PAStreamWriteCb L699–755：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/pa_renderer_stream_impl.cpp#L699
- SinkRenderPrimaryProcess L2315–2354：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2315
- PAStreamStartSuccessCb L835–855：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/pa_renderer_stream_impl.cpp#L835

---

## 05 5.1 普通主输出：渲染与 HDI 写分属两线程

时间：3分钟

旧方案的成本不能靠概念描述。5.1 hdi_sink的普通主输出，在ProcessRenderUseTiming里调用SinkRenderPrimary取得pa_memchunk，随后pa_asyncmsgq_post把HDI_RENDER和chunk送入primary.dq。另一侧ThreadFuncWriteHDI阻塞在pa_asyncmsgq_get，拿到消息后进入ProcessHdiRendererPrimary，检查设备启动状态再调用RenderWrite。SinkAdapter最终向HDI提交。
这个结构带来一个明确的跨线程排队与唤醒边界。代码传递的是pa_memchunk结构与内存块引用，不能把它画成每次PCM memcpy，也不能凭此给出时延百分比。旧写线程还能处理HDI_START、HDI_STOP与QUIT，线程职责并非纯写入。下一页严格对照同一普通主输出路径，看看自研引擎把哪段交接收到了同一执行链。

演示 cue：无
讲述安排：建议3分钟，包含逐步读图、停顿与互动。指出primary.dq两侧执行上下文；询问chunk引用传递是否必然等于PCM复制。
转场：把这个交接与新HPAE同范围路径并列。
技术边界：旧方案具体路径；不能推广到所有PA设备、DIRECT或offload路径。

依据：
- ProcessRenderUseTiming L2449–2477：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2449
- ProcessHdiRendererPrimary / ThreadFuncWriteHDI L3821–3887：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L3821

---

## 06 同一普通输出路径：跨线程交接在哪里收拢

时间：3分钟

将前后两个固定源码版本的普通主输出放在同一范围比较。旧hdi_sink生成chunk后经primary.dq交给HDI写线程。新HpaeSignalProcessThread先HandleMsg，再调用HpaeRendererManager::Process；随后进入OutputCluster的DoProcess、SinkOutput的DoProcess，并在这条调用链里RenderFrame。自研在这里收拢了旧渲染到HDI写线程的交接，减少一次可定位的排队/唤醒边界。
图不声称操作系统、驱动或硬件再没有其他线程，也不将两个版本所有特殊播放路径混在一起。资源和时延收益由用户提供的是定性结论；静态代码只解释为什么这个改动可能改善延迟和调度开销。下一页拆开新处理线程：它怎样同时处理控制和数据，何时等待。

演示 cue：无
讲述安排：建议3分钟，包含逐步读图、停顿与互动。分别沿左右链路走一遍，在旧dq位置停顿，解释删除的是哪一段交接。
转场：新线程如何同时承接消息和音频处理？
技术边界：两个版本的实现对照，不是相同设备上的实测数值。

依据：
- ProcessRenderUseTiming L2449–2477：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2449
- ProcessHdiRendererPrimary / ThreadFuncWriteHDI L3821–3887：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L3821
- Notify / Run L75–125：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_signal_process_thread.cpp#L75
- Process L1640–1664：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1640
- OutputCluster::DoProcess L79–84：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_output_cluster.cpp#L79
- SinkOutput::DoProcess / RenderFrame L121–165：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L121

---

## 07 新处理线程：消息与音频怎样共用执行循环

时间：4分钟

HpaeSignalProcessThread的Run不是一个固定10ms定时器。线程等待在condition变量上，谓词包括running停止、Manager已在运行、有待处理消息、收到Notify。醒来后调用manager->HandleMsg()，随后调用manager->Process()，最后清recvSignal标记，进入下一轮。Manager的SendRequest负责把控制lambda送到无锁消息队列，并按路径Notify。
这解释了为什么线程合并不等于在数据处理期间随意并发修改图：控制变更被投递到处理上下文，先处理消息，再拉音频数据。Notify本身仍持mutex并触发condition_variable，不能称整个控制链无锁。图中只说明该线程循环的源码顺序，设备RenderFrame耗时、其他设备线程与实时调度效果要另外测。下一页用SinkOutput的一次拉取说明这里的Process实际如何拿到足够设备帧。

演示 cue：无
讲述安排：建议4分钟，包含逐步读图、停顿与互动。让听众指出控制修改在Process之前消费，以及Notify仍有哪类同步。
转场：Process怎样拉到足够数据并适配设备提交块？
技术边界：处理顺序来自Run；不声明固定调度周期或系统硬实时。

依据：
- Notify / Run L75–125：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_signal_process_thread.cpp#L75
- SendRequest L1755–1770：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1755
- Process L1640–1664：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1640

---

## 08 Buffer 减在哪，仍保留在哪

时间：4分钟

线程交接减少后，Buffer不能简单清零。当前服务端仍用共享缓冲承接应用数据，WriteData从缓冲读取、复制并推进读指针。处理图中格式转换节点有已经处理过的缓存，OutputPort仅在其输出队列为空时才触发节点DoProcess；Converter自己的processedBuffer_要积累到outputFrameLen20ms_才能提取并消费，这与OutputPort队列条件是两个不同判断。SinkOutput的ReadDataAndConvertFormat按currentSize_ < renderSize_循环：向前驱拉取、从float转换并累积到renderFrameData_，拼满后再调用RenderFrame。这里renderSize_是字节数，不是时长。图中三处是不同职责的库存：供数、格式适配和提交拼帧。
旧普通主输出的primary.dq跨线程chunk交接已不在这条新调用链里。实际总Buffer数量、每段时延和端到端抗抖动能力需要同硬件同业务测量；用户团队给出的保持抗抖动是定性结论，静态代码只能解释这些保留缓存如何承担职责。试听素材可用来帮助新员工理解欠载声音，但不能冒充实机验证。

演示 cue：可选试听：先连续版本10秒，再人为模拟断音版本10秒；仅用于解释连续性，不代表产品测量。
讲述安排：建议4分钟，包含逐步读图、停顿与互动。分别解释端口结果队列、Converter缓存和SinkOutput字节拼帧，不把三者混为一处。
转场：接着看控制请求进入该线程的队列算法。
技术边界：未给默认帧数或毫秒值，因设备/配置可变。

依据：
- WriteData L1122–1161：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L1122
- ExtractOutputFromProcessedBuffer L815–840：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_audio_format_converter_node.cpp#L815
- InputPort::ReadPreOutputData L315–325：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/include/hpae_node.h#L315
- ReadDataAndConvertFormat L680–707：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L680
- SinkOutput::DoProcess / RenderFrame L121–165：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L121
- ProcessRenderUseTiming L2449–2477：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2449
- OutputPort::PullOutputData L389–404：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/include/hpae_node.h#L389

---

## 09 无锁消息队列：CAS 发布与批次消费

时间：4分钟

Start将工作包装成lambda，再通过SendRequest送入请求队列。生产者先从空闲节点链中原子摘取节点，填入request，然后通过CAS把节点压到请求头。多个线程竞争时，CAS成功次序定义入链先后；链表按头插法反转了它。消费者HandleRequests用CAS一次摘走当前整批，ProcessRequests沿链放进临时数组，再反向遍历执行，恢复批内发布次序。执行的每个lambda本身并非原子操作，也不承诺跨批次或外部业务请求的全局语义顺序。
这就是无锁消息队列值得讲的算法细节：常规取节点、发布、摘批依赖原子操作，让控制请求进入处理侧不必围绕同一业务锁串行。但慢路径TryExpandQueue持expandMutex且分配新节点，处理线程的Notify也有锁；达到最大容量仍无空节点时会上报并丢弃请求。这里不说全链无锁、零分配。

演示 cue：无
讲述安排：建议4分钟，包含逐步读图、停顿与互动。以两个依次成功CAS发布的请求说明头插反转与消费反向遍历，无需新增产品假数据。
转场：消费者执行的lambda会操作怎样的处理图？
技术边界：不保证所有请求必达或所有操作无锁。

依据：
- SendRequest L1755–1770：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1755
- PushRequest / HandleRequests / TryExpandQueue L57–145：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L57
- PushRequestNode 原子发布 L172–191：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L172
- ProcessRequests 批量执行 L227–262：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L227
- 队列容量与扩容阈值 L28–38：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.h#L28

---

## 10 节点图：输出端拉取，处理结果正向返回

时间：4分钟

当前ProcessCluster::Connect建立真实的输入链：SinkInput到Converter，按条件加入SessionEffect，再经过LoudnessGain、Gain、sceneMixer，场景后还可接RenderEffect。OutputCluster连接场景转换、输出混音与SinkOutput，最后SinkOutput调用RenderFrame。图上箭头要区分两个方向：输出侧InputPort向前驱请求结果，结果帧沿节点连接正向返回。OutputPort有数据时可直接取；队列空才让所属节点DoProcess。
节点化的扩展价值因此更具体：格式转换、增益、混音与音效职责分离，一个会话音效无需复制整条设备通路。Manager对场景簇与设备簇进行创建、映射和状态管理。说“节点类型可复用”不等于“所有会话共享同一个节点实例”；默认、bypass等过程簇有条件地创建和复用。下页看一个局部重连的真实代码分支。

演示 cue：无
讲述安排：建议4分钟，包含逐步读图、停顿与互动。先正向读数据处理职责，再从输出端反向沿连接指出拉取请求。
转场：用会话音效插入，看节点化怎样集中修改范围。
技术边界：当前源码配置路径；不声称每个产品都启用所有音效。

依据：
- ProcessCluster::Connect L206–232：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L206
- OutputCluster::Connect L110–135：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_output_cluster.cpp#L110
- CreateProcessClusterInner L179–240：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L179
- InputPort::ReadPreOutputData L315–325：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/include/hpae_node.h#L315
- OutputPort::PullOutputData L389–404：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/include/hpae_node.h#L389
- SinkOutput::DoProcess / RenderFrame L121–165：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L121

---

## 11 接入会话音效：成功创建后才重连

时间：3分钟

拿接入会话音效这个真实功能看节点化价值。ProcessCluster::CreateSessionEffectNode先检查该session没有已绑定音效，再查Converter与LoudnessGain两端存在。创建HpaeSessionEffectNode后调用CreateEffectWithInstance。只有创建成功才断开原Converter到LoudnessGain的连接，将SessionEffectNode接在两者之间，并更新idSessionEffectMap。
这个顺序的工程价值是失败时不用恢复一条已被破坏的通路：找不到节点、重复绑定或初始化失败都在DisConnect前返回。这里说的是这段函数的局部图修改，不保证其外部生命周期和并发操作也具备事务原子性。当前AISS接入分支还有48kHz双声道格式约束，不能说任意音效/格式都可即插即用。设备输出、通用Gain和sceneMixer继续复用，需求变更集中在会话链局部。

演示 cue：无
讲述安排：建议3分钟，包含逐步读图、停顿与互动。请听众找出最后一个失败返回点与第一个DisConnect之间的关系。
转场：图的生命周期还要响应Pause和Stop。
技术边界：局部函数失败保持旧边；不夸大为整图事务。

依据：
- CreateSessionEffectNode L547–582：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L547
- SessionEffect 输入格式约束 L351–365：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L351
- ProcessCluster::Connect L206–232：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L206

---

## 12 Pause / Stop：淡出完成后再断开节点

时间：4分钟

这里画的是设备RendererManager内部HPAE_SESSION状态，而不是客户端API状态。普通活跃流Pause会SetSessionFade进入PAUSING；Stop进入STOPPING。Gain节点输出淡出后调用OnFadeDone，OnFadeDone再次把工作送回设备队列，在该上下文暂停会话音效、DisConnectInputSession、置PAUSED或STOPPED，再触发状态回调。先过渡再拆图，把声音渐变与资源连接协调起来。
有两个重要条件。若节点已经PAUSED/STOPPED、无Gain、Manager未运行或standby等，会走直接终态回调路径。若淡出完成消息回来时节点已恢复RUNNING，OnFadeDone退出，避免迟到的回调把新播放的连接拆掉。管理层还有pending transition和超时兜底，不能把管理回调当成设备完成屏障。旧PA同样有淡出，这里展示自研通过节点状态、Gain回调和设备队列组织职责，不宣称首次发明渐变。

演示 cue：无
讲述安排：建议4分钟，包含逐步读图、停顿与互动。沿Pause一行走正常路径，再用“淡出中恢复Start”解释过时回调保护。
转场：同样的连接管理怎样服务系统设备切换？
技术边界：管理状态回程/超时与真实设备完成分开；旧PA也有淡出。

依据：
- SetSessionFade L1861–1904：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1861
- OnFadeDone L1777–1804：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1777
- Pause L1110–1141：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1110

---

## 13 切换设备：迁移输入对象，重建目标连接

时间：4分钟

全局策略先按usage、client等选择目标设备。图把策略和服务到引擎的中间层折叠，从HpaeManager的已有目标sink迁移路径展开。HpaeManager找到旧RendererManager后请求MoveStream；MoveStreamSync保留shared_ptr指向的SinkInput对象，在需要时让会话音效准备迁移，触发当前状态，删除旧会话连接但保留音效attach状态，再以MOVE_SINK_INPUT回调交回Manager。
Manager把对象交给目标RendererManager::AddNodeToSink，这又是一次请求入队。AddSingleNodeToSink会更新deviceClass、deviceName、网络与地址、状态回调、sceneType及帧长，发UPDATE_SPAN_SIZE，创建目标过程簇；仅在isConnect且内部状态RUNNING时连接输入。Manager还更新会话到sink的映射。保留输入对象不等于保留所有处理节点；目标处理图要按目标设备条件建立。图不声称所有设备类型通用，也不把迁移回调当作声学无缝完成。

演示 cue：无
讲述安排：建议4分钟，包含逐步读图、停顿与互动。指出保持的SinkInput对象与需要按目标设备重建的连接不是同一层概念。
转场：有了具体机制，应该分别观察哪些事件来验证收益？
技术边界：MOVE成功是管理语义；声学连续性需实机测量。

依据：
- FetchOutputDevices L966–978：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_policy/server/domain/zone/src/audio_zone_service.cpp#L966
- MoveSinkInputByIndexOrName L1065–1095：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1065
- MoveStreamSync L872–916：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L872
- 目标Manager接入与映射更新 L1181–1227：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1181
- AddSingleNodeToSink L106–179：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L106
- UPDATE_SPANSIZE 状态处理 L1157–1183：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/hpae_renderer_stream_impl.cpp#L1157

---

## 14 性能观测：分别记录控制确认和数据执行

时间：4分钟

这页给可执行的观测位置，没有填入不存在的实测曲线。客户端StartAudioStream入口和IPC返回可观察管理调用；OnOperationHandled对应RUNNING。引擎可观察队列发布和HandleRequests消费、SinkInput首次取到数据、SinkOutput首次RenderFrame，外部回环或声学检测观察实际出声。左右是两组事件，不画RUNNING和首帧之间的固定时间顺序。
同一时钟域中可计算入口到状态确认的管理响应、队列发布到消费的等待、供数到RenderFrame的处理段。声学端到端要对齐采集时钟，不能直接相减不同机器时间戳。旧PA的post/get也可作为交接事件，与新引擎同业务语义对照。CPU时间、线程唤醒、欠载和能量应在同硬件、同负载、同输出设备和音量下联合观察；Buffer和块长差异必须记录。用户团队确认方向为时延降低、性能提升和功耗下降，本轮没有产品数值，最终收益等待数据。
采集时用session标识、可检测信号或标记帧把同一段目标音频关联起来，不能把启动后的静音首帧与目标声音的声学检测误配。

演示 cue：无
讲述安排：建议4分钟，包含逐步读图、停顿与互动。让听众选择要测管理响应还是声学端到端，并解释时钟对齐和目标声音标记。
转场：回顾已经用源码解释清楚的新旧设计差异。
技术边界：跨时钟域需对齐；CPU降低不能直接换算功耗百分比。

依据：
- StartAudioStream / 等待RUNNING L1398–1454：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/client/src/renderer_in_client_public.cpp#L1398
- STARTED 状态回程 L411–428：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L411
- PushRequest / HandleRequests / TryExpandQueue L57–145：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L57
- ProcessRenderUseTiming L2449–2477：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2449
- ProcessHdiRendererPrimary / ThreadFuncWriteHDI L3821–3887：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L3821
- SinkOutput::DoProcess / RenderFrame L121–165：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L121
- WriteData L1122–1161：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L1122

---

## 15 自研的技术价值，落在可验证的执行设计上

时间：4分钟

主讲最后回顾已经逐图走过的机制。第一，普通主输出从旧render经primary.dq到HDI写线程，改为当前设备处理线程拉图后提交；少了一段明确的线程交接。第二，旧Start实例持PaLockGuard调用cork并经操作回调通知，新引擎把控制lambda原子发布给管理/设备队列，在处理上下文更新状态；这里比较组织方式，不能概括旧PA全有锁或当前全无锁。第三，旧hdi_sink的混音、场景音效、特殊通路实现被更明确的节点职责和簇连接组织；PA本身也有模块化，改进体现于当前底座的职责边界和可组合处理链。第四，Pause/Stop利用中间态与Gain完成回调协调断图，并防止过时回调误拆恢复的播放链。
这些设计仍在全局策略、服务状态和设备能力约束中工作。用户团队确认时延、性能和功耗方向性收益；具体产品数据和场景需要后续补充。附录提供缓存参数、队列容量、Pull条件和竞态核验，供答疑深入。

演示 cue：无
讲述安排：建议4分钟，包含逐步读图、停顿与互动。用四条已经展示的机制回顾，全套量化结果等待产品数据，不现场估算百分比。
转场：主讲结束，进入5分钟问答；按问题选择A1–A6。
技术边界：旧PA具有模块化与异步队列；不把本页当成全部功能差异表。

依据：
- ProcessRenderUseTiming L2449–2477：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2449
- ProcessHdiRendererPrimary / ThreadFuncWriteHDI L3821–3887：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L3821
- Start / pa_stream_cork L154–182：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/pa_renderer_stream_impl.cpp#L154
- PaLockGuard L25–63：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/include/pa_adapter_tools.h#L25
- PushRequestNode 原子发布 L172–191：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L172
- ProcessCluster::Connect L206–232：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L206
- CreateSessionEffectNode L547–582：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L547
- RendererManager::Start L919–945：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919

---

## A1 A1  Buffer 参数怎样避免比错

时间：0分钟

5.1 ConnectRendererStreamToPA以BUF_LENGTH_IN_MSEC为基准，普通流的prebuf与minreq对应20ms字节数，tlength与maxlength对应80ms；DUP/DUAL有不同分支。这些数值传给pa_stream_connect_playback并带ADJUST_LATENCY等flags，是请求的PA属性，不是端到端实测时延，也不是每个时刻真实库存。
当前HPAE则需分别看帧粒度frameLen/span、SinkOutput的字节提交块renderSize_、Converter已处理缓存和各处真实库存。设备迁移还会按目标设备调整frameLen并通知span。比较新旧时应固定业务语义、设备和负载，抓运行时属性与队列库存，不能用80减20直接宣布降低60ms。

演示 cue：无
讲述安排：按答疑问题选讲，不计入55分钟主讲。先走正常路径，再解释条件与边界。
转场：队列容量和异常路径见A2。
技术边界：20/80ms不是实测时延；新配置按设备变化。

依据：
- ConnectRendererStreamToPA L673–702：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/pa_adapter_manager.cpp#L673
- ReadDataAndConvertFormat L680–707：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L680
- AddSingleNodeToSink L106–179：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L106
- UPDATE_SPANSIZE 状态处理 L1157–1183：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/hpae_renderer_stream_impl.cpp#L1157

---

## A2 A2  队列容量与耗尽路径

时间：0分钟

无锁算法之外还要看容量。当前常量初始1000节点，90%使用阈值触发尝试扩容，每次最多增加1000，到5000封顶。若取空闲节点失败，PushRequest强制尝试扩容，再取一次；仍失败会上报队列异常并丢本次请求。TryExpandQueue在加锁前后均检查容量与阈值，锁内分配新块并追加到空闲节点链。
因此不能说每个Push恒定时间或从不分配。正常发布用原子操作，而慢路径仍可能发生互斥与内存分配。调用方也不能从void PushRequest接口推断所有请求已可靠送达；容量监控与产品负载测试仍有必要。这些是当前实现常量，不是性能指标。

演示 cue：无
讲述安排：按答疑问题选讲，不计入55分钟主讲。先走正常路径，再解释条件与边界。
转场：节点拉取与缓存命中见A3。
技术边界：达到上限不等于立即丢请求；仅无空闲节点且扩容后仍失败才丢弃。

依据：
- PushRequest / HandleRequests / TryExpandQueue L57–145：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L57
- 队列容量与扩容阈值 L28–38：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.h#L28
- PushRequestNode 原子发布 L172–191：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L172

---

## A3 A3  一次 Pull：有结果就取，空队列才计算

时间：0分钟

InputPort::ReadPreOutputData遍历连接的前驱并调用其OutputPort::PullOutputData。OutputPort先检查outputData_队列，只有空队列才调用所属Node的DoProcess。随后若队列已有结果，移动back并pop_back返回；计算后仍为空就返回nullptr；InputPort只收集非空结果。图中橙色DoProcess是条件分支，不是每次Pull的必经步骤。
这解释为什么不能说一轮Process中所有节点必然各运行一次。下游按需要反向索取，上游已有结果可被消费；有些节点如Converter还维护自己独立的处理帧缓存，与端口结果队列不同。SinkOutput可能重复拉取并拼成设备renderSize。所有条件都来自现有代码，图中没有设置虚构的默认帧数或时长。

演示 cue：无
讲述安排：按答疑问题选讲，不计入55分钟主讲。先走正常路径，再解释条件与边界。
转场：公共服务层过时回调竞态见A4。
技术边界：端口结果队列与Converter内部缓存是不同对象。

依据：
- InputPort::ReadPreOutputData L315–325：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/include/hpae_node.h#L315
- OutputPort::PullOutputData L389–404：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/include/hpae_node.h#L389
- ExtractOutputFromProcessedBuffer L815–840：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_audio_format_converter_node.cpp#L815
- ReadDataAndConvertFormat L680–707：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_sink_output_node.cpp#L680

---

## A4 A4  迟到的 Drain 回调，怎样避免复活已停流

时间：0分钟

更深入看整个底座的一个真实竞态。客户端Stop对普通流会先尝试Drain；Drain等待超时并不阻断后续Stop，因此服务端先因Stop请求进入STOPPING，再因OPERATION_STOPPED完成回调进入STOPPED，之后Drain回调才到。服务端OnStatusUpdate处理OPERATION_DRAINED时明确检查当前status_仍为I_STATUS_DRAINING，才恢复STARTED并发送Drain完成；若已经STOPPED等其他状态，不按旧Drain结果恢复。
这里画的是一种可能发生的交错，不是每次Stop必经的固定时序。条件检查让迟到完成事件不能覆盖更新的生命周期状态。它是当前公共流服务层的正确性设计，不应宣传为自研引擎独创。主讲Start展示管理状态与执行分叉，Pause展示设备内部过渡，这页则补公共服务如何处理过时异步事件。

演示 cue：无
讲述安排：按答疑问题选讲，不计入55分钟主讲。先走正常路径，再解释条件与边界。
转场：新旧设备迁移组织对照见A5。
技术边界：公共服务层状态保护；不宣称自研新增或所有Stop都会Drain成功。

依据：
- Drain迟到回调的状态保护 L450–477：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L450
- StopAudioStream L1554–1603：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/client/src/renderer_in_client_public.cpp#L1554
- Stop设置STOPPING L1889–1916、OPERATION_STOPPED处理 L437–443：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L437

---

## A5 A5  设备迁移：PA 与 HPAE 的真实设计对照

时间：0分钟

PA的libpulse发送MOVE_SINK_INPUT，控制上下文通过pa_sink_input_move_to迁移同一个sink_input。start_move同步向旧sink I/O发START_MOVE，让其detach并处理rewind。finish_move更新sink、resampler和音量，然后同步向目标I/O发FINISH_MOVE，目标attach并按latency条件处理drop/rewind。控制侧完成hook与订阅通知，协议ACK返回。两次send是等待I/O处理的握手；ACK也不等于声学切换无间隙。
新HPAE同样保留输入对象，旧Renderer在设备队列中断旧图并回调，HpaeManager交目标Renderer再次入队，更新设备信息与span，根据RUNNING状态连接目标过程簇。这里的设计对照是执行上下文、同步边界和节点状态组织，不是“旧方案重建流、新方案才复用对象”。两边都有可移动性或格式条件，不能推广任意流无损迁移。

演示 cue：无
讲述安排：按答疑问题选讲，不计入55分钟主讲。先走正常路径，再解释条件与边界。
转场：版本与路径适用范围见A6。
技术边界：旧PA固定bc6e4fe5；不把对象复用作为自研独有创新。

依据：
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

---

## A6 A6  版本、路径与证据范围

时间：0分钟

当前框架固定3a2688e8，5.1框架c42a228d，第三方PA 5.1对象bc6e4fe5；完整SHA和每页固定函数行号都在讲稿与sources_and_claims中。当前普通路径下三项自研设计有源码依据，但GetPlaybackManager还有DIRECT、VOIP、硬件解码、Vivid等分支，一些构建还能通过SUPPORT_OLD_ENGINE/flag走旧PA。不能因为讲了普通HPAE就声称全系统所有流都按同一线程模型执行。
本次把证据分三类：函数、状态、队列与连接由固定源码说明；时延降低、性能提升、功耗降低及保持抗抖动是用户团队提供的定性结论；幅度、具体产品配置与声学完成需要同口径实验。三个层次各自有边界，资料可以直接用于讲机制，指标页等待产品数据。

演示 cue：无
讲述安排：按答疑问题选讲，不计入55分钟主讲。先走正常路径，再解释条件与边界。
转场：结束答疑。
技术边界：OpenHarmony公开源码实现不自动等于所有内部产品配置。

依据：
- GetPlaybackManager L29–64：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/i_stream_manager.cpp#L29
- GetPlaybackManager L22–39：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/i_stream_manager.cpp#L22
- paDaemonThread / ohos_pa_main L261–273：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/audio_server.cpp#L261
- PushRequestNode 原子发布 L172–191：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/utils/hpae_no_lock_queue.cpp#L172
- ProcessCluster::Connect L206–232：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp#L206