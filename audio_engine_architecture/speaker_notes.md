## 1. 音频引擎的软件架构演进时间线

建议讲述 2 分钟。这里梳理系统音频软件架构，不是播放器、编解码器或音效算法的历史。1990 年代常见设备接口以 OSS 为例，后续 ALSA 提供驱动及用户态接口。设备抽象层并没有被用户态音频服务取代，现代 Linux 音频服务仍常通过 ALSA 对接设备。2000 年代形成两种侧重：PulseAudio 解决桌面多应用共享与流管理，JACK 侧重专业音频的同步回调与应用互连。PulseAudio 在 2006 年从 Polypaudio 更名，不能把更名年份写成前身诞生年份。PipeWire 在 2017 年正式发布项目，2023 年发布 1.0，逐步在统一媒体图里兼顾桌面与专业用途。PreeAudio 放在当代终端系统路线单独说明，不暗示其由 PipeWire 继承，也不给未经核实的首发年份。

资料来源（查阅日期 2026-10-22）
https://www.kernel.org/doc/html/latest/sound/index.html
https://docs.kernel.org/sound/alsa-configuration.html
https://0pointer.de/blog/projects/pulse-release.html
https://jackaudio.org/api/index.html
https://blogs.gnome.org/uraeus/2017/09/19/launching-pipewire/
https://github.com/PipeWire/pipewire/blob/master/NEWS

## 2. 演进中的四个软件架构变化

建议讲述 2 分钟。第一行说明硬件差异与服务职责逐步分离。第二行说明多应用共享催生流、Sink 和 Source 等管理对象。第三行说明专业处理要求应用在音频周期内合作，图不只是画出来的连接，还涉及运行依赖。第四行强调控制与数据处理分工。这不是严格按年份逐一发生的替换过程，JACK 的图和实时回调在 2000 年代已经出现。对 PreeAudio 可映射到 Manager 管理连接与状态、Node 承担处理、Cluster 组织一组处理，以及 Policy/Service 与引擎间的职责分工。线程实现不可简单等同，HPAE 原有源码资料显示消息与数据处理在同一工作循环中衔接，不能宣称它完全复制 PipeWire 的主线程/数据线程结构。

资料来源（查阅日期 2026-10-22）
https://docs.kernel.org/sound/alsa-configuration.html
https://wiki.freedesktop.org/www/Software/PulseAudio/Documentation/Developer/Threading/
https://jackaudio.org/api/index.html
https://docs.pipewire.org/page_scheduling.html
https://docs.pipewire.org/page_session_manager.html
https://gitcode.com/openharmony/multimedia_audio_framework/blob/93f5fd0909cb495bc673f4eeeea6997c56f63114/services/audio_engine/manager/src/hpae_signal_process_thread.cpp

## 3. PulseAudio：以流和设备组织音频服务

图据 Gavv 的源码阅读和实验文章 High-level components、Buffering、Threads 整理，并使用官方 Threading 文档交叉核对。原文版本为 PulseAudio 11.1，不将所有模块细节当作当前产品配置。客户端通过 libpulse 接入 Native 协议，控制和流管理由服务主循环协调，实时 I/O 线程面向 Sink 处理音频。共享内存可以运送 PCM，socket 仍承担协议通信，具体传输取决于环境。sink-input 包含流级格式适配等职责，Sink 汇合多流，经后端输出到 ALSA。图只展开一个常见输出方向。PA 主循环/实时线程分工与 HPAE 的消息/数据执行机制不一一对应。

资料来源（查阅日期 2026-10-22）
https://wiki.freedesktop.org/www/Software/PulseAudio/Documentation/Developer/Threading/
https://gavv.net/articles/pulseaudio-under-the-hood/
https://gitcode.com/openharmony/multimedia_audio_framework/blob/93f5fd0909cb495bc673f4eeeea6997c56f63114/services/audio_engine/manager/src/hpae_renderer_manager.cpp

## 4. JACK：共享端口缓冲与依赖图调度

