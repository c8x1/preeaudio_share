# 鸿蒙音频底座技术分享 · Implementation Notes

最后更新：2026-10-20。当前技术深化版位于 hongmeng_audio_design_review；旧版 hongmeng_audio_foundation 保留为历史基线。后续先读本文件的当前版本表，再读该页JSON和review。

## 当前技术深化版（制作与逐页复审已完成）

主讲15页建议55分钟（包含读图、互动与停顿），另5分钟答疑。A1–A6按需。已按用户反馈把真实时序、状态机、算法条件与新旧设计对照放到正文。每页均重新独立审查，旧版PASS没有沿用。

| 页 | 当前主题 | 状态 |
|---|---|---|
| P01 | 一次 Start，什么时候才算开始播放？ | [PASS](hongmeng_audio_design_review/reviews/P01.md) |
| P02 | 音频底座的对象与通信通道 | [PASS](hongmeng_audio_design_review/reviews/P02.md) |
| P03 | Start 如何穿过策略、服务与两级队列 | [PASS](hongmeng_audio_design_review/reviews/P03.md) |
| P04 | 5.1 方案：PA Start 的同步返回与操作回调 | [PASS](hongmeng_audio_design_review/reviews/P04.md) |
| P05 | 5.1 普通主输出：渲染与 HDI 写分属两线程 | [PASS](hongmeng_audio_design_review/reviews/P05.md) |
| P06 | 同一普通输出路径：跨线程交接在哪里收拢 | [PASS](hongmeng_audio_design_review/reviews/P06.md) |
| P07 | 新处理线程：消息与音频怎样共用执行循环 | [PASS](hongmeng_audio_design_review/reviews/P07.md) |
| P08 | Buffer 减在哪，仍保留在哪 | [PASS](hongmeng_audio_design_review/reviews/P08.md) |
| P09 | 无锁消息队列：CAS 发布与批次消费 | [PASS](hongmeng_audio_design_review/reviews/P09.md) |
| P10 | 节点图：输出端拉取，处理结果正向返回 | [PASS](hongmeng_audio_design_review/reviews/P10.md) |
| P11 | 接入会话音效：成功创建后才重连 | [PASS](hongmeng_audio_design_review/reviews/P11.md) |
| P12 | Pause / Stop：淡出完成后再断开节点 | [PASS](hongmeng_audio_design_review/reviews/P12.md) |
| P13 | 切换设备：迁移输入对象，重建目标连接 | [PASS](hongmeng_audio_design_review/reviews/P13.md) |
| P14 | 性能观测：分别记录控制确认和数据执行 | [PASS](hongmeng_audio_design_review/reviews/P14.md) |
| P15 | 自研的技术价值，落在可验证的执行设计上 | [PASS](hongmeng_audio_design_review/reviews/P15.md) |
| P16 | A1  Buffer 参数怎样避免比错 | [PASS](hongmeng_audio_design_review/reviews/P16.md) |
| P17 | A2  队列容量与耗尽路径 | [PASS](hongmeng_audio_design_review/reviews/P17.md) |
| P18 | A3  一次 Pull：有结果就取，空队列才计算 | [PASS](hongmeng_audio_design_review/reviews/P18.md) |
| P19 | A4  迟到的 Drain 回调，怎样避免复活已停流 | [PASS](hongmeng_audio_design_review/reviews/P19.md) |
| P20 | A5  设备迁移：PA 与 HPAE 的真实设计对照 | [PASS](hongmeng_audio_design_review/reviews/P20.md) |
| P21 | A6  版本、路径与证据范围 | [PASS](hongmeng_audio_design_review/reviews/P21.md) |

源文件：pages/Pxx.json 为权威内容，包含技术讲稿、来源与原生元素。构建：build/rebuild.ps1。全页重审记录：reviews/TECHNICAL_REDESIGN_AUDIT.md。GitHub：https://github.com/c8x1/preeaudio_share；P01–P21已逐页通过后提交推送，最终整合提交另记。

## 已确认的定位

标题：《一段声音的旅程——鸿蒙音频底座的协同与自研演进》。

核心问题：鸿蒙怎样协调应用、场景和设备，让声音及时、稳定地播放？自研引擎怎样改善整套系统的效率？

受众：跨领域新员工，具备一般软件/算法背景。跳过 PCM、采样率等基础教学。分享范围是整个系统音频底座，覆盖应用接口、策略、流服务、引擎、设备适配与驱动。引擎是重点，策略必须贯穿全场。

叙事：系统体验与全局协同 → 原有方案的演进压力 → 执行层三项创新 → 回到整个底座验证收益。

贯穿场景：音乐播放，游戏音效加入，收到提醒，切到耳机。焦点/duck/并发与路由结果由具体策略决定，不编造所有产品的统一规则。

## 用户提供的团队事实

- 自研带来时延降低、性能提升、功耗降低。
- 无锁消息队列减少原有锁竞争，使消息流转更顺畅。
- 精简并合并部分 PA 线程，减少 Buffer，同时保持端到端抗抖动能力。
- 节点按职责分工、灵活组装通路，减少按通路分别实现的重复，提高扩展性。
- 以上采用团队定性说明。量化收益、产品测试条件、贡献人尚缺失，不编造。

