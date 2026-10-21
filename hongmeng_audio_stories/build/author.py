from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parents[1]
N='3a2688e805df970739e3b0cebf9cc05d8cb24e9b';O='c42a228d60b64a90d6b05cf26278a89253e5310b';P='bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca'
C={}
def cite(k,repo,f,a,b,label):C[k]=(repo,f,a,b,label)
cite('client','N','services/audio_service/client/src/renderer_in_client_public.cpp',1398,1454,'Client Start等待RUNNING')
cite('server','N','services/audio_service/server/src/renderer_in_server.cpp',1576,1606,'Server Start：校验、策略与连接等待')
cite('mgrstart','N','services/audio_engine/manager/src/hpae_manager.cpp',1830,1875,'管理队列Start及状态回程')
cite('start','N','services/audio_engine/manager/src/hpae_renderer_manager.cpp',919,945,'设备Start：入队、连接、淡入')
cite('oldpost','O','frameworks/native/pulseaudio/modules/hdi/hdi_sink.c',2449,2477,'旧PA渲染与post')
cite('oldgate','O','frameworks/native/pulseaudio/modules/hdi/hdi_sink.c',3523,3574,'旧普通主输出dflag门控')
cite('oldwriter','O','frameworks/native/pulseaudio/modules/hdi/hdi_sink.c',3821,3887,'旧写线程get、写入、清dflag')
cite('oldwrite','O','frameworks/native/pulseaudio/modules/hdi/hdi_sink.c',374,418,'RenderWrite与原始chunk引用')
cite('paqueue','P','src/pulsecore/asyncmsgq.c',124,263,'PA post/send/get/done同步与引用')
cite('pacork','P','src/pulsecore/protocol-native.c',3856,3883,'PA cork协议处理与ACK')
cite('paset','P','src/pulsecore/sink-input.c',702,732,'PA SET_STATE同步I/O握手')
cite('oldstart','O','services/audio_service/server/src/pa_renderer_stream_impl.cpp',154,182,'旧Start的mainloop保护与cork')
cite('run','N','services/audio_engine/manager/src/hpae_signal_process_thread.cpp',76,125,'设备线程Run与Notify')
cite('process','N','services/audio_engine/manager/src/hpae_renderer_manager.cpp',1640,1664,'Renderer Process')
cite('sink','N','services/audio_engine/node/src/hpae_sink_output_node.cpp',121,165,'SinkOutput提交与余量搬移')
cite('stitch','N','services/audio_engine/node/src/hpae_sink_output_node.cpp',680,707,'字节拼帧循环')
cite('sinksize','N','services/audio_engine/node/src/hpae_sink_output_node.cpp',62,69,'设备提交块初始化')
cite('qpush','N','services/audio_engine/utils/hpae_no_lock_queue.cpp',57,89,'取节点、发布与原子摘批')
cite('qcas','N','services/audio_engine/utils/hpae_no_lock_queue.cpp',173,187,'CAS失败重试与next重建')
cite('qget','N','services/audio_engine/utils/hpae_no_lock_queue.cpp',142,155,'index/flag与版本增加')
cite('qrun','N','services/audio_engine/utils/hpae_no_lock_queue.cpp',206,267,'节点取出、回收、闭包执行与头空检查')
cite('qexpand','N','services/audio_engine/utils/hpae_no_lock_queue.cpp',103,139,'扩容锁与节点分配')
cite('qconst','N','services/audio_engine/utils/hpae_no_lock_queue.h',28,42,'节点结构及1000/90%/5000')
cite('gain','N','services/audio_engine/node/src/hpae_gain_node.cpp',207,281,'Gain有效/无效输入淡出与回调')
cite('fade','N','services/audio_engine/manager/src/hpae_renderer_manager.cpp',1861,1904,'SetSessionFade条件与中间态')
cite('pause','N','services/audio_engine/manager/src/hpae_renderer_manager.cpp',1110,1141,'Pause提交与直接断连分支')
cite('fadedone','N','services/audio_engine/manager/src/hpae_renderer_manager.cpp',1777,1804,'FadeDone入队与执行时守卫')
cite('drain','N','services/audio_service/server/src/renderer_in_server.cpp',437,477,'公共服务迟到Drain状态保护')
cite('xml','N','services/audio_policy/server/infra/config/file/audio_strategy_router.xml',16,22,'默认媒体Router顺序')
cite('router','N','services/audio_policy/server/domain/router/audio_router_center.cpp',43,60,'第一个有效Router短路返回')
cite('zone','N','services/audio_policy/server/domain/router/audio_router_center.cpp',384,405,'非零zone提前返回分支')
cite('privacy','N','services/audio_policy/server/domain/router/router_base.h',72,101,'过滤后的最新候选选择')
cite('private','N','services/audio_policy/server/domain/router/privacy_priority_router.cpp',27,38,'媒体privacy选择')
cite('pipe','N','services/audio_policy/server/domain/pipe/src/audio_pipe_selector.cpp',2217,2226,'同pipe DEFAULT/否则MOVE')
cite('action','N','services/audio_policy/server/service/service_main/src/audio_core_service_private.cpp',1087,1097,'DEFAULT与MOVE共分支')
cite('route','N','services/audio_policy/server/service/service_main/src/audio_core_service_private.cpp',1696,1713,'Move后的条件路由更新')
cite('move','N','services/audio_engine/manager/src/hpae_manager.cpp',1030,1091,'CheckMove与同sink早退')
cite('detach','N','services/audio_engine/manager/src/hpae_renderer_manager.cpp',872,916,'旧Renderer拆图与传递输入')
cite('movein','N','services/audio_engine/manager/src/hpae_manager.cpp',1157,1227,'目标提交、映射和回程')
cite('attach','N','services/audio_engine/manager/src/hpae_renderer_manager.cpp',107,176,'目标设备/span与RUNNING连接条件')
cite('pamove','P','src/pulsecore/sink-input.c',1867,1930,'PA旧sink START_MOVE')
cite('pafinish','P','src/pulsecore/sink-input.c',2159,2243,'PA目标FINISH_MOVE及通知')
cite('paiomove','P','src/pulsecore/sink.c',2748,2866,'PA I/O detach/attach')
cite('effect','N','services/audio_engine/node/src/hpae_process_cluster.cpp',547,582,'会话音效先初始化再插边')
cite('fxformat','N','services/audio_engine/node/src/hpae_process_cluster.cpp',351,365,'AISS格式48k/双声道')
cite('entry','N','services/audio_service/server/src/i_stream_manager.cpp',29,64,'管理器分支范围')
cite('attr','O','services/audio_service/server/src/pa_adapter_manager.cpp',673,702,'PA请求缓冲属性')
cite('pull','N','services/audio_engine/node/include/hpae_node.h',315,325,'InputPort读取前驱')
cite('pullout','N','services/audio_engine/node/include/hpae_node.h',389,404,'OutputPort空队列触发计算')
def refs(keys):
 out=[]
 for k in keys:
  repo,f,a,b,label=C[k];sha={'N':N,'O':O,'P':P}[repo];name='third_party_pulseaudio' if repo=='P' else 'multimedia_audio_framework'
  out.append(f'{label} L{a}–{b}：https://gitcode.com/openharmony/{name}/blob/{sha}/{f}#L{a}')
 return out
