# PA 与 HPAE：结构对照

两页开篇，承接《一首歌，三个操作》结尾的提问"换一个引擎会怎样"。论点：维护成本的差别不在代码行数，在"同一件事写几遍、改一处要碰多大面积"。

- [可编辑演示稿](结构对照_PA与HPAE.pptx)
- [全部页面预览](全部页面预览.html)：下载本目录后用浏览器打开。
- [本版逐页讲稿与源码依据](speaker_notes.md)
- `pages/`：两页内容与图形位置。

- P1 同一件事，写了几遍：暂停恢复的淡入淡出，在旧方案 HDI sink 模块（单文件 4823 行、190 函数）里按主通路/多声道/低时延各写一套、状态回调 4 变体；在 HPAE 里是增益节点（521 行）一套状态机，流类型只是挂链参数。
- P2 改动半径：加限幅、接新设备两类情景的触碰面对照；节点层 32 文件一职责、33 个节点单测。

对照基线：旧方案取 OpenHarmony-v5.1.0-Release 的 `frameworks/native/pulseaudio/modules/hdi/hdi_sink.c`；新引擎取主干 0d073de5 的 `services/audio_engine`。行数为对应文件实测；对照限定在设备侧音频引擎这一具体问题，不构成对 PulseAudio 设计目标（通用桌面音频服务器）的全维度评价。老方案的支持面与生态成熟度是另一组维度，本 deck 不比较。

诚实边界：HPAE 的抽象层次更多，排查一个请求要追队列、线程、节点，前期学习成本更高；本 deck 的论点仅是改动半径小、重复少。

## 构建

沿用 audio_scenario 的构建环境与命令，通过环境变量指定目录、交付文件名与预览标题：

```powershell
python hongmeng_audio_design_review/build/scenario_revision_pa.py
$env:SCENARIO_ROOT='audio_pa_compare'; $env:SCENARIO_FILE='结构对照_PA与HPAE.pptx'
node hongmeng_audio_design_review/build/scenario_deck.mjs all
$env:SCENARIO_TITLE='PA 与 HPAE：结构对照'
python hongmeng_audio_design_review/build/scenario_package.py
```

第一步生成页面 JSON 与讲稿；第二步生成 PPTX、SVG 与 PNG；第三步生成网页预览并校验（点击步数与页面 reveal 分组一致、页面文本无源码符号泄漏）。运行时依赖与非 Windows 环境的覆盖变量见 `audio_scenario/README.md` 的构建一节。
