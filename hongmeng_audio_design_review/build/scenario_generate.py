from pathlib import Path
import json,re

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
def blocks(x,y,count=4,c='blue',w=22,h=25,gap=7):
    for i in range(count): r(x+i*(w+gap),y,w,h,c)
def bottom(s): l(64,604,1214,604);t(64,617,1140,35,s,26,'navy',True)
raw=(BASE/'hongmeng_audio_design_review/用户场景主线_逐页讲稿.md').read_text(encoding='utf8')
sections=re.split(r'## 第 \d 页',raw)[1:7]
def save(i,title,take,foot,minutes=1.5):
    script=sections[i-1] if len(sections)>=i else ''
    p=dict(n=i,title=title,takeaway=take,titleSize=42,section='一首歌，三个操作',elements=E.copy(),
           footer=foot,minutes=minutes,objective=take,script=script,
           next='',boundary=foot,cue='按图中编号依次讲述；本文件为静态可编辑页，不含自动动画。',
           pacing='先定位用户操作，再沿控制与数据关系推演，最后指出设计约束。',
           sources=['本地源码基线 3a2688e805df970739e3b0cebf9cc05d8cb24e9b；核验依据见讲稿中的源码落点。'])
    p['from']='延续同一个播放会话'
    (OUT/'pages'/f'P{i:02}.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf8')
    E.clear()

# 1: shared system map, with meaningful control/data relationships
t(64,236,1140,38,'暂停一下                 继续播放                 切到耳机',32,'navy',True)
l(64,290,1214,290)
t(64,320,150,32,'控制与状态',23,'gray',True)
n(244,316,190,55,'用户操作','blue')
n(530,316,215,55,'流状态与设备选择','navy',23)
n(860,316,240,55,'设备处理请求','blue')
a(434,343,530,343,'blue',True);a(745,343,860,343,'blue',True)
a(980,371,980,402,'blue',True)
l(777,402,980,402,'blue',2);a(777,402,777,445,'blue',True)
t(64,454,150,32,'音频数据',23,'teal',True)
n(244,445,170,65,'同一播放会话','teal',23)
r(460,445,156,65,'none','light',2);blocks(474,463,4,'teal')
t(460,519,160,30,'缓冲中的数据',21,'gray',False,'center')
n(674,445,207,65,'格式／增益／音效','navy',22)
n(950,445,150,65,'输出设备','teal')
a(414,477,460,477,'teal');a(616,477,674,477,'teal');a(881,477,950,477,'teal')
bottom('操作随时到来，音频处理还在持续进行。')
save(1,'一首歌，三个日常操作','从用户操作出发，看控制请求怎样改变正在流动的声音。','实线：音频数据    虚线：控制与通知；图为职责关系，非完整线程拓扑',1)

# 2 pause timeline
xs=[245,490,760,1020]
for x,lab in zip(xs,['① 暂停请求','② 开始淡出','③ 淡出完成','④ 断开输入']):
    t(x-36,235,225,36,lab,25,'navy',True)
    l(x,282,x,568,'light',1)
t(64,302,145,40,'控制处理',23,'blue',True)
a(245,323,490,323,'blue',True);t(292,286,175,28,'排队后执行',20,'gray')
a(760,323,1020,323,'blue',True);t(792,286,194,28,'完成请求再次入队',20,'gray')
t(64,398,145,40,'数据通路',23,'teal',True)
blocks(230,406,5,'teal',26,25,10)
a(420,419,490,419,'teal')
r(490,392,270,54,'#E1F2EF');t(506,398,240,40,'继续处理，完成淡出',23,'teal',True,'center')
a(760,419,995,419,'teal');l(1008,405,1028,433,'amber',4);l(1028,405,1008,433,'amber',4)
t(1044,401,162,36,'输入已断开',22,'gray')
t(64,493,145,38,'增益变化',23,'gray',True)
l(245,500,490,500,'teal',4);l(490,500,760,552,'teal',4);l(760,552,1135,552,'teal',4)
t(260,538,165,35,'播放中',23,'gray')
t(530,550,210,35,'正在暂停',23,'amber',True)
t(1030,550,150,35,'已暂停',23,'gray')
bottom('淡出期间保持输入连接，声音处理完成后再收尾。')
save(2,'暂停：控制请求与声音变化需要衔接','暂停已经提出，不代表音频数据可以立即停止处理。','普通活跃播放示意；无增益节点、设备未运行等条件可直接完成。时间不按比例。',1.7)