def paragraphs(name,start,end):
 s=(R/'scripts'/name).read_text(encoding='utf-8').split(start,1)[1].split(end,1)[0]
 return [p for p in s.strip().split('\n\n') if not p.startswith('#')]
OPEN=paragraphs('00_opening_and_closing.md','## 开篇讲述正文','## 收束讲述正文')
END=paragraphs('00_opening_and_closing.md','## 收束讲述正文','## 课堂检验与答案')
S1=paragraphs('01_threads_and_buffers.md','## 完整讲述稿','## 四轮库存板书')
S2=paragraphs('02_control_and_lifecycle.md','## 讲述正文','## 逐步推演用表')
S3=paragraphs('03_routing_and_graph.md','## 完整讲述稿','## 推演表')
def t(x,y,w,h,s,size=24,c='navy',bold=False,align='left'):return ['text',x,y,w,h,s,size,c,bold,align]
def l(x,y,xx,yy,c='light',width=2,dash=False):return ['line',x,y,xx,yy,c,width,dash]
def a(x,y,xx,yy,c='blue',dash=False):return ['arrow',x,y,xx,yy,c,dash]
def box(x,y,w,h,s,c='blue',size=23):return ['node',x,y,w,h,s,c,size]
def table(x,y,w,h,rows,widths=None,size=22):return ['table',x,y,w,h,rows,widths,size]
def msg(x,xx,y,s,c='blue',size=22):return [a(x,y,xx,y,c),t(min(x,xx)+8,y-31,abs(xx-x)-14,29,s,size,c)]
def lanes(names,xs,y=200,bottom=610,size=23):
 e=[]
 for name,x in zip(names,xs):e += [t(x-120,y,240,40,name,size,'navy',True,'center'),l(x,y+47,x,bottom)]
 return e
def save(n,title,takeaway,outcome,elements,script,keys,question,answer,condition,minutes=0,chapter='',prev='',next='',cue='',label=None):
 d=dict(n=n,title=title,takeaway=takeaway,outcome=outcome,elements=elements,script=script,sources=refs(keys),question=question,answer=answer,condition=condition,minutes=minutes,chapter=chapter,prev=prev,next=next,cue=cue,sourceKeys=list(keys),version='three-stories')
 if label:d['label']=label
 (R/'pages'/f'P{n:02}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 dest=R/'research/evidence';dest.mkdir(parents=True,exist_ok=True)
 for k in keys:
  repo,f,a0,b,lab=C[k];src=R.parent/({'N':'source_gitcode','O':'source_audio_5_1','P':'source_pulseaudio'}[repo])
  if repo=='P':text=subprocess.run(['git','-C',str(src),'show',f'{P}:{f}'],capture_output=True,encoding='utf-8',check=True).stdout
  else:text=(src/f).read_text(encoding='utf-8')
  lines=text.splitlines();(dest/f'{k}.txt').write_text(refs([k])[0]+'\n'+'\n'.join(f'{i+1}: {lines[i]}' for i in range(a0-1,min(b,len(lines)))),encoding='utf-8')
 print('Authored',n)
