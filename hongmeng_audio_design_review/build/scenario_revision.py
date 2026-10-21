"""Author six editable mechanism slides. Coordinates are CSS pixels."""
from pathlib import Path
import json, math

BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'audio_scenario'
for d in ['pages','previews','assets/diagrams','build/.private']:
    (OUT/d).mkdir(parents=True,exist_ok=True)
E=[]
def t(x,y,w,h,s,size=25,c='navy',b=False,a='left'): E.append(['text',x,y,w,h,s,size,c,b,a])
def r(x,y,w,h,c='none',stroke='none',sw=0): E.append(['rect',x,y,w,h,c,stroke,sw])
def l(x,y,X,Y,c='light',sw=2): E.append(['line',x,y,X,Y,c,sw])
def a(x,y,X,Y,c='blue',dash=False): E.append(['arrow',x,y,X,Y,c,dash])
def n(x,y,w,h,s,c='blue',size=24): E.append(['node',x,y,w,h,s,c,size])
def reveal(k): E.append(['reveal',k])
def blocks(x,y,count=4,c='teal',w=24,h=26,gap=8):
    for i in range(count): r(x+i*(w+gap),y,w,h,c)
def rule(y): l(64,y,1214,y)
def tag(x,y,s='音乐 A'): n(x,y,140,45,s,'teal',24)
def wave(x,y,w,h,fade=False,cut=False):
    # Editable evidence: an explicitly schematic waveform, not a recorded signal.
    last=None
    for i in range(81):
        f=i/80
        amp=(1-f) if fade else 1
        yy=y-math.sin(f*math.pi*8+0.8)*h*amp
        if cut and f>.55: yy=y
        cur=(x+f*w,yy)
        if last:l(*last,*cur,'amber' if cut else 'teal',2)
        last=cur

sha='3a2688e805df970739e3b0cebf9cc05d8cb24e9b'
url=f'https://gitcode.com/openharmony/multimedia_audio_framework/blob/{sha}/services/audio_engine/manager/src/hpae_renderer_manager.cpp'
scripts=[]
def save(i,title,foot,script,cue,sources,minutes=1.5):
    p=dict(n=i,title=title,titleSize=42,takeaway='',section='',elements=E.copy(),
      footer=foot,minutes=minutes,objective=title,script=script,next='',boundary=foot,cue=cue,
      pacing='先看初始图，再按鼠标逐步揭示。每次点击后沿编号指图解释。',sources=sources)
    p['from']='音乐 A 始终表示同一路音乐播放会话'
    (OUT/'pages'/f'P{i:02}.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf8')
    scripts.append(f'## {i}. {title}\n\n{script}\n\n演示顺序：{cue}\n\n范围：{foot}\n\n依据：\n'+ '\n'.join('- '+s for s in sources))
    E.clear()

# 1 — one recognizable stream, operations attached to the affected part.
t(64,139,1120,42,'扬声器正在放歌。我们暂停一下，继续播放，再切到耳机。',28,'gray')
tag(64,350)
t(64,403,140,52,'同一路音乐\n后文称“会话”',20,'gray',False,'center')
r(274,338,180,70,'none','light',2);blocks(291,360,4)
t(274,423,180,34,'待处理的数据',23,'gray',False,'center')
n(535,338,180,70,'增益与音效','navy',26)
n(824,338,180,70,'设备输出','navy',26)
t(1060,351,155,45,'扬声器',27,'teal',True)
a(204,373,274,373,'teal');a(454,373,535,373,'teal');a(715,373,824,373,'teal');a(1004,373,1054,373,'teal')
reveal(1)
t(472,228,300,40,'① 暂停   ② 恢复',29,'blue',True,'center')
a(625,275,625,331,'blue',True)
t(450,508,350,68,'先改变增益，\n还要处理连接和播放状态。',25,'navy',False,'center')
reveal(2)
t(887,228,320,40,'③ 切到耳机',29,'blue',True,'center')
a(1048,276,1048,302,'blue',True);a(1048,302,914,302,'blue',True);a(914,302,914,331,'blue',True)
t(904,508,290,68,'换输出设备，\n也要改变处理连接。',25,'navy',False,'center')
save(1,'一首歌，三个操作','实线表示数据；虚线表示控制。处理链为简化示意。',
 '先看这一条线。音乐 A 是同一路播放会话，数据已经在缓冲中等待处理，经过增益和音效后送往扬声器。这里不展开全部节点，只保留后面会改变的部分。\n\n第一次点击：暂停和恢复首先涉及增益，但还会改变输入连接和播放状态。暂停需要让声音平顺地停下来，恢复则要让新的播放状态不被旧操作破坏。\n\n第二次点击：切耳机改变了输出设备，也改变了会话应该接入的处理链。接下来从暂停开始，看这些动作怎么落实。',
 '初始显示一条数据链；第一次点击显示暂停与恢复；第二次点击显示设备切换。',
 [url+'#L919',url+'#L1110',url+'#L872'],1)

