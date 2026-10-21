# 一首歌，三个操作 · 修订讲稿

六页主讲，按点击顺序揭示。时长需以实际试讲为准。

## 1. 一首歌，三个操作

先看这一条线。音乐 A 是同一路播放会话，数据已经在缓冲中等待处理，经过增益和音效后送往扬声器。这里不展开全部节点，只保留后面会改变的部分。

第一次点击：暂停和恢复首先涉及增益，但还会改变输入连接和播放状态。暂停需要让声音平顺地停下来，恢复则要让新的播放状态不被旧操作破坏。

第二次点击：切耳机改变了输出设备，也改变了会话应该接入的处理链。接下来从暂停开始，看这些动作怎么落实。

演示顺序：初始显示一条数据链；第一次点击显示暂停与恢复；第二次点击显示设备切换。

范围：实线表示数据；虚线表示控制。处理链为简化示意。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1110
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L872

## 2. 暂停时，先淡出，再断开

直接截断一段幅度不为零的波形，可能产生突变。先逐渐降低增益，可以减轻这种突变。看下面的时间轴：暂停请求提出之后，先等待设备侧执行。

第一次点击：开始淡出时，输入连接必须保留，否则后面的处理无法完成。增益逐渐下降，淡出完成后的处理再次进入请求队列。等这个请求执行，才暂停相关音效、断开输入、更新会话状态。图上的“正在暂停”对应设备侧会话状态，不是用户界面的状态。

第二次点击：声音的渐变结束和输入连接拆除不是一个时刻。理解这个等待窗口，下一页的恢复交错就不神秘了。若缺少增益节点、设备未运行或处于相应旁路条件，实现也允许直接完成，本页专讲正常淡出路径。

演示顺序：先看两种波形与暂停请求；第一次点击揭示淡出、完成排队和断开；第二次点击强调两个时刻。

范围：正常淡出路径；波形与时间均为示意，不代表设备实测。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1110
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1777
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1868

## 3. 已经恢复播放，旧的暂停还会生效吗？

上一页中，淡出完成后的收尾需要等待执行。本页选择一种具体交错：恢复请求已经排在前面，淡出完成请求随后加入。队列左侧是下一条要执行的请求。这里描述的是引擎执行顺序，不把界面点击等同于可任意并发的客户端调用。

第一次点击：恢复请求先执行，会话回到正在播放，输入相连，恢复所需的淡入已安排。

第二次点击：旧的暂停收尾终于执行。假如不检查状态，它就会暂停相关音效、拆掉输入，并写回暂停状态。实际处理会先检查当前是否已经恢复运行；如果是，就结束本次收尾，保留当前通路。

这个检查针对图示交错。它不是给所有旧事件加了代次号，也不能据此宣称任意多次暂停恢复的交错都由这一个判断解决。

演示顺序：初始只显示待执行请求及音乐 A；第一次点击执行恢复；第二次点击执行旧的收尾并显示检查结果。

范围：一种请求交错；不表示每次快速点击都能触发。这里只讨论恢复后尚未再次暂停的情况。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1777

## 4. 淡入为什么要先于音效启动？

只知道“恢复时会淡入”还不够，设置的时机也影响声音。先看上行假设：处理链已经接上，应用又预先准备了数据。如果先启动会话音效，等启动完成才设置淡入，这段窗口里就可能有数据按全增益输出。上行是用来说明风险的反事实，不是在描述某个历史版本。

点击后看下行：实际顺序是在接入之后立即安排淡入，然后才启动会话音效。实现注释明确解释了预缓冲数据和音效启动耗时带来的窗口。上下行用同一时间方向比较先后，增益曲线只是说明淡入已经安排，不能读成淡入在音效启动前一定完成。

演示顺序：先展示设置偏晚的风险窗口；点击后展示实际顺序与增益示意。

范围：上行为假设的错误顺序，下行为实际顺序；增益曲线仅示意，不表达淡入时长。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919

## 5. 切到耳机，哪些东西变了？

第一幅是切换前：音乐 A 接到扬声器侧处理链，管理层把它归属到扬声器。设备策略已经选定耳机作为目标，我们只看引擎怎样执行迁移。

第一次点击：旧设备侧移除输入会话，但持有同一个输入节点并将其交接出去。音乐 A 的身份延续。目标侧接收后，更新设备相关信息，并依据目标采样率和处理帧长度调整处理粒度。帧粒度可以理解为一轮处理多少音频数据，不是歌曲的播放进度。不同设备的具体数值依配置而定，本页不编造固定参数。

第二次点击：目标侧创建或接入相应处理簇，符合连接条件且会话处于运行状态时，接入耳机侧处理链。管理层更新会话映射。这些动作跨越异步交接，图只表达阶段，不把映射更新画成所有设备动作完成的同步栅栏。目标不可用和状态变化会走其他分支。

演示顺序：先看切换前；第一次点击看断开和参数调整；第二次点击看目标连接与归属变化。

范围：普通迁移路径示意；交接中不承诺零间隙，接入成功也不等于声学输出已稳定。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L872
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L114
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1181

## 6. 再看这三个操作

回到第一页的音乐 A。缓冲、增益和设备链还是这几个对象。第一次点击：暂停要求让增益变化做完再拆输入；恢复要求旧请求执行时重新看状态；切设备要求同一个会话进入目标设备处理链。

第二次点击：这些动作都要及时完成，背后的线程、队列以及缓冲该怎样安排？这才是下一部分比较 PA 和 HPAE 的具体问题。我们将看控制请求经过哪些交接、音频处理在哪个线程完成，以及设备迁移如何组织节点生命周期。这里不把上述能力说成 HPAE 独有，也不从结构图推导未测量的时延或功耗幅度。

演示顺序：先回到同一路音乐；第一次点击回顾三处具体动作；第二次点击提出线程与队列问题。

范围：下一部分：在相同普通输出路径下，对比 PA 与 HPAE 的执行组织。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1110
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1777
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L872
