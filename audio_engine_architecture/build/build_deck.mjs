import fs from 'node:fs/promises';
import fsSync from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const P=Presentation.create({slideSize:{width:1280,height:720}});
const C={bg:'#F6F8FB',ink:'#10243A',muted:'#617389',blue:'#3478F6',teal:'#10A5A1',purple:'#87789A',line:'#CCD7E3',pale:'#E7EFFD',white:'#FFFFFF',hw:'#46515E'};
const FONT='Hiragino Sans GB';
const sources={
 kernel:'https://www.kernel.org/doc/html/latest/sound/index.html',
 alsa:'https://docs.kernel.org/sound/alsa-configuration.html',
 pa:'https://wiki.freedesktop.org/www/Software/PulseAudio/',
 paThread:'https://wiki.freedesktop.org/www/Software/PulseAudio/Documentation/Developer/Threading/',
 paName:'https://0pointer.de/blog/projects/pulse-release.html',
 jack:'https://jackaudio.org/api/index.html',
 pwLaunch:'https://blogs.gnome.org/uraeus/2017/09/19/launching-pipewire/',
 pwNews:'https://github.com/PipeWire/pipewire/blob/master/NEWS',
 pwDesign:'https://docs.pipewire.org/page_design.html',
 pwSchedule:'https://docs.pipewire.org/page_scheduling.html',
 pwSession:'https://docs.pipewire.org/page_session_manager.html',
 hpae:'https://gitcode.com/openharmony/multimedia_audio_framework/blob/93f5fd0909cb495bc673f4eeeea6997c56f63114/'
};
if (!process.env.RUNTIME_NODE_MODULES) throw new Error('Set RUNTIME_NODE_MODULES to the Artifact Tool dependency directory');
for (const folder of ['output','build','previews']) await fs.mkdir(path.join(root,folder),{recursive:true});
let S; const notes=[];
function image(name,x,y,w,h){ S.images.add({blob:new Uint8Array(fsSync.readFileSync(path.join(root,'assets/reference',name))),contentType:'image/png',position:{left:x,top:y,width:w,height:h},fit:'contain',alt:name}); }
function frame(x,y,w,h,label){rect(x,y,w,h,'none',C.line);text(label,x+14,y+5,w-28,32,22,C.muted,true);}
function contrast(lines){text('与 PreeAudio 对照',985,224,235,42,25,C.blue,true);text(lines,985,282,235,305,23,C.ink);}

function text(t,x,y,w,h,size=26,color=C.ink,bold=false,align='left'){
 const s=S.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 s.text=t;s.text.style={typeface:FONT,fontSize:size,bold,color,alignment:align,verticalAlignment:'middle',insets:0,autoFit:'none',wrap:'none'};return s;
}
function rect(x,y,w,h,fill,line='none'){return S.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:line,width:line==='none'?0:1.2}})}
function line(x,y,x2,y2,color=C.line,dash=false){return S.shapes.add({geometry:'line',position:{left:Math.min(x,x2),top:Math.min(y,y2),width:Math.abs(x2-x)||.01,height:Math.abs(y2-y)||.01,horizontalFlip:x2<x,verticalFlip:y2<y},fill:'none',line:{fill:color,width:2,style:dash?'dash':'solid'}})}
function arrow(x,y,x2,y2,color=C.blue,dash=false){line(x,y,x2,y2,color,dash);if(y===y2){line(x2-7,y2-5,x2,y2,color);line(x2-7,y2+5,x2,y2,color)}else{line(x2-5,y2-7,x2,y2,color);line(x2+5,y2-7,x2,y2,color)}}
function node(t,x,y,w,h=68,color=C.blue,size=26){rect(x,y,w,h,color);text(t,x+10,y+4,w-20,h-8,size,C.white,true,'center')}
function base(n,title,sub,footer,note,urls){S=P.slides.add();S.background.fill=C.bg;text(title,64,42,1152,64,44,C.ink,true);text(sub,64,121,1152,48,27,C.muted);line(64,190,1216,190);text(footer,64,655,1120,34,17,C.muted);text(String(n).padStart(2,'0'),1202,660,36,28,18,C.muted);const full=note+'\n\n资料来源（查阅日期 2026-10-22）\n'+urls.join('\n');S.speakerNotes.text=full;notes.push({n,title,note:full});}
function table(values,x,y,width,height,widths,size=24){
 const t=S.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width,height,columnWidths:widths,values});
 t.borders.assign({fill:C.line,width:1,style:'solid'});
 for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){
  const cell=t.getCell(r,c);cell.fill=r===0?C.ink:(c===values[0].length-1?C.pale:(r%2?C.white:C.bg));
  cell.text.style={typeface:FONT,fontSize:size,color:r===0?C.white:C.ink,bold:r===0||c===0,verticalAlignment:'middle',alignment:'left',wrap:'none'};
 }
 return t;
}

