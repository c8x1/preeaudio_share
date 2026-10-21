from author import *

rows=[['轮次 / 上下文','实际发生的工作','请求链 / 输入状态'],['N · HandleMsg','Pause已被执行；进入PAUSING','本批已摘走；随后进入Process'],['N · Process期间','另一个线程先成功发布Start','全局：Start → ∅'],['N · Gain继续处理','淡出完成；OnFadeDone发布F','全局：F → Start → ∅'],['N+1 · HandleMsg','摘批后反向调用：先Start','输入改为RUNNING并恢复连接'],['N+1 · 随后的F','闭包内部再读当前状态','RUNNING：直接返回，不拆图']]
e=[table(54,210,1170,350,rows,[245,485,440],21),t(54,579,1170,40,'反事实：去掉执行时guard，旧F会暂停音效、拆掉新连接、回写PAUSED',24,'amber',True),t(54,625,1170,30,'同批Pause→Start可能重置淡出而不产生旧F；此guard也没有暂停代次令牌',21,'navy')]
save(9,'迟到的 FadeDone，能拆掉刚恢复的通路吗？','正确排队仍不足够：真正改状态之前，必须再检查当前条件',
 '能推演N/N+1批次、F→Start与逆序执行，指出guard为何必须位于闭包内部及其范围。',e,'\n\n'.join(S2[15:19]+S2[20:23]),
 ['pause','fade','gain','start','fadedone','run','qrun','drain'],
 'N+1轮执行完Start后再执行旧F；若只在F发布之前检查状态，足够吗？',
 '不足。排队期间Start已把输入改为RUNNING；F须在执行时再读状态并退出，否则旧完成会破坏新决定。',
 '教学合法交错：N轮Pause已执行，Process期间先发布Start再发布F；不是每次Pause/Start都产生旧F',5,'故事二 · 迟到事件竞态',
 prev='普通Pause完成需要另一个收尾闭包，新的决定可能在它之前生效。',next='状态与排队讲清以后，再看选择新设备时究竟需要改变什么。')
