from redesign import *
p=R/'pages/P01.json';d=json.loads(p.read_text(encoding='utf-8'))
d.update(title='一段声音的旅程',takeaway='鸿蒙音频底座的协同与自研演进',section='技术分享',minutes=0.5,titleSize=52,
 objective='30秒开题，只交代研究对象和主线，不重复Start完成语义。',
 script='今天沿启动、暂停和切换设备三个操作，拆开鸿蒙音频底座的执行过程。重点比较PA旧方案与自研引擎：线程交接怎样减少，控制消息怎样并发发布，处理节点怎样随状态安全地连接和拆除。先看一次播放涉及哪些对象，然后进入实际调用和数据处理。',
 pacing='开场约30–45秒，按稿正常讲述；不安排停顿或互动补足时长。',
 next='用P02定位对象与通道，P03才完整展开Start时序。',
 footer='依据固定OpenHarmony源码；具体产品量化收益另行测量',
 elements=[t(64,292,1150,64,'从 Start、Pause、Move 进入真实执行过程',36,'navy',True),
 t(64,406,1150,92,'线程交接怎样减少\n消息与节点怎样安全改变正在运行的通路',31,'blue'),
 t(64,583,1150,45,'PA 5.1 与当前 HPAE 的源码设计对照',26,'gray')],
 teaching_status='P01修订待教学密度复审')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('P01 changed to 30-second opening')
