from author import write
write(11,'一个会话接入音效，哪些逻辑能复用','在局部连接中插入SessionEffect，复用已有转换、增益与混音',
'以源码确认的可选会话音效功能解释新增需求的组合接入，具体展示复用和约束。',
'''假设需求是给一个会话启用独立音效，而其他已有处理职责继续工作。这里使用公开代码已实现的能力作例子，不将它包装为未经提供的内部项目故事。
当前ProcessCluster::CreateSessionEffectNode先检查该会话是否已绑定音效，确认Converter和LoudnessGain节点存在，再创建会话音效节点并初始化实例。初始化失败时返回错误；成功后才把Converter到LoudnessGain之间的原连接拆开，改成Converter接SessionEffect，SessionEffect接LoudnessGain，最后登记到会话映射。
这样，已有转换、增益和后续Mixer职责继续复用，新能力集中在一个处理单元及其连接，而不必重写整条通路。Connect函数也会根据是否存在SessionEffect选择前驱。相较旧集成把场景处理放在HDI专用路径函数内，新模型提供了明确的局部组合位置。这里不声称存在同功能跨版本代码量对比。
组合仍然有契约。当前会话音效相关输入要求48kHz双声道，还要管理初始化、启动、Flush、销毁与设备迁移状态。这些约束需要算法与框架一起对齐。节点化让接口和责任更明确，并不让任意算法可以无条件插入。
下页把这个局部能力放回策略、服务和设备变化的全过程，检查自研创新究竟服务于谁。''',
[['text',64,247,1150,42,'未启用会话音效',28,'gray',True],['node',64,305,270,78,'Converter','blue',27],['node',858,305,356,78,'LoudnessGain / Gain / Mixer','blue',23],['arrow',346,344,846,344,'gray'],
 ['text',64,428,1150,42,'初始化成功后，插入会话音效',28,'teal',True],['node',64,486,270,89,'Converter','blue',27],['node',429,486,334,89,'SessionEffect','teal',28],['node',858,486,356,89,'LoudnessGain\nGain / Mixer','blue',25],['arrow',346,530,417,530],['arrow',775,530,846,530],
 ['text',64,609,1150,38,'复用处理单元，也必须遵守格式、生命周期与迁移状态契约',27,'navy',True]],
 keys=['sessionfx','fxformat','connect','effectold'],section='第三部分 · 创新三：一个具体接入例子',prev='上一页建立了节点、簇和管理器的职责。',next='把三项创新放回开场场景，看策略如何驱动、各层怎样协同执行。',footer='固定源码功能例子，非内部项目成果；图将下游增益与混音职责折叠显示',boundary='SessionEffect有格式和状态条件；不提供未经核实的旧新代码量或交付周期对比。')
