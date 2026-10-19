from redesign import *
S['pausefade']=(CUR,'services/audio_engine/manager/src/hpae_renderer_manager.cpp',1861,1904,'SetSessionFade')
S['fadedone']=(CUR,'services/audio_engine/manager/src/hpae_renderer_manager.cpp',1777,1804,'OnFadeDone')
S['pausecmd']=(CUR,'services/audio_engine/manager/src/hpae_renderer_manager.cpp',1110,1141,'Pause')
e=[t(64,247,1140,38,'HpaeRendererManager 的内部状态（HPAE_SESSION_ 前缀省略）',24,'navy',True)]
for y,cmd,mid,end in [(325,'Pause','PAUSING','PAUSED'),(460,'Stop','STOPPING','STOPPED')]:
 e += [box(64,y,210,60,'RUNNING','navy'),box(475,y,230,60,mid,'amber'),box(1025,y,190,60,end,'teal'),a(274,y+30,475,y+30),t(305,y-9,150,35,cmd,23,'blue'),a(705,y+30,1025,y+30,'teal'),t(730,y-10,290,35,'OnFadeDone → 再入队',20,'teal')]
e += [t(64,573,535,63,'无 Gain / standby 等条件\n可直接设置终态与回调',23,'gray'),t(650,573,565,63,'过时淡出回调发现已 RUNNING\n立即退出，避免拆掉恢复后的连接',23,'blue')]
save(12,'Pause / Stop：淡出完成后再断开节点','中间态把 Gain 渐变、音效暂停和断图衔接起来',e,'这里画的是设备RendererManager内部HPAE_SESSION状态，而不是客户端API状态。普通活跃流Pause会SetSessionFade进入PAUSING；Stop进入STOPPING。Gain节点输出淡出后调用OnFadeDone，OnFadeDone再次把工作送回设备队列，在该上下文暂停会话音效、DisConnectInputSession、置PAUSED或STOPPED，再触发状态回调。先过渡再拆图，把声音渐变与资源连接协调起来。\n有两个重要条件。若节点已经PAUSED/STOPPED、无Gain、Manager未运行或standby等，会走直接终态回调路径。若淡出完成消息回来时节点已恢复RUNNING，OnFadeDone退出，避免迟到的回调把新播放的连接拆掉。管理层还有pending transition和超时兜底，不能把管理回调当成设备完成屏障。旧PA同样有淡出，这里展示自研通过节点状态、Gain回调和设备队列组织职责，不宣称首次发明渐变。',['pausefade','fadedone','pausecmd'],'普通活跃流正常路径；实际条件旁路在下方；状态属于设备RendererManager','管理状态回程/超时与真实设备完成分开；旧PA也有淡出。')
