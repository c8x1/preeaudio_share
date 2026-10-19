from redesign import *
xs=[165,400,640,880,1110];e=lanes(['客户端','流服务','策略','HpaeManager','RendererManager'],xs,240,601)
e+=msg(165,400,315,'IPC Start','navy',21)
e+=msg(400,640,360,'UpdateSessionOperation','purple',19)
e+=[t(450,391,390,35,'非 FAST：WaitForDataConnection',20,'purple')] + msg(400,880,448,'stream Start → 管理队列','blue',20) + msg(880,1110,499,'设备级 Start 入队','blue',20) + msg(880,400,553,'STARTED 回程','navy',20) + msg(400,165,594,'RUNNING 通知','navy',20) + [t(70,622,1140,35,'设备请求另行执行；状态回程没有首帧消费完成屏障',23,'blue',True)]
save(3,'Start 如何穿过策略、服务与两级队列','管理状态回程与设备级执行分叉，不能合并成一次成功',e,'客户端先经IPC向RendererInServer请求Start。服务端验证状态和共享缓冲，调用策略UpdateSessionOperation；普通非FAST路径在设备激活后WaitForDataConnection，目的是避免蓝牙连接前后数据不连续造成爆音，之后调用流Start。HpaeManager先把Start封成管理请求。管理线程消费时找到RendererManager，再调用它的Start，而RendererManager只是把具体连接、淡入、音效工作放入设备级队列。随后管理状态STARTED可以回传服务端和客户端，客户端等待RUNNING。\n图上第二次入队与上行状态是两条分叉，不用从设备级队列向STARTED画完成箭头。RendererManager的请求实际执行时才置HPAE_SESSION_RUNNING、ConnectInputSession、SetSessionFade、启动可选SessionEffect。这里的RUNNING是管理状态，不是设备或声学首帧的同步屏障。策略先被调用是系统协同的一部分，具体声音并发规则和目标设备依业务策略而定。',['clientstart','start','managerstart','renderstart','status'],'控制泳道；设备执行发生于另一次排队，未绘出精细回调条件','普通 HPAE 路径；非 FAST 的连接等待有条件；无跨线程全局总序。')

