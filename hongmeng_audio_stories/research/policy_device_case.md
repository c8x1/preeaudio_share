# 一次真实的音乐设备决策：先选设备，再判断执行通路

核验基线：multimedia_audio_framework `3a2688e805df970739e3b0cebf9cc05d8cb24e9b`。以下是静态源码控制流核验，未在产品上运行。源码短摘录逐行附后。所有路径相对此仓库根目录。

## 1. 建议用于课程的最窄场景

音乐流已经 STARTED，当前设备为本地扬声器，随后一个本地有线/USB 耳机成功连接。明确配置前提：使用仓内默认 usage / router / privacy XML；该流属于 zone 0；系统处于普通媒体场景（没有通话跟随/来电跟随）；vehiclePriority 为 false；没有更高优先级的有效用户选择、配对路由；没有 refiner 改写最终设备；耳机没有被禁用、异常、排除或冲突过滤。

在这些前提下，默认 XML 把 MUSIC 映射到 MEDIA_RENDER；按 UserSelect → PairDevice → PrivacyPriority → PublicPriority → StreamFilter → Default 顺序询问，第一个返回有效设备的 router 获胜。新连接耳机属于 privacy/media/output 候选，过滤后按 connectTimeStamp 选最新一个，因此该耳机可以成为目标。注意：优先级在 router 之间，最新连接规则只适用于此 router 的合格候选内部。

不要讲“插入耳机必然优先”，应让听众回答：如果 UserSelect 已经返回有效扬声器，后面的最新耳机会不会被询问？按此配置链不会。

## 2. Zone 与普通 Router 是分支，不能串成必经链

`AudioRouterCenter::PreFetchOutputDevices` 先 FindAudioZone(uid, usage, OUTPUT_DEVICE, streamId)。只有 zoneId != 0 才调用 `AudioZoneService::FetchOutputDevices`；该 zone 返回非空设备时立刻短路普通 Router。

`AudioZoneService::FetchOutputDevices` 本身只是 FindZone → zone->FetchOutputDevices。AudioZone 当前实现不再调用 AudioRouterCenter。在 MULTI_USER_ZONE 编译下，AudioZoneRouter 过滤 available/output 再按 ZoneDevicePriority 排序（蓝牙、扬声器等的 zone 特定优先级）；非该编译分支返回 zone devices 列表中的第一个 active 输出。这不是普通媒体 UserSelect/Privacy 链。

故课程主场景画 zone0 → 普通 Router；旁边一个 alt “nonzero zone 且有设备→zone 输出直接返回” 即可。不要把 zone 蓝牙排序当成手机音乐普遍规则。

## 3. 输入、候选与可预测结果

输入包括实际/会话覆盖后的 usage、真实 UID、privacy type、bundle name、sessionId；BatchFetchAndStartOutputStreams 会先查询 AudioSessionStreamUsage，合法则覆盖 rendererInfo usage。不是只用 MUSIC 一个枚举决策。

UserSelectRouter 针对 uid/sessionId 查询偏好；检查 stream usage、DP usage，处理冲突、A2DP/SCO 替换；要求 deviceId != 0、支持 MEDIA；GetPairDevice 再在连接设备中按角色、类型、networkId、MAC 配对，检查 enable/exception/connectState。无有效偏好才返回 NONE，允许后续 router 尝试。

PrivacyPriorityRouter 获取 media privacy 候选，追加 active SCO，清理冲突，然后 GetLatestNonExcludedConnectDevice。过滤项包括：null、被跳过类型、exception、disabled、SCO suspend/excluded、设备被排除、不支持 MEDIA、静音控制、remote car/A2DP 冲突、DP usage 限制。对合格列表按连接时间升序，取 back()。本场景选有线/USB，可避免把无线静音/SCO 等扩展分支讲成普遍必经步骤。

DefaultRouter 也不是立即固定扬声器：先 GetMediaDefaultOutputDevice(uid, session)，为 null 才 GetRenderDefaultDevice；后者复制 speaker_。本例初始状态选择扬声器需明确“上游无有效候选且默认设备上下文为空”。

## 4. 连接事件怎样变为执行操作

AudioDeviceStatus::OnDeviceStatusUpdated：HandleLocalDeviceConnected 成功 → 更新 connected devices → 发设备变化回调 → FetchOutputDeviceAndRoute。当前 SHA 不存在名为 FetchStreamsForDeviceChange 的函数，切勿沿用旧版该名字。

FetchOutputDeviceAndRoute：拿全部输出 stream desc → 检查 modem/ring/voip 的提前重选分支 → sort → BatchFetchAndStartOutputStreams → 把结果写入每流 old/newDeviceDescs → 更新活跃设备与音量 → FetchRendererPipesAndExecute。

后者经 AudioPipeSelector::FetchPipesAndExecute 重建/匹配 pipe，判断 pipeAction 和 streamAction，然后分别进入 UPDATE / NEW / RELOAD 处理。选择目标设备 != 已经完成迁移；此时只是决定下一步执行计划。

## 5. 最重要的三层区别：device ID / pipe / sink

`JudgeStreamAction`：远端 offload 特例可 RECREATE；普通路径 IsSamePipe → DEFAULT，否则 MOVE。IsSamePipe 判 name 相同 OR id 相同，并不是 deviceId 相同。不同设备可以属于相同 pipe。