base(1,'音频引擎的软件架构演进时间线','以 Linux / POSIX 路线为主，观察设备抽象、共享服务和实时处理如何发展',
 '年代表示代表性阶段，各层与路线长期并存。PreeAudio 的定位沿用现有分享材料中的公开源码快照。',
 '建议讲述 2 分钟。这里梳理系统音频软件架构，不是播放器、编解码器或音效算法的历史。1990 年代常见设备接口以 OSS 为例，后续 ALSA 提供驱动及用户态接口。设备抽象层并没有被用户态音频服务取代，现代 Linux 音频服务仍常通过 ALSA 对接设备。2000 年代形成两种侧重：PulseAudio 解决桌面多应用共享与流管理，JACK 侧重专业音频的同步回调与应用互连。PulseAudio 在 2006 年从 Polypaudio 更名，不能把更名年份写成前身诞生年份。PipeWire 在 2017 年正式发布项目，2023 年发布 1.0，逐步在统一媒体图里兼顾桌面与专业用途。PreeAudio 放在当代终端系统路线单独说明，不暗示其由 PipeWire 继承，也不给未经核实的首发年份。',
 [sources.kernel,sources.alsa,sources.paName,sources.jack,sources.pwLaunch,sources.pwNews]);
const tx=[64,355,646,937],tw=260;
const stages=[
 ['1990 年代','设备接口','OSS 等设备接口','应用直接读写设备\n上层承担更多协调'],
 ['1990 年代末起','驱动与库分层','ALSA','统一硬件访问\n为上层服务提供底座'],
 ['2000 年代','用户态音频服务','PulseAudio / JACK','桌面多流管理\n专业同步处理分化'],
 ['2017 年至今','统一媒体图','PipeWire','音视频节点与连接\n兼顾桌面和专业音频']
];
stages.forEach((a,i)=>{text(a[0],tx[i],223,tw,46,29,C.blue,true);line(tx[i],293,tx[i]+tw,293,C.blue);if(i<3)arrow(tx[i]+tw,293,tx[i+1],293);text(a[1],tx[i],320,tw,44,30,C.ink,true);text(a[2],tx[i],382,tw,42,25,C.teal,true);text(a[3],tx[i],444,tw,82,24,C.muted)});
text('2006 年更名为 PulseAudio',646,527,270,25,18,C.muted);text('2023 年发布 1.0',937,527,260,25,18,C.muted);
line(64,560,1216,560);text('当代终端路线',64,578,235,42,26,C.blue,true);text('PreeAudio：在鸿蒙音频框架内组织节点处理，衔接系统策略与设备输出',310,576,890,60,25,C.ink);

base(2,'演进中的四个软件架构变化','新增需求不断改变职责划分，现代方案把更多运行机制明确到框架中',
 '这里比较设计侧重，不表示早期方案完全缺少相关能力，也不构成不同产品的性能排名。',
 '建议讲述 2 分钟。第一行说明硬件差异与服务职责逐步分离。第二行说明多应用共享催生流、Sink 和 Source 等管理对象。第三行说明专业处理要求应用在音频周期内合作，图不只是画出来的连接，还涉及运行依赖。第四行强调控制与数据处理分工。这不是严格按年份逐一发生的替换过程，JACK 的图和实时回调在 2000 年代已经出现。对 PreeAudio 可映射到 Manager 管理连接与状态、Node 承担处理、Cluster 组织一组处理，以及 Policy/Service 与引擎间的职责分工。线程实现不可简单等同，HPAE 原有源码资料显示消息与数据处理在同一工作循环中衔接，不能宣称它完全复制 PipeWire 的主线程/数据线程结构。',
 [sources.alsa,sources.paThread,sources.jack,sources.pwSchedule,sources.pwSession,sources.hpae+'services/audio_engine/manager/src/hpae_signal_process_thread.cpp']);
table([
 ['架构问题','代表性变化','对 PreeAudio 的理解'],
 ['硬件访问','设备接口逐步形成驱动、库和服务分层','引擎经 Sink 对接设备边界'],
 ['多应用共享','音频服务管理流、混音与设备输出','Manager 组织输入流和输出'],
 ['复杂处理组织','处理单元形成图，按依赖交付数据','Node / Cluster 承接处理管线'],
 ['动态状态变化','控制、策略与实时处理明确分工','Policy / Service / Engine 协作']
],64,224,1152,362,[214,510,428],25);
text('架构主线：硬件访问逐步抽象，处理单元逐步组合，运行职责逐步分离',64,600,1152,38,27,C.blue,true);

