from author import write
write(4,'PulseAudio时代，整个底座怎样协同','鸿蒙策略与流服务之下，PA流模型连接自定义音效和HDI适配',
'展示5.1旧方案全局职责，区分PA三方能力与鸿蒙已有适配。',
'''沿用刚才的分工，只把执行部分切回OpenHarmony5.1。应用和鸿蒙策略、流服务已经存在，普通播放由PaAdapterManager接入PA。服务端流通过libpulse的context和stream操作播放，PA的sink-input与sink模型组织输入和输出。
鸿蒙没有把全部行为交给一个外部黑盒。策略适配调用PA移动sink-input等接口落实路由；框架自定义hdi_sink模块包含场景取数、混音、音效调用和硬件适配。AudioServer还在audio_server进程内启动线程调用ohos_pa_main，因此不能把图画成所有PA都在独立进程。
普通主输出中，hdi_sink渲染侧生成数据，再用消息队列交给独立HDI写线程。DIRECT和VOIP当时还有ProAudioStreamManager等其他路径，我们这次不混用路径来比较。
PA提供成熟的流与输出组织机制，鸿蒙侧承接系统规则和设备集成。自研演进需要保持这些系统能力，同时重新组织处理执行。这张图既是下一页找成本的地图，也是后续比较时保留上层职责的基线。''',
[['node',363,245,552,74,'鸿蒙音频策略：焦点 / 路由 / 音量','purple',28],['arrow',466,326,466,375,'purple',True],['arrow',793,326,793,375,'purple',True],
 ['node',64,390,209,109,'应用接口','gray',28],['node',348,390,245,109,'流服务\nPaAdapterManager','navy',24],['node',668,390,245,109,'PA流 / sink模型\n框架hdi_sink模块','blue',24],['node',988,390,226,109,'HDI适配\n驱动 / 设备','teal',26],
 ['arrow',282,444,337,444],['arrow',603,444,658,444],['arrow',923,444,978,444],
 ['text',64,550,1145,45,'旧方案已经提供混音、音效、路由及设备集成',32,'navy',True],['text',64,609,1145,38,'演进重点：保持系统职责，改善执行结构与扩展方式',27,'blue',True]],
 keys=['oldentry','daemon','pa','oldpolicy','effectold','post','writer'],minutes=4,section='第二部分 · 旧方案与演进压力',prev='全局场景协同已经建立。',next='业务要求提高后，哪些成本值得优化？沿执行与维护边界逐一定位。',footer='5.1 Release固定基线；普通播放职责图，其他播放路径未展开',boundary='PA版本声明17.0另见附录；图不表示独立进程边界，旧方案能力不等于全部由PA上游实现。')