# 2 — why fade, and a shared timeline for control, data and state.
t(64,140,270,35,'直接截断',25,'amber',True)
wave(240,186,210,22,cut=True);t(480,163,240,40,'波形可能突然跳变',23,'gray')
t(767,140,270,35,'逐渐降低增益',25,'teal',True)
wave(982,186,210,22,fade=True)
rule(232)
for x,lab in [(300,'提出暂停'),(570,'开始淡出'),(850,'淡出结束'),(1110,'完成收尾')]:
    t(x-75,247,180,35,lab,24,'navy',True,'center');l(x,291,x,576,'light',1)
t(64,311,190,38,'控制请求',23,'blue',True)
a(300,330,570,330,'blue',True);t(358,294,170,32,'等待执行',21,'gray')
reveal(1)
a(850,330,1110,330,'blue',True);t(873,291,225,32,'完成处理再次排队',21,'gray')
t(64,402,190,38,'输入连接',23,'teal',True)
l(300,422,1088,422,'teal',4)
t(357,379,390,32,'仍相连，继续处理以完成淡出',23,'teal')
l(1100,410,1120,434,'amber',4);l(1120,410,1100,434,'amber',4)
t(1126,402,90,38,'断开',23,'gray')
t(64,492,190,38,'增益',23,'gray',True)
l(300,496,570,496,'teal',4);l(570,496,850,555,'teal',4);l(850,555,1190,555,'teal',4)
t(340,546,170,35,'播放中',23,'gray')
t(647,567,300,35,'正在暂停',23,'amber',True,'center')
t(1108,567,110,35,'已暂停',23,'gray')
reveal(2)
t(64,618,1130,36,'“淡出结束”和“输入断开”是两个时刻，中间还可能等待执行。',27,'navy',True)
save(2,'暂停时，先淡出，再断开','正常淡出路径；波形与时间均为示意，不代表设备实测。',
 '直接截断一段幅度不为零的波形，可能产生突变。先逐渐降低增益，可以减轻这种突变。看下面的时间轴：暂停请求提出之后，先等待设备侧执行。\n\n第一次点击：开始淡出时，输入连接必须保留，否则后面的处理无法完成。增益逐渐下降，淡出完成后的处理再次进入请求队列。等这个请求执行，才暂停相关音效、断开输入、更新会话状态。图上的“正在暂停”对应设备侧会话状态，不是用户界面的状态。\n\n第二次点击：声音的渐变结束和输入连接拆除不是一个时刻。理解这个等待窗口，下一页的恢复交错就不神秘了。若缺少增益节点、设备未运行或处于相应旁路条件，实现也允许直接完成，本页专讲正常淡出路径。',
 '先看两种波形与暂停请求；第一次点击揭示淡出、完成排队和断开；第二次点击强调两个时刻。',
 [url+'#L1110',url+'#L1777',url+'#L1868'],1.7)