base(3,'PulseAudio：以流和设备组织音频服务','设计侧重多流共享与设备管理，主循环和实时 I/O 通过消息协作',
 '参考 Gavv（2017，PA 11.1）与官方线程文档重绘。蓝色为 PCM 数据，紫色虚线为控制关系。',
 '图据 Gavv 的源码阅读和实验文章 High-level components、Buffering、Threads 整理，并使用官方 Threading 文档交叉核对。原文版本为 PulseAudio 11.1，不将所有模块细节当作当前产品配置。客户端通过 libpulse 接入 Native 协议，控制和流管理由服务主循环协调，实时 I/O 线程面向 Sink 处理音频。共享内存可以运送 PCM，socket 仍承担协议通信，具体传输取决于环境。sink-input 包含流级格式适配等职责，Sink 汇合多流，经后端输出到 ALSA。图只展开一个常见输出方向。PA 主循环/实时线程分工与 HPAE 的消息/数据执行机制不一一对应。',
 [sources.paThread,'https://gavv.net/articles/pulseaudio-under-the-hood/',sources.hpae+'services/audio_engine/manager/src/hpae_renderer_manager.cpp']);
frame(64,220,210,345,'客户端进程');frame(492,220,452,345,'PulseAudio 服务进程');
node('应用',82,278,174,55,C.hw,26);node('libpulse',82,367,174,55,C.blue,25);arrow(169,333,169,367);
node('Native 协议模块',510,276,194,57,C.purple,22);node('Core / Modules',726,276,200,57,C.purple,22);arrow(704,304,726,304,C.purple,true);
text('主循环',510,343,110,28,20,C.purple);
line(256,393,294,393,C.purple,true);line(294,304,294,393,C.purple,true);arrow(294,304,510,304,C.purple,true);text('socket / 协议',307,265,175,30,20,C.purple);
node('共享内存\nPCM 传输',312,449,160,74,C.teal,23);line(256,401,284,401,C.blue);line(284,401,284,486,C.blue);arrow(284,486,312,486);
text('实时 I/O 线程：pa_rtpoll',510,379,416,31,21,C.muted);
node('sink-input\n适配 / 音量',510,425,194,78,C.blue,22);node('Sink\n混音 / 设备时钟',726,425,200,78,C.blue,22);arrow(472,486,510,486);arrow(704,464,726,464);
arrow(824,333,824,425,C.purple,true);text('pa_asyncmsgq',640,343,170,28,20,C.purple);
arrow(824,503,824,584);node('ALSA 后端与设备',644,584,300,43,C.hw,23);
contrast('PA 以流、Sink\n和设备时钟组织服务\n缓冲承担协调作用\n\nPreeAudio 用节点\n与处理簇组织计算\nManager 管连接状态\n\n比较重点是流管理\n与处理管线的组织');

base(4,'JACK：共享端口缓冲与依赖图调度','跨应用的 process() 回调按连接依赖协作，JACK2 可利用互不依赖的分支',
 '依据 Fons Adriaensen（2014）讲解与 JACK 官方 API 重绘。箭头表示数据依赖，下方说明缓冲与调度职责。',
 '主图是根据 Fons Adriaensen 的 A quick introduction to Jack 的客户端、端口、处理周期和调度说明重绘的教学图，不是 JACK 某一版本的完整内部类图。输入端口把采集结果交给 A、B 两个客户端，C 在两者结果可用后处理，最后写往播放端口。每个客户端链接 libjack 并注册 process() 回调，应用的实时处理线程参与执行；音频端口缓冲可位于共享内存，控制消息与音频样本传输需要区分。JACK server 管理连接和运行周期，Backend 抽象设备访问。JACK1 与 JACK2 的调度实现不同，JACK2 在依赖允许时可并行，不能把所有 JACK 系统概括为固定串行执行，也不能断言任何分支一定同时运行。与 PreeAudio 的主要差异是客户端应用互连图与系统引擎内部处理图的集成边界。',
 [sources.jack,'https://kokkinizita.linuxaudio.org/export/jackpres.pdf']);
node('采集端口',64,321,145,65,C.hw,24);
frame(263,230,217,92,'A 进程 / libjack');node('process() 回调',276,270,191,40,C.blue,21);
frame(263,355,217,92,'B 进程 / libjack');node('process() 回调',276,395,191,40,C.blue,21);
frame(557,289,217,98,'C 进程 / libjack');node('process() 回调',570,333,191,40,C.teal,21);
node('播放端口',821,321,139,65,C.hw,24);
line(209,354,234,354,C.blue);line(234,292,234,415,C.blue);arrow(234,292,276,292);arrow(234,415,276,415);
line(467,292,513,292,C.blue);line(513,292,513,354,C.blue);line(467,415,513,415,C.blue);line(513,354,513,415,C.blue);arrow(513,354,570,354);arrow(761,354,821,354);
text('A、B 可独立处理，C 等待上游结果',263,459,696,35,24,C.blue,true);
rect(263,507,697,43,C.pale);text('端口音频缓冲：共享内存',278,510,667,37,24,C.blue,true,'center');
frame(64,568,896,66,'JACK server');text('Backend / Driver       连接图管理       周期与客户端同步',237,585,700,36,22,C.ink);

contrast('JACK 让处理者按\n共同节奏协作\n端口图决定执行依赖\n\nPreeAudio 用处理簇\n组织引擎内的计算\nManager 管生命周期\n\n共同约束：周期预算\n差异：图的组织尺度\n及状态管理职责');

