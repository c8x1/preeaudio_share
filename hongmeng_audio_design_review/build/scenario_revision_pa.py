"""Author the PA-vs-HPAE structure comparison slides. Coordinates are CSS pixels."""
from pathlib import Path
import json

BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'audio_pa_compare'
for d in ['pages','previews','assets/diagrams','build/.private']:
    (OUT/d).mkdir(parents=True,exist_ok=True)
E=[]
def t(x,y,w,h,s,size=25,c='navy',b=False,a='left'): E.append(['text',x,y,w,h,s,size,c,b,a])
def r(x,y,w,h,c='none',stroke='none',sw=0): E.append(['rect',x,y,w,h,c,stroke,sw])
def l(x,y,X,Y,c='light',sw=2): E.append(['line',x,y,X,Y,c,sw])
def a(x,y,X,Y,c='blue',dash=False): E.append(['arrow',x,y,X,Y,c,dash])
def n(x,y,w,h,s,c='blue',size=24): E.append(['node',x,y,w,h,s,c,size])
def reveal(k): E.append(['reveal',k])

sha='0d073de5a30f33ab6716d9abd481d76eca843741'
tag='OpenHarmony-v5.1.0-Release'
blob='https://gitcode.com/openharmony/multimedia_audio_framework/blob'
hdi=f'{blob}/{tag}/frameworks/native/pulseaudio/modules/hdi/hdi_sink.c'
gain=f'{blob}/{sha}/services/audio_engine/node/src/hpae_gain_node.cpp'
limiter=f'{blob}/{sha}/services/audio_engine/node/src/hpae_limiter_node.cpp'
rman=f'{blob}/{sha}/services/audio_engine/manager/src/hpae_renderer_manager.cpp'

scripts=[]
appendix=[]
def save(i,title,foot,scope,script,cue,sources,minutes=1.5):
    p=dict(n=i,title=title,titleSize=42,takeaway='',section='',elements=E.copy(),
      footer=foot,minutes=minutes,objective=title,script=script,next='',boundary=scope,cue=cue,
      pacing='先看初始图，再按鼠标逐步揭示。每次点击后沿编号指图解释。',sources=sources)
    p['from']='承接《一首歌，三个操作》结尾的提问：换一个引擎会怎样'
    (OUT/'pages'/f'P{i:02}.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf8')
    scripts.append(f'## {i}. {title}\n\n{script}')
    appendix.append(f'### P{i} {title}\n\n演示顺序：{cue}\n\n范围：{scope}\n\n依据：\n'+ '\n'.join('- '+s for s in sources))
    E.clear()

# 1 — the same guarantee, written how many times.
t(64,136,1140,42,'暂停恢复的淡入淡出，这一个保证，两边各写了几遍。',27,'gray')
reveal(1)
r(64,200,560,380,'none','gray',2)
t(84,214,520,35,'PA · HDI sink 模块',24,'gray',True)
t(84,254,520,30,'单文件 4823 行 · 190 个函数',21,'gray')
t(84,304,540,30,'主通路：一套淡入完成检查',21,'blue',True)
t(84,338,540,30,'多声道：又一套完成检查',21,'purple',True)
t(84,372,540,30,'低时延通路：专属一组处理',21,'amber',True)
t(84,406,540,30,'状态回调：按流类型 4 个变体',21,'gray',True)
t(84,444,560,24,'DoFading · CheckPrimaryFadeinIsDone',17,'gray')
t(84,470,560,24,'CheckMultiChannelFadeinIsDone · 状态回调 ×4',17,'gray')
t(84,504,540,56,'同文件还装着：设备开关、格式转换 ×8、限幅器、\n缓冲管理、静音检测、内录、会话策略',19,'gray')
reveal(2)
r(656,200,560,380,'none','teal',2)
t(676,214,520,35,'HPAE · 增益节点',24,'teal',True)
t(676,254,520,30,'单节点 521 行 · 一套状态机',21,'teal')
n(676,296,220,52,'增益节点','teal',22)
t(916,300,290,48,'挂标志 → 逐帧执行\n→ 就地回调',19,'navy')
t(676,368,520,30,'主通路 / 多声道 / 低时延：同一个节点',21,'navy')
t(676,400,520,30,'差异只是挂哪条链——挂链时的参数',21,'navy')
t(676,444,520,52,'节点层 32 个文件，一文件一职责；\n每个节点带独立单测',19,'gray')
t(64,614,1140,40,'流类型的差异：PA 织进每个关注点的代码分叉，HPAE 是挂链时的一个参数。',26,'navy',True)
save(1,'同一件事，写了几遍','左为旧方案单模块，右为新引擎节点层；行号与文件见讲稿附录。',
 '对照基于 v5.1.0-Release 的 HDI sink 模块与当前主干的引擎节点层；行数为对应文件实测，其余为结构对照，不构成全维度评价。',
 '上一部分结尾问：换一个引擎，这三个操作会是什么样？先看结构，再看执行组织。\n\n左边是老方案里干活的文件：HDI sink 模块，四千八百行、一百九十个函数，一个文件。设备开关、格式转换、淡入淡出、状态回调、低时延通路、限幅器、缓冲管理，全在里面。\n\n单看“暂停恢复要淡入淡出”这一件事。主通路一套淡入完成检查，多声道又一套，状态回调按流类型写了四个变体。流类型的差异，被织进了每一个关注点的代码里——每支持一种新的流类型，每个关注点都要再分叉一次。\n\n右边是 HPAE 的做法。淡入淡出整个住在增益节点里，五百行出头，一套状态机：挂标志、逐帧执行、就地回调。主通路、多声道、低时延的流，用的是同一个增益节点。它们的差异只决定挂在哪条处理链上，是挂链时的一个参数，不是代码里的分叉。\n\n维护成本的差别就在这：不是谁的代码行数少，而是同一件事要写几遍、改一处要读懂多少。',
 '初始只显示引子；第一次点击展开 PA 侧单模块；第二次点击展开 HPAE 侧节点与底部对照句。',
 [hdi+'#L1094',hdi+'#L1219',hdi+'#L1469',hdi+'#L3025',gain+'#L207'],2)