但 DEFAULT 也不等于完全不调用 Move API：`ProcessOutputPipeUpdate` 中 DEFAULT 与 MOVE 同 case。STARTED 且非 focus standby 走 MoveToNewOutputDevice；其他走 MoveStreamSink。二者本地路径均进入 MoveToLocalOutputDevice，使用目标 `pipeInfo->moduleInfo_.name` 作为 sinkName，再调用 MoveSinkInputByIndexOrName。

HPAE 收到请求后先 CheckMoveSinkInput。有效请求若 sinkName == 当前 rendererIdSinkNameMap 名字，回 SUCCESS 并 return；不同 sink 才记录 movingIds 并调用 oldRendererManager->MoveStream。课程必须把“收到 Move 方法调用”与“发生跨 RendererManager 的节点迁移”分开。

与此同时，普通运行流的 MoveToNewOutputDevice 在 move API 后按 GetUpdateRouteSupport / ShouldUpdateOutputRoute 条件 UpdateOutputRoute。UpdateOutputRoute 普通音乐分支进入 HandleNormalOrDualToneRoute。故同 primary 的设备变化可能保留 sink、由后续设备 route 更新完成物理输出改变；不是每次选中耳机都拆图。

## 6. 建议的两层教学推演

第一层反例：扬声器与有线耳机在当前产品配置中映射到同一 primary sink。目标 device 改了，pipe 可仍相同；policy 仍可调用 move API，但 HPAE 同 sink 早退。继续 device route 更新。提问：图上的 SinkInput 必须跨 RendererManager 吗？没有这个必要。

第二层合法迁移：产品配置使目标耳机映射到不同 sink，目标 RendererManager 已成功打开且 Init，stream isMoveAble；普通可迁移输出且不走 FAST/offload/recreate 特例。此时不同 sink 才进入 oldRendererManager->MoveStream，接已有研究中的旧图断边/保留输入/目标接图。USB 耳机可作为候选设备例子，但必须先核验实际产品 XML 对其 sink 的映射，不能仅凭 USB 类型宣布一定跨 sink。

记忆点：策略先回答“去哪个设备”，pipe 选择回答“走哪条执行通路”，HPAE 再决定“是否需要迁移节点”。三种标识和三次判断各自有职责。

## 7. 不能画成事实、仍需产品信息的内容

- 仓内默认 XML 不是所有产品的实际部署 XML。配置解析支持 USE_CONFIG_POLICY/GetOneCfgFile；需拿产品配置确认顺序与设备属性。
- 不将单一最新连接规则推广到非零 zone、用户指定输出、车机场景、通话、无线协同、双音、offload/FAST。
- 不保证 UserSelect 偏好跨场景都保留；连接处理、上下文策略可能更新偏好。本例以“此时返回 NONE 或有效 device”作为可观测条件。
- 不将 Move 方法 SUCCESS 画成首帧已到目标设备或无声学间隙；HPAE 入口异步发布请求，回调与实际提交另需追踪。
- 本报告 stop at policy Move API → HPAE entry 的控制流；适配器/IPC 中介层详述可单独追加，不假称这些调用发生在同一线程或同一栈。
- 相同 sink 早退前 CheckMoveSinkInput 仍须通过；不要画为无条件立即成功。

## 8. 逐段源码证据（固定 SHA）

### `services/audio_policy/server/infra/config/file/audio_usage_strategy.xml:16–21`

```cpp
16: <audioUsageStrategy xmlns:xi="http://www.w3.org/2001/XInclude">
17:     <adapter name="streamUsage">
18:         <strategy name="MEDIA_RENDER" streamUsage="STREAM_USAGE_UNKNOWN,STREAM_USAGE_MEDIA,STREAM_USAGE_MUSIC,STREAM_USAGE_MOVIE,STREAM_USAGE_GAME,STREAM_USAGE_AUDIOBOOK,STREAM_USAGE_NAVIGATION,STREAM_USAGE_ULTRASONIC,STREAM_USAGE_VOICE_MESSAGE"/>
19:         <strategy name="CALL_RENDER"  streamUsage="STREAM_USAGE_VOICE_COMMUNICATION,STREAM_USAGE_VOICE_MODEM_COMMUNICATION,STREAM_USAGE_VIDEO_COMMUNICATION,STREAM_USAGE_VOICE_CALL_ASSISTANT,STREAM_USAGE_INTERPHONE,STREAM_USAGE_VOICE_TRANSFER_COMMUNICATION"/>
20:         <strategy name="RING_RENDER"  streamUsage="STREAM_USAGE_ALARM,STREAM_USAGE_NOTIFICATION_RINGTONE,STREAM_USAGE_RINGTONE,STREAM_USAGE_RANGING,STREAM_USAGE_VOICE_RINGTONE,STREAM_USAGE_ANNOUNCEMENT,STREAM_USAGE_EMERGENCY,STREAM_USAGE_VOICE_TRANSFER_RINGTONE"/>
21:         <strategy name="TONE_RENDER"  streamUsage="STREAM_USAGE_NOTIFICATION,STREAM_USAGE_ACCESSIBILITY,STREAM_USAGE_SYSTEM,STREAM_USAGE_DTMF,STREAM_USAGE_ENFORCED_TONE,STREAM_USAGE_VOICE_ASSISTANT"/>
```

### `services/audio_policy/server/infra/config/file/audio_strategy_router.xml:16–22`