base(5,'PipeWire：策略管理与媒体图执行分离','控制层配置对象与连接，实时数据线程按图的依赖关系运行',
 '依据官方 Session Manager / Graph Scheduling 文档重绘。此图展开同步图，省略异步节点和复杂设备路径。',
 '以机制和策略分工解释 PipeWire 的设计理念。WirePlumber 决定设备与连接策略，PipeWire 的主线程处理对象配置与 IPC，数据线程执行已准备好的图。Driver 发起周期，节点在依赖满足后运行，通过共享的 activation 记录及 eventfd 协调，缓冲等资源预先准备。图中的依赖唤醒是同步图的简化示例，异步节点另有处理方式。与 PreeAudio 对比：二者都有节点与图，不应把节点化本身当作区别。PipeWire 以通用媒体图为中心，可以跨进程组织媒体处理；本次公开 HPAE 实现以 Manager 组织 Node/Cluster，在工作循环中衔接消息与 Process。PreeAudio 的策略规则由 Policy/Service 与引擎协作，不能宣称策略与机制分工是某一方独有。差异落在图的组织尺度、控制到执行的职责分配，以及场景处理单元的组织。',
 [sources.pwSchedule,sources.pwSession,sources.hpae+'services/audio_engine/manager/src/hpae_signal_process_thread.cpp',sources.hpae+'services/audio_engine/manager/src/hpae_renderer_manager.cpp']);
node('WirePlumber\n设备与连接策略',64,228,258,82,C.purple,25);
node('PipeWire 主线程\n对象 / 连接 / 配置',388,228,572,82,C.purple,26);arrow(322,269,388,269,C.purple,true);
text('控制层：策略决定目标，核心准备图与运行资源',64,327,896,35,24,C.purple);
frame(64,388,896,176,'实时数据线程：按依赖执行图');
node('Driver\n发起周期',87,452,170,75,C.hw,24);node('节点 A\n处理数据',328,452,170,75,C.blue,24);node('节点 B\n消费结果',569,452,170,75,C.teal,24);node('输出',810,452,126,75,C.hw,24);
arrow(257,490,328,490);arrow(498,490,569,490);arrow(739,490,810,490);
arrow(680,310,680,388,C.purple,true);text('预先配置',702,350,225,31,21,C.purple);
text('共享缓冲与 activation 记录，eventfd 传递运行唤醒',83,578,864,36,24,C.blue,true);
contrast('PipeWire 围绕通用\\n媒体图分配控制\\n与实时执行职责\\n\\nPreeAudio 围绕\\nManager / Cluster\\n组织场景处理\\n\\n两者都有处理图\\n差异在组织尺度\\n和执行职责分配'.replaceAll('\\n','\n'));

base(6,'设计理念与软件架构的横向对比','比较设计出发点、基本抽象、执行模型与动态控制',
 'PreeAudio 按既有分享的 HPAE 公开实现描述。时延、CPU、功耗及音质优劣需要同平台、同路径实测。',
 '建议讲述 2 分钟。这里对比可观察到的架构重心，设计出发点和取舍是基于机制的归纳，不冒充内部设计目标声明。PA 围绕流与设备组织通用音频服务，JACK 把各处理者纳入共同周期及依赖约束，PipeWire 把通用媒体图执行与会话策略分工，PreeAudio 的公开 HPAE 结构体现 Manager、Node、Cluster 对场景处理及状态的组织。四者都有实时性、缓冲和动态控制问题，不把任何共性包装成独有优势。本次 HPAE 工作循环是消息处理后衔接数据处理，不能泛化为整个系统只有一个线程。没有统一测量时不宣称谁的时延、功耗或音质更好。',
 [sources.pa,sources.paThread,sources.jack,sources.pwDesign,sources.pwSchedule,sources.pwSession,sources.hpae+'services/audio_service/server/src/i_stream_manager.cpp',sources.hpae+'services/audio_engine/manager/src/hpae_renderer_manager.cpp']);
table([
 ['维度','PulseAudio','JACK','PipeWire','PreeAudio'],
 ['设计重心','多流共享\n动态设备管理','周期内协作\n低延迟处理','通用媒体图\n策略机制分离','场景化处理\n系统状态协同'],
 ['基本抽象','Stream\nSink / Source','Client / Port\n处理回调','Node / Port\nLink','Manager\nNode / Cluster'],
 ['执行模型','按设备 I/O 线程\n适配和汇合流','按依赖唤醒\nJACK2 可并行','Driver 启动周期\n数据线程执行图','消息处理后\n驱动处理簇'],
 ['动态控制','主循环与 I/O\n通过消息协作','维护端口连接图\n更新执行依赖','主线程配置图\n会话层管理策略','Manager 管状态\n上层策略协同'],
 ['架构取舍','缓冲、响应速度\n设备时钟协调','周期预算\n分支与关键路径','媒体图通用性\n图与进程协调','场景处理复用\n节点与状态管理']
],64,221,1152,397,[132,255,255,255,255],23);



