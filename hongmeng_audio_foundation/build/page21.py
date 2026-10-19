from author import write,R
import json,subprocess
write(21,'A6  源码版本与测量口径','固定版本解释实现，明确起止点与条件后再讨论指标',
'集中版本和指标定义，声明源码事实、团队定性说明、演示与测量设计的区别。',
'''本次当前框架固定到3a2688e805df970739e3b0cebf9cc05d8cb24e9b。历史框架5.1固定c42a228d60b64a90d6b05cf26278a89253e5310b，PA5.1仓库固定bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca，其README.OpenSource声明版本17.0。所有源码细节以这些快照为准，不用滚动master链接代替。
讲述中有四种依据。源码事实解释职责、队列、节点和调用边界。时延降低、性能提升、功耗降低及抗抖动保持来自团队定性说明。音频是原创合成，用于听辨场景和模拟连续性。完整场景验证页是拟议方案，没有执行板端实验或生成产品成绩。
响应时延必须给起点、终点和时钟对齐方法，例如应用事件到回环或声学检测。缓冲容量、当前库存、算法块长和设备提交粒度是不同量。PA请求的prebuf/minreq/tlength不能直接作端到端时延。稳定性比较必须固定负载与扰动并观察欠载或断音；CPU和能量要带测量范围、窗口及环境条件。
产品构建开关、不同播放类型以及旧新版本的其他变化也必须记录。没有这些条件，就不应把局部代码结构和版本差值包装成准确的产品收益幅度。附录和随附证据表保留原始位置，便于讲师继续补充真实产品资料。''',
[['text',64,248,300,41,'当前框架',27,'blue',True],['text',365,248,849,41,'3a2688e805df970739e3b0cebf9cc05d8cb24e9b',23,'navy'],
 ['text',64,310,300,41,'5.1 框架',27,'purple',True],['text',365,310,849,41,'c42a228d60b64a90d6b05cf26278a89253e5310b',23,'navy'],
 ['text',64,372,300,41,'5.1 PA（17.0）',27,'purple',True],['text',365,372,849,41,'bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca',23,'navy'],
 ['line',64,447,1214,447,'light',2],
 ['text',64,480,1150,42,'响应：事件到声音，明确起止点与时钟',29,'blue',True],['text',64,537,1150,42,'稳定：同负载、同扰动下观察欠载和断音',29,'teal',True],['text',64,594,1150,42,'资源：CPU与能量，记录范围、窗口和环境',29,'navy',True]],
 keys=['entry','oldentry','attr'],minutes=0,section='技术附录 · A6',prev='按版本、来源与测试口径问题进入。',next='返回主讲收束页或结束答疑。',footer='源码事实、团队定性结果、合成演示与验证设计分别标明；未做板端或声学性能测试',boundary='不确认商业产品部署或未披露量化数据，PA版本声明不代表原封不动上游实现。',label='A6')
p=R/'pages/P21.json';d=json.loads(p.read_text(encoding='utf-8'))
d['sources'].append('PA版本声明：https://gitcode.com/openharmony/third_party_pulseaudio/blob/bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca/README.OpenSource')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
v=subprocess.check_output(['git','-C',str(R.parent/'source_pulseaudio'),'show','bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca:README.OpenSource']).decode()
(R/'appendix/source_evidence/pa_version.txt').write_text(d['sources'][-1]+'\n'+v,encoding='utf-8')
