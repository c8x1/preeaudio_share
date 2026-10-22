# PA 与 HPAE：结构对照 · 讲稿

两页开篇，承接《一首歌，三个操作》的结尾提问。正文为口播语言；演示顺序、范围与源码依据见文末备讲附录。时长需以实际试讲为准。

## 1. 同一件事，写了几遍

上一部分结尾问：换一个引擎，这三个操作会是什么样？先看结构，再看执行组织。

左边是老方案里干活的文件：HDI sink 模块，四千八百行、一百九十个函数，一个文件。设备开关、格式转换、淡入淡出、状态回调、低时延通路、限幅器、缓冲管理，全在里面。

单看“暂停恢复要淡入淡出”这一件事。主通路一套淡入完成检查，多声道又一套，状态回调按流类型写了四个变体。流类型的差异，被织进了每一个关注点的代码里——每支持一种新的流类型，每个关注点都要再分叉一次。

右边是 HPAE 的做法。淡入淡出整个住在增益节点里，五百行出头，一套状态机：挂标志、逐帧执行、就地回调。主通路、多声道、低时延的流，用的是同一个增益节点。它们的差异只决定挂在哪条处理链上，是挂链时的一个参数，不是代码里的分叉。

维护成本的差别就在这：不是谁的代码行数少，而是同一件事要写几遍、改一处要读懂多少。

## 2. 改动半径：加限幅，接新设备

再看两类最常见的改动，各要碰多大面积。

第一件：给所有通路加限幅。老方案里，限幅器就长在 sink 模块里，加它、改它，动的都是那个四千八百行的文件。HPAE 里它是一个独立的限幅节点，挂进链就行，带着自己的单测。

第二件：接一种新的输出设备。老方案要动 sink 模块里的设备分支和格式转换。HPAE 里节点不关心具体设备：设备信息、帧长、采样率，都是挂到目标侧时填进节点信息的参数。

一个数字收尾：HPAE 的节点层是三十多个文件，每个文件一个职责，最大的一个一千一百行；每个节点有自己的单测，三十多个测试文件。改限幅不用读格式转换，改增益不用碰设备。

所以这一部分的论点先立在这：老方案把流类型和设备差异织进代码分叉，每加一种就全文再分叉一次；HPAE 把它们变成挂链时的参数，每个保证只写一遍。接下来看执行组织——线程和队列——两边又是怎么安排的。

# 备讲附录

以下内容不讲，供试讲与答疑准备。

### P1 同一件事，写了几遍

演示顺序：初始只显示引子；第一次点击展开 PA 侧单模块；第二次点击展开 HPAE 侧节点与底部对照句。

范围：对照基于 v5.1.0-Release 的 HDI sink 模块与当前主干的引擎节点层；行数为对应文件实测，其余为结构对照，不构成全维度评价。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/OpenHarmony-v5.1.0-Release/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L1094
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/OpenHarmony-v5.1.0-Release/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L1219
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/OpenHarmony-v5.1.0-Release/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L1469
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/OpenHarmony-v5.1.0-Release/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L3025
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/node/src/hpae_gain_node.cpp#L207

### P2 改动半径：加限幅，接新设备

演示顺序：初始只显示引子；第一次点击展开“加限幅”情景；第二次点击展开“接新设备”情景与底部对照句。

范围：情景为结构对照，未覆盖全部改动类型；老方案的支持面与生态成熟度是另一组维度，不在本页比较。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/OpenHarmony-v5.1.0-Release/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c#L2376
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/node/src/hpae_limiter_node.cpp
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L114
