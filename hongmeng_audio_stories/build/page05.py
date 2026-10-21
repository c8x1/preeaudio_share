from author import *
rows=[['观察同一问题','5.1 PA 控制路径','当前 HPAE 普通路径'],['框架怎样交接','PaLockGuard(mainloop)\npa_stream_cork提交命令','保存sessionId的闭包\nSendRequest发布'],['谁改变执行状态','协议 → PA控制上下文\nsend(SET_STATE)到sink I/O','设备队列 → HandleMsg\n消费闭包后才Process'],['谁等待谁','send等待I/O处理\nACK后框架操作回调','发布不等待业务完成\n消费侧闭包逐项执行'],['原子与锁的层次','多写端包装有mutex\nasyncq槽位有原子操作','常规请求链表用CAS\nNotify / 扩容仍有锁']]
e=[table(54,215,1170,370,rows,[220,475,475],21),t(54,612,1170,42,'比较同步边界与完成语义：发布更轻，不会让音效、接图或设备准备瞬间完成',24,'navy',True)]
save(5,'旧新两种工作交接：谁在等待谁？','控制线程不能任意拆正在处理的图，需要进入对应执行上下文',
 '能区分PA的mainloop保护、同步send握手和HPAE的普通请求发布，不混淆原子与全部执行。',e,'\n\n'.join(S2[:4]),
 ['oldstart','paqueue','pacork','paset','run','qpush'],
 'PA send返回和HPAE普通请求发布返回，保证的是同一件事吗？',
 '不是。send等待对应I/O处理；普通发布只是交接请求，后续闭包仍要被消费并执行。',
 '比较选定的状态控制路径；PA也有异步post与底层原子槽位，HPAE不等于全链无锁',3,'故事二 · 控制交接',
 prev='声音处理还在执行，控制请求首先需要安全交接。',next='进入请求链内部：两个人同时发布，为什么CAS失败后还必须重写next？')
