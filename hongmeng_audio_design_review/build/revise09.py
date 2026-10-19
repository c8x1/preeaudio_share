from redesign import *
e=[t(65,255,450,40,'生产者：SendRequest',27,'blue',True),t(650,255,540,40,'消费者：HandleRequests',27,'teal',True),l(625,255,625,595)]
for x,items,c in [(65,['free node 原子摘取','填入 request lambda','CAS 发布到 requestHead'], 'blue'),(650,['CAS 摘取整批请求','沿链读入临时数组','反向遍历并逐项执行'], 'teal')]:
 for i,s in enumerate(items):
  y=324+i*77;e += [box(x,y,535,58,s,c,22)]
  if i<2:e += [a(x+267,y+58,x+267,y+77,c)]
e += [t(65,573,535,35,'请求发布次序由CAS确定',22,'navy'),t(650,573,540,35,'摘批是原子；任务执行不是原子',22,'navy'),t(64,621,1140,34,'队列耗尽会扩容；扩容使用 mutex 与分配，达到上限仍无空节点会报告并丢弃请求',20,'amber',True)]
save(9,'无锁消息队列：发布、摘批与逆序执行','常规链表头用 CAS；消费者摘批后反向遍历执行',e,'管理请求例如Start会由SendRequest包装成lambda。生产者先从空闲节点链中原子摘取节点，填入request，然后通过CAS把节点压到请求头。多个线程竞争时，CAS成功次序定义入链先后；链表按头插法反转了它。消费者HandleRequests用CAS一次摘走当前整批，ProcessRequests沿链放进临时数组，再反向遍历执行，恢复批内发布次序。执行的每个lambda本身并非原子操作，也不承诺跨批次或外部业务请求的全局语义顺序。\n这就是无锁消息队列值得讲的算法细节：常规取节点、发布、摘批依赖原子操作，让控制请求进入处理侧不必围绕同一业务锁串行。但慢路径TryExpandQueue持expandMutex且分配新节点，处理线程的Notify也有锁；达到最大容量仍无空节点时会上报并丢弃请求。这里不说全链无锁、零分配。',['send','queue','queuecas','queuerun','queueconst'],'CAS决定节点入链，批内逆序遍历恢复发布次序；慢路径有锁与分配','不保证所有请求必达或所有操作无锁。')
