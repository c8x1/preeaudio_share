from author import write
write(19,'A4  策略、服务与引擎的启动协作','请求接受、RUNNING状态和首帧消费需要分别观察',
'给出折叠的跨层Start控制关系，避免把成功返回当成声学出声。',
'''客户端Start先检查状态，调用IPC启动并检查同步返回，再通过条件变量等待RUNNING；超时会Stop。服务端StartInner验证状态和缓冲后，更新策略侧会话操作。普通非FAST分支随后WaitForDataConnection，再进入具体流的Start，DIRECT等路径另有StartRender。
HpaeRendererStreamImpl转给HpaeManager。HpaeManager把lambda入队，执行时调用对应RendererManager::Start；后者再次排队设备级连接与状态工作。管理层随后可发出STARTED状态，服务端转成操作完成回程，客户端据此进入RUNNING。
重要的是，这个管理状态回程没有等待设备级lambda实际完成的屏障。设备级连接、正式数据拉取和实际声学出声是不同观察点。跨线程并发下，不能单凭本图保证客户端观察RUNNING与真实数据消费有固定全局先后顺序。
图中的策略操作返回也不等于设备输出已准备完毕，服务端还有条件性的等待连接。它解释为什么完整底座中的状态与资源协调不能被一个引擎调用替代。数据共享缓冲和PCM传输没有画在这张控制关系图中。''',
[['text',64,248,250,40,'客户端',27,'gray',True,'center'],['text',355,248,250,40,'流服务',27,'navy',True,'center'],['text',646,248,250,40,'策略',27,'purple',True,'center'],['text',937,248,277,40,'引擎管理',27,'blue',True,'center'],
 ['line',189,300,189,605,'light',2],['line',480,300,480,605,'light',2],['line',771,300,771,605,'light',2],['line',1075,300,1075,605,'light',2],
 ['arrow',189,325,480,325,'navy'],['text',210,290,250,33,'IPC Start',23,'navy'],
 ['arrow',480,385,771,385,'purple'],['text',490,350,280,33,'更新会话操作',23,'purple'],
 ['arrow',771,431,480,431,'purple'],['text',493,437,440,34,'返回后按条件等待数据连接',22,'gray'],
 ['arrow',480,502,1075,502,'blue'],['text',585,468,440,32,'流Start / 管理请求入队',23,'blue'],
 ['arrow',1075,553,480,553,'blue'],['text',604,518,400,31,'STARTED 状态回调',23,'blue'],
 ['arrow',480,599,189,599,'navy'],['text',215,563,250,31,'RUNNING 通知',23,'navy'],
 ['text',64,622,1150,34,'设备级请求还有一次入队；管理状态确认不等于声学出声',25,'navy',True]],
 keys=['clientstart','start','managerstart','renderstart','status'],minutes=0,section='技术附录 · A4',prev='按跨层控制与成功语义问题进入。',next='设备迁移和状态保留看A5。',footer='控制中间层折叠；图不按真实耗时缩放，也未绘制PCM数据轨',boundary='不声明RUNNING与真实首帧消费的固定总序；限定普通HPAE路径，其他类型有分支。',label='A4')
