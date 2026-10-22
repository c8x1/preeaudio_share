# 一首歌，三个操作

十一页音频引擎场景演示稿，以暂停、恢复播放、切换耳机为主线。页面使用可编辑机制图，源码依据放在演讲备注和备讲材料中。

- [可编辑演示稿](一首歌三个操作_场景演示稿.pptx)
- [全部页面预览](全部页面预览.html)：下载本目录后用浏览器打开。
- [本版逐页讲稿与源码依据](speaker_notes.md)
- `pages/`：六页内容与图形位置。
- `previews/`：逐页 PNG。
- `assets/diagrams/`：逐页 SVG。

2026-10-21 修订：P3 展示请求排队与执行，P4 对比淡入设置时机，P5 展示设备切换的三个阶段。全篇使用“音乐 A”标记同一路会话，删除重复总结。

2026-10-21 二次修订：装上“表面简单→底层复杂→复杂必要”的叙事脊。P1 立三次点击的表面简单，并预告三种朴素做法会听到的失败声；P2–P4 的失败模式改为耳朵语言，P3 补“若不检查”的后果；P5 补朴素做法（停下重开）的代价；P6 收出时间、队列、状态、设备差异、耳朵五样约束再桥接下一部分。讲稿正文只留口播语言，演示顺序、范围与源码依据移入文末备讲附录；页面脚注只保留图例类短句。

2026-10-21 三次修订：兑现开头承诺，新增两页实现篇。P6“这些请求，谁来执行？”给出执行模型——控制请求进免锁队列、由信号处理线程先排空队列再跑一轮音频处理，淡出完成由处理链在真实数据上就地回调，短淡出 5 毫秒；P7“三个保证，落在代码的哪里？”逐行映射暂停渐变、恢复首行状态检查、淡入先于音效（含代码注释原文语义）、切耳机参数调整的代码落点。原总结页顺延为 P8，桥接改为“换 PA 会怎样”。源码依据整体更新至主干 0d073de5（2026-10-21），原引用行号未变，新增增益节点与信号处理线程两处引用。

2026-10-21 四次修订：新增三页时序图，把执行模型落成完整跑动。P7“一次暂停，从头到尾”：暂停请求→入队→挂淡出→逐帧淡出→就地回调→收尾入队→执行收尾→状态回调；P8“恢复抢先一步”：恢复请求排在旧收尾前，旧收尾首行检查后直接返回；P9“切到耳机：三方接力”：设备策略→管理器→旧侧摘除并交接同一输入节点→目标侧调帧长、运行中接入→归属更新。统一四泳道（应用/渲染管理器/请求队列·信号线程/处理链·增益节点，P9 为三方）。原保证表顺延为 P10、总结页顺延为 P11。时序图均为源码调用关系的简化示意。

PPTX 含原生点击出现效果，每页 1–2 次点击。HTML 预览也支持逐步揭示；PNG 为全部内容展开状态。机制范围为普通 HPAE 播放路径，条件时序不代表每次用户点击都会复现，未开展设备性能实验。动画结构经过检查，尚未在桌面 PowerPoint 中实际放映验证。

## 构建

沿用仓库现有的 `@oai/artifact-tool` 构建环境，字体为 Microsoft YaHei。运行时路径见 `hongmeng_audio_design_review/build/README.md`，新环境需调整本机绝对路径并配置模块依赖。非 Windows 环境可用 `PRESENTATIONS_PYTHON`、`RUNTIME_NODE_MODULES`、`PRESENTATIONS_SKILL_DIR` 三个环境变量覆盖本机 python 可执行、node 模块目录与 presentations 技能目录（默认值仍为原 Windows 路径）；校验回执目录 `.codex-finalizer/` 需事先存在。

构建链支持多套 deck：`SCENARIO_ROOT` 指定页面目录（默认本目录）、`SCENARIO_FILE` 指定交付文件名、`SCENARIO_TITLE` 指定网页预览标题（scenario_package 的页数与每页点击步数从页面 JSON 的 reveal 分组动态推导）。另一套 deck 见 `audio_pa_compare/`。

在仓库根目录运行：

```powershell
python hongmeng_audio_design_review/build/scenario_generate.py
node hongmeng_audio_design_review/build/scenario_deck.mjs all
```

第一步调用 `scenario_revision.py` 生成页面 JSON 和本版讲稿。第二步生成原生可编辑 PPTX，调用 `scenario_reveals.py` 加入原生点击出现效果，执行文件校验后更新交付稿。`build/final.json` 记录交付文件及其哈希；中间版本留在私有构建目录。

更新网页预览并检查动画引用：

```powershell
python hongmeng_audio_design_review/build/scenario_package.py
```

可通过 `PRESENTATIONS_SKILL_DIR` 指定演示文稿技能目录。当前本机版本为 `26.1020.11127`。