# 3 — make publication / execution ordering concrete without claiming API interleaving.
t(64,139,1140,39,'淡出刚结束时，恢复请求已经排在前面。',28,'gray')
t(64,212,215,35,'待执行请求',24,'blue',True)
t(312,211,300,32,'下一条先执行',21,'gray')
n(312,254,285,62,'① 恢复播放','blue',27)
n(682,254,350,62,'② 淡出完成后的收尾','amber',25)
a(670,285,609,285,'gray')
t(1053,260,160,62,'随后加入\n等待执行',21,'gray')
rule(346)
tag(64,392)
t(64,449,160,32,'播放状态',22,'gray')
reveal(1)
t(312,372,360,37,'执行 ① 恢复播放',27,'blue',True)
n(312,437,250,55,'正在播放','teal',27)
t(312,512,345,65,'输入保持连接\n恢复所需的增益已安排',24,'gray')
reveal(2)
t(724,372,470,37,'执行 ② 旧的暂停收尾',27,'amber',True)
t(724,435,470,42,'检查：现在已经在播放',28,'navy',True)
l(724,492,1195,492,'teal',4)
t(724,514,470,66,'结束这次收尾处理，\n不暂停音效、不拆输入连接。',25,'teal',True)
save(3,'已经恢复播放，旧的暂停还会生效吗？','一种请求交错；不表示每次快速点击都能触发。这里只讨论恢复后尚未再次暂停的情况。',
 '上一页中，淡出完成后的收尾需要等待执行。本页选择一种具体交错：恢复请求已经排在前面，淡出完成请求随后加入。队列左侧是下一条要执行的请求。这里描述的是引擎执行顺序，不把界面点击等同于可任意并发的客户端调用。\n\n第一次点击：恢复请求先执行，会话回到正在播放，输入相连，恢复所需的淡入已安排。\n\n第二次点击：旧的暂停收尾终于执行。假如不检查状态，它就会暂停相关音效、拆掉输入，并写回暂停状态。实际处理会先检查当前是否已经恢复运行；如果是，就结束本次收尾，保留当前通路。\n\n这个检查针对图示交错。它不是给所有旧事件加了代次号，也不能据此宣称任意多次暂停恢复的交错都由这一个判断解决。',
 '初始只显示待执行请求及音乐 A；第一次点击执行恢复；第二次点击执行旧的收尾并显示检查结果。',
 [url+'#L919',url+'#L1777'],1.8)

# 4 — counterfactual / actual order, same coordinate system.
t(64,136,1140,42,'已有音频数据等待处理时，接通之后的增益设置不能拖后。',27,'gray')
for x,lab in [(350,'接通处理链'),(620,'音效启动中'),(1000,'音效启动完成')]:
    t(x-50,208,235,35,lab,23,'gray',False,'center');l(x,252,x,583,'light',1)
t(64,281,230,65,'如果淡入设置晚了',25,'amber',True)
r(350,286,650,57,'#F9EBDC');t(365,297,615,35,'这段窗口内，预缓冲数据可能按全增益输出',23,'amber',True,'center')
l(350,385,1000,385,'amber',4)
t(350,351,390,30,'增益尚未按淡入设置',21,'amber')
t(1025,292,175,65,'到这时\n才设置淡入',23,'amber',True)
reveal(1)
rule(423)
t(64,467,230,65,'实际处理顺序',25,'teal',True)
n(350,472,205,53,'先设置淡入','teal',25)
a(555,498,615,498,'blue',True)
t(636,473,360,50,'再启动会话音效',26,'navy',True)
l(350,582,1000,540,'teal',4)
t(645,601,510,35,'示意：已有数据按淡入处理',23,'teal')
save(4,'淡入为什么要先于音效启动？','上行为假设的错误顺序，下行为实际顺序；增益曲线仅示意，不表达淡入时长。',
 '只知道“恢复时会淡入”还不够，设置的时机也影响声音。先看上行假设：处理链已经接上，应用又预先准备了数据。如果先启动会话音效，等启动完成才设置淡入，这段窗口里就可能有数据按全增益输出。上行是用来说明风险的反事实，不是在描述某个历史版本。\n\n点击后看下行：实际顺序是在接入之后立即安排淡入，然后才启动会话音效。实现注释明确解释了预缓冲数据和音效启动耗时带来的窗口。上下行用同一时间方向比较先后，增益曲线只是说明淡入已经安排，不能读成淡入在音效启动前一定完成。',
 '先展示设置偏晚的风险窗口；点击后展示实际顺序与增益示意。',
 [url+'#L919'],1.3)