base(7,'素材参考：PulseAudio 的多级缓冲','原图呈现客户端、传输、服务端与 ALSA 的缓冲边界',
 '原图：Gavv，PulseAudio under the hood，Buffering（2017，面向 PA 11.1）。原图保留英文标签。',
 '来源原图，未重绘。阅读顺序为 client、transport、server、alsa。原图区分 socket buffers 与共享内存池，继而展示 stream buffer、resampler buffer、render queue 和 device buffer。适合在需要解释多级缓冲时作为备份素材使用，不能把原图当作当前所有 PA 配置的唯一实现。',
 ['https://gavv.net/articles/pulseaudio-under-the-hood/','https://gavv.net/articles/pulseaudio-under-the-hood/diagrams/buffers.png']);
image('pa-buffers.png',64,235,1152,343);
text('传输缓冲、流缓冲与设备缓冲处于不同边界，时延分析需要沿整条路径展开',64,597,1152,38,26,C.blue,true);

base(8,'JACK 附录：一个处理周期如何完成','同步模式示例：数据依赖决定执行顺序，实时工作共享周期预算',
 '原图局部：Fons Adriaensen（2014），PDF 第 3 页。周期算例为教学假设，非实测端到端时延。',
 '原图给出多个客户端和端口的分支、汇合关系。同步处理周期的概念顺序是采集就绪、运行满足依赖的客户端、完成下游处理、向设备提交结果。process(nframes) 在实时线程内读取输入端口缓冲、执行本块 DSP、填充输出端口缓冲。不要在回调中引入可能阻塞的磁盘 I/O、分配或锁等待，具体限制见官方 jack_set_process_callback 文档。假设块长 N=128、采样率 48kHz，名义周期 T=N/fs 约为2.67ms，这只是块周期；读写设备、驱动、安全缓冲与运行模式还会影响端到端时延。整个图、同步与调度开销需要放进预算，不能给每个节点都独占2.67ms。',
 ['https://kokkinizita.linuxaudio.org/export/jackpres.pdf','https://jackaudio.org/api/group__ClientCallbacks.html',sources.jack]);
image('jack-graph-crop.png',64,231,680,233);
text('实时回调承担一块计算',796,226,420,41,28,C.blue,true);
text('输入端口缓冲\nprocess(nframes)\n输出端口缓冲',796,285,420,126,28,C.ink);
text('回调内避免阻塞操作',796,428,420,37,25,C.purple,true);
['采集数据就绪','激活可运行客户端','传播下游依赖','提交设备输出'].forEach((t,i)=>{node(t,64+i*294,501,270,62,i===1?C.teal:C.blue,24);if(i<3)arrow(334+i*294,532,358+i*294,532);});
text('N = 128，fs = 48 kHz：名义周期约 2.67 ms，预算由整张图共同使用',64,596,1152,38,27,C.blue,true);

base(9,'JACK 附录：串行顺序与依赖驱动','简化依赖图中，A 与 B 独立，C 等待 A、B，D 等待 C',
 '教学算例：A=2、B=3、C=2、D=1 个时间单位。忽略同步、缓存和调度开销，不是性能实测。',
 '依据 jackdmp 2005 原始论文及 JACK2 README 解释数据流激活。JACK1 的经典模型把客户图排列成串行激活顺序；JACK2 允许依赖已满足的独立客户端同时运行，能否并行取决于图、可用核和系统调度。上图选取 A 然后 B 然后 C 然后 D 的一种合法串行顺序，计算工作合计8单位。下图假设两个工作核可用，A与B从0同时开始，C必须等B在第3单位完成，再运行2单位，D最后运行1单位，总计6单位。关键路径为max(A,B)+C+D，不能把所有节点的计算时间简单除以核数，也不能从该算例推导真实加速比。JACK2 的图访问使用无锁技术，目的是减少图变化干扰实时执行，此描述只针对图访问，不等同于全引擎所有路径无锁。',
 ['https://archive2010.grame.fr/ressources/publications/Jackdmp-lac2005.pdf','https://raw.githubusercontent.com/jackaudio/jack2/develop/README.rst']);