```cpp
16: <audioStrategyRouter version="1.0" xmlns:xi="http://www.w3.org/2001/XInclude">
17:     <strategy name="MEDIA_RENDER" routers="UserSelectRouter,PairDeviceRouter,PrivacyPriorityRouter,PublicPriorityRouter,StreamFilterRouter,DefaultRouter"/>
18:     <strategy name="CALL_RENDER"  routers="UserSelectRouter,PrivacyPriorityRouter,CockpitPhoneRouter,StreamFilterRouter,DefaultRouter"/>
19:     <strategy name="RING_RENDER"  routers="UserSelectRouter,PrivacyPriorityRouter,PublicPriorityRouter,StreamFilterRouter,DefaultRouter"/>
20:     <strategy name="TONE_RENDER"  routers="UserSelectRouter,PrivacyPriorityRouter,PublicPriorityRouter,StreamFilterRouter,DefaultRouter"/>
21:     <strategy name="RECORD_CAPTURE" routers="UserSelectRouter,PairDeviceRouter,PrivacyPriorityRouter,PublicPriorityRouter,StreamFilterRouter,DefaultRouter"/>
22:     <strategy name="CALL_CAPTURE"  routers="UserSelectRouter,PairDeviceRouter,PrivacyPriorityRouter,CockpitPhoneRouter,StreamFilterRouter,DefaultRouter"/>
```

### `services/audio_policy/server/infra/config/file/audio_device_privacy.xml:16–25`

```cpp
16: <audiodeviceprivacy version="1.0" xmlns:xi="http://www.w3.org/2001/XInclude">
17:     <adapter name="privacy">
18:         <devices>
19:             <device name="Wired Headset" type="DEVICE_TYPE_WIRED_HEADSET" role="output,input" Category="" usage="media,voice,recongnition"/>
20:             <device name="Wired Headphones" type="DEVICE_TYPE_WIRED_HEADPHONES" role="output" Category="" usage="media,voice"/>
21:             <device name="Usb Headset Hifi" type="DEVICE_TYPE_USB_HEADSET" role="output,input" Category="" usage="media,voice,recongnition"/>
22:             <device name="Usb Arm Headset" type="DEVICE_TYPE_USB_ARM_HEADSET" role="output,input" Category="" usage="media,voice,recongnition"/>
23:             <device name="Bt A2dp" type="DEVICE_TYPE_BLUETOOTH_A2DP" role="output" Category="HEADPHONE,GLASSES" usage="media"/>
24:             <device name="Bt Sco" type="DEVICE_TYPE_BLUETOOTH_SCO" role="output,input" Category="HEADPHONE,GLASSES," usage="voice,recongnition"/>
25:             <device name="Nearlink" type="DEVICE_TYPE_NEARLINK" role="output" Category="HEADPHONE,GLASSES" usage="media,voice"/>
```

### `services/audio_policy/server/infra/config/parser/src/audio_strategy_router_parser.cpp:34–47`

```cpp
34: bool AudioStrategyRouterParser::LoadConfiguration()
35: {
36:     curNode_ = AudioXmlNode::Create();
37:     int32_t ret = 0;
38: #ifdef USE_CONFIG_POLICY
39:     char buf[MAX_PATH_LEN];
40:     char *path = GetOneCfgFile(DEVICE_CONFIG_FILE, buf, MAX_PATH_LEN);
41:     if (path != nullptr && *path != '\0') {
42:         AUDIO_INFO_LOG("strategy router file path: %{public}s", path);
43:         ret = curNode_->Config(path, nullptr, 0);
44:     }
45: #else
46:     ret = curNode_->Config(DEVICE_CONFIG_FILE, nullptr, 0);
47:     AUDIO_INFO_LOG("use default strategy router file path:%{public}s", DEVICE_CONFIG_FILE);
```

### `services/audio_policy/server/domain/router/audio_router_center.cpp:43–60`

```cpp
43: shared_ptr<AudioDeviceDescriptor> AudioRouterCenter::FetchMediaRenderDevice(
44:     StreamUsage streamUsage, int32_t clientUID, RouterType &routerType, const std::set<RouterType> &bypassTypeSet,
45:     const uint32_t streamId)
46: {
47:     for (auto &router : mediaRenderRouters_) {
48:         RouterType usedType = router->GetRouterType();
49:         if (bypassTypeSet.count(usedType)) {
50:             AUDIO_INFO_LOG("bypass %{public}d", usedType);
51:             continue;
52:         }
53:         shared_ptr<AudioDeviceDescriptor> desc = router->GetMediaRenderDevice(streamUsage, clientUID, streamId);
54:         if ((desc != nullptr) && (desc->deviceType_ != DEVICE_TYPE_NONE)) {
55:             routerType = usedType;
56:             return desc;
57:         }
58:     }
59:     return make_shared<AudioDeviceDescriptor>();
60: }
```

### `services/audio_policy/server/domain/router/audio_router_center.cpp:308–329`

