# HPAE 设计模式分享讲稿

对应 6 页图解 PPT，完整讲述约 12–14 分钟。

“现场讲述”可直接使用。“看图顺序”和“备答”供主讲人准备，不必逐字念。类名首次出现时结合图指一下，后面可以直接说“管理器”“父类”“流对象”。

## 第 1 页　简单工厂：产品接口与具体实现

约 2 分钟

**看图顺序**

先指下方三个具体类，再指向上方抽象类，最后看左侧调用者。

**现场讲述**

HPAE 里有普通播放、快速播放和 Offload 等不同实现。它们都要管理播放流，但内部处理方式不一样。我们先看一个问题：上层用这些对象的时候，需要把每一种实现都了解一遍吗？

看图下方，这三个框就是三种具体的 Manager。沿着线往上看，它们都继承了 IHpaeRendererManager。空心三角指向父类。父类把 Start、Process 这些操作定义下来，具体怎么启动、怎么处理，由下面各个实现负责。方法后面的“等于零”，在 C++ 里表示这是一个纯虚函数，需要派生类提供实现。

这样，上层就可以拿着同一种接口调用 Start，不用在每次调用前再判断一遍，这个对象到底是普通版还是 Fast 版。

那对象最开始由谁创建？看左边的 HpaeManager。它调用中间这个 CreateRendererManager，把输出端的信息传进去。函数选好具体实现，再以父类的智能指针返回。创建出来的对象有区别，调用者拿到的接口是统一的。

这里有个容易看错的地方：源码把创建函数放在 IHpaeRendererManager 自己身上，用 static 标了出来。因此，图上没有另外一个叫 Factory 的类。我们说它有工厂的作用，指的是这段代码集中承担了选择和创建对象的工作。

下面再看一次实际创建时，这个选择怎么发生。

**备答**

若被问到“这是什么工厂”：这里按简单工厂来讲。静态函数内部根据条件构造具体产品，并非通过 Creator 子类重写创建方法的 GoF Factory Method。图中省略了其他产品分支和上层基类。

**源码定位**

- [i_hpae_renderer_manager.h](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_engine/manager/include/i_hpae_renderer_manager.h)
- [i_hpae_renderer_manager.cpp](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_engine/manager/src/i_hpae_renderer_manager.cpp)
- [hpae_manager.cpp](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_engine/manager/src/hpae_manager.cpp)

## 第 2 页　简单工厂：一次调用如何选出产品

约 1 分半钟

**看图顺序**

从左到右走一遍，再沿右侧三条分支分别指示。

**现场讲述**

假设现在要为一个输出端建立播放 Manager。左侧的调用者先准备好 sinkInfo，里面包括设备类别、设备名等信息，然后交给中间的创建函数。

函数会检查这些信息。比如，符合图上的 primary_mmap 这一类条件，就创建 Fast Manager；符合 offload 相关条件，就创建 Offload Manager；前面那些分支都没有匹配上，最后走默认分支，创建普通 Manager。源码还有别的分支，这页只保留了三种。

所以，从调用者的角度看，它做的事情很简单：传入输出端信息，拿回一个能用的 Manager。至于里面调用哪个构造函数，集中在这里决定。

这会给后续修改带来什么方便？假设又增加了一种播放实现，我们可以到这个入口里补上选择条件，其他通过统一接口使用 Manager 的地方，就有机会沿用原来的调用代码。需要检查的创建逻辑集中在一处，比较容易找，也容易核对有没有漏掉某种类型。

当然，这个创建函数本身还是要维护，分支也可能继续增加。工厂模式并没有让变化消失，它只是让创建对象这件事有一个明确的落点。

这一步发生在建立 Manager 的时候。Manager 建好之后，上层再调用它提供的流管理接口。接下来就看这些接口怎样和 Service 接起来。

**备答**

primary_mmap 只是 Fast 分支的一个条件，源码还包括其他 mmap、VoIP 等类别。不要据此推断应用每次点击播放都会重新创建 Manager，也不要把创建分支当成设备切换的完整流程。

**源码定位**

- [i_hpae_renderer_manager.cpp](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_engine/manager/src/i_hpae_renderer_manager.cpp)
- [hpae_manager.cpp](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_engine/manager/src/hpae_manager.cpp)

## 第 3 页　适配器：两层包装连接两套接口

约 2 分半钟

**看图顺序**

先看左右两组继承关系，再从左下角顺着蓝色折线走到右侧。

**现场讲述**

Service 这一侧已经有一套流管理接口。比如，启动播放用的是左上角的 StartRender，传进去一个 streamIndex。HPAE 引擎这一侧，Start 接收的则是流类型和 sessionId。两边的接口长得不一样，需要有人把它们接起来。

