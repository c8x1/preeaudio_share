from redesign import *
e=[t(64,249,540,40,'5.1 普通 PA 流：请求的属性',26,'gray',True),t(680,249,535,40,'当前 HPAE：区分三种量',26,'blue',True),l(635,250,635,601)]
for i,(s,v) in enumerate([('prebuf','20ms 对应字节数'),('minreq','20ms 对应字节数'),('tlength / maxlength','80ms 对应字节数')]):
 y=331+i*78;e += [t(64,y,260,38,s,25,'navy',True),t(325,y,285,38,v,22)]
for i,(s,v) in enumerate([('frameLen / span','以帧为单位的处理粒度'),('renderSize_','设备提交块的字节数'),('实际库存','运行时排队数据量')]):
 y=331+i*78;e += [t(680,y,240,38,s,24,'blue',True),t(928,y,286,38,v,21)]
e += [t(64,603,1150,42,'属性请求、处理粒度、实际库存、端到端时延，是不同的测量对象',24,'navy',True)]
save(16,'A1  Buffer 参数怎样避免比错','旧 PA 请求值与新引擎的帧粒度、字节提交块不能直接相减',e,'5.1 ConnectRendererStreamToPA以BUF_LENGTH_IN_MSEC为基准，普通流的prebuf与minreq对应20ms字节数，tlength与maxlength对应80ms；DUP/DUAL有不同分支。这些数值传给pa_stream_connect_playback并带ADJUST_LATENCY等flags，是请求的PA属性，不是端到端实测时延，也不是每个时刻真实库存。\n当前HPAE则需分别看帧粒度frameLen/span、SinkOutput的字节提交块renderSize_、Converter已处理缓存和各处真实库存。设备迁移还会按目标设备调整frameLen并通知span。比较新旧时应固定业务语义、设备和负载，抓运行时属性与队列库存，不能用80减20直接宣布降低60ms。',['attr','stitch','attach','span'],'5.1普通流请求值；DUP/DUAL配置另有分支','20/80ms不是实测时延；新配置按设备变化。')