```cpp
308: std::vector<std::shared_ptr<AudioDeviceDescriptor>> AudioRouterCenter::FetchOutputDevicesInner(FetchDeviceInfo &info)
309: {
310:     auto earlyResult = PreFetchOutputDevices(info);
311:     CHECK_AND_RETURN_RET(earlyResult.empty(), earlyResult);
312: 
313:     StreamUsage streamUsage = info.streamUsage;
314:     int32_t clientUID = info.clientUID;
315:     RouterType routerType = ROUTER_TYPE_NONE;
316:     vector<std::shared_ptr<AudioDeviceDescriptor>> descs;
317:     FetchDeviceInfo bak = info;
318:     bak.preStreamUsage = streamUsage;
319:     bak.audioPipeType = PIPE_TYPE_OUT_NORMAL;
320: 
321:     if (renderConfigMap_[streamUsage] == MEDIA_RENDER_ROUTERS || renderConfigMap_[streamUsage] == TONE_RENDER_ROUTERS) {
322:         descs.push_back(FetchMediaOrToneRenderDevice(bak, clientUID, routerType, info.streamId));
323:     } else if (renderConfigMap_[streamUsage] == RING_RENDER_ROUTERS) {
324:         DealRingRenderRouters(descs, bak, routerType);
325:     } else if (renderConfigMap_[streamUsage] == CALL_RENDER_ROUTERS) {
326:         descs.push_back(FetchCallRenderDevice(streamUsage, clientUID, routerType, bak.bypassType));
327:     } else {
328:         AUDIO_INFO_LOG("streamUsage %{public}d didn't config router strategy, skipped", streamUsage);
329:         descs.push_back(make_shared<AudioDeviceDescriptor>());
```

### `services/audio_policy/server/domain/router/audio_router_center.cpp:384–405`

```cpp
384: std::vector<std::shared_ptr<AudioDeviceDescriptor>> AudioRouterCenter::PreFetchOutputDevices(
385:     const FetchDeviceInfo &info)
386: {
387:     int32_t zoneId = AudioZoneService::GetInstance().FindAudioZone(info.clientUID, info.streamUsage, OUTPUT_DEVICE,
388:         info.streamId);
389:     if (zoneId != 0) {
390:         vector<shared_ptr<AudioDeviceDescriptor>> zoneDescs =
391:             AudioZoneService::GetInstance().FetchOutputDevices(zoneId, info.streamUsage,
392:                 info.clientUID, ROUTER_TYPE_NONE);
393:         if (zoneDescs.size() != 0) {
394:             return zoneDescs;
395:         }
396:     }
397:     if (info.streamUsage == STREAM_USAGE_ULTRASONIC &&
398:         AudioStreamCollector::GetAudioStreamCollector().GetRunningStreamUsageNoUltrasonic() == STREAM_USAGE_INVALID) {
399:         AUDIO_INFO_LOG("Stream ULTRASONIC always choose spk");
400:         vector<shared_ptr<AudioDeviceDescriptor>> descs;
401:         descs.push_back(AudioDeviceManager::GetAudioDeviceManager().GetRenderDefaultDevice());
402:         return descs;
403:     }
404:     return {};
405: }
```

### `services/audio_policy/server/domain/zone/src/audio_zone_service.cpp:966–978`

```cpp
966: std::vector<std::shared_ptr<AudioDeviceDescriptor>> AudioZoneService::FetchOutputDevices(int32_t zoneId,
967:     StreamUsage streamUsage, int32_t clientUid, RouterType bypassType)
968: {
969:     std::vector<std::shared_ptr<AudioDeviceDescriptor>> devices;
970:     std::lock_guard<std::mutex> lock(zoneMutex_);
971:     auto zone = FindZone(zoneId);
972:     CHECK_AND_RETURN_RET_LOG(zone != nullptr, devices, "zone id %{public}d is not found", zoneId);
973:     auto res = zone->FetchOutputDevices(streamUsage, clientUid, bypassType);
974:     JUDGE_AND_INFO_LOG(!res.empty() && res.front() != nullptr, "fetch from zone %{public}d," \
975:         "usage:%{public}d, client:%{public}d router:%{public}d desc:%{public}s",
976:         zoneId, streamUsage, clientUid, bypassType, res.front()->GetName().c_str());
977:     return res;
978: }
```

### `services/audio_policy/server/domain/zone/src/audio_zone.cpp:467–483`

```cpp
467: std::vector<std::shared_ptr<AudioDeviceDescriptor>> AudioZone::FetchOutputDevices(StreamUsage streamUsage,
468:     int32_t clientUid, const RouterType &bypassType)
469: {
470:     std::lock_guard<std::mutex> lock(zoneMutex_);
471: #ifdef MULTI_USER_ZONE
472:     return zoneRouter_.FetchOutputDevices(devices_);
473: #else
474:     std::vector<std::shared_ptr<AudioDeviceDescriptor>> descs;
475:     for (const auto &device : devices_) {
476:         if (device.second && device.first->deviceRole_ == OUTPUT_DEVICE) {
477:             descs.emplace_back(device.first);
478:             return descs;
479:         }
480:     }
481:     return descs;
482: #endif
483: }
```

### `services/audio_policy/server/domain/zone/src/audio_zone_router.cpp:45–70`

```cpp
45: std::vector<std::shared_ptr<AudioDeviceDescriptor>> AudioZoneRouter::FetchOutputDevices(
46:     const std::list<std::pair<std::shared_ptr<AudioDeviceDescriptor>, bool>> &devices)
47: {
48:     std::vector<std::shared_ptr<AudioDeviceDescriptor>> result;
49:     for (const auto &item : devices) {
50:         CHECK_AND_CONTINUE(IsAvailableOutput(item));
51:         result.emplace_back(item.first);
52:     }
53: 
54:     std::sort(result.begin(), result.end(),
55:         [](const std::shared_ptr<AudioDeviceDescriptor> &a, const std::shared_ptr<AudioDeviceDescriptor> &b) {
56:             ZoneDevicePriority priorityA = AudioZoneRouter::GetZoneDevicePriority(a);
57:             ZoneDevicePriority priorityB = AudioZoneRouter::GetZoneDevicePriority(b);
58:             if (priorityA != priorityB) {
59:                 return static_cast<int32_t>(priorityA) > static_cast<int32_t>(priorityB);
60:             }
61:             if (priorityA == ZoneDevicePriority::ZONE_DEVICE_PRIORITY_BLUETOOTH) {
62:                 return a->connectTimeStamp_ > b->connectTimeStamp_;
63:             }
64:             return false;
65:         });
66: 
67:     return result;
68: }
69: 
70: std::shared_ptr<AudioDeviceDescriptor> AudioZoneRouter::FetchInputDevice(
```