text('JACK1 经典模型',64,214,360,34,27,C.blue,true);
text('顺序执行',64,289,172,41,25,C.ink,true);
const gx=256,unit=76;
for(let j=0;j<=8;j++){const xx=gx+j*unit;line(xx,272,xx,325);text(String(j),xx-12,245,30,24,18,C.muted,false,'center');}
let pos=0;[['A',2,C.blue],['B',3,C.teal],['C',2,C.blue],['D',1,C.ink]].forEach(([t,d,c])=>{node(t,gx+pos*unit,282,d*unit,42,c,24);pos+=d;});
text('JACK2 依赖驱动',64,370,360,42,28,C.blue,true);
text('工作核 1',64,433,172,41,25,C.ink,true);text('工作核 2',64,497,172,41,25,C.ink,true);
line(gx,454,gx+8*unit,454);line(gx,518,gx+8*unit,518);
node('A',gx,433,2*unit,42,C.blue,24);node('B',gx,497,3*unit,42,C.teal,24);node('C',gx+3*unit,433,2*unit,42,C.blue,24);node('D',gx+5*unit,433,unit,42,C.ink,24);
text('等待 B',gx+2*unit,435,unit,38,18,C.muted,false,'center');
text('8 单位',940,280,270,43,30,C.ink,true);text('6 单位',940,429,270,43,30,C.teal,true);text('关键路径\nmax(A,B)+C+D',940,489,275,76,24,C.ink);
text('图访问采用无锁技术，降低连接变化对实时执行的干扰',64,595,1152,40,27,C.blue,true);

base(10,'JACK 附录：同步与异步的交付取舍','并行度描述周期内怎样执行，同步方式描述何时交付计算结果',
 '依据 JACK2 README 和作者论文。异步模式增加一个处理周期的流水线延迟，不等于端到端总时延。',
 'JACK2 README 区分两种服务器级激活模式。同步模式在当前周期等待图内客户端完成，然后使用当前周期的输出。异步模式使用上一周期算好的输出，并在当前周期运行新一轮图，从而解耦设备交付和当前计算。代价是相对同步模型多一个处理周期的流水线等待。若某一客户端未能按期运行，其他客户端仍可能继续并产生部分输出，这不构成任意负载下无断音的保证。同步/异步与串行/并行是不同维度，不可把异步等同于多核并行，也不能把异步理解成没有实时截止期。块周期为2.67ms的教学例子中，这一流水线代价约为2.67ms，设备及其它缓冲时延另计。作者论文讨论各模式的容错行为，不能把所有晚到问题都视为被隔离。',
 ['https://raw.githubusercontent.com/jackaudio/jack2/develop/README.rst','https://lac.linuxaudio.org/2009/cdm/Thursday/01_Letz/01.pdf']);
['周期 n','周期 n+1','周期 n+2'].forEach((t,i)=>text(t,310+i*290,231,258,38,26,C.muted,false,'center'));
text('同步模式',64,290,225,44,30,C.blue,true);text('等待当期图完成',64,341,225,39,24,C.muted);
text('异步模式',64,446,225,44,30,C.teal,true);text('使用前一周期结果',64,497,237,39,24,C.muted);
for(let i=0;i<3;i++){
 const x=310+i*290,idx=['n','n+1','n+2'][i],old=['n−1','n','n+1'][i];
 node(`计算 ${idx}\n写出 ${idx}`,x,291,258,90,C.blue,27);
 node(`计算 ${idx}\n写出 ${old}`,x,448,258,90,C.teal,27);
 if(i<2){arrow(x+258,336,x+290,336);arrow(x+258,493,x+290,493,C.teal);}
}
text('同步：当前结果直接参与交付',64,592,555,40,26,C.blue,true);text('异步：以一个周期等待换取交付解耦',650,592,567,40,26,C.teal,true);

base(11,'PipeWire 附录：会话策略如何改变运行图','设备和用户偏好变化先转成对象配置与连接决策，再由实时图执行',
 '依据 WirePlumber 官方会话管理说明。图示为职责关系，不承诺设备切换无中断或所有模块的固定调用顺序。',
 'WirePlumber 的会话管理不仅是连线，还包括设备启用、配置、部分访问控制、节点配置、链接及元数据管理。用设备变化的概念示例串起这些职责：监视器发现设备，策略依据配置和偏好作选择，配置节点格式与端口，管理连接，使媒体图满足当前场景。实际实现是持续事件处理，图中顺序用于理解职责，不表示每次热插拔都严格走同一调用链。控制决策不需要逐块参与音频运算。PipeWire 的主线程处理对象与配置，数据线程执行已准备好的图。对照 PreeAudio：Policy/Service 与引擎也有职责分工，具体差异应看规则如何转化为 Manager 的连接和状态更新，不能把策略分离当作 PipeWire 独有特性。',
 ['https://pipewire.pages.freedesktop.org/wireplumber/design/understanding_session_management.html',sources.pwSession,sources.pwSchedule]);
text('事件与策略层',64,222,350,42,29,C.purple,true);
const policySteps=['设备 / 偏好变化','选择配置与目标','配置节点与端口','创建或调整连接'];
policySteps.forEach((t,i)=>{node(t,64+i*294,293,270,68,C.purple,25);if(i<3)arrow(334+i*294,327,358+i*294,327,C.purple,true);});
text('WirePlumber 持续监视事件，并维护设备、节点、连接与元数据',64,384,1152,37,26,C.purple);
arrow(1080,361,1080,465,C.purple,true);text('准备图和运行资源',744,421,320,33,24,C.purple);
frame(64,466,1152,112,'实时执行层');
node('流节点',89,516,260,45,C.blue,25);node('处理节点',483,516,260,45,C.teal,25);node('设备节点',925,516,260,45,C.blue,25);arrow(349,539,483,539);arrow(743,539,925,539);
text('架构重点：策略决定图如何组织，实时层按准备好的资源持续处理数据',64,601,1152,38,27,C.blue,true);

