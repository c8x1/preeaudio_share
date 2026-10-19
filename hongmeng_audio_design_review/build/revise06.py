from redesign import *
e=[t(65,256,520,40,'5.1 普通主输出',27,'navy',True),t(690,256,520,40,'当前 HPAE 普通输出',27,'blue',True),l(635,260,635,603,'light',2)]
for x,steps,col in [(64,['SinkRenderPrimary','primary.dq','HDI 写线程','RenderWrite'], 'navy'),(690,['HpaeSignalProcessThread','HandleMsg() → Process()','OutputCluster → SinkOutput','RenderFrame()'],'blue')]:
 for i,s in enumerate(steps):
  y=327+i*71;e += [box(x,y,515,54,s,col,23)]
  if i<3:e += [a(x+257,y+54,x+257,y+71,col)]
e += [t(64,615,1150,37,'已减少的边界：旧主输出 render → primary.dq → HDI 写线程；驱动下游不在比较内',21,'navy',True)]
save(6,'同一普通输出路径：跨线程交接在哪里收拢','旧 render 到写线程的队列交接，变为当前处理线程内连续调用',e,'将前后两个固定源码版本的普通主输出放在同一范围比较。旧hdi_sink生成chunk后经primary.dq交给HDI写线程。新HpaeSignalProcessThread先HandleMsg，再调用HpaeRendererManager::Process；随后进入OutputCluster的DoProcess、SinkOutput的DoProcess，并在这条调用链里RenderFrame。自研在这里收拢了旧渲染到HDI写线程的交接，减少一次可定位的排队/唤醒边界。\n图不声称操作系统、驱动或硬件再没有其他线程，也不将两个版本所有特殊播放路径混在一起。资源和时延收益由用户提供的是定性结论；静态代码只解释为什么这个改动可能改善延迟和调度开销。下一页拆开新处理线程：它怎样同时处理控制和数据，何时等待。',['post','writer','run','process','out','sink'],'比较范围：5.1普通主输出与当前HPAE普通输出；驱动下游另行测量','两个版本的实现对照，不是相同设备上的实测数值。')
