# 一首歌，三个操作 · 讲稿

十一页主讲，按点击顺序揭示。正文为口播语言；演示顺序、范围与源码依据见文末备讲附录。时长需以实际试讲为准。

## 1. 一首歌，三个操作

先做三个动作：暂停、恢复播放、切到耳机。每个都是一次点击，屏幕立刻响应，声音立刻跟上，谁都觉得理所当然。

现在把最直接的实现写出来。暂停，就是把数据流立即截断；恢复，就是原样接回；切耳机，就是从扬声器这边拔下来、插到耳机那边。真这么做会听到什么？暂停是一声“啪”，波形在半幅上被切断；恢复是一声“bang”，等着的数据按全音量冲出来；切耳机，歌断一拍。

真实引擎这三步一步都不敢做。接下来，把这三个朴素做法逐个推翻，先看引擎做了什么，再看它把保证写在了哪里。

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

摘旧连接、调参数、接新链，三个阶段，一个都不能省。至于这些动作由谁、在哪条线程上执行——下一页见。

## 6. 这些请求，谁来执行？

前四页反复出现两个词：“排队”和“等待执行”。现在看它们的物理载体。

每个控制动作——暂停、恢复、切设备，连淡出完成后的收尾——都被打包成一个小任务，丢进同一个队列。执行它们的是一条专用线程：被唤醒后，先把队列排空，把该办的控制动作办完；然后跑一轮音频处理。办完再睡，等下一次唤醒。

这个安排有个直接好处：改处理图的人，就是跑数据的人。同一条线程串行，队列不需要锁，图变更不会跟数据处理撞车。

还有一件事值得看清楚：淡出完成不是靠定时器猜的。处理链在真实数据上一帧帧把增益降下来，降到零的那一刻，就地发回一个“淡出完成”。这个回调本身也是一个请求，排到队尾等执行。前面说“声音没了”和“线拆了”是两个时刻，中间隔的就是这一趟排队。

量级也有数：短淡出按 5 毫秒设计，默认淡出在一轮数据之内完成。都是毫秒级的事，但一步都省不掉。

接下来三页，用这套角色把一次暂停、一次恢复交错、一次切耳机，完整走一遍时序。

## 7. 一次暂停，从头到尾

把上一页的模型跑一遍：一次暂停，从头到尾。

应用发出暂停请求。渲染管理器不自己动手，把请求丢进队列。信号处理线程被唤醒，先排空队列：执行暂停请求——不碰连接，只在增益节点上挂一个淡出标志，会话状态改成“暂停中”。

然后线程照常跑音频处理。处理链看到淡出标志，就在真实数据上逐帧把增益降下来。降到零的那一刻，处理链就地发回“淡出完成”。

注意这个回调的去向：它回到渲染管理器，又变成一个请求进队列。线程下一轮排空队列时执行收尾：查状态、停音效、断输入、把状态改成“已暂停”，最后把状态回调给应用。

一次暂停，两个请求，中间夹着一段毫秒级的淡出。前面讲的时间轴，落到角色上就是这一条链。

## 8. 恢复抢先一步，时序会怎样？

同一套角色，换个剧本：收尾还在队里，用户已经点了恢复。

恢复请求进来，也进队列——排在了旧收尾前面。线程先执行它：状态改成“运行中”，接上输入，挂好淡入，启动音效，处理链带着淡入继续跑。

然后才轮到那条旧的暂停收尾。它执行的第一件事是查状态：已经在运行？好，这次收尾就地结束，不碰音效，不碰输入。

应用最终收到的状态回调是“运行中”。一次交错，被两条小规则消化：先到先执行，动手前看状态。

## 9. 切到耳机：三方接力

切耳机是三方接力：设备策略、管理器、两侧渲染。

策略已经选定耳机。管理器向旧设备侧发起迁移。旧侧摘除这路音乐的连接，但输入节点带着自己的状态保留下来，交还给管理器——音乐 A 还是那个音乐 A。

管理器把节点交给目标侧。目标侧接手后：设备信息改成耳机，处理粒度按目标的帧长和采样率调整，处理簇就绪之后，只有正在运行的会话才接进新链。

最后归属更新，迁移完成。节点不换人，参数跟设备走——这就是“同一路音乐”在代码里的样子。

## 10. 三个保证，落在代码的哪里？

把三个保证落到代码上看，每个都不大。

暂停：渐变不靠外部定时器，挂在增益节点的状态机上，处理链每跑一轮就顺便执行一次，在真实数据上把增益从一降到零。做完，才回调收尾。

恢复：恢复请求执行的第一步，就是把会话状态改成“运行中”，之后才接输入、挂淡入、启动音效。旧收尾执行时的第一行就是检查这个状态：已在运行，直接返回，不碰音效不碰输入。一次险情，一行检查。

淡入时机：接通之后立刻挂淡入，然后才启动会话音效。代码注释写得直白：音效启动要花时间，预缓冲的数据会在“接通到挂淡入”的窗口里按全音量漏出去。先挂淡入，窗口就封住了。

切耳机：输入节点带着自己的状态交接过去；目标侧拿到节点，先把设备信息改成自己，按自己的帧长和采样率调整处理粒度，最后只有“正在运行”的会话才接进新链。

一个状态标志、一行状态检查、一个先后顺序、一次参数调整。复杂性摊开看，就是这些小东西的叠加。