base(12,'PipeWire 附录：依赖计数决定节点何时运行','Driver 发起周期，节点等待上游完成，再把运行条件传递给下游',
 '仅展开同步图。pending 数字表示 Driver 已发起周期后仍未满足的上游依赖，省略 Driver 自身计数与反馈连接。',
 '依据 Graph Scheduling 文档解释同步图。Driver 由硬件事件或定时器等发起处理周期；节点激活记录包含 required 与 pending 等状态，依赖未满足时不能执行。图中 A、B 可运行，C 依赖两者。示例在 Driver 发起周期并释放其门控依赖后，只显示上游工作依赖，因此 C 从2到1再到0。A完成会减少C的待满足依赖数，B完成后C就绪，通过eventfd触发处理。这个简化计数不能直接当作真实activation结构完整数值，因为真实图还包括Driver相关依赖及完成回报。节点完成后继续传播就绪条件，周期结束时Driver可统计处理情况。异步节点不遵循同一同步依赖链，第14页另讲。与HPAE相比，应具体核对其Manager如何驱动OutputCluster并向上游取数，不因两者都叫处理图就假定调度器相同。',
 [sources.pwSchedule,sources.hpae+'services/audio_engine/manager/src/hpae_renderer_manager.cpp']);
node('Driver\n启动本周期',64,313,230,96,C.hw,27);
node('节点 A\n上游依赖就绪',378,235,258,83,C.blue,25);node('节点 B\n上游依赖就绪',378,396,258,83,C.teal,25);
node('节点 C\n等待 A 与 B',838,315,330,96,C.blue,28);
line(294,361,330,361,C.blue);line(330,277,330,438,C.blue);arrow(330,277,378,277);arrow(330,438,378,438);
line(636,277,736,277,C.blue);line(736,277,736,361,C.blue);line(636,438,736,438,C.teal);line(736,361,736,438,C.teal);arrow(736,361,838,361);
text('完成后传播就绪条件',675,227,495,38,25,C.muted);
const states=[['pending = 2','A、B 均未完成',C.hw],['pending = 1','A 完成，仍等 B',C.blue],['pending = 0','B 也完成，C 可运行',C.teal]];
states.forEach(([a,b,c],i)=>{const x=64+i*392;text(a,x,530,350,45,31,c,true);text(b,x,584,350,35,25,C.ink);if(i<2)arrow(x+332,552,x+381,552,c);});

base(13,'PipeWire 附录：跨进程的数据与唤醒协作','对象配置走控制通信，媒体计算共享缓冲，节点完成后可直接触发后继',
 '图为同机跨进程处理的简化模型。共享内存降低传输复制，格式转换、混音及设备路径仍可能需要复制。',
 '依据 Design、Objects Design 与 Graph Scheduling 文档。PipeWire节点可以位于服务进程或客户端进程。主线程先进行IPC与图配置，在处理开始前准备缓冲、I/O区域和激活记录。对远端节点，此处远端指其它本机进程，eventfd与activation记录可传递给客户端；客户端可以直接唤醒相连节点，不要求每一步都回服务器中转。样本数据与唤醒信号是两类信息：共享缓冲承载媒体块，eventfd传递运行通知，activation记录保存执行及依赖状态。图中只画主要关系，未列所有映射、权限与驱动节点。共享内存不是全链零拷贝保证，媒体转换和混音可能产生新的缓冲或复制。对PreeAudio的比较应落在图执行者的分布及缓冲所有权，而不是应用调用哪个API。',
 [sources.pwDesign,'https://docs.pipewire.org/page_objects_design.html',sources.pwSchedule]);
node('PipeWire 主线程：配置对象、连接与共享资源',64,221,1152,65,C.purple,28);
frame(64,370,290,161,'进程 A');node('节点 A\n实时处理线程',84,419,250,88,C.blue,26);
frame(926,370,290,161,'进程 B');node('节点 B\n实时处理线程',946,419,250,88,C.teal,26);
rect(438,366,404,164,C.pale,C.blue);text('共享资源',459,377,362,37,28,C.blue,true,'center');
text('媒体缓冲 / I/O 区\nactivation 依赖与状态',459,431,362,77,25,C.ink,false,'center');
arrow(209,286,209,370,C.purple,true);arrow(1071,286,1071,370,C.purple,true);text('IPC / 配置',269,311,250,32,22,C.purple);text('IPC / 配置',804,311,250,32,22,C.purple);
arrow(354,463,438,463);arrow(842,463,926,463,C.teal);
arrow(209,574,1071,574,C.teal,true);text('eventfd：完成后唤醒后继，通知与样本数据分开',261,586,763,36,25,C.teal,true,'center');