# 3 condition sequence
t(65,235,680,32,'一种需要防护的执行交错',26,'navy',True)
t(835,235,360,32,'完成请求执行时，再看当前状态',24,'navy',True)
l(785,236,785,582)
for y,num,lab,sub in [
 (291,'1','暂停进入淡出','输入仍相连'),
 (369,'2','淡出结束，完成请求等待执行','异步通知存在排队窗口'),
 (447,'3','恢复请求先执行','当前会话已恢复播放'),
 (525,'4','旧的完成请求随后执行','此时还能断开输入吗？')]:
    t(66,y,40,38,num,28,'blue',True)
    t(120,y,620,32,lab,25,'navy',True)
    t(120,y+34,620,28,sub,20,'gray')
    if num!='4': a(85,y+42,85,y+72,'light')
n(845,299,330,58,'当前已恢复播放？','navy',26)
a(910,357,910,420,'teal',True);t(925,371,100,30,'是',23,'teal',True)
n(835,425,175,63,'保留当前连接','teal',22)
a(1110,357,1110,420,'gray',True);t(1123,371,70,30,'否',23,'gray')
r(1030,425,174,63,'none','light',2);t(1037,430,160,52,'继续暂停收尾',21,'gray',True,'center')
blocks(840,539,4,'teal',23,22);a(967,550,1187,550,'teal')
t(846,502,340,30,'已经恢复的数据通路继续工作',21,'teal')
bottom('完成通知属于过去的操作，后续动作必须符合当前状态。')
save(3,'恢复：迟到的完成通知不能拆掉当前通路','在执行后续动作的那一刻，检查会话是否已经恢复播放。','条件时序示意；快速点击不保证产生此交错，客户端也有状态检查与等待。',1.8)

# 4 control order with data buffer
for x,num,title in [(254,'1','接入处理链'),(570,'2','设置淡入'),(910,'3','启动会话音效')]:
    t(x-30,244,250,38,f'{num}  {title}',28,'navy',True)
a(435,263,535,263,'blue',True);a(755,263,875,263,'blue',True)
r(246,314,240,228,'none','light',2)
t(268,329,200,36,'已准备的音频数据',23,'navy',True)
blocks(270,390,5,'teal',29,34,9)
blocks(270,437,3,'teal',29,34,9)
t(267,491,205,30,'接通后即可参与处理',21,'gray')
a(488,418,560,418,'teal')
r(570,314,265,228,'#E1F2EF')
t(590,329,225,36,'先布置增益变化',24,'teal',True)
l(595,477,810,477,'light',2);l(595,477,810,387,'teal',4)
t(590,491,225,30,'第一段声音按淡入处理',21,'teal')
r(886,314,319,228,'none','light',2)
t(907,329,280,36,'音效启动需要处理时间',24,'navy',True)
l(913,416,1180,416,'blue',5);l(913,405,913,427,'blue',3);l(1180,405,1180,427,'blue',3)
t(907,446,270,70,'已有预缓冲数据时，\n淡入不能等到这之后',24,'gray')
bottom('连接后及时设置淡入，避免启动窗口内出现全增益输出。')
save(4,'恢复播放：第一段声音的增益要先安排好','处理链接入之后，音效启动之前，先布置淡入。','按启用会话音效的路径示意；图为控制顺序与数据条件，不表示数据串行流过这些步骤。',1.3)

