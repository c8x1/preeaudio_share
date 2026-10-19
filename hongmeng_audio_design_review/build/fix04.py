import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from redesign import *
p=Path(__file__).parents[1]/'pages/P04.json';d=json.loads(p.read_text(encoding='utf-8'))
d['elements']=lanes(['RendererInServer','PaRendererStreamImpl','PA 异步操作','状态回程'],[165,475,820,1125],245,595)
d['elements']+=msg(165,475,318,'Start()','navy',22)+[t(485,352,350,35,'PaLockGuard(mainloop)',22,'amber')]+msg(475,820,404,'pa_stream_cork(0)','amber',21)+msg(475,165,470,'同步返回 SUCCESS','navy',21)+msg(820,475,530,'操作回调(success 参数)','blue',20)+msg(475,1125,583,'OnStatusUpdate(STARTED)','blue',20)+[t(64,619,1150,36,'回调会更新 RUNNING 并通知状态；5.1 实现未在回调中检查 success 参数',21,'navy',True)]
d['title']='5.1 方案：PA Start 的同步返回与操作回调'
d['takeaway']='pa_stream_cork 提交后函数返回，状态在操作回调中更新'
d['script']=d['script'].replace('状态更新在后面的PAStreamStartSuccessCb：置RUNNING并调用statusCallback的OPERATION_STARTED。','后续PAStreamStartSuccessCb操作回调置RUNNING并调用statusCallback的OPERATION_STARTED。这个5.1回调收到success参数，但当前实现未检查它便更新状态，因此图和讲述只称“操作回调”，不据此声称底层实际输出成功。')
d['script']=d['script'].replace('图中的PA主循环与PA stream是逻辑参与者，不能据此断言cork在同一个回调栈中同步完成。','图中的PA异步操作是一条折叠泳道，不展开第三方库内部处理顺序。Start同步返回SUCCESS与后续操作回调分开画。')
d['footer']='5.1固定版本；PA异步操作内部未在本图展开；回调未检查 success 参数'
d['boundary']='旧版5.1普通PA路径；操作回调不等于声学出声；回调未检查success参数。'
d['sources'] += ['PAStreamStartSuccessCb L835–855：https://gitcode.com/openharmony/multimedia_audio_framework/blob/c42a228d60b64a90d6b05cf26278a89253e5310b/services/audio_service/server/src/pa_renderer_stream_impl.cpp#L835']
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
