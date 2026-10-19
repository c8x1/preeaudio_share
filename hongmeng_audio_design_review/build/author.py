from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1]
CUR='3a2688e805df970739e3b0cebf9cc05d8cb24e9b';OLD='c42a228d60b64a90d6b05cf26278a89253e5310b'
S={
'focus':(CUR,'services/audio_policy/server/domain/zone/src/audio_zone_service.cpp',818,853,'ActivateAudioInterrupt'),
'route':(CUR,'services/audio_policy/server/domain/zone/src/audio_zone_service.cpp',966,978,'FetchOutputDevices'),
'volume':(CUR,'services/audio_policy/server/domain/zone/src/audio_zone_service.cpp',720,734,'SetSystemVolumeLevel'),
'start':(CUR,'services/audio_service/server/src/renderer_in_server.cpp',1576,1606,'StartInner'),
'buffer':(CUR,'services/audio_service/server/src/renderer_in_server.cpp',1122,1161,'WriteData'),
'entry':(CUR,'services/audio_service/server/src/i_stream_manager.cpp',29,64,'GetPlaybackManager'),
'adapter':(CUR,'services/audio_service/server/src/hpae_adapter_manager.cpp',273,307,'CreateRendererStream'),
'queue':(CUR,'services/audio_engine/utils/hpae_no_lock_queue.cpp',57,145,'PushRequest / HandleRequests / TryExpandQueue'),
'send':(CUR,'services/audio_engine/manager/src/hpae_renderer_manager.cpp',1755,1770,'SendRequest'),
'run':(CUR,'services/audio_engine/manager/src/hpae_signal_process_thread.cpp',75,125,'Notify / Run'),
'process':(CUR,'services/audio_engine/manager/src/hpae_renderer_manager.cpp',1640,1664,'Process'),
'out':(CUR,'services/audio_engine/node/src/hpae_output_cluster.cpp',79,84,'OutputCluster::DoProcess'),
'sink':(CUR,'services/audio_engine/node/src/hpae_sink_output_node.cpp',121,165,'SinkOutput::DoProcess / RenderFrame'),
'stitch':(CUR,'services/audio_engine/node/src/hpae_sink_output_node.cpp',680,707,'ReadDataAndConvertFormat'),
'connect':(CUR,'services/audio_engine/node/src/hpae_process_cluster.cpp',206,232,'ProcessCluster::Connect'),
'nodes':(CUR,'services/audio_engine/node/src/hpae_output_cluster.cpp',110,135,'OutputCluster::Connect'),
'share':(CUR,'services/audio_engine/manager/src/hpae_renderer_manager.cpp',179,240,'CreateProcessClusterInner'),
'pull':(CUR,'services/audio_engine/node/include/hpae_node.h',315,325,'InputPort::ReadPreOutputData'),
'move':(CUR,'services/audio_engine/manager/src/hpae_manager.cpp',1065,1095,'MoveSinkInputByIndexOrName'),
'detach':(CUR,'services/audio_engine/manager/src/hpae_renderer_manager.cpp',872,916,'MoveStreamSync'),
'attach':(CUR,'services/audio_engine/manager/src/hpae_renderer_manager.cpp',106,179,'AddSingleNodeToSink'),
'oldentry':(OLD,'services/audio_service/server/src/i_stream_manager.cpp',22,39,'GetPlaybackManager'),
'daemon':(OLD,'services/audio_service/server/src/audio_server.cpp',261,273,'paDaemonThread / ohos_pa_main'),
'pa':(OLD,'services/audio_service/server/src/pa_renderer_stream_impl.cpp',699,755,'pa_stream_write / PAStreamWriteCb'),
'palock':(OLD,'services/audio_service/server/include/pa_adapter_tools.h',25,63,'PaLockGuard'),
'pastart':(OLD,'services/audio_service/server/src/pa_renderer_stream_impl.cpp',154,182,'Start / pa_stream_cork'),
'post':(OLD,'frameworks/native/pulseaudio/modules/hdi/hdi_sink.c',2449,2477,'ProcessRenderUseTiming'),
'writer':(OLD,'frameworks/native/pulseaudio/modules/hdi/hdi_sink.c',3821,3887,'ProcessHdiRendererPrimary / ThreadFuncWriteHDI'),
'effectold':(OLD,'frameworks/native/pulseaudio/modules/hdi/hdi_sink.c',2315,2354,'SinkRenderPrimaryProcess'),
'pathsold':(OLD,'frameworks/native/pulseaudio/modules/hdi/hdi_sink.c',3409,3491,'MultiChannel processing'),
'attr':(OLD,'services/audio_service/server/src/pa_adapter_manager.cpp',673,702,'ConnectRendererStreamToPA'),
'oldpolicy':(OLD,'frameworks/native/audioadapter/src/pulse_audio_service_adapter_impl.cpp',447,473,'MoveSinkInputByIndexOrName'),
'converterbuf':(CUR,'services/audio_engine/node/src/hpae_audio_format_converter_node.cpp',815,840,'ExtractOutputFromProcessedBuffer'),
'queuecas':(CUR,'services/audio_engine/utils/hpae_no_lock_queue.cpp',172,191,'PushRequestNode 原子发布'),
'queuerun':(CUR,'services/audio_engine/utils/hpae_no_lock_queue.cpp',227,262,'ProcessRequests 批量执行'),
'renderstart':(CUR,'services/audio_engine/manager/src/hpae_renderer_manager.cpp',919,945,'RendererManager::Start'),
'sessionfx':(CUR,'services/audio_engine/node/src/hpae_process_cluster.cpp',547,582,'CreateSessionEffectNode'),
'fxformat':(CUR,'services/audio_engine/node/src/hpae_process_cluster.cpp',351,365,'SessionEffect 输入格式约束'),
'queueconst':(CUR,'services/audio_engine/utils/hpae_no_lock_queue.h',28,38,'队列容量与扩容阈值'),
'pullout':(CUR,'services/audio_engine/node/include/hpae_node.h',389,404,'OutputPort::PullOutputData'),
'outcreate':(CUR,'services/audio_engine/node/src/hpae_output_cluster.cpp',32,47,'OutputCluster 构造与limiter条件'),
'clientstart':(CUR,'services/audio_service/client/src/renderer_in_client_public.cpp',1398,1454,'StartAudioStream / 等待RUNNING'),
'managerstart':(CUR,'services/audio_engine/manager/src/hpae_manager.cpp',1830,1875,'HpaeManager::Start'),
'status':(CUR,'services/audio_service/server/src/renderer_in_server.cpp',411,428,'STARTED 状态回程'),
'movein':(CUR,'services/audio_engine/manager/src/hpae_manager.cpp',1181,1227,'目标Manager接入与映射更新'),
'span':(CUR,'services/audio_service/server/src/hpae_renderer_stream_impl.cpp',1157,1183,'UPDATE_SPANSIZE 状态处理'),
}
def refs(ks):return [f'{S[k][4]} L{S[k][2]}–{S[k][3]}：https://gitcode.com/openharmony/multimedia_audio_framework/blob/{S[k][0]}/{S[k][1]}#L{S[k][2]}' for k in ks]
def sync():
 p=R.parent/'IMPLEMENTATION_NOTES.md';s=p.read_text(encoding='utf-8')
 a=s.index('## 当前制作状态');b=s.index('## 实施日志',a)
 table='## 当前制作状态\n\n| 页 | 状态 | 评审记录 |\n|---|---|---|\n'
 for n in range(1,22):
  id=f'P{n:02}';q=R/'reviews'/f'{id}.md';state='待制作'
  if (R/'pages'/f'{id}.json').exists():state='已制作，待审'
  if q.exists():
   t=q.read_text(encoding='utf-8');state='评审通过' if re.search(r'状态[：:]\s*PASS',t) else '待修订/复审'
  table+=f'| {id} | {state} | '+(f'[评审](hongmeng_audio_foundation/reviews/{id}.md)' if q.exists() else '—')+' |\n'
 p.write_text(s[:a]+table+'\n'+s[b:],encoding='utf-8')
