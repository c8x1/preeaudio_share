from redesign import *
S['latedrain']=(CUR,'services/audio_service/server/src/renderer_in_server.cpp',450,477,'Drain迟到回调的状态保护')
S['clientstop']=(CUR,'services/audio_service/client/src/renderer_in_client_public.cpp',1554,1603,'StopAudioStream')
e=lanes(['客户端','RendererInServer','引擎回调'],[220,640,1060],245,600)
e+=msg(220,640,318,'Drain → I_STATUS_DRAINING','blue',21)
e+=[t(65,355,540,35,'Drain等待超时；继续 Stop',23,'amber')]+msg(220,640,427,'Stop → I_STATUS_STOPPED','navy',21)+msg(1060,640,493,'迟到的 OPERATION_DRAINED','amber',21)
e += [box(653,534,562,62,'仅 status_ == I_STATUS_DRAINING 才恢复 STARTED','teal',18),t(64,618,1150,36,'保护当前终态，避免迟到 Drain 回调把已经 STOPPED 的服务端错误恢复为 STARTED',21,'navy',True)]
save(19,'A4  迟到的 Drain 回调，怎样避免复活已停流','服务状态检查挡住过时完成事件，体现跨层异步正确性',e,'更深入看整个底座的一个真实竞态。客户端Stop对普通流会先尝试Drain；Drain等待超时并不阻断后续Stop，因此Stop可能已完成，之后Drain回调才到。服务端OnStatusUpdate处理OPERATION_DRAINED时明确检查当前status_仍为I_STATUS_DRAINING，才恢复STARTED并发送Drain完成；若已经STOPPED等其他状态，不按旧Drain结果恢复。\n这里画的是一种可能发生的交错，不是每次Stop必经的固定时序。条件检查让迟到完成事件不能覆盖更新的生命周期状态。它是当前公共流服务层的正确性设计，不应宣传为自研引擎独创。主讲Start展示管理状态与执行分叉，Pause展示设备内部过渡，这页则补公共服务如何处理过时异步事件。',['latedrain','clientstop'],'示例为可能的并发交错；I_STATUS_属于服务端，非客户端RUNNING','公共服务层状态保护；不宣称自研新增或所有Stop都会Drain成功。')
