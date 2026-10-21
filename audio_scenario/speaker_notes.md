# 一首歌，三个操作 · 讲稿

六页主讲，按点击顺序揭示。正文为口播语言；演示顺序、范围与源码依据见文末备讲附录。时长需以实际试讲为准。

## 1. 一首歌，三个操作

先做三个动作：暂停、恢复播放、切到耳机。每个都是一次点击，屏幕立刻响应，声音立刻跟上，谁都觉得理所当然。

现在把最直接的实现写出来。暂停，就是把数据流立即截断；恢复，就是原样接回；切耳机，就是从扬声器这边拔下来、插到耳机那边。真这么做会听到什么？暂停是一声“啪”，波形在半幅上被切断；恢复是一声“bang”，等着的数据按全音量冲出来；切耳机，歌断一拍。

真实引擎这三步一步都不敢做。接下来三页，把这三个朴素做法逐个推翻，看引擎实际做了什么。

## 2. 暂停时，先淡出，再断开

暂停为什么会“啪”？切断的那一刻，波形幅度不是零。半幅上切一刀，扬声器收到一个突变，就是一声爆音。所以暂停的第一步不是切断，是降音量：增益逐渐降到零，让声音干净地淡出去。

看这条时间轴。暂停请求提出后不是立刻执行，先等设备侧。淡出开始之后，输入线还必须连着：淡出本身要靠处理链继续跑，先拆线，淡出就没法完成。增益一路降到零，淡出结束，收尾再排一次队等执行：暂停音效、断开输入、更新状态，都在这一步做。

所以“声音没了”和“线拆了”是两个时刻，中间隔着一个等待窗口。记住这个窗口，下一页它就有用了。

## 3. 已经恢复播放，旧的暂停还会生效吗？

上一页的窗口还开着：淡出结束后的收尾还在排队等执行。这时候用户的手比队列快，已经点了恢复。于是队列里排着两条：恢复在前，旧的暂停收尾在后。

按顺序执行。恢复先跑：状态回到正在播放，输入连着，淡入也安排上了。然后轮到旧的收尾。它如果不看状态、照原计划办，就会暂停音效、拆掉输入、把状态写回暂停。用户看到的是：我明明点了恢复，界面也显示在播，却没有声音。

所以收尾动手前先查一眼：现在是不是已经在播放？是，这次收尾就地结束，不碰音效，不碰输入。一句“动手前先看当前状态”，把这次险情救了回来。

## 4. 淡入为什么要先于音效启动？

恢复这边也有同一个坑，方向相反。恢复时缓冲里往往已经躺着数据。处理链接通之后，如果先启动会话音效、等启动完成再设置淡入，麻烦就来了：音效启动不是瞬间完成的，这段窗口里，等着的数据按全增益处理。听到的不是淡入，是“bang”一下爆音。

实际顺序反过来：接通之后立刻安排淡入，然后才启动音效。启动再慢，增益也已经被淡入曲线按住了。

注意这两行的比法：同一条时间轴，只差两个动作的先后。先后差一步，爆音还是淡入，就决定在这一步上。

## 5. 切到耳机，哪些东西变了？

第三个动作切耳机，看起来最像“拔了插过去”，实际最麻烦。设备策略已经选定耳机，我们只看引擎怎么执行。

先说朴素做法：把这路音乐停掉，在耳机侧重开。能响，但丢的不只是一根连接：缓冲里的数据、当前的播放状态，全部重来，这路音乐的连续性断了。所以引擎的做法是交接：旧设备侧摘除连接，但握着同一个输入节点交出去。音乐 A 还是那个音乐 A。

目标侧接手之后还有两件事。一是改参数：设备信息改成耳机，处理粒度按目标的采样率和帧长调整，不同设备一轮吃的数据量不一样，不调，数据就和设备对不上拍。二是接链：目标侧处理簇就绪、条件满足，把正在播放的会话接入耳机侧处理链，归属随之更新。

摘旧连接、调参数、接新链，三个阶段，一个都不能省。

## 6. 再看这三个操作

回到这一路音乐，把三个操作放在一起说。

暂停：让增益降完再拆输入，因为时间不能跳过去。恢复：旧请求执行前先看新状态，因为请求会排队、新旧会交错。切耳机：交接同一个会话、接入目标链，因为设备参数各不相同，而音乐必须是同一路。

还有一条底线压在所有这些上面：耳朵什么都不能听见。不能有爆音，不能有全音量冲出来的那一声，不能断拍，不能状态错乱。

时间、队列、状态、设备差异，再加耳朵，五样都得交代。三个操作背后那些复杂性，就是这五样换来的代价。

五样都交代完，下一个问题自然浮出来：这么多事同时发生，线程、队列、缓冲该怎样组织？这正是下一部分比较 PA 和 HPAE 要回答的。

# 备讲附录

以下内容不讲，供试讲与答疑准备。

### P1 一首歌，三个操作

演示顺序：初始只显示数据链；第一次点击显示暂停与恢复的朴素做法和会听到的声音；第二次点击显示切耳机的朴素做法与结尾句。

范围：处理链为简化示意；“会听到”为示意性描述，未做设备实测。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1110
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L872

### P2 暂停时，先淡出，再断开

演示顺序：先看两种波形与暂停请求；第一次点击揭示淡出、完成排队和断开；第二次点击强调两个时刻。

范围：正常淡出路径；波形与时间均为示意，不代表设备实测。若缺少增益节点、设备未运行或处于相应旁路条件，实现也允许直接完成，本页专讲正常淡出路径。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1110
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1777
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1868

### P3 已经恢复播放，旧的暂停还会生效吗？

演示顺序：初始只显示待执行请求及音乐 A；第一次点击执行恢复；第二次点击执行旧的收尾并显示检查结果与不检查的后果。

范围：一种请求交错；不表示每次快速点击都能触发。这里只讨论恢复后尚未再次暂停的情况；描述的是引擎执行顺序，不把界面点击等同于可任意并发的客户端调用。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1777

### P4 淡入为什么要先于音效启动？

演示顺序：先展示设置偏晚的风险窗口；点击后展示实际顺序与增益示意。

范围：上行为假设的错误顺序，下行为实际顺序；增益曲线仅示意，不表达淡入时长。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919

### P5 切到耳机，哪些东西变了？

演示顺序：先看切换前；第一次点击看交接、参数调整与朴素做法的代价；第二次点击看目标连接与归属变化。

范围：普通迁移路径示意；交接中不承诺零间隙，接入成功也不等于声学输出已稳定。目标不可用和状态变化会走其他分支。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L872
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L114
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_manager.cpp#L1181

### P6 再看这三个操作

演示顺序：先回到同一路音乐；第一次点击回顾三处具体动作；第二次点击收出五样约束。

范围：不把上述能力说成 HPAE 独有，也不从结构图推导未测量的时延或功耗幅度。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1110
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1777
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L872