# 5 — three snapshots. A remains visibly the same object, never an intermediate station.
t(64,138,1140,40,'同一路音乐保留下来，设备归属和处理连接随目标变化。',27,'gray')
for y in [293,446]: rule(y)
t(64,214,170,37,'① 切换前',27,'navy',True)
tag(254,209)
a(394,232,490,232,'teal')
n(490,204,350,56,'扬声器侧处理链','navy',25)
a(840,232,915,232,'teal');t(936,209,250,42,'扬声器出声',26,'teal',True)
t(490,264,620,26,'会话归属：扬声器',21,'gray')
reveal(1)
t(64,360,170,37,'② 交接中',27,'navy',True)
tag(254,355)
l(394,377,430,377,'gray',2);l(440,366,460,389,'amber',3);l(460,366,440,389,'amber',3)
t(492,327,680,38,'摘除旧连接，交接同一个会话',26,'navy',True)
t(492,373,700,32,'设备信息改为耳机；处理帧长按目标条件调整',24,'gray')
reveal(2)
t(64,515,170,37,'③ 接入后',27,'navy',True)
tag(254,509)
a(394,532,490,532,'teal')
n(490,504,350,56,'耳机侧处理链','teal',25)
a(840,532,915,532,'teal');t(936,509,250,42,'耳机输出',26,'teal',True)
t(490,568,650,31,'会话归属更新；运行中的会话接入目标链',23,'gray')
save(5,'切到耳机，哪些东西变了？','普通迁移路径示意；交接中不承诺零间隙，接入成功也不等于声学输出已稳定。',
 '第一幅是切换前：音乐 A 接到扬声器侧处理链，管理层把它归属到扬声器。设备策略已经选定耳机作为目标，我们只看引擎怎样执行迁移。\n\n第一次点击：旧设备侧移除输入会话，但持有同一个输入节点并将其交接出去。音乐 A 的身份延续。目标侧接收后，更新设备相关信息，并依据目标采样率和处理帧长度调整处理粒度。帧粒度可以理解为一轮处理多少音频数据，不是歌曲的播放进度。不同设备的具体数值依配置而定，本页不编造固定参数。\n\n第二次点击：目标侧创建或接入相应处理簇，符合连接条件且会话处于运行状态时，接入耳机侧处理链。管理层更新会话映射。这些动作跨越异步交接，图只表达阶段，不把映射更新画成所有设备动作完成的同步栅栏。目标不可用和状态变化会走其他分支。',
 '先看切换前；第一次点击看断开和参数调整；第二次点击看目标连接与归属变化。',
 [url+'#L872',url+'#L114',f'https://gitcode.com/openharmony/multimedia_audio_framework/blob/{sha}/services/audio_engine/manager/src/hpae_manager.cpp#L1181'],2)

# 6 — return to same signal path and a concrete next question.
t(64,140,1140,40,'回到这一路音乐，三个操作分别改变了什么？',28,'gray')
tag(64,319)
a(204,341,280,341,'teal')
r(280,307,175,68,'none','light',2);blocks(293,329,4)
n(535,307,190,68,'增益与音效','navy',26)
n(873,307,220,68,'设备处理链','navy',26)
a(455,341,535,341,'teal');a(725,341,873,341,'teal');a(1093,341,1200,341,'teal')
reveal(1)
t(64,433,300,37,'暂停',29,'amber',True)
t(64,483,325,74,'完成淡出，\n再断开输入。',27,'navy')
t(450,433,300,37,'恢复',29,'blue',True)
t(450,483,325,74,'执行旧请求前，\n确认是否已恢复。',27,'navy')
t(836,433,350,37,'切耳机',29,'teal',True)
t(836,483,350,74,'交接同一个会话，\n接入目标设备链。',27,'navy')
reveal(2)
rule(590)
t(64,613,1140,47,'这些动作都要及时完成，线程与队列该怎样组织？',32,'navy',True)
save(6,'再看这三个操作','下一部分：在相同普通输出路径下，对比 PA 与 HPAE 的执行组织。',
 '回到第一页的音乐 A。缓冲、增益和设备链还是这几个对象。第一次点击：暂停要求让增益变化做完再拆输入；恢复要求旧请求执行时重新看状态；切设备要求同一个会话进入目标设备处理链。\n\n第二次点击：这些动作都要及时完成，背后的线程、队列以及缓冲该怎样安排？这才是下一部分比较 PA 和 HPAE 的具体问题。我们将看控制请求经过哪些交接、音频处理在哪个线程完成，以及设备迁移如何组织节点生命周期。这里不把上述能力说成 HPAE 独有，也不从结构图推导未测量的时延或功耗幅度。',
 '先回到同一路音乐；第一次点击回顾三处具体动作；第二次点击提出线程与队列问题。',
 [url+'#L1110',url+'#L1777',url+'#L872'],1)

(OUT/'speaker_notes.md').write_text('# 一首歌，三个操作 · 修订讲稿\n\n六页主讲，按点击顺序揭示。时长需以实际试讲为准。\n\n'+'\n\n'.join(scripts)+'\n',encoding='utf8')
print('Authored six revised slides and speaker notes')
