from author import *

cite('usage','N','services/audio_policy/server/infra/config/file/audio_usage_strategy.xml',16,21,'MUSIC映射到媒体策略')
cite('userrouter','N','services/audio_policy/server/domain/router/user_select_router.cpp',28,56,'用户选择Router结果')
cite('defaultrouter','N','services/audio_policy/server/domain/router/default_router.cpp',26,36,'Default先查媒体上下文')
cite('privacyxml','N','services/audio_policy/server/infra/config/file/audio_device_privacy.xml',19,23,'有线及USB候选隐私类别')
e=[t(54,206,1170,36,'本次条件：zone0普通音乐，仓库默认XML，无后续refiner改写；先选有效设备',23,'navy',True)]
names=['UserSelect','PairDevice','Privacy','Public','StreamFilter','Default']
for i,name in enumerate(names):
 x=54+i*198
 e.append(box(x,264,180,62,name,'teal' if i==2 else 'blue',21))
 if i<5:e.append(a(x+180,295,x+198,295))
e += [t(54,344,1170,40,'Router间：第一个有效结果就返回，后面的Router不再参与',25,'blue',True),t(54,404,1170,40,'Privacy内部：候选 → 过滤禁用 / 异常 / 排除项 → 合格列表中选最新连接',23,'teal',True)]
rows=[['改变一个条件','预测结果'],['UserSelect仍返回有效扬声器','立即返回扬声器；更新的耳机轮不到Privacy来覆盖'],['前方无结果，最新Privacy设备被禁用','先排除它，再从合格候选中选；时间最新不能豁免过滤']]
e += [table(54,475,1170,165,rows,[430,740],21)]
save(10,'新耳机为什么可能获胜，也可能轮不到它？','Router优先级与Router内部的候选排序，是两层不同规则',
 '能预测有效用户选择与禁用候选的反例，解释首个有效短路、过滤后选最新及zone分支范围。',e,'\n\n'.join(S3[:8]),
 ['usage','xml','router','userrouter','private','privacy','privacyxml','defaultrouter','zone'],
 'UserSelect已返回有效扬声器，晚连接的耳机会自动覆盖它吗？',
 '本默认链不会。有效结果短路返回；只有进入Privacy后才谈合格候选中的连接时间排序。非零zone还有提前返回分支。',
 '限定zone0默认配置；非零zone可提前返回；产品XML可覆盖；Default先查上下文，不总是写死扬声器',4,'故事三 · 策略选择真实分支',
 prev='节点与控制最终服务于场景；先确认系统究竟选择了哪个目标。',next='选中耳机以后，device变了，pipe和sink也一定变吗？')