# 2 — blast radius of two common changes.
t(64,136,1140,42,'两类常见改动，各自要碰多大面积。',27,'gray')
reveal(1)
t(64,198,300,35,'给所有通路加限幅',25,'navy',True)
n(64,246,540,62,'PA：限幅器长在 sink 文件里','gray',22)
t(64,318,540,28,'加一个效果，动的是那个 4823 行的文件',19,'gray')
n(656,246,540,62,'HPAE：挂一个限幅节点进链','teal',22)
t(656,318,540,28,'独立文件、独立单测，不碰别的节点',19,'gray')
reveal(2)
t(64,406,300,35,'接一种新输出设备',25,'navy',True)
n(64,454,540,62,'PA：动 sink 的设备分支与格式转换','gray',21)
t(64,526,540,28,'设备差异写进模块代码',19,'gray')
n(656,454,540,62,'HPAE：节点信息按目标侧填参数','teal',21)
t(656,526,540,28,'帧长采样率来自目标，节点不改',19,'gray')
t(64,614,1140,40,'PA 把流类型与设备差异写成代码分叉；HPAE 把它们变成挂链时的参数。',26,'navy',True)
save(2,'改动半径：加限幅，接新设备','情景为结构对照；具体行号见讲稿附录。',
 '情景为结构对照，未覆盖全部改动类型；老方案的支持面与生态成熟度是另一组维度，不在本页比较。',
 '再看两类最常见的改动，各要碰多大面积。\n\n第一件：给所有通路加限幅。老方案里，限幅器就长在 sink 模块里，加它、改它，动的都是那个四千八百行的文件。HPAE 里它是一个独立的限幅节点，挂进链就行，带着自己的单测。\n\n第二件：接一种新的输出设备。老方案要动 sink 模块里的设备分支和格式转换。HPAE 里节点不关心具体设备：设备信息、帧长、采样率，都是挂到目标侧时填进节点信息的参数。\n\n一个数字收尾：HPAE 的节点层是三十多个文件，每个文件一个职责，最大的一个一千一百行；每个节点有自己的单测，三十多个测试文件。改限幅不用读格式转换，改增益不用碰设备。\n\n所以这一部分的论点先立在这：老方案把流类型和设备差异织进代码分叉，每加一种就全文再分叉一次；HPAE 把它们变成挂链时的参数，每个保证只写一遍。接下来看执行组织——线程和队列——两边又是怎么安排的。',
 '初始只显示引子；第一次点击展开“加限幅”情景；第二次点击展开“接新设备”情景与底部对照句。',
 [hdi+'#L2376',limiter,rman+'#L114'],2)

(OUT/'speaker_notes.md').write_text(
 '# PA 与 HPAE：结构对照 · 讲稿\n\n两页开篇，承接《一首歌，三个操作》的结尾提问。正文为口播语言；演示顺序、范围与源码依据见文末备讲附录。时长需以实际试讲为准。\n\n'
 +'\n\n'.join(scripts)
 +'\n\n# 备讲附录\n\n以下内容不讲，供试讲与答疑准备。\n\n'
 +'\n\n'.join(appendix)+'\n',encoding='utf8')
print('Authored two comparison slides and speaker notes')