### `services/audio_policy/server/domain/router/user_select_router.cpp:28–56`

```cpp
28: shared_ptr<AudioDeviceDescriptor> UserSelectRouter::GetMediaRenderDevice(StreamUsage streamUsage, int32_t clientUID,
29:     const uint32_t sessionID)
30: {
31:     if (streamUsage == STREAM_USAGE_RINGTONE || streamUsage == STREAM_USAGE_VOICE_RINGTONE ||
32:         streamUsage == STREAM_USAGE_VOICE_TRANSFER_RINGTONE) {
33:         AUDIO_INFO_LOG("Ringtone skip user select");
34:         return make_shared<AudioDeviceDescriptor>();
35:     }
36:     shared_ptr<AudioDeviceDescriptor> perDev_ =
37:         AudioRouterSelectStrategy::GetInstance().GetMediaOutputDevice(clientUID, sessionID);
38:     CHECK_AND_RETURN_RET_LOG(perDev_ != nullptr, make_shared<AudioDeviceDescriptor>(), "perDev is null");
39:     bool ret = CheckStreamUsage(perDev_, streamUsage);
40:     CHECK_AND_RETURN_RET(ret, make_shared<AudioDeviceDescriptor>());
41:     ret = CheckDpStreamUsage(perDev_, streamUsage);
42:     CHECK_AND_RETURN_RET(!ret, make_shared<AudioDeviceDescriptor>());
43:     vector<shared_ptr<AudioDeviceDescriptor>> mediaDevices =
44:         AudioDeviceManager::GetAudioDeviceManager().GetConnectedDevices();
45:     RouterBase::ClearConflictDevice(mediaDevices, GetRouterType());
46:     RouterBase::ReplaceConflictA2dpWithSco(perDev_, GetRouterType());
47:     if (perDev_->deviceId_ == 0 || !RouterBase::IsDeviceUsageSupported(MEDIA_OUTPUT_DEVICES, perDev_)) {
48:         AUDIO_DEBUG_LOG(" PreferredMediaRenderDevice is null or device is not available now");
49:         return make_shared<AudioDeviceDescriptor>();
50:     } else {
51:         int32_t audioId = perDev_->deviceId_;
52:         AUDIO_INFO_LOG(" PreferredMediaRenderDevice audioId is %{public}d", audioId);
53:         return RouterBase::GetPairDevice(perDev_, mediaDevices, MEDIA_OUTPUT_DEVICES);
54:     }
55: }
56: 
```

### `services/audio_policy/server/domain/router/privacy_priority_router.cpp:27–38`

```cpp
27: shared_ptr<AudioDeviceDescriptor> PrivacyPriorityRouter::GetMediaRenderDevice(StreamUsage streamUsage,
28:     int32_t clientUID, const uint32_t sessionID)
29: {
30:     vector<shared_ptr<AudioDeviceDescriptor>> descs =
31:         AudioDeviceManager::GetAudioDeviceManager().GetMediaRenderPrivacyDevices();
32:     AppendActiveScoDevice(descs);
33:     RouterBase::ClearConflictDevice(descs, GetRouterType());
34:     shared_ptr<AudioDeviceDescriptor> desc = GetLatestNonExcludedConnectDevice(MEDIA_OUTPUT_DEVICES, descs);
35:     AUDIO_DEBUG_LOG("streamUsage %{public}d clientUID %{public}d fetch device %{public}d", streamUsage,
36:         clientUID, desc->deviceType_);
37:     return desc;
38: }
```

### `services/audio_policy/server/domain/router/router_base.h:72–101`

```cpp
72:     std::shared_ptr<AudioDeviceDescriptor> GetLatestNonExcludedConnectDevice(AudioDeviceUsage audioDevUsage,
73:         std::vector<std::shared_ptr<AudioDeviceDescriptor>> &descs, StreamUsage streamUsage = STREAM_USAGE_UNKNOWN)
74:     {
75:         std::vector<std::shared_ptr<AudioDeviceDescriptor>> filteredDescs;
76:         // remove abnormal device or excluded device
77:         for (const auto &desc : descs) {
78:             CHECK_AND_CONTINUE(desc != nullptr &&
79:                 !AudioRouterSelectStrategy::GetInstance().IsDeviceTypeSkipped(desc->deviceType_));
80:             if (desc->exceptionFlag_ || !desc->isEnable_ ||
81:                 (desc->deviceType_ == DEVICE_TYPE_BLUETOOTH_SCO &&
82:                     (desc->connectState_ == SUSPEND_CONNECTED ||
83:                         AudioRouterSelectStrategy::GetInstance().GetScoExcluded())) ||
84:                 AudioRouterSelectStrategy::GetInstance().IsDeviceExcluded(desc, audioDevUsage) ||
85:                 !IsDeviceUsageSupported(audioDevUsage, desc) ||
86:                 IsNeedSilentControl(desc, streamUsage)) {
87:                 continue;
88:             }
89:             CHECK_AND_CONTINUE(!ExistSameRemoteCarWithA2DP(desc));
90:             CHECK_AND_CONTINUE(!CheckDpStreamUsage(desc, streamUsage));
91:             filteredDescs.push_back(desc);
92:         }
93:         if (filteredDescs.size() > 0) {
94:             auto compare = [&] (std::shared_ptr<AudioDeviceDescriptor> &desc1,
95:                 std::shared_ptr<AudioDeviceDescriptor> &desc2) {
96:                 return desc1->connectTimeStamp_ < desc2->connectTimeStamp_;
97:             };
98:             sort(filteredDescs.begin(), filteredDescs.end(), compare);
99:             return std::move(filteredDescs.back());
100:         }
101:         return std::make_shared<AudioDeviceDescriptor>();
```

