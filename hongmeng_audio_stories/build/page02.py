from author import *
e=lanes(['PA渲染线程','primary.dq','HDI写线程','设备接口'],[180,500,820,1110],205,627,23)
e+=[box(54,269,250,54,'dflag++，生成 A','navy',22)]
e+=msg(180,500,355,'post：A 的引用','blue',22)
e+=msg(500,820,410,'get：取出 A','blue',22)
e+=[t(54,425,430,70,'下一轮见 dflag == 1\n等待，尚不生成 B',23,'amber',True)]
e+=msg(820,1110,487,'RenderWrite / RenderFrame','teal',18)
e += [a(820,558,180,558,'teal',True),t(330,520,470,34,'写端完成后 atomic dflag--',22,'teal')]
e+=msg(180,500,618,'后续轮次才生成、投递 B','blue',20)
save(2,'A 已经生成，为什么 B 还在上游？','旧主输出有跨线程交接，也有 dflag 门控生产节奏',
 '能预测写端未清忙时不会在此路径继续生成B，区分交接等待与无限队列积压。',e,'\n\n'.join(S1[:8]),
 ['oldpost','oldgate','oldwriter','oldwrite','paqueue'],
 '写线程尚未得到调度，render会继续post B、C吗？',
 '本普通路径不会；dflag==1时安排等待，下一块生成依赖写端清忙。虚线表示共享标志依赖，不是额外消息。',
 '5.1普通主输出的合法交错，不按耗时绘制；post传chunk引用，非此处整块PCM复制',5,'故事一 · 等待边界',
 prev='从全局控制转到一块已经处理完成的数据A。',next='HPAE收拢了这段交接，新的同线程执行又有什么约束？')
