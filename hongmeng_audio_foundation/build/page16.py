from author import write
write(16,'A1  线程与Buffer边界对照','定位已移除的交接，同时区分仍保留的缓存与下游执行',
'补足新旧线程/Buffer的局部细节，避免用线程或缓存对象个数推断全链收益。',
'''旧方案还有PA daemon主循环、PaAdapterManager的threaded mainloop、HDI模块渲染和设备写入等执行角色。它们不一定全部每流独占，也不能从函数名直接得到产品线程总数。本图只展开普通主输出中已经逐函数确认的一段。
服务端数据通过libpulse流写入，PA流有缓冲请求和协商语义。hdi_sink渲染侧生成chunk，通过primary.dq交给独立HDI写线程。队列传递的是memchunk及其内存引用，不应假定每交接都必然复制整块音频。
当前HPAE普通回调拉取链中，服务端从共享音频缓冲复制到SinkInput请求内存，后续Converter可能保留格式/块长适配数据，SinkOutput按提交粒度拼帧，再在处理调用链中RenderFrame。旧primary.dq与独立写线程之间的边界不再位于这条引擎提交链中，但设备适配和驱动内部行为必须继续看具体实现。
因此，说Buffer减少时需要标明位置：这里直接证明的是一处中转交接消失，当前仍有必要缓存。PA的20/80毫秒参数是请求属性，不是测得的端到端时延；当前mixer常见20毫秒块长也不是全链统一周期。
要补全某产品的完整线程及缓存清单，应结合构建配置、运行时dump和实际设备路径逐一对应。静态源码不能替代运行时库存与调度测量。''',
[['text',64,246,1150,42,'5.1 普通主输出（其他执行角色见备注）',28,'purple',True],
 ['node',64,305,240,85,'PA 流缓冲','purple',26],['node',366,305,240,85,'hdi_sink 渲染','purple',25],['node',668,305,240,85,'primary.dq\nchunk 引用交接','gray',24],['node',970,305,244,85,'HDI 写线程','purple',26],['arrow',316,348,354,348,'purple'],['arrow',618,348,656,348,'purple'],['arrow',920,348,958,348,'purple'],
 ['text',64,438,1150,42,'当前 HPAE：处理线程拉图与提交（图省略中间节点）',28,'blue',True],
 ['node',64,497,240,85,'共享缓冲读取\n复制到输入内存','navy',24],['node',366,497,240,85,'Converter 缓存\n块长 / 格式适配','blue',24],['node',668,497,240,85,'SinkOutput\n按提交粒度拼帧','blue',24],['node',970,497,244,85,'RenderFrame\n进入设备适配','teal',25],['arrow',316,540,354,540],['arrow',618,540,656,540],['arrow',920,540,958,540]],
 keys=['daemon','pa','attr','post','writer','buffer','converterbuf','stitch','sink'],minutes=0,section='技术附录 · A1',prev='按线程与缓存问题进入。',next='需要无锁队列并发细节时看A2。',footer='局部路径清单，非所有线程/缓存的穷举；chunk引用交接不等于必然整块复制',boundary='不从请求缓冲属性推导产品时延或线程总数。',label='A1')
