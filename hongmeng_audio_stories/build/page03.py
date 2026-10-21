from author import *
e=[t(54,207,1170,36,'设备处理线程：函数执行顺序，不按真实耗时缩放',24,'navy',True)]
e += [box(54,285,230,78,'HandleMsg','blue',26),box(316,285,635,78,'Process：拉图 → SinkOutput → RenderFrame','teal',23),box(984,285,240,78,'下一轮 HandleMsg','blue',23)]
e += [a(284,325,316,325),a(951,325,984,325)]
e += [t(600,394,585,37,'RenderFrame 尚未返回',25,'teal',True),box(575,464,295,80,'控制侧另一线程\n发布Pause / Notify','amber',22),a(870,504,1104,504,'amber'),t(878,454,310,35,'留待后续消费',22,'amber')]
e += [l(1104,364,1104,445,'blue',2,True),t(54,570,1170,45,'少一次跨线程中转；设备调用耗时也会占用这个控制执行上下文',27,'navy',True)]
save(3,'线程合并以后，Pause 在哪里等？','Notify 唤醒等待，不会抢占正在执行的 RenderFrame',
 '能预测Process期间发布的Pause要等当前调用返回和后续消费，理解线程合并的约束。',e,'\n\n'.join(S1[8:11]),
 ['run','process','sink'],'RenderFrame还没返回，Pause已经发布，它会立刻拆图吗？',
 '不会。普通设备线程先完成当前Process，再到后续HandleMsg按批次消费；Notify不抢占函数执行。',
 '限定普通HPAE设备线程调用链；不声明驱动无其他线程，也不保证固定调度周期',3,'故事一 · 执行组织的取舍',
 prev='旧PA通过dq交接，新路径沿设备处理调用链直接提交。',next='少了中转，为什么仍有Buffer？逐字节算四轮输出。')

