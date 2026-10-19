from redesign import *
e=lanes(['PA 主输出渲染线程','primary.dq','HDI 写线程','SinkAdapter'],[190,500,820,1110],240,591)
e+=[t(75,310,440,40,'ProcessRenderUseTiming()',24,'navy',True),t(75,361,435,44,'SinkRenderPrimary() 生成 chunk',23,'navy')]
e+=msg(190,500,445,'pa_asyncmsgq_post(HDI_RENDER)','amber',19)
e+=[t(488,481,400,39,'队列保存 chunk 引用',22,'amber')]
e+=msg(500,820,527,'pa_asyncmsgq_get()','amber',21)
e+=msg(820,1110,584,'ProcessHdiRendererPrimary → RenderWrite','teal',18)
e+=[t(64,622,1140,35,'跨线程交接在 primary.dq；源码只显示 chunk 引用传递，不等于每次复制 PCM',21,'navy',True)]
save(5,'5.1 普通主输出：渲染与 HDI 写分属两线程','primary.dq 承接 chunk，写线程再调用 RenderWrite',e,'旧方案的成本不能靠概念描述。5.1 hdi_sink的普通主输出，在ProcessRenderUseTiming里调用SinkRenderPrimary取得pa_memchunk，随后pa_asyncmsgq_post把HDI_RENDER和chunk送入primary.dq。另一侧ThreadFuncWriteHDI阻塞在pa_asyncmsgq_get，拿到消息后进入ProcessHdiRendererPrimary，检查设备启动状态再调用RenderWrite。SinkAdapter最终向HDI提交。\n这个结构带来一个明确的跨线程排队与唤醒边界。代码传递的是pa_memchunk结构与内存块引用，不能把它画成每次PCM memcpy，也不能凭此给出时延百分比。旧写线程还能处理HDI_START、HDI_STOP与QUIT，线程职责并非纯写入。下一页严格对照同一普通主输出路径，看看自研引擎把哪段交接收到了同一执行链。',['post','writer'],'5.1普通主输出；交接的是chunk引用，未据此推断测量瓶颈排名','旧方案具体路径；不能推广到所有PA设备、DIRECT或offload路径。')
