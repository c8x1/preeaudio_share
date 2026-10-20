from redesign import *
e=lanes(['下游 InputPort','前驱 OutputPort','前驱 Node'],[220,640,1060],245,600)
e+=msg(220,640,329,'ReadPreOutputData → PullOutputData','blue',20)
e+=[t(662,369,535,35,'if outputData_.empty()',22,'amber')]+msg(640,1060,429,'为空才调用 DoProcess()','amber',21)+msg(1060,640,493,'结果写入输出队列','teal',21)+msg(640,220,553,'取 back() 并 pop_back()','teal',21)
e += [t(64,615,1150,39,'队列已有结果时跳过 DoProcess；计算后仍为空则返回 nullptr，上游失败向下传播',21,'navy',True)]
save(18,'A3  一次 Pull：有结果就取，空队列才计算','OutputPort 的队列条件决定是否触发前驱节点处理',e,'InputPort::ReadPreOutputData遍历连接的前驱并调用其OutputPort::PullOutputData。OutputPort先检查outputData_队列，只有空队列才调用所属Node的DoProcess。随后若队列已有结果，移动back并pop_back返回；计算后仍为空就返回nullptr。图中橙色DoProcess是条件分支，不是每次Pull的必经步骤。\n这解释为什么不能说一轮Process中所有节点必然各运行一次。下游按需要反向索取，上游已有结果可被消费；有些节点如Converter还维护自己独立的处理帧缓存，与端口结果队列不同。SinkOutput可能重复拉取并拼成设备renderSize。所有条件都来自现有代码，图中没有设置虚构的默认帧数或时长。',['pull','pullout','converterbuf','stitch'],'橙色调用仅在空队列时发生；实际InputPort可有多个前驱','端口结果队列与Converter内部缓存是不同对象。')