## 源码基线与边界

- 当前 multimedia_audio_framework：3a2688e805df970739e3b0cebf9cc05d8cb24e9b，目录 source_gitcode。
- 5.1 Release framework：c42a228d60b64a90d6b05cf26278a89253e5310b，目录 source_audio_5_1。
- 5.1 PulseAudio：bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca，source_pulseaudio Git 对象可读。
- 旧报告供检索：preeaudio_onboarding/appendix/technical_expert_review.md、pulseaudio_5_1_review.md、thread_buffer_evolution_review.md。引用须指固定 commit 和函数/行号。
- 可证实：旧普通主输出渲染线程通过 primary.dq 交给独立 HDI 写线程；新 HPAE 处理线程拉图后直接调用 RenderFrame。仅此层的交接集中，不能声称所有驱动线程消失。
- 无锁队列常规发布/摘取用原子操作；扩容、Notify、共享缓冲读取仍有锁。不声称全链无锁、零拷贝。
- 保持抗抖动是用户团队结论，静态结构不单独证明等价。

## 最初批准的提纲（历史记录；当前主题以顶部表格为准）

### 第一部分 · 一段声音，牵动整个音频底座（10分钟）

1. **我们要交付怎样的声音体验（3分钟）**：贯穿场景提出多应用行为合理、设备切换符合预期、响应及时、播放连续、资源开销可控。全局体验目标，不展开基础音频概念。
2. **鸿蒙音频底座：谁决策，谁管理，谁执行（4分钟）**：全局图覆盖应用接口、音频策略、流服务、自研引擎、设备适配与驱动。明确职责、控制关系和数据方向，并突出引擎侧重点。
3. **一次场景变化，怎样传遍整个系统（3分钟）**：游戏加入、切耳机。策略决定并发与路由，服务协调流和状态，引擎调整处理图，设备输出。行为由全链协作产生。

### 第二部分 · 为什么演进原有音频底座（10分钟）

4. **PulseAudio时代，我们怎样实现这些能力（4分钟）**：5.1鸿蒙策略/服务、PA流与处理模型、自定义音效和HDI适配。PA不是外部纯黑盒。
5. **业务要求提高后，成本出现在哪里（3分钟）**：线程/缓冲交接、控制同步竞争、不同通路实现与维护成本，对应响应、效率和演进。区别事实与机制解释。
6. **自研要改变什么，又必须守住什么（3分钟）**：时延/性能/功耗/扩展目标，抗抖动、策略语义、已有场景与设备能力约束。引出三项创新。

### 第三部分 · 自研引擎怎样改善底座的执行效率（23分钟）

7. **线程精简：减少声音在执行环节之间的交接（4分钟）**：新旧线程职责，已取消的交接，排队/唤醒/调度影响。
8. **Buffer精简：降低时延，怎样同时守住抗抖动（4分钟）**：哪些中转减少，哪些余量/适配缓存保留，设计机制与验证口径。
9. **无锁消息队列：让控制变化顺畅进入执行侧（4分钟）**：音量/启动暂停等控制事件，旧锁保护实例、新原子发布/消费、执行侧状态与无锁边界。
10. **节点化：把通路中的处理职责变成可复用单元（4分钟）**：节点/簇/Manager，转换/增益/混音/音效组合，展示职责而非纯类名。
11. **一个新需求，怎样通过节点组合接入（3分钟）**：代码确认的会话音效可选接入例子，对比通路职责修改与现有Converter/Gain/Mixer复用。无内部项目材料时讲明确的源码功能例子，不冒充团队项目成果。
12. **回到全局：策略决定变化，引擎执行变化（4分钟）**：重访开场场景，把策略决策、服务协调、引擎消息/处理图、设备输出连起来，三项创新服务上层业务。

### 第四部分 · 从架构改进到真实系统收益（12分钟）

13. **收益怎样在整条音频链路上体现（4分钟）**：机制对应时延/性能/功耗/扩展，区分局部与端到端。没有自动按结构推算百分比。
14. **用一个完整场景验证改进（4分钟）**：真实数据缺失，采用可执行验证设计，说明设备/负载/扰动/时延/CPU或能量/欠载/切换指标；呈现团队定性结论，不伪造实验结果。
15. **鸿蒙音频底座的演进：协同有序，执行高效，扩展灵活（4分钟）**：回扣策略组织行为、服务管理状态、引擎执行效率、设备兑现输出，用贯穿场景收束。

### 可选技术附录（主讲完成后按需）

A1 新旧完整线程与Buffer对照；A2 无锁队列并发机制与异常边界；A3 真实节点连接与拉取执行；A4 策略/服务/引擎控制时序；A5 设备迁移状态衔接；A6 源码版本与指标定义。

## 制作与逐页评审流程

