# 资料来源与技术边界

整理日期：2026-10-22。各页的具体引用与讲述边界见 [speaker_notes.md](speaker_notes.md)。

## 音频架构与演进

- [Linux 内核音频子系统](https://www.kernel.org/doc/html/latest/sound/index.html)
- [ALSA 配置与 OSS 兼容](https://docs.kernel.org/sound/alsa-configuration.html)
- [PulseAudio 更名后的发布说明（2006）](https://0pointer.de/blog/projects/pulse-release.html)
- [PipeWire 项目发布介绍（2017）](https://blogs.gnome.org/uraeus/2017/09/19/launching-pipewire/)
- [PipeWire 发布历史](https://github.com/PipeWire/pipewire/blob/master/NEWS)

## PulseAudio

- [官方项目资料](https://wiki.freedesktop.org/www/Software/PulseAudio/)
- [官方线程模型](https://wiki.freedesktop.org/www/Software/PulseAudio/Documentation/Developer/Threading/)
- [Gavv：PulseAudio under the hood（2017，面向 PA 11.1）](https://gavv.net/articles/pulseaudio-under-the-hood/)
- [多级缓冲原图](https://gavv.net/articles/pulseaudio-under-the-hood/diagrams/buffers.png)：第 7 页，仓库图片 `assets/reference/pa-buffers.png`。

## JACK

- [官方 API 总览](https://jackaudio.org/api/index.html)
- [处理回调及实时约束](https://jackaudio.org/api/group__ClientCallbacks.html)
- [JACK2 官方 README](https://raw.githubusercontent.com/jackaudio/jack2/develop/README.rst)
- [Fons Adriaensen：A quick introduction to Jack（2014）](https://kokkinizita.linuxaudio.org/export/jackpres.pdf)：第 8 页图形取自讲义第 3 页的图形部分，仓库图片 `assets/reference/jack-graph-crop.png`。
- [S. Letz, D. Fober, Y. Orlarey：jackdmp: Jack server for multi-processor machines（LAC 2005）](https://archive2010.grame.fr/ressources/publications/Jackdmp-lac2005.pdf)
- [Stéphane Letz 等：What's new in JACK2?（LAC 2009）](https://lac.linuxaudio.org/2009/cdm/Thursday/01_Letz/01.pdf)

JACK 的串行 8 单位与双核 6 单位是理想化教学算例，假设 A=2、B=3、C=2、D=1，A/B 独立，C 等待两者，D 等待 C，忽略调度与同步开销。串行/并行与同步/异步是不同维度。

## PipeWire

- [官方 Design](https://docs.pipewire.org/page_design.html)
- [官方 Objects Design](https://docs.pipewire.org/page_objects_design.html)
- [官方 Graph Scheduling](https://docs.pipewire.org/page_scheduling.html)
- [官方 Session Manager](https://docs.pipewire.org/page_session_manager.html)
- [SPA Buffers](https://docs.pipewire.org/group__spa__buffer.html)
- [WirePlumber：Understanding Session Management](https://pipewire.pages.freedesktop.org/wireplumber/design/understanding_session_management.html)
- [Wim Taymans：PipeWire State of the Union（FOSDEM 2024）](https://archive.fosdem.org/2024/events/attachments/fosdem-2024-1988-pipewire-state-of-the-union/slides/22795/PipeWire-slides_JBa52sZ.pdf)：第 15 页保留 PDF 第 3 页 Overview 原图，仓库图片 `assets/reference/pipewire-overview.png`。

PipeWire 的 pending 算例省略 Driver 自身计数，仅表示周期启动后的上游依赖。异步 Link 双槽示意针对一般稳态连接，未展开 Driver 输出等特殊处理。共享内存不代表全链零拷贝，异步 Link 的周期代价也不等于固定的端到端时延。

## PreeAudio / HPAE

沿用既有分享的 OpenHarmony 音频框架公开源码快照：`master`，commit `93f5fd0909cb495bc673f4eeeea6997c56f63114`。

- [官方仓库](https://gitcode.com/openharmony/multimedia_audio_framework)
- [Manager 的连接、状态与处理组织](https://gitcode.com/openharmony/multimedia_audio_framework/blob/93f5fd0909cb495bc673f4eeeea6997c56f63114/services/audio_engine/manager/src/hpae_renderer_manager.cpp)
- [工作线程的消息和数据处理衔接](https://gitcode.com/openharmony/multimedia_audio_framework/blob/93f5fd0909cb495bc673f4eeeea6997c56f63114/services/audio_engine/manager/src/hpae_signal_process_thread.cpp)
- [ProcessCluster](https://gitcode.com/openharmony/multimedia_audio_framework/blob/93f5fd0909cb495bc673f4eeeea6997c56f63114/services/audio_engine/node/src/hpae_process_cluster.cpp)
- [OutputCluster](https://gitcode.com/openharmony/multimedia_audio_framework/blob/93f5fd0909cb495bc673f4eeeea6997c56f63114/services/audio_engine/node/src/hpae_output_cluster.cpp)

以上用于解释公开结构，不表示内部部署、产品范围或量化性能承诺。对设计重心与架构取舍的总结是基于机制的归纳。

外部图形版权归原作者，保留作者、年份与原文出处。仓库不附带上游文章或论文全文。
