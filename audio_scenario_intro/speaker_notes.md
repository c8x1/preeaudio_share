# 一首歌，三个操作 · 四页引入讲稿

用途：建立“简单操作背后需要多方协调”的认识，再进入架构讲解。主讲约 5 分钟，具体以试讲为准。主讲正文与转场供口述，演示提示不念，技术细节保留在备讲说明中。

## 1. 我们只做了三个动作

### 主讲正文

手机正在放歌。我们点一下暂停，再继续播放，然后把声音切到耳机。整个过程只有几个动作，我们通常不会觉得这有什么难的。

但我们对结果其实很挑剔：暂停时，不能突然“啪”一下；恢复时，声音不能猛地冲出来；切到耳机以后，音乐还得接着放。

这些要求都没有写在按钮上，却都需要底层替我们考虑。我们就从最简单的暂停开始，看看里面藏着哪些事情。

### 转场

按了暂停，为什么不能立刻把数据通路断掉？

### 演示提示（不念）

初始：依次指向暂停、继续播放、切到耳机。第一次点击：揭示每个动作背后的体验期待。第二次点击：提出底层需要考虑什么。

### 备讲说明（答疑时使用）

三项是体验目标，不是对每条设备路径的效果承诺。后续示例来自普通 HPAE 播放路径，波形与连线均为教学示意。

### 源码依据

- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1110
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L872

## 2. 暂停一下，为什么不能直接停？

### 主讲正文

先看上面的波形。直接把还没降到零的波形截断，幅度就会突然跳变，可能听到咔哒声。为了让声音平顺地停下来，可以先逐渐降低幅度，也就是淡出。

但淡出需要继续处理一小段音频。如果刚收到暂停就把输入断开，后面的淡出也做不完了。所以要先保留这一路连接，让淡出处理完成，再做断开和状态更新。

事情还没结束。如果暂停还没收尾，用户又点了继续播放呢？恢复后的声音也要平顺，之前留下的暂停操作还不能把刚恢复的播放再次停掉。底层需要在执行旧操作时确认当前状态。

你看，一个暂停按钮，已经牵涉声音怎么变化、连接什么时候断、先前的操作现在还能不能执行。这些安排都有具体的理由。

### 转场

再看切到耳机。这一次，连输出设备都换了，需要顾及的事情更多。

### 演示提示（不念）

初始：比较直接截断与逐渐淡出的波形。第一次点击：沿“保留连接、完成淡出、断开输入”说明先后理由。第二次点击：引入暂停未收尾时又恢复的情况。

### 备讲说明（答疑时使用）

Pause 通过 SetSessionFade 安排淡出，OnFadeDone 提交收尾请求并在执行时检查输入节点是否为 RUNNING。正常恢复在接通后先设置淡入，再按条件启动会话音效。缺少增益节点、设备未运行或 standby 等条件可能直接完成暂停。RUNNING 检查只支持这里的恢复后尚未再次暂停的例子，不代表任意多次交错均被解决。引擎完成淡出不等于扬声器同一时刻静音。

### 源码依据

- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1110
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1777
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1868
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919

## 3. 切到耳机，为什么不只是换个出口？

### 主讲正文

音乐还在播放，我们把声音切到耳机。听起来只是换个出口，底层却需要把正在工作的播放路径衔接起来。

首先，系统要确定这次该用哪个设备。设备由策略侧选择，引擎再把这一路播放交给目标设备。这里延续的是原来的播放，不能因为换了设备就把它当作一首新歌重新开始。

接着，还要适配目标设备的要求。比如，目标侧的采样率和每轮处理的数据量可能不同。连接换过去了，数据处理的方式也要跟上。

此外，耳机侧的处理链需要准备好，旧设备侧也需要收尾。什么时候接入，还要看当前是否在播放、目标是否允许连接。

这些事情共同影响切换时的声音。我们希望音乐尽量连续、少一些突变，但做完连接并不等于听感一定无缝，还要看设备和具体路径。

### 转场

还有一个要求：需要继续播放的时候，设备不能一直等控制操作处理完。

### 演示提示（不念）

初始：展示音乐从扬声器切到耳机的场景，以及“要做的事／为什么要做”。第一次点击：揭示目标选择、同一路播放交接。第二次点击：揭示参数适配、处理链衔接及体验目标。

### 备讲说明（答疑时使用）

MoveStreamSync 保留同一个输入节点并交接；目标侧 AddSingleNodeToSink 更新设备信息，按目标采样率与帧长调整处理粒度，再按 isConnect 和 RUNNING 状态连接。管理层映射更新不构成设备侧全部完成的同步栅栏。“继续播放”是会话延续的说明，不保证零间隙、不丢失任何样本或任意路径无缝。

### 源码依据

- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L872
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L114
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1181

## 4. 这些事情，还得在播放过程中完成

### 主讲正文

把刚才的场景放在一起看。上面是用户发来的控制动作，下面表示需要继续播放时的数据处理。这时候，设备还在等下一批音频数据。

引擎要一边处理声音，一边改变连接和状态。顺序不对，可能把刚恢复的输入又断开；处理拖得太久，后续供数也可能受到影响。缓冲能吸收一部分波动，但不能让设备一直等下去。

所以，前面那些额外步骤都有用处：让声音平顺地变化，让操作和当前状态一致，让新旧设备之间能够衔接。我们既要把事情做对，也要及时完成。

那这些工作该由谁来做？控制请求和音频处理怎样配合？切换设备时，怎样组织处理链？接下来，我们就带着这些问题看音频引擎的设计，再比较 PA 和 HPAE 的做法。

### 演示提示（不念）

初始：看到控制动作与持续的数据处理两条线。第一次点击：解释顺序和及时性对体验的影响。第二次点击：提出后续架构讲解要回答的问题。

### 备讲说明（答疑时使用）

上下两条线是职责示意，不表示具体线程数、线程映射或时长比例。供数延迟是否导致可闻断音取决于缓冲与设备路径，不给出未测量的时延阈值。PA 也具备状态控制和迁移能力，后续应比较相同路径下的执行组织，不能由这张图推出性能优劣。

### 源码依据

- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1110
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L872
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1777