主图是根据 Fons Adriaensen 的 A quick introduction to Jack 的客户端、端口、处理周期和调度说明重绘的教学图，不是 JACK 某一版本的完整内部类图。输入端口把采集结果交给 A、B 两个客户端，C 在两者结果可用后处理，最后写往播放端口。每个客户端链接 libjack 并注册 process() 回调，应用的实时处理线程参与执行；音频端口缓冲可位于共享内存，控制消息与音频样本传输需要区分。JACK server 管理连接和运行周期，Backend 抽象设备访问。JACK1 与 JACK2 的调度实现不同，JACK2 在依赖允许时可并行，不能把所有 JACK 系统概括为固定串行执行，也不能断言任何分支一定同时运行。与 PreeAudio 的主要差异是客户端应用互连图与系统引擎内部处理图的集成边界。

资料来源（查阅日期 2026-10-22）
https://jackaudio.org/api/index.html
https://kokkinizita.linuxaudio.org/export/jackpres.pdf

## 5. PipeWire：策略管理与媒体图执行分离

以机制和策略分工解释 PipeWire 的设计理念。WirePlumber 决定设备与连接策略，PipeWire 的主线程处理对象配置与 IPC，数据线程执行已准备好的图。Driver 发起周期，节点在依赖满足后运行，通过共享的 activation 记录及 eventfd 协调，缓冲等资源预先准备。图中的依赖唤醒是同步图的简化示例，异步节点另有处理方式。与 PreeAudio 对比：二者都有节点与图，不应把节点化本身当作区别。PipeWire 以通用媒体图为中心，可以跨进程组织媒体处理；本次公开 HPAE 实现以 Manager 组织 Node/Cluster，在工作循环中衔接消息与 Process。PreeAudio 的策略规则由 Policy/Service 与引擎协作，不能宣称策略与机制分工是某一方独有。差异落在图的组织尺度、控制到执行的职责分配，以及场景处理单元的组织。

资料来源（查阅日期 2026-10-22）
https://docs.pipewire.org/page_scheduling.html
https://docs.pipewire.org/page_session_manager.html
https://gitcode.com/openharmony/multimedia_audio_framework/blob/93f5fd0909cb495bc673f4eeeea6997c56f63114/services/audio_engine/manager/src/hpae_signal_process_thread.cpp
https://gitcode.com/openharmony/multimedia_audio_framework/blob/93f5fd0909cb495bc673f4eeeea6997c56f63114/services/audio_engine/manager/src/hpae_renderer_manager.cpp

## 6. 设计理念与软件架构的横向对比

建议讲述 2 分钟。这里对比可观察到的架构重心，设计出发点和取舍是基于机制的归纳，不冒充内部设计目标声明。PA 围绕流与设备组织通用音频服务，JACK 把各处理者纳入共同周期及依赖约束，PipeWire 把通用媒体图执行与会话策略分工，PreeAudio 的公开 HPAE 结构体现 Manager、Node、Cluster 对场景处理及状态的组织。四者都有实时性、缓冲和动态控制问题，不把任何共性包装成独有优势。本次 HPAE 工作循环是消息处理后衔接数据处理，不能泛化为整个系统只有一个线程。没有统一测量时不宣称谁的时延、功耗或音质更好。

资料来源（查阅日期 2026-10-22）
https://wiki.freedesktop.org/www/Software/PulseAudio/
https://wiki.freedesktop.org/www/Software/PulseAudio/Documentation/Developer/Threading/
https://jackaudio.org/api/index.html
https://docs.pipewire.org/page_design.html
https://docs.pipewire.org/page_scheduling.html
https://docs.pipewire.org/page_session_manager.html
https://gitcode.com/openharmony/multimedia_audio_framework/blob/93f5fd0909cb495bc673f4eeeea6997c56f63114/services/audio_service/server/src/i_stream_manager.cpp
https://gitcode.com/openharmony/multimedia_audio_framework/blob/93f5fd0909cb495bc673f4eeeea6997c56f63114/services/audio_engine/manager/src/hpae_renderer_manager.cpp

## 7. 素材参考：PulseAudio 的多级缓冲

来源原图，未重绘。阅读顺序为 client、transport、server、alsa。原图区分 socket buffers 与共享内存池，继而展示 stream buffer、resampler buffer、render queue 和 device buffer。适合在需要解释多级缓冲时作为备份素材使用，不能把原图当作当前所有 PA 配置的唯一实现。