## 11. 再看这三个操作

回到这一路音乐，把三个操作放在一起说。

暂停：让增益降完再拆输入，因为时间不能跳过去。恢复：旧请求执行前先看新状态，因为请求会排队、新旧会交错。切耳机：交接同一个会话、接入目标链，因为设备参数各不相同，而音乐必须是同一路。

还有一条底线压在所有这些上面：耳朵什么都不能听见。不能有爆音，不能有全音量冲出来的那一声，不能断拍，不能状态错乱。

时间、队列、状态、设备差异，再加耳朵，五样都得交代。这一部分看到的，就是 HPAE 交的答卷：一条线程、一个队列，和几个落在具体位置的小保证。

那么换一个引擎，同样的三个操作会是什么样？PA 是怎么组织这些事情的，跟这套做法差别在哪、各自换来什么？这就是下一部分的内容。

# 备讲附录

以下内容不讲，供试讲与答疑准备。

### P1 一首歌，三个操作

演示顺序：初始只显示数据链；第一次点击显示暂停与恢复的朴素做法和会听到的声音；第二次点击显示切耳机的朴素做法与结尾句。

范围：处理链为简化示意；“会听到”为示意性描述，未做设备实测。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1110
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L872

### P2 暂停时，先淡出，再断开

演示顺序：先看两种波形与暂停请求；第一次点击揭示淡出、完成排队和断开；第二次点击强调两个时刻。

范围：正常淡出路径；波形与时间均为示意，不代表设备实测。若缺少增益节点、设备未运行或处于相应旁路条件，实现也允许直接完成，本页专讲正常淡出路径。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1110
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1777
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1868
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/node/src/hpae_gain_node.cpp#L253

### P3 已经恢复播放，旧的暂停还会生效吗？

演示顺序：初始只显示待执行请求及音乐 A；第一次点击执行恢复；第二次点击执行旧的收尾并显示检查结果与不检查的后果。

范围：一种请求交错；不表示每次快速点击都能触发。这里只讨论恢复后尚未再次暂停的情况；描述的是引擎执行顺序，不把界面点击等同于可任意并发的客户端调用。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1777

### P4 淡入为什么要先于音效启动？

演示顺序：先展示设置偏晚的风险窗口；点击后展示实际顺序与增益示意。

范围：上行为假设的错误顺序，下行为实际顺序；增益曲线仅示意，不表达淡入时长。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/node/src/hpae_gain_node.cpp#L284

### P5 切到耳机，哪些东西变了？

演示顺序：先看切换前；第一次点击看交接、参数调整与朴素做法的代价；第二次点击看目标连接与归属变化。

范围：普通迁移路径示意；交接中不承诺零间隙，接入成功也不等于声学输出已稳定。目标不可用和状态变化会走其他分支。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L872
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L114
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_manager.cpp#L1181

### P6 这些请求，谁来执行？

演示顺序：初始只显示线程循环；第一次点击显示请求队列与流向；第二次点击显示免锁原因、淡出闭环与量级。

范围：队列与线程按引擎结构示意；线程唤醒后先排空请求再跑一轮处理为源码逻辑，未做时延测量。短淡出常数见增益节点源码。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1755
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_signal_process_thread.cpp#L83
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/node/src/hpae_gain_node.cpp#L42

### P7 一次暂停，从头到尾

演示顺序：初始显示角色与生命线；第一次点击走完请求到淡出；第二次点击走完回调、收尾与状态回调。

范围：时序按源码调用关系简化：上层调用到渲染管理器的中间环节合并，线程执行与处理链的帧级细节合并；不表示实测时延。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1110
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1755
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/node/src/hpae_gain_node.cpp#L232
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1777

### P8 恢复抢先一步，时序会怎样？

演示顺序：初始显示队列里的旧收尾；第一次点击恢复请求入队并执行；第二次点击旧收尾执行检查并返回。

范围：一种请求交错；不表示每次快速点击都能触发。时序按源码调用关系简化。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1755
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1777

### P9 切到耳机：三方接力

演示顺序：初始显示三方角色；第一次点击旧侧摘除并交接节点；第二次点击目标侧接手、调参接入并更新归属。

范围：普通迁移路径；目标不可用与状态变化走其他分支。时序按源码调用关系简化。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_manager.cpp#L1065
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L872
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_manager.cpp#L1181
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L114

### P10 三个保证，落在代码的哪里？

演示顺序：第一次点击显示暂停与恢复的落点；第二次点击显示淡入时机与切耳机的落点。

范围：行为与代码位置对应源码树当前主干；描述的是这一路径的行为，不构成对其他版本或分支的描述。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/node/src/hpae_gain_node.cpp#L207
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/node/src/hpae_gain_node.cpp#L232
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L919
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1777
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L114

### P11 再看这三个操作

演示顺序：先回到同一路音乐；第一次点击回顾三处具体动作；第二次点击收出五样约束。

范围：不把上述能力说成 HPAE 独有，也不从结构图推导未测量的时延或功耗幅度。

依据：
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1755
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L1110
- https://gitcode.com/openharmony/multimedia_audio_framework/blob/0d073de5a30f33ab6716d9abd481d76eca843741/services/audio_engine/manager/src/hpae_renderer_manager.cpp#L872