先看左边的继承关系。HpaeAdapterManager 实现了 IStreamManager，所以 Service 可以继续按 IStreamManager 的方式使用它。这里的关键是，它对上层提供什么接口，以及它在内部怎样完成这个接口要求的操作。

我们跟着一次启动走。调用 StartRender 以后，适配管理器先根据 streamIndex，在自己的流表里找到对应对象，再调用这个对象的 Start。图中间的蓝色折线表示，它持有并使用的是 IRendererStream 接口。

运行时，这个接口背后的对象可以是下面的 HpaeRendererStreamImpl。它收到 Start，再向右调用 HPAE 的管理接口，把播放类型和会话 ID 传进去。这样，Service 发出的一次启动操作，就沿着这两层对象传到了引擎。

这个例子里，适配工作分在管理器和流包装对象两层：管理器接住上层的流管理调用，流对象再衔接引擎操作。以后读源码时，顺着这条线看，就能分清每一层负责哪一段。

这种安排的用处，是把两套接口之间的差异收在接入层。Service 不需要直接理解引擎的全部对象结构，引擎接口的具体用法也有地方集中处理。这里讲的适配器，主要就是这个作用。

接口接好以后，声音进入引擎内部。下一页看单个处理节点里的代码怎么复用。

**备答**

图中省略了校验、错误处理和其他流操作。streamIndex 与 sessionId 在这里分别按接口参数讲解，不额外假设它们必定是两套不同数值。HpaeAdapterManager 没有直接包办所有引擎调用，启动主线经过流包装对象。

**源码定位**

- [hpae_adapter_manager.h](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_service/server/include/hpae_adapter_manager.h)
- [hpae_adapter_manager.cpp](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_service/server/src/hpae_adapter_manager.cpp)
- [hpae_renderer_stream_impl.h](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_service/server/include/hpae_renderer_stream_impl.h)
- [hpae_renderer_stream_impl.cpp](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_service/server/src/hpae_renderer_stream_impl.cpp)

## 第 4 页　模板方法：父类留出一个算法扩展点

约 2 分钟

**看图顺序**

先沿右侧流程往下讲，到中间绿色步骤时，再指向左下方两个子类。

**现场讲述**

增益节点负责调音量，混音节点负责把几路输入合到一起。它们做的运算不同，但处理一块数据时，都有一些共同的步骤。

先看右边：取到上游数据，调用处理算法，再把结果写出去。这段顺序，在 HpaePluginNode 的 DoProcess 里已经组织好了。

中间这一步，父类只规定调用 SignalProcess，没有把具体算法写死。看左边的类图，这个函数后面也有“等于零”，表示父类要求派生类去实现它。增益节点在这里写增益计算，混音节点在这里写混音计算。

运行时，如果当前对象是增益节点，父类流程走到 SignalProcess，就会执行增益节点提供的实现；如果当前对象是混音节点，就会执行混音节点的实现。公共流程相同，具体运算由对象自己的类型决定。

这就是模板方法的做法：父类把一段流程组织好，再把其中需要变化的步骤留给子类。这里说的“模板”，是流程上的模板，和 C++ 的 template 关键字没有关系。

这种分工对维护代码很有用。比如只想调整增益的计算方式，首先去看 HpaeGainNode 的 SignalProcess，而不必先改整套取数和输出流程。反过来，公共流程如果需要维护，也有一个相对集中的位置。

图上画的是输入正常、处理启用时的这一条分支。实际代码还有旁路、静音等处理，也有节点会重写 DoProcess。我们用这几个类来理解它的复用方式。

单个节点看清楚了，下一页把几个节点放到一起。

**备答**

父类的 SignalProcess 为 protected 纯虚函数，图中用 # 表示受保护成员，+ 表示公开成员。若被问到和策略模式的区别：本例通过继承和重写提供变化步骤，适合讲模板方法。

**源码定位**

- [hpae_plugin_node.h](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_engine/node/include/hpae_plugin_node.h)
- [hpae_plugin_node.cpp](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_engine/node/src/hpae_plugin_node.cpp)
- [hpae_gain_node.h](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_engine/node/include/hpae_gain_node.h)
- [hpae_mixer_node.h](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_engine/node/include/hpae_mixer_node.h)

## 第 5 页　组合：Cluster 把子图封装成一个节点单元

约 2 分钟

**看图顺序**

从顶部共同基类看起，再看左侧 Cluster 和中间“持有”的箭头。

**现场讲述**

一条音频输入进来以后，通常要经过好几步处理。比如格式要对齐，音量要调整，多路输入最后还要混在一起。如果上层直接管理每一个小节点，就得了解它们之间的连接关系。节点一多，管理起来会比较细碎。