资料来源（查阅日期 2026-10-22）
https://gavv.net/articles/pulseaudio-under-the-hood/
https://gavv.net/articles/pulseaudio-under-the-hood/diagrams/buffers.png

## 8. JACK 附录：一个处理周期如何完成

原图给出多个客户端和端口的分支、汇合关系。同步处理周期的概念顺序是采集就绪、运行满足依赖的客户端、完成下游处理、向设备提交结果。process(nframes) 在实时线程内读取输入端口缓冲、执行本块 DSP、填充输出端口缓冲。不要在回调中引入可能阻塞的磁盘 I/O、分配或锁等待，具体限制见官方 jack_set_process_callback 文档。假设块长 N=128、采样率 48kHz，名义周期 T=N/fs 约为2.67ms，这只是块周期；读写设备、驱动、安全缓冲与运行模式还会影响端到端时延。整个图、同步与调度开销需要放进预算，不能给每个节点都独占2.67ms。

资料来源（查阅日期 2026-10-22）
https://kokkinizita.linuxaudio.org/export/jackpres.pdf
https://jackaudio.org/api/group__ClientCallbacks.html
https://jackaudio.org/api/index.html

## 9. JACK 附录：串行顺序与依赖驱动

依据 jackdmp 2005 原始论文及 JACK2 README 解释数据流激活。JACK1 的经典模型把客户图排列成串行激活顺序；JACK2 允许依赖已满足的独立客户端同时运行，能否并行取决于图、可用核和系统调度。上图选取 A 然后 B 然后 C 然后 D 的一种合法串行顺序，计算工作合计8单位。下图假设两个工作核可用，A与B从0同时开始，C必须等B在第3单位完成，再运行2单位，D最后运行1单位，总计6单位。关键路径为max(A,B)+C+D，不能把所有节点的计算时间简单除以核数，也不能从该算例推导真实加速比。JACK2 的图访问使用无锁技术，目的是减少图变化干扰实时执行，此描述只针对图访问，不等同于全引擎所有路径无锁。

资料来源（查阅日期 2026-10-22）
https://archive2010.grame.fr/ressources/publications/Jackdmp-lac2005.pdf
https://raw.githubusercontent.com/jackaudio/jack2/develop/README.rst

## 10. JACK 附录：同步与异步的交付取舍

JACK2 README 区分两种服务器级激活模式。同步模式在当前周期等待图内客户端完成，然后使用当前周期的输出。异步模式使用上一周期算好的输出，并在当前周期运行新一轮图，从而解耦设备交付和当前计算。代价是相对同步模型多一个处理周期的流水线等待。若某一客户端未能按期运行，其他客户端仍可能继续并产生部分输出，这不构成任意负载下无断音的保证。同步/异步与串行/并行是不同维度，不可把异步等同于多核并行，也不能把异步理解成没有实时截止期。块周期为2.67ms的教学例子中，这一流水线代价约为2.67ms，设备及其它缓冲时延另计。作者论文讨论各模式的容错行为，不能把所有晚到问题都视为被隔离。

资料来源（查阅日期 2026-10-22）
https://raw.githubusercontent.com/jackaudio/jack2/develop/README.rst
https://lac.linuxaudio.org/2009/cdm/Thursday/01_Letz/01.pdf

## 11. PipeWire 附录：会话策略如何改变运行图

WirePlumber 的会话管理不仅是连线，还包括设备启用、配置、部分访问控制、节点配置、链接及元数据管理。用设备变化的概念示例串起这些职责：监视器发现设备，策略依据配置和偏好作选择，配置节点格式与端口，管理连接，使媒体图满足当前场景。实际实现是持续事件处理，图中顺序用于理解职责，不表示每次热插拔都严格走同一调用链。控制决策不需要逐块参与音频运算。PipeWire 的主线程处理对象与配置，数据线程执行已准备好的图。对照 PreeAudio：Policy/Service 与引擎也有职责分工，具体差异应看规则如何转化为 Manager 的连接和状态更新，不能把策略分离当作 PipeWire 独有特性。

资料来源（查阅日期 2026-10-22）
https://pipewire.pages.freedesktop.org/wireplumber/design/understanding_session_management.html
https://docs.pipewire.org/page_session_manager.html
https://docs.pipewire.org/page_scheduling.html