### `services/audio_policy/server/domain/router/default_router.cpp:26–36`

```cpp
26: shared_ptr<AudioDeviceDescriptor> DefaultRouter::GetMediaRenderDevice(StreamUsage streamUsage, int32_t clientUID,
27:     const uint32_t sessionID)
28: {
29:     auto desc = AudioRouterSelectStrategy::GetInstance().GetMediaDefaultOutputDevice(clientUID, sessionID);
30:     if (desc == nullptr) {
31:         desc = AudioDeviceManager::GetAudioDeviceManager().GetRenderDefaultDevice();
32:     }
33:     AUDIO_DEBUG_LOG("streamUsage %{public}d clientUID %{public}d fetch device %{public}d", streamUsage, clientUID,
34:         desc->deviceType_);
35:     return desc;
36: }
```

### `services/audio_policy/server/domain/device/src/audio_device_manager.cpp:928–932`

```cpp
928: shared_ptr<AudioDeviceDescriptor> AudioDeviceManager::GetRenderDefaultDevice()
929: {
930:     shared_ptr<AudioDeviceDescriptor> devDesc = make_shared<AudioDeviceDescriptor>(speaker_);
931:     return devDesc;
932: }
```

### `services/audio_policy/server/domain/device/src/audio_device_status.cpp:147–167`

```cpp
147:     if (isConnected) {
148:         // If device already in list, remove it else do not modify the list
149:         audioConnectedDevice_.DelConnectedDevice(updatedDesc.networkId_, updatedDesc.deviceType_,
150:             updatedDesc.macAddress_, updatedDesc.deviceRole_);
151:         // If the pnp device fails to load, it will not connect
152:         result = HandleLocalDeviceConnected(updatedDesc);
153:         CHECK_AND_RETURN_LOG(result == SUCCESS, "Connect local device failed.");
154:         audioDeviceCommon_.UpdateConnectedDevicesWhenConnecting(updatedDesc, descForCb);
155: 
156:         reason = AudioStreamDeviceChangeReason::NEW_DEVICE_AVAILABLE;
157:     } else {
158:         audioDeviceCommon_.UpdateConnectedDevicesWhenDisconnecting(updatedDesc, descForCb);
159:         reason = AudioStreamDeviceChangeReason::OLD_DEVICE_UNAVALIABLE;
160:     }
161: 
162:     TriggerDeviceChangedCallback(descForCb, isConnected);
163:     TriggerAvailableDeviceChangedCallback(descForCb, isConnected);
164: 
165:     // fetch input&output device
166:     coreService->FetchOutputDeviceAndRoute("OnDeviceStatusUpdated_2", reason);
167:     coreService->FetchInputDeviceAndRoute("OnDeviceStatusUpdated_2", reason);
```

### `services/audio_policy/server/service/service_main/src/audio_core_service.cpp:2795–2806`

```cpp
2795: 
2796:     AudioCoreServiceUtils::SortOutputStreamDescsForUsage(outputStreamDescs);
2797:     BatchFetchAndStartOutputStreams(outputStreamDescs, caller);
2798:     // todo fix
2799:     HandleA2dpSuspendWhenFetch(reason, audioRouterSelectStrategy_.Get1stCurrentOutputDevice(), outputStreamDescs);
2800:     // this will update volume device map
2801:     audioActiveDevice_.UpdateStreamDeviceMapForOutput("FetchOutputDeviceAndRoute");
2802:     audioActiveDevice_.UpdateUidVolumeDeviceMapForEnhancedRouting();
2803:     // here will update volume must after UpdateStreamDeviceMap
2804:     bool deviceUpdate = UpdateActiveDeviceAndVolumeBeforeMoveSession(outputStreamDescs, reason);
2805: 
2806:     int32_t ret = FetchRendererPipesAndExecute(outputStreamDescs, reason);
```

### `services/audio_policy/server/service/service_main/src/audio_core_service_private.cpp:3534–3551`

```cpp
3534:     std::string fetchCaller = caller + "FetchOutputDeviceAndRoute";
3535:     std::vector<FetchDeviceInfo> outInfos;
3536:     for (auto &streamDesc : outputStreamDescs) {
3537:         CHECK_AND_CONTINUE(streamDesc != nullptr);
3538:         CHECK_AND_CONTINUE(!(VolumeUtils::IsPCVolumeEnable() && !isFirstScreenOn_.load()));
3539:         CHECK_AND_CONTINUE(streamDesc->rendererTarget_ != INJECT_TO_VOICE_COMMUNICATION_CAPTURE);
3540:         StreamUsage streamUsage = audioSessionService_.GetAudioSessionStreamUsageForDevice(GetRealPid(streamDesc));
3541:         streamUsage = (streamUsage != StreamUsage::STREAM_USAGE_INVALID) ? streamUsage :
3542:             streamDesc->rendererInfo_.streamUsage;
3543:         FetchDeviceInfo info = { streamUsage, GetRealUid(streamDesc), streamDesc->GetRenderPrivacyType(),
3544:             fetchCaller, streamDesc->bundleName_ };
3545:         info.streamId = streamDesc->sessionId_;
3546:         outInfos.push_back(info);
3547:     }
3548:     auto outResult = audioRouterCenter_.FetchOutputDevicesForAllOutputStreams(outInfos);
3549:     for (auto &streamDesc : outputStreamDescs) {
3550:         UpdateStreamDevicesForStart(streamDesc, fetchCaller, outResult);
3551:     }
```