HPAE 在这里用了 Cluster，把相关的节点放在一个处理单元里组织。

看图左边的 HpaeProcessCluster。它自己也提供 Connect、DoProcess、GetOutputPort 这些接口。对外部来说，可以连接这个处理单元、触发它处理，再取得输出。

但它内部并非只有一个算法。沿着中间“持有”这条线看，它还管理着增益、混音等具体节点，实际代码里还有格式转换、响度增益和音效相关对象。这些节点怎么组织、怎样连接，由 Cluster 内部负责。

再往图上方看，Cluster 和普通处理节点最终都有 HpaeNode 这个共同基类。一个小节点能够参与处理，组合了多个小节点的处理单元，也能以节点的形式接到更大的结构里。我们在这里讲组合模式，主要看这个关系。

它让上层可以在更大的粒度上管理处理图。上层关心接哪个 Cluster，Cluster 再负责自己内部的节点。至于内部增加哪一步、某个场景怎样连接，就有一个相对集中的管理位置。

这个实现还有自己的细节，例如一些输出接口会直接转交给内部节点。理解到这一层就够了：Cluster 对外提供节点式的用法，对内组织一组节点。

最后一页看一个动态问题：正在处理音频时，启动请求怎样交给工作线程执行。

**备答**

图中省略 OutputNode、InputNode 等中间基类。成员由 shared_ptr 和 map 等结构持有，图用成员持有关系表达，没有宣称严格的独占生命周期组合。此例体现组合思想和子图封装，不能将全部处理拓扑概括为标准树形 Composite。

**源码定位**

- [hpae_node.h](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_engine/node/include/hpae_node.h)
- [hpae_process_cluster.h](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_engine/node/include/hpae_process_cluster.h)
- [hpae_process_cluster.cpp](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_engine/node/src/hpae_process_cluster.cpp)

## 第 6 页　命令：提交请求与执行请求分开发生

约 2 分半钟

**看图顺序**

先说明时间从上往下，再按 ① 到 ④ 走。讲到队列时停一下，说明队列本身没有执行线程。

**现场讲述**

点下播放以后，调用最终会进入 HpaeRendererManager 的 Start。这个函数接到请求时，会先把接下来要做的启动操作封装起来。

我们按图上的时间顺序往下看。第一步，调用线程准备一个 lambda，里面保存这次要操作的 sessionId，以及启动时需要执行的逻辑，然后把它放进请求队列。第二步，通知工作线程，有事情需要处理了。

中间这个队列只负责保存请求。请求放进去以后，真正执行它的，还是右边的音频工作线程。

工作线程被唤醒后，先走 HandleMsg。在这个过程中，它调用队列的处理函数，执行已经提交的 lambda。启动相关的状态更新、输入连接等操作，就在这个阶段发生。处理完消息，再走下面的 Process，处理音频数据。

所以，一次启动可以分成两个时刻：调用线程提交请求，工作线程稍后执行请求。我们把“一次要做的操作”和“操作所需的参数”包装在一起，再交给另一个执行位置，这里就体现了命令模式的用法。

教科书里可能会为命令定义一个类，再给它一个 Execute 方法。HPAE 这里用的是函数对象，Request 的类型是 std::function<void()>，lambda 就能把这件事表达出来。读这段代码时，要看它怎样保存和传递操作。

这也解释了一个调试时要注意的现象：Start 返回成功，和工作线程已经完成启动，是两件需要分别确认的事。如果出现状态没跟上，可以继续沿着入队、通知、消费这几个位置查。

这几页回头连起来看：创建对象时看工厂，跨层接入时看适配，单个节点里看模板方法，多节点组织看 Cluster，控制请求交接时看命令。再遇到这些类名，就能大致判断它们在处理哪一类问题。

**备答**

图是调用顺序示意，不表达真实耗时或独立的队列线程。Start 的返回路径不等于异步操作完成，初始化检查和队列容量等仍可能影响执行。工作循环先 HandleMsg 再 Process，不能据此推断整个引擎只有一个线程，也不能保证每个命令一定及时完成。

**源码定位**

- [hpae_renderer_manager.cpp](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_engine/manager/src/hpae_renderer_manager.cpp)
- [hpae_signal_process_thread.cpp](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_engine/manager/src/hpae_signal_process_thread.cpp)
- [hpae_no_lock_queue.h](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_engine/utils/hpae_no_lock_queue.h)
- [hpae_no_lock_queue.cpp](https://gitcode.com/openharmony/multimedia_audio_framework/blob/75806a3e619d76a98e02b4984f08da8b0727d441/services/audio_engine/utils/hpae_no_lock_queue.cpp)
