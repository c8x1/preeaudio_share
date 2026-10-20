# 一首歌，三个操作

六页音频引擎场景演示稿，以暂停、恢复播放、切换耳机为主线。页面使用可编辑机制图，源码依据放在演讲备注和备讲材料中。

- [可编辑演示稿](一首歌三个操作_场景演示稿.pptx)
- [全部页面预览](全部页面预览.html)：下载本目录后用浏览器打开。
- [逐页讲稿与源码核验落点](../hongmeng_audio_design_review/用户场景主线_逐页讲稿.md)
- `pages/`：六页内容与图形位置。
- `previews/`：逐页 PNG。
- `assets/diagrams/`：逐页 SVG。

当前为静态图示，无自动动画。机制范围为普通 HPAE 播放路径；条件时序不代表每次用户点击都会复现，未开展设备性能实验。

## 构建

沿用仓库现有的 `@oai/artifact-tool` 构建环境，字体为 Microsoft YaHei。运行时路径见 `hongmeng_audio_design_review/build/README.md`，新环境需调整本机绝对路径并配置模块依赖。

在仓库根目录运行：

```powershell
python hongmeng_audio_design_review/build/scenario_generate.py
node hongmeng_audio_design_review/build/scenario_deck.mjs all
```

第一步从作者脚本与逐页讲稿生成页面 JSON；第二步生成原生可编辑 PPTX、渲染图片并执行文件校验。构建会生成新文件，不覆盖已有交付稿。`build/final.json` 记录本次构建文件及其哈希；仓库只提交确认后的交付稿，不提交中间版本。
