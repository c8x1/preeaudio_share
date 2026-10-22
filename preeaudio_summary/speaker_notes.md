# 总结页讲稿

最后回到 PreeAudio 引擎本身，把今天的内容收在三个设计选择上。

第一，是怎样组织处理。格式转换、增益、混音和音效可以由不同节点承担，再通过 Cluster 把相关节点组合起来。这样，算法有自己的处理职责，外部也能按一组相关处理来管理管线。前面讲的模板方法和组合思想，都是在帮助这类处理复用和组织。

第二，是怎样把控制和持续处理衔接起来。Manager 管理流、连接和运行状态。我们看到的普通有处理线程路径，会把 Start 等操作封装为请求，提交到相应工作上下文，工作循环先处理消息，再处理音频数据。请求提交和实际执行是两个时刻；整个引擎也不能因此理解成只有一条线程。

第三，是怎样管理运行中的变化。暂停涉及淡出与收尾，恢复需要结合当前状态处理；迁移到新设备，还要调整目标输出、处理参数以及连接。它们都会影响正在工作的处理管线，因此不能只把引擎理解成依次调用几个算法的函数集合。

把它和 PulseAudio、JACK、PipeWire 放在一起看，重点是处理单元怎样划分、计算由谁推动、状态变化怎样进入执行过程。不同方案有不同的设计侧重，实际表现还要结合路径和测量条件判断。

所以，理解 PreeAudio，需要把处理图、执行循环和状态变化放在一起看。对算法同学来说，这能帮助找到计算单元放在哪里、输入输出怎样约定；对 AI Infra 同学来说，可以沿着运行上下文、资源组织和动态更新去理解它的系统设计。

资料来源：OpenHarmony 固定源码快照 3a2688e805df970739e3b0cebf9cc05d8cb24e9b；沿用主分享的核验范围。普通工作线程路径及启停、迁移均有条件分支，页面为职责归纳，不承诺任意路径无缝切换。
https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_renderer_manager.cpp
https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/manager/src/hpae_signal_process_thread.cpp
https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_engine/node/src/hpae_process_cluster.cpp