base(14,'PipeWire 附录：异步 Link 的周期隔离','异步节点与同步依赖链解耦，双槽缓冲隔开本周期的读写',
 '一般异步 Link 的稳态示意，周期 0 前已有数据。每条异步 Link 增加一个图周期，Driver 输出等特殊分支未展开。',
 '依据Graph Scheduling的Async scheduling章节。异步节点不计入普通同步节点之间的依赖，完成与否不影响同步图周期完成。为避免并行读写同一块数据，异步链接使用两个I/O缓冲槽：周期计数为c时，输出使用(c+1)&1槽，输入使用c&1槽。因而消费者读取上一周期的结果，通常每条异步Link增加一个图周期的延迟。这里采用稳态示例，周期0的槽0中已有上一周期的数据；启动时可能为空。Driver输出存在特殊处理，未在该页展开。异步处理可隔离同步图对该节点的完成依赖，但不保证晚到节点内容始终完整或无失真。JACK2服务器级同步/异步激活与这里的节点/Link级异步机制作用范围不同，不能直接等同。PreeAudio若要做类似比较，需要核实是否存在对应的跨周期缓冲和调度边界，不能仅凭异步消息队列类名推断。',
 [sources.pwSchedule,'https://docs.pipewire.org/group__spa__buffer.html']);
table([
 ['运行位置','周期 0','周期 1','周期 2'],
 ['生产节点 A','写槽 1：数据 0','写槽 0：数据 1','写槽 1：数据 2'],
 ['消费节点 B','读槽 0：旧数据','读槽 1：数据 0','读槽 0：数据 1']
],64,237,1152,225,[216,312,312,312],25);
text('获得的自由度',64,497,500,42,30,C.blue,true);text('异步节点与同步图的完成依赖解耦',64,550,550,41,26,C.ink);
text('付出的代价',690,497,500,42,30,C.teal,true);text('每条异步 Link 多一个图周期',690,550,526,41,26,C.ink);
text('JACK2 的服务器级激活与 PipeWire 的节点 / Link 级异步，作用范围不同',64,605,1152,36,25,C.purple,true);

base(15,'素材参考：PipeWire 作者的整体架构图','Wim Taymans，FOSDEM 2024，Overview 原图',
 '来源：FOSDEM 2024，PipeWire State of the Union，PDF 第 3 页。此页保留原图，适合作为放大查阅的备份素材。',
 '保留作者 Overview 架构图原页，作为可放大阅读的素材参考。该图同时展示音频与视频生态，包含应用兼容接口、WirePlumber、媒体图、SPA、ALSA-lib、BlueZ、libcamera 与内核设备。它属于 2024 年讲义快照，不把当年的实现细节或状态列表当作当前版本承诺。主稿第 5 页展开策略、控制与图执行的架构分工，原图用于补充整体背景。',
 ['https://archive.fosdem.org/2024/events/attachments/fosdem-2024-1988-pipewire-state-of-the-union/slides/22795/PipeWire-slides_JBa52sZ.pdf']);
image('pipewire-overview.png',268,205,744,444);

await fs.writeFile(path.join(root,'speaker_notes.md'),notes.map(x=>`## ${x.n}. ${x.title}\n\n${x.note}`).join('\n\n'));
await fs.writeFile(path.join(root,'build/font-policy.json'),JSON.stringify({basis:'design',families:[FONT]}));
await (await PresentationFile.exportPptx(P)).save(path.join(root,'build/candidate.pptx'));
for(let i=0;i<P.slides.items.length;i++){
 const b=await P.export({slide:P.slides.items[i],format:'png',scale:1.5});
 await fs.writeFile(path.join(root,'previews',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await b.arrayBuffer()));console.log('Rendered',i+1);
}
const b=await P.export({slide:P.slides.items[0],format:'png',scale:1.5});await fs.writeFile(path.join(root,'previews/slide-01.png'),new Uint8Array(await b.arrayBuffer()));
const skill=process.env.PRESENTATIONS_SKILL_DIR;
if (!skill || !process.env.RUNTIME_PYTHON) throw new Error('Set PRESENTATIONS_SKILL_DIR and RUNTIME_PYTHON');
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
console.log(await finalizePresentation({workspaceDir:root,candidatePath:path.join(root,'build/candidate.pptx'),finalPath:path.resolve(root,process.env.FINAL_PPTX || 'output/rebuilt.pptx'),pythonExecutable:process.env.RUNTIME_PYTHON,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),explicitTotalSlideCount:15,requiredNativeTableOwnerSlides:[2,6,14],fontPolicy:{basis:'design',families:[FONT]},layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit','--require-native-table-slide','2','--require-native-table-slide','6','--require-native-table-slide','14'],verifyArtifactToolImport:true,receiptPath:path.resolve(root,process.env.VALIDATION_RECEIPT || 'build/rebuilt.validation.json')}));