def write(n,title,takeaway,objective,script,elements,keys=(),minutes=3,section='',prev='',next='',footer='',boundary='',cue='',pacing='',label=None,dark=False):
 p=dict(n=n,title=title,takeaway=takeaway,objective=objective,script=script,elements=elements,minutes=minutes,section=section,from_=prev,next=next,footer=footer,boundary=boundary,cue=cue,pacing=pacing or ('按答疑问题选择展开，附录不计主讲时长。' if minutes==0 else '按本页分钟数讲述：先联系场景，再解释图，最后回扣结论并转场。'),sources=refs(keys),dark=dark)
 p['from']=p.pop('from_')
 if label:p['label']=label
 (R/'pages'/f'P{n:02}.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
 evidence=R/'appendix/source_evidence';evidence.mkdir(exist_ok=True)
 for k in keys:
  sha,f,a,b,fn=S[k];src=R.parent/('source_gitcode' if sha==CUR else 'source_audio_5_1')/f
  lines=src.read_text(encoding='utf-8').splitlines()
  (evidence/f'{k}.txt').write_text(refs([k])[0]+'\n'+'\n'.join(f'{i+1}: {lines[i]}' for i in range(a-1,min(b,len(lines)))),encoding='utf-8')
 sync();print('Authored',n,title)