1. 新建 hongmeng_audio_foundation，逐页内容独立JSON，配讲稿、来源、可见结论、承接句和页面目标。
2. 每完成一页，构建可编辑页面并渲染PNG，再交 page_reviewer subagent 审查。
3. 审查维度：提纲覆盖、技术准确、叙事承接、屏幕/讲稿分工、视觉可读。具体缺漏必须修订；无阻断问题才进入下一页。
4. 每页评审落盘 reviews/Pxx.md，并在下表记录通过或带条件通过。最终全套结构验收、备注一致性、媒体检查及打包。
5. 不复制旧版增量补丁结构。新PPT由独立构建脚本生成，图表/架构以原生对象保持可编辑。
6. 需要氛围图可用gpt-image，架构不可伪造为生成图。音频为原创演示，不能冒充实机故障或测量结果。

## 上一版制作状态（历史）

| 页 | 状态 | 评审记录 |
|---|---|---|
| P01 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P01.md) |
| P02 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P02.md) |
| P03 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P03.md) |
| P04 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P04.md) |
| P05 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P05.md) |
| P06 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P06.md) |
| P07 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P07.md) |
| P08 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P08.md) |
| P09 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P09.md) |
| P10 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P10.md) |
| P11 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P11.md) |
| P12 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P12.md) |
| P13 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P13.md) |
| P14 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P14.md) |
| P15 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P15.md) |
| P16 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P16.md) |
| P17 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P17.md) |
| P18 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P18.md) |
| P19 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P19.md) |
| P20 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P20.md) |
| P21 | 评审通过 | [评审](hongmeng_audio_foundation/reviews/P21.md) |

## 实施日志

- 2026-10-17：用户确认整体底座视角与15页提纲；要求持久化notes并逐页subagent review。本轮开始创建独立交付目录。

## 待补材料

讲师/团队正式信息；内部产品与公开commit对应；量化成果的测试平台、负载、数据与披露口径；真实项目协同故事；最终现场PowerPoint/WPS和音响试听。

- 2026-10-18进度：P01–P08通过逐页评审；P07简化末行措辞、P08补缓冲职责图折叠说明；P09首次发现标题过长，修复后复审。

- 2026-10-18完成：P01–P21逐页subagent审查全部PASS。P09标题、P10控制连线、P17原子摘取/执行措辞经修订复审。主讲15页55分钟、另5分钟答疑及6页技术附录均完成。当前正式文案为hongmeng_audio_foundation/pages/Pxx.json；完整构建、媒体、证据与review随新交付目录保存。

## 2026-10-18 用户反馈后的技术深化修订（进行中）

旧版 PASS 不代表本轮通过。用户要求以 P19 时序图为密度标准，先全页重审，再逐页修改并经 subagent 复审。新版目录：hongmeng_audio_design_review；旧版保留。

全页审查：[TECHNICAL_REDESIGN_AUDIT.md](hongmeng_audio_design_review/reviews/TECHNICAL_REDESIGN_AUDIT.md)。新的逐页主线如下：

P01 启动的三个观察点；P02 真实对象与通道；P03 启动的跨层时序；P04 PA 启动与回调；P05 PA 普通输出双线程；P06 新旧提交链对比；P07 新线程调度循环；P08 缓存与输出拼帧；P09 CAS 发布与批次消费；P10 节点图与反向拉取；P11 会话音效局部重连；P12 Pause/Stop 淡出状态机；P13 设备迁移时序；P14 延迟事件观测；P15 新旧设计证据总结；P16 缓存参数核对；P17 队列扩容状态；P18 Pull 缓存条件；P19 Start 精细异步关系；P20 迁移对象与旧 PA 对照；P21 分支和证据索引。

本轮通过标准：图上有真实对象、调用或状态、条件和执行边界；技术页至少解释一个非显然设计；量化收益仍等待产品数据。每页新评审见新版 reviews/Pxx.md。

## 2026-10-19 技术深化进度

新版主讲 P01–P15 已全部经逐页 subagent 复审 PASS，并逐页推送到 https://github.com/c8x1/preeaudio_share 。附录P16–P21也已全部修订并复审PASS。每页正文的真实设计已提升到画面。P19改为迟到Drain回调竞态，避免重复主讲P03的Start时序。

源码专家补核验了5.1第三方PA本体：旧PA迁移也复用同一sink_input，采用旧/目标sink I/O的同步消息握手。新版P20将如实比较同步与节点组织，不能把对象复用宣传为自研独有。

- 2026-10-20：完成技术深化版21页逐页审查与推送，整套讲稿承接、输出文件与预览一致性验收已完成。P19改为迟到Drain回调竞态；P20以PA本体说明两种方案都复用输入对象。

- 最终验收：21页/21份备注/21张预览/21页复审及整套叙事复审通过；668个原生可编辑对象，3个配套原创WAV。PPTX已完成工具导出、包结构/字体/几何/再导入核验，尚未在PowerPoint/WPS原生程序和现场音响验收。新完整输出：hongmeng_audio_design_review/鸿蒙音频底座_技术深化版.pptx；独立交付包：鸿蒙音频底座_技术深化版_全套交付.zip。
