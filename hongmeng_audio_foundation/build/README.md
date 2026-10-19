# 构建与维护

先读交付包根目录IMPLEMENTATION_NOTES.md。当前正式内容是pages/P01.json–P21.json，每页含目标、正文、转场、源引用与原生元素位置。源JSON修改会直接进入PPT与讲稿。

- deck.mjs：使用@oai/artifact-tool生成原生文字、节点、线与完整演讲备注。传页码只构建该页并渲染PNG，传all生成全套、执行结构/几何/字体及再导入验收。
- pageXX.py：本次逐页制作的作者快照，便于重现最初内容；若已手工改JSON，不要直接重跑旧作者快照。
- audio.py：可复现3个原创WAV及测量数据。
- package.py：要求21页review均PASS，检查完整备注一致性与音频，生成HTML、接触表、证据表、说明和ZIP。
- rebuild.ps1：按本机Codex捆绑Node/Python路径重建，已有PPT不覆盖。无需重新安装运行时。新主机可修改脚本中的依赖路径。

正常重建：powershell -ExecutionPolicy Bypass -File build/rebuild.ps1。完整源码仓库没有打包，固定行号摘录在appendix/source_evidence。单纯重建PPT不需联网；重新提取源码时需按author.py记录准备固定SHA仓库。

内容改动后应重新请subagent审查受影响页面，再运行整体验收。review文件保留问题与修复历史；PASS表示本轮内容/逻辑/视觉检查通过，不代表板端性能实测。