## 12. PipeWire 附录：依赖计数决定节点何时运行

依据 Graph Scheduling 文档解释同步图。Driver 由硬件事件或定时器等发起处理周期；节点激活记录包含 required 与 pending 等状态，依赖未满足时不能执行。图中 A、B 可运行，C 依赖两者。示例在 Driver 发起周期并释放其门控依赖后，只显示上游工作依赖，因此 C 从2到1再到0。A完成会减少C的待满足依赖数，B完成后C就绪，通过eventfd触发处理。这个简化计数不能直接当作真实activation结构完整数值，因为真实图还包括Driver相关依赖及完成回报。节点完成后继续传播就绪条件，周期结束时Driver可统计处理情况。异步节点不遵循同一同步依赖链，第14页另讲。与HPAE相比，应具体核对其Manager如何驱动OutputCluster并向上游取数，不因两者都叫处理图就假定调度器相同。

资料来源（查阅日期 2026-10-22）
https://docs.pipewire.org/page_scheduling.html
https://gitcode.com/openharmony/multimedia_audio_framework/blob/93f5fd0909cb495bc673f4eeeea6997c56f63114/services/audio_engine/manager/src/hpae_renderer_manager.cpp

## 13. PipeWire 附录：跨进程的数据与唤醒协作

依据 Design、Objects Design 与 Graph Scheduling 文档。PipeWire节点可以位于服务进程或客户端进程。主线程先进行IPC与图配置，在处理开始前准备缓冲、I/O区域和激活记录。对远端节点，此处远端指其它本机进程，eventfd与activation记录可传递给客户端；客户端可以直接唤醒相连节点，不要求每一步都回服务器中转。样本数据与唤醒信号是两类信息：共享缓冲承载媒体块，eventfd传递运行通知，activation记录保存执行及依赖状态。图中只画主要关系，未列所有映射、权限与驱动节点。共享内存不是全链零拷贝保证，媒体转换和混音可能产生新的缓冲或复制。对PreeAudio的比较应落在图执行者的分布及缓冲所有权，而不是应用调用哪个API。

资料来源（查阅日期 2026-10-22）
https://docs.pipewire.org/page_design.html
https://docs.pipewire.org/page_objects_design.html
https://docs.pipewire.org/page_scheduling.html

## 14. PipeWire 附录：异步 Link 的周期隔离

依据Graph Scheduling的Async scheduling章节。异步节点不计入普通同步节点之间的依赖，完成与否不影响同步图周期完成。为避免并行读写同一块数据，异步链接使用两个I/O缓冲槽：周期计数为c时，输出使用(c+1)&1槽，输入使用c&1槽。因而消费者读取上一周期的结果，通常每条异步Link增加一个图周期的延迟。这里采用稳态示例，周期0的槽0中已有上一周期的数据；启动时可能为空。Driver输出存在特殊处理，未在该页展开。异步处理可隔离同步图对该节点的完成依赖，但不保证晚到节点内容始终完整或无失真。JACK2服务器级同步/异步激活与这里的节点/Link级异步机制作用范围不同，不能直接等同。PreeAudio若要做类似比较，需要核实是否存在对应的跨周期缓冲和调度边界，不能仅凭异步消息队列类名推断。

资料来源（查阅日期 2026-10-22）
https://docs.pipewire.org/page_scheduling.html
https://docs.pipewire.org/group__spa__buffer.html

## 15. 素材参考：PipeWire 作者的整体架构图

保留作者 Overview 架构图原页，作为可放大阅读的素材参考。该图同时展示音频与视频生态，包含应用兼容接口、WirePlumber、媒体图、SPA、ALSA-lib、BlueZ、libcamera 与内核设备。它属于 2024 年讲义快照，不把当年的实现细节或状态列表当作当前版本承诺。主稿第 5 页展开策略、控制与图执行的架构分工，原图用于补充整体背景。

资料来源（查阅日期 2026-10-22）
https://archive.fosdem.org/2024/events/attachments/fosdem-2024-1988-pipewire-state-of-the-union/slides/22795/PipeWire-slides_JBa52sZ.pdf