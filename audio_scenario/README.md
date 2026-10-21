# 一首歌，三个操作

六页音频引擎场景演示稿，以暂停、恢复播放、切换耳机为主线。页面使用可编辑机制图，源码依据放在演讲备注和备讲材料中。

- [可编辑演示稿](一首歌三个操作_场景演示稿.pptx)
- [全部页面预览](全部页面预览.html)：下载本目录后用浏览器打开。
- [本版逐页讲稿与源码依据](speaker_notes.md)
- `pages/`：六页内容与图形位置。
- `previews/`：逐页 PNG。
- `assets/diagrams/`：逐页 SVG。

2026-10-21 修订：P3 展示请求排队与执行，P4 对比淡入设置时机，P5 展示设备切换的三个阶段。全篇使用“音乐 A”标记同一路会话，删除重复总结。

PPTX 含原生点击出现效果，每页 1–2 次点击。HTML 预览也支持逐步揭示；PNG 为全部内容展开状态。机制范围为普通 HPAE 播放路径，条件时序不代表每次用户点击都会复现，未开展设备性能实验。动画结构经过检查，尚未在桌面 PowerPoint 中实际放映验证。

## 构建

沿用仓库现有的 `@oai/artifact-tool` 构建环境，字体为 Microsoft YaHei。运行时路径见 `hongmeng_audio_design_review/build/README.md`，新环境需调整本机绝对路径并配置模块依赖。

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