### `services/audio_policy/server/service/service_main/src/audio_core_service_private.cpp:3571–3579`

```cpp
3571:     } else {
3572:         auto it = outResult.find(streamDesc->sessionId_);
3573:         if (it != outResult.end()) {
3574:             devices = it->second;
3575:         }
3576:     }
3577: 
3578:     CHECK_AND_RETURN_LOG(!devices.empty(), "devices is empty");
3579:     pipeManager_->UpdateNewDeviceDescWithCheck(streamDesc, devices);
```

### `services/audio_policy/server/domain/pipe/src/audio_pipe_selector.cpp:2217–2226`

```cpp
2217: AudioStreamAction AudioPipeSelector::JudgeStreamAction(
2218:     std::shared_ptr<AudioPipeInfo> newPipe, std::shared_ptr<AudioPipeInfo> oldPipe)
2219: {
2220:     CHECK_AND_RETURN_RET(!IsRemoteOffloadNeedRecreate(newPipe, oldPipe), AUDIO_STREAM_ACTION_RECREATE);
2221: 
2222:     if (AudioPipeManager::GetPipeManager()->IsSamePipe(newPipe, oldPipe)) {
2223:         return AUDIO_STREAM_ACTION_DEFAULT;
2224:     }
2225:     return AUDIO_STREAM_ACTION_MOVE;
2226: }
```

### `services/audio_policy/server/domain/pipe/src/audio_pipe_manager.cpp:349–356`

```cpp
349: bool AudioPipeManager::IsSamePipe(std::shared_ptr<AudioPipeInfo> info, std::shared_ptr<AudioPipeInfo> cmpInfo)
350: {
351:     CHECK_AND_RETURN_RET_LOG(info && cmpInfo, false, "info or cmpInfo is nullptr");
352:     if (info->name_ == cmpInfo->name_ || info->id_ == cmpInfo->id_) {
353:         return true;
354:     }
355:     return false;
356: }
```

### `services/audio_policy/server/service/service_main/src/audio_core_service_private.cpp:1087–1097`

```cpp
1087:             case AUDIO_STREAM_ACTION_DEFAULT:
1088:             case AUDIO_STREAM_ACTION_MOVE:
1089:                 CheckAndUpdateOffloadEnableForStream(OFFLOAD_MOVE_OUT, desc, pipeInfo->id_);
1090:                 if (desc->streamStatus_ != STREAM_STATUS_STARTED ||
1091:                     pipeManager_->IsFocusStandby(desc->sessionId_)) {
1092:                     MoveStreamSink(desc, pipeInfo, reason);
1093:                 } else {
1094:                     MoveToNewOutputDevice(desc, pipeInfo, reason);
1095:                 }
1096:                 CheckAndUpdateOffloadEnableForStream(OFFLOAD_MOVE_IN, desc, pipeInfo->id_);
1097:                 break;
```

### `services/audio_policy/server/service/service_main/src/audio_core_service_private.cpp:1696–1713`

```cpp
1696:     auto pipeDeviceVolumeGroup = AudioPipeManager::GetPipeManager()->GetPipeDeviceVolumeInfoForPipe(pipeInfo);
1697:     AudioAdapterManager::GetInstance().UpdateAudioPipeVolume(pipeDeviceVolumeGroup);
1698: 
1699:     auto ret = (newDeviceDesc->networkId_ == LOCAL_NETWORK_ID)
1700:         ? MoveToLocalOutputDevice(targetSinkInputs, pipeInfo, newDeviceDesc)
1701:         : MoveToRemoteOutputDevice(targetSinkInputs, pipeInfo, newDeviceDesc);
1702:     CHECK_AND_CALL_FUNC_RETURN_HILOG(ret == SUCCESS,
1703:         StreamDfxManager::GetInstance().SendAudioErrorEvent(IPCSkeleton::GetCallingUid(),
1704:             ERR_PLAY_DEVICE_SWITCH_OPERATION_FAILED, "MoveToNewOutputDevice failed", false),
1705:         "[MoveToNewOutputDevice]Move sink faild!");
1706: 
1707:     sleAudioDeviceManager_.UpdateSleStreamTypeCount(streamDesc, false);
1708:     bool shouldUpdateOutputRoute = ShouldUpdateOutputRoute(streamDesc, reason);
1709:     if (pipeManager_->GetUpdateRouteSupport() && shouldUpdateOutputRoute) {
1710:         UpdateOutputRoute(streamDesc, pipeInfo->id_);
1711:     }
1712: 
1713:     streamCollector_.UpdateRendererDeviceInfo(newDeviceDesc);
```

### `services/audio_policy/server/service/service_main/src/audio_core_service_private.cpp:2361–2375`

