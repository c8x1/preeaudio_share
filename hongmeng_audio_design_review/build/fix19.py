from redesign import *
p=R/'pages/P19.json';d=json.loads(p.read_text(encoding='utf-8'))
e=lanes(['客户端','RendererInServer','引擎回调'],[220,640,1060],245,610)
e+=msg(220,640,315,'Drain → I_STATUS_DRAINING','blue',21)
e+=[t(65,344,540,35,'Drain等待超时；继续 Stop',23,'amber')]
e+=msg(220,640,410,'Stop 请求 → I_STATUS_STOPPING','navy',20)
e+=msg(1060,640,465,'OPERATION_STOPPED → STOPPED','teal',20)
e+=msg(1060,640,520,'迟到的 OPERATION_DRAINED','amber',21)
e+=[box(653,555,562,60,'仅 status_ == I_STATUS_DRAINING 才恢复 STARTED','teal',18),t(64,622,1150,31,'Stop 请求先进入 STOPPING；完成回调设置 STOPPED 后，迟到 Drain 不再恢复状态',20,'navy',True)]
d['elements']=e
d['script']=d['script'].replace('因此Stop可能已完成，之后Drain回调才到。','因此服务端先因Stop请求进入STOPPING，再因OPERATION_STOPPED完成回调进入STOPPED，之后Drain回调才到。')
d['sources'] += ['Stop设置STOPPING L1889–1916、OPERATION_STOPPED处理 L437–443：https://gitcode.com/openharmony/multimedia_audio_framework/blob/3a2688e805df970739e3b0cebf9cc05d8cb24e9b/services/audio_service/server/src/renderer_in_server.cpp#L437']
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
