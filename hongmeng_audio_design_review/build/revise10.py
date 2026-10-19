from redesign import *
e=[t(65,258,1100,38,'ProcessCluster：每路输入建立职责链',26,'blue',True)]
xs=[64,257,450,643,836,1029];names=['SinkInput','Converter','SessionEffect*','LoudnessGain','Gain','SceneMixer']
for i,(x,name) in enumerate(zip(xs,names)):
 e += [box(x,330,160,60,name,'blue' if i>0 else 'navy',17)]
 if i<5:e += [a(x+160,360,xs[i+1],360,'teal')]
e += [t(64,427,1120,37,'* 音效节点按会话配置可选；RenderEffect 在场景混音后按条件接入',22,'gray'),t(64,491,520,37,'拉取方向',25,'blue',True),a(584,530,65,530,'blue'),t(650,491,520,37,'PCM 结果方向',25,'teal',True),a(650,530,1188,530,'teal'),t(64,598,1140,43,'OutputCluster：场景转换 → 输出混音 → SinkOutput → RenderFrame',23,'navy',True)]
save(10,'节点图：输出端拉取，处理结果正向返回','节点负责处理；簇连接职责；Manager按会话和设备管理图',e,'当前ProcessCluster::Connect建立真实的输入链：SinkInput到Converter，按条件加入SessionEffect，再经过LoudnessGain、Gain、sceneMixer，场景后还可接RenderEffect。OutputCluster连接场景转换、输出混音与SinkOutput，最后SinkOutput调用RenderFrame。图上箭头要区分两个方向：输出侧InputPort向前驱请求结果，结果帧沿节点连接正向返回。OutputPort有数据时可直接取；队列空才让所属节点DoProcess。\n节点化的扩展价值因此更具体：格式转换、增益、混音与音效职责分离，一个会话音效无需复制整条设备通路。Manager对场景簇与设备簇进行创建、映射和状态管理。说“节点类型可复用”不等于“所有会话共享同一个节点实例”；默认、bypass等过程簇有条件地创建和复用。下页看一个局部重连的真实代码分支。',['connect','nodes','share','pull','pullout','sink'],'* 表示条件节点；箭头上为拉取请求、下为结果方向示意','当前源码配置路径；不声称每个产品都启用所有音效。')
