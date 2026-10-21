from author import *

rows=[['PAUSING后的Process输入','Gain执行的工作','完成事件'],['有效样本','ApplyFadeOut：处理样本增益\n再置DONE_FADEOUT','调用OnFadeDone'],['无效输入，且DO_FADEOUT','不做样本渐变\n直接置DONE_FADEOUT','仍调用OnFadeDone']]
e=[t(54,205,1170,36,'普通分支前提：输入与Gain存在、设备运行、非standby；Pause已被消费',23,'navy',True),table(54,259,1170,186,rows,[360,510,300],21)]
e += [box(54,488,245,69,'PAUSING\n暂时保留连接','blue',22),a(299,522,352,522),box(352,488,245,69,'OnFadeDone\n发布收尾闭包F','teal',22),a(597,522,650,522),box(650,488,245,69,'后续HandleMsg\n执行F并检查状态','blue',22),a(895,522,948,522),box(948,488,276,69,'仍PAUSING：断开输入\nPAUSED + 回调','teal',22)]
e += [t(54,594,1170,62,'另一条旁路：无Gain / 设备未运行 / standby / 已暂停或停止\nSetSessionFade直接写终态并回调；返回Pause后断图，不等Gain事件',22,'gray')]
supp='补充区分Gain的两个实际分支：DoFading收到无效输入且处于DO_FADEOUT时，直接写DONE_FADEOUT并调用OnFadeDone，不执行样本渐变。有效输入才进入ApplyFadeOut；未定义CONFIG_FACTORY_VERSION时处理样本增益，随后写DONE并回调，工厂构建跳过实际样本渐变。它们与SetSessionFade因无Gain、设备未运行、standby或已处于PAUSED/STOPPED而直接完成的旁路是不同条件。本图正常收尾假设F执行时输入仍存在且仍为PAUSING；恢复引入的迟到事件在下一页展开。'
save(8,'Pause 已开始，为什么先不拆连接？','中间态保留处理机会；有样本、无效输入和直接完成是三条条件分支',
 '能沿有效/无效输入分支走到OnFadeDone，解释PAUSING与后续断图、旁路直接完成的差别。',e,'\n\n'.join([S2[14],supp,S2[19]]),
 ['pause','fade','gain','fadedone'],
 'Gain收到无效输入时，是否必须一直等到有效样本回来才完成Pause？',
 '不是。DO_FADEOUT且输入无效时直接置DONE并回调；它不同于无Gain或standby等SetSessionFade直接完成旁路。',
 '普通非INTERPHONE、非工厂构建且回调有效；F执行时输入仍在且仍PAUSING，恢复竞态见下一页',3,'故事二 · Pause状态与完成条件',
 prev='消息已经交接，下一步要让图修改与正在执行的处理对齐。',next='如果F排队时用户已恢复播放，旧完成事件还能拆图吗？')
