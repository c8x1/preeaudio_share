from redesign import *
e=[t(65,252,520,38,'控制事件',27,'navy',True),t(680,252,530,38,'数据与声学事件',27,'teal',True),l(630,255,630,595)]
for x,items,c in [(64,['StartAudioStream 入口','IPC Start 返回','OnOperationHandled → RUNNING'],'navy'),(680,['SinkInput 首次消费数据','SinkOutput 首次 RenderFrame','外部检测实际出声'],'teal')]:
 for i,s in enumerate(items):e += [box(x,325+i*77,535,56,s,c,21)]
e += [t(64,579,540,63,'入口到 RUNNING：管理响应\n另记录队列发布 / 消费时间',23,'navy'),t(680,579,535,63,'入口到出声：端到端时延\n提交到出声：下游设备路径',23,'teal')]
save(14,'性能观测：分别记录控制确认和数据执行','用真实事件定位排队、供数与设备开销，再讨论整机收益',e,'这页给可执行的观测位置，没有填入不存在的实测曲线。客户端StartAudioStream入口和IPC返回可观察管理调用；OnOperationHandled对应RUNNING。引擎可观察队列发布和HandleRequests消费、SinkInput首次取到数据、SinkOutput首次RenderFrame，外部回环或声学检测观察实际出声。左右是两组事件，不画RUNNING和首帧之间的固定时间顺序。\n同一时钟域中可计算入口到状态确认的管理响应、队列发布到消费的等待、供数到RenderFrame的处理段。声学端到端要对齐采集时钟，不能直接相减不同机器时间戳。旧PA的post/get也可作为交接事件，与新引擎同业务语义对照。CPU时间、线程唤醒、欠载和能量应在同硬件、同负载、同输出设备和音量下联合观察；Buffer和块长差异必须记录。用户团队确认方向为时延降低、性能提升和功耗下降，本轮没有产品数值，最终收益等待数据。',['clientstart','status','queue','post','writer','sink','buffer'],'观测设计，尚未执行产品测量；左右并列不构成跨线程总序','跨时钟域需对齐；CPU降低不能直接换算功耗百分比。')
