from redesign import *
e=[t(64,251,540,38,'5.1 PA：控制与 sink I/O 握手',26,'gray',True),t(680,251,535,38,'当前 HPAE：跨 Manager 接图',26,'blue',True),l(635,250,635,601)]
old=['MOVE 命令 → pa_sink_input_move_to','START_MOVE 同步到旧 I/O：detach','更新 sink / resampler / volume','FINISH_MOVE 同步到目标 I/O：attach']
new=['MoveStream 请求进入旧 Renderer','保留 SinkInput，断旧连接后回调','目标 AddNodeToSink 再次入队','更新设备 / span，RUNNING 才连接']
for x,items,c in [(64,old,'navy'),(680,new,'blue')]:
 for i,s in enumerate(items):
  y=328+i*64;e += [box(x,y,535,48,s,c,18)]
  if i<3:e += [a(x+267,y+48,x+267,y+64,c)]
e += [t(64,615,1150,38,'两种方案都复用输入对象；差异在跨线程同步、状态衔接和处理连接的组织方式',22,'navy',True)]
save(20,'A5  设备迁移：PA 与 HPAE 的真实设计对照','旧方案已有输入对象复用，自研用 Manager 与节点图组织迁移',e,'PA的libpulse发送MOVE_SINK_INPUT，控制上下文通过pa_sink_input_move_to迁移同一个sink_input。start_move同步向旧sink I/O发START_MOVE，让其detach并处理rewind。finish_move更新sink、resampler和音量，然后同步向目标I/O发FINISH_MOVE，目标attach并按latency条件处理drop/rewind。控制侧完成hook与订阅通知，协议ACK返回。两次send是等待I/O处理的握手；ACK也不等于声学切换无间隙。\n新HPAE同样保留输入对象，旧Renderer在设备队列中断旧图并回调，HpaeManager交目标Renderer再次入队，更新设备信息与span，根据RUNNING状态连接目标过程簇。这里的设计对照是执行上下文、同步边界和节点状态组织，不是“旧方案重建流、新方案才复用对象”。两边都有可移动性或格式条件，不能推广任意流无损迁移。',['oldpolicy','move','detach','movein','attach','span'],'PA同步send等待I/O处理；HPAE请求入队不等于目标执行完毕','旧PA固定bc6e4fe5；不把对象复用作为自研独有创新。')
p=R/'pages/P20.json';d=json.loads(p.read_text(encoding='utf-8'))
base='https://gitcode.com/openharmony/third_party_pulseaudio/blob/bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca/'
d['sources'] += [f'PA move协议：{base}src/pulsecore/protocol-native.c#L4483',f'PA start_move / finish_move / move_to：{base}src/pulsecore/sink-input.c#L1867',f'PA finish_move：{base}src/pulsecore/sink-input.c#L2159',f'PA sink I/O START_MOVE / FINISH_MOVE：{base}src/pulsecore/sink.c#L2748']
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
