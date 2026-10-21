from author import *

cite('samepipe','N','services/audio_policy/server/domain/pipe/src/audio_pipe_manager.cpp',349,356,'IsSamePipe比较名称或标识')
cite('targetname','N','services/audio_policy/server/service/service_main/src/audio_core_service_private.cpp',2361,2375,'目标pipe模块名作为sinkName')
cite('batchevent','N','services/audio_policy/server/service/service_main/src/audio_core_service_private.cpp',3534,3579,'批量选目标与执行pipe计划')
e=[box(54,214,340,64,'device：物理输出目标','blue',24),box(469,214,340,64,'pipe：策略执行计划','purple',24),box(884,214,340,64,'sink：引擎归属名称','teal',24)]
rows=[['沿一次合法分支','具体判断 / 动作','不能据此推出'],['① 目标device不同','扬声器 → 耳机','pipe必然不同'],['② pipe名称或标识相同','计划可为DEFAULT；与MOVE共分支','不会调用Move接口'],['③ Move传入目标sinkName','CheckMove通过，且与当前sink相同\nHPAE成功早退，不向旧Renderer发移动','调用Move = 跨Renderer搬输入'],['④ 后续设备route','普通运行流再按条件更新输出route','同sink意味着物理输出不变']]
e += [table(54,315,1170,300,rows,[270,550,350],21),t(54,630,1170,28,'教学配置：两设备映射同一primary sink；真正跨sink的分支下一页展开',22,'navy',True)]
save(11,'看到 Move 日志，就发生了节点迁移吗？','分别追踪device、pipe和sink；方法入口不能代替最终分支',
 '能解释device变化但同pipe、同sink的完整反例，区分Move调用、HPAE早退与设备route。',e,'\n\n'.join(S3[8:13]),
 ['batchevent','samepipe','pipe','action','targetname','move','route'],
 'device已变、Move已调用，但验证后sinkName相同；旧Renderer会收到拆图请求吗？',
 '不会，HPAE同sink成功早退。设备route仍按后续条件更新；调用Move不能证明发生了跨Renderer迁移。',
 '普通运行且非重建等特殊路径；同sink早退须先通过CheckMove；产品映射需核对部署XML',3,'故事三 · 三种标识与分支',
 prev='策略给出设备以后，还要把结果映射为执行计划与引擎目标。',next='明确目标sink不同且可移动后，才进入真正的输入迁移。')