# 5 migration with old/new regions and center handoff
t(64,235,1140,36,'设备选择确定目标；引擎负责交接播放会话并适配目标处理链。',25,'gray')
for x,title,col in [(64,'扬声器处理区域','gray'),(850,'耳机处理区域','teal')]:
    r(x,301,364,271,'none','light',2)
    t(x+18,315,325,35,title,27,col,True)
n(90,377,307,49,'旧输入连接','gray',24)
n(90,460,142,40,'格式适配','gray',21)
n(250,460,147,40,'增益／音效','gray',20)
a(232,480,250,480,'gray')
t(90,520,307,32,'扬声器输出',23,'gray',True,'center')
a(161,426,161,460,'gray')
a(323,500,323,520,'gray')
l(151,435,171,451,'amber',3);l(171,435,151,451,'amber',3)
t(196,428,200,29,'旧连接摘除',20,'amber',True)
n(498,363,278,65,'同一个播放会话','teal',27)
t(502,438,274,58,'会话标识延续\n相关状态随迁移交接',23,'gray',False,'center')
a(397,401,498,401,'blue',True)
a(776,401,878,401,'blue',True)
n(878,377,307,49,'目标侧接收并安排接入','teal',23)
n(878,460,142,40,'格式适配','teal',21)
n(1038,460,147,40,'增益／音效','teal',20)
a(1020,480,1038,480,'teal')
a(949,426,949,460,'teal')
a(1111,500,1111,520,'teal')
t(973,428,225,29,'运行中则建立连接',20,'teal')
t(878,520,307,32,'耳机输出',23,'teal',True,'center')
t(65,280,360,27,'① 从旧设备侧摘除',21,'gray')
t(497,280,280,27,'② 交接输入会话',21,'blue')
t(850,280,360,27,'③ 适配并接入目标侧',21,'teal')
t(500,521,290,54,'设备信息、帧粒度更新\n管理层更新会话归属',22,'navy',True,'center')
bottom('会话继续存在，设备相关信息与处理连接随目标改变。')
save(5,'切到耳机：播放会话进入另一条设备处理链','用户换了出声位置，运行中的连接与设备参数也要一起调整。','迁移存在检查和异步交接；管理侧成功通知不等于目标设备声学输出已稳定。',2)

# 6 common base consolidated, richer than table summary
t(64,235,1140,35,'同一个引擎，同时协调控制进度、数据处理和设备连接。',26,'gray')
labels=[(64,'暂停','等待淡出完成','中间状态连接声音变化与收尾动作','amber'),
        (450,'恢复','执行前看当前状态','避免旧的完成通知破坏新播放','blue'),
        (836,'切换设备','迁移会话并适配目标','保持会话归属与处理链一致','teal')]
for x,title,sub,desc,c in labels:
    t(x,299,350,45,title,34,c,True)
    l(x,360,x+345,360,c,4)
    t(x,382,350,36,sub,27,'navy',True)
    t(x,433,345,68,desc[:12]+'\n'+desc[12:] if len(desc)>16 else desc,23,'gray')
r(64,550,1117,43,'#E5EBF3')
t(75,550,1095,43,'控制请求与执行时机        音频数据与缓冲        会话与设备处理链',25,'navy',True,'center')
bottom('理解这些协作，再比较 PA 与 HPAE 如何组织线程、请求和处理图。')
save(6,'音频引擎把用户操作落实到声音处理','顺畅的体验，来自控制状态与持续数据处理之间的协调。','本段聚焦普通播放机制；性能与切换体验的量化结论需要设备测试。',1)

# Reuse the established native-object renderer with separate output paths.
source=(BASE/'hongmeng_audio_design_review/build/deck.mjs').read_text(encoding='utf8')
source=source.replace("const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');",
                      "const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../audio_scenario');")
source=source.replace('鸿蒙音频底座_技术深化版','一首歌三个操作_音频引擎场景版')
(BASE/'hongmeng_audio_design_review/build/scenario_deck.mjs').write_text(source,encoding='utf8')
print('Authored 6 scenario pages')