```cpp
2361:     // start move.
2362:     uint32_t sinkId = -1; // invalid sink id, use sink name instead.
2363:     std::vector<uint64_t> sessionIdForLog{};
2364:     std::string sinkName = localDeviceDescriptor->deviceType_ == DEVICE_TYPE_REMOTE_CAST ?
2365:             "RemoteCastInnerCapturer" : pipeInfo->moduleInfo_.name;
2366:     for (size_t i = 0; i < sinkInputIds.size(); i++) {
2367:         if (sinkName == BLUETOOTH_SPEAKER) {
2368:             std::string activePort = BLUETOOTH_SPEAKER;
2369:             audioPolicyManager_.SuspendAudioDevice(activePort, false);
2370:         }
2371:         int32_t ret = audioPolicyManager_.MoveSinkInputByIndexOrName(sinkInputIds[i].paStreamId, sinkId, sinkName);
2372:         CHECK_AND_RETURN_RET_LOG(ret == SUCCESS, ERROR,
2373:             "move [%{public}d] to local failed", sinkInputIds[i].streamId);
2374:         sessionIdForLog.push_back(sinkInputIds[i].streamId);
2375:         audioRouteMap_.AddRouteMapInfo(sinkInputIds[i].uid, LOCAL_NETWORK_ID, sinkInputIds[i].pid);
```

### `services/audio_engine/manager/src/hpae_manager.cpp:1065–1091`

```cpp
1065: int32_t HpaeManager::MoveSinkInputByIndexOrName(uint32_t sinkInputId, uint32_t sinkIndex, std::string sinkName)
1066: {
1067:     auto request = [this, sinkInputId, sinkName]() {
1068:         if (!CheckMoveSinkInput(sinkInputId, sinkName)) {
1069:             if (auto serviceCallback = serviceCallback_.lock()) {
1070:                 serviceCallback->OnMoveSinkInputByIndexOrNameCb(ERROR_INVALID_PARAM);
1071:             }
1072:             return;
1073:         }
1074: 
1075:         std::string name = rendererIdSinkNameMap_[sinkInputId];
1076:         if (sinkName == name) {
1077:             if (auto serviceCallback = serviceCallback_.lock()) {
1078:                 serviceCallback->OnMoveSinkInputByIndexOrNameCb(SUCCESS);
1079:             }
1080:             return;
1081:         }
1082: 
1083:         std::shared_ptr<IHpaeRendererManager> oldRendererManager = GetRendererManagerById(sinkInputId);
1084:         AUDIO_INFO_LOG("start move session:%{public}u, [%{public}s] --> [%{public}s],state:%{public}d", sinkInputId,
1085:             GetEncryptStr(name).c_str(), GetEncryptStr(sinkName).c_str(), rendererIdStreamInfoMap_[sinkInputId].state);
1086:         movingIds_.emplace(sinkInputId, rendererIdStreamInfoMap_[sinkInputId].state);
1087:         oldRendererManager->MoveStream(sinkInputId, sinkName);
1088:     };
1089:     SendRequest(request, __func__);
1090:     return SUCCESS;
1091: }
```

### `services/audio_policy/server/service/service_main/src/audio_core_service_private.cpp:2074–2099`

```cpp
2074: void AudioCoreService::UpdateOutputRoute(std::shared_ptr<AudioStreamDescriptor> streamDesc, const uint32_t pipeId)
2075: {
2076:     CHECK_AND_RETURN_LOG(streamDesc != nullptr && streamDesc->newDeviceDescs_.size() > 0 &&
2077:         streamDesc->newDeviceDescs_.front() != nullptr, "streamDesc is nullptr");
2078:     StreamUsage streamUsage = streamDesc->rendererInfo_.streamUsage;
2079:     InternalDeviceType deviceType = streamDesc->newDeviceDescs_.front()->deviceType_;
2080:     AUDIO_DEBUG_LOG("[PipeExecInfo] Update route streamUsage:%{public}d, devicetype:[%{public}s]",
2081:         streamUsage, streamDesc->GetNewDevicesTypeString().c_str());
2082: 
2083:     if (Util::IsEnhancedRoutingSupported()) {
2084:         AudioScene pipeScene = CalculatePipeAudioScene(pipeId);
2085:         AudioServerProxy::GetInstance().SetAudioSceneForPipeProxy(pipeId, pipeScene, false);
2086:         AUDIO_INFO_LOG("Set AudioScene %{public}d for pipe %{public}u in multi-device mode", pipeScene, pipeId);
2087:     }
2088:     shouldUpdateDeviceDueToDualTone_ = false;
2089:     if (Util::IsRingerOrAlarmerStreamUsage(streamUsage) && IsRingerOrAlarmerDualDevicesRange(deviceType) &&
2090:         !VolumeUtils::IsPCVolumeEnable()) {
2091:         HandleRingerOrAlarmerRoute(streamDesc, deviceType, pipeId, streamUsage);
2092:     } else if (AudioCollaborativeService::GetAudioCollaborativeService().GetRealCollaborativeState() &&
2093:         (streamDesc->isNearLinkCollaborationEnable_ || deviceType == DEVICE_TYPE_BLUETOOTH_A2DP ||
2094:         CheckCollaborativeStreamRunning())) {
2095:         // for collaboration, the route should be updated
2096:         UpdateRouteForCollaboration(deviceType, pipeId);
2097:     } else {
2098:         HandleNormalOrDualToneRoute(streamDesc, deviceType, pipeId, streamUsage);
2099:     }
```
