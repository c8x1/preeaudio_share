from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1];p=R.parent/'IMPLEMENTATION_NOTES.md'
s=p.read_text(encoding='utf-8')
s=re.sub(r'最后更新：[^\n]+', '最后更新：2026-10-20。当前技术深化版位于 hongmeng_audio_design_review；旧版 hongmeng_audio_foundation 保留为历史基线。后续先读本文件的当前版本表，再读该页JSON和review。',s,count=1)
start='## 当前技术深化版（制作与逐页复审已完成）\n\n'
start+='主讲15页建议55分钟（包含读图、互动与停顿），另5分钟答疑。A1–A6按需。已按用户反馈把真实时序、状态机、算法条件与新旧设计对照放到正文。每页均重新独立审查，旧版PASS没有沿用。\n\n'
start+='| 页 | 当前主题 | 状态 |\n|---|---|---|\n'
for q in sorted((R/'pages').glob('P??.json')):
 d=json.loads(q.read_text(encoding='utf-8'));start+=f"| P{d['n']:02} | {d['title']} | [PASS](hongmeng_audio_design_review/reviews/P{d['n']:02}.md) |\n"
start+='\n源文件：pages/Pxx.json 为权威内容，包含技术讲稿、来源与原生元素。构建：build/rebuild.ps1。全页重审记录：reviews/TECHNICAL_REDESIGN_AUDIT.md。GitHub：https://github.com/c8x1/preeaudio_share；P01–P21已逐页通过后提交推送，最终整合提交另记。\n\n'
s=s.replace('## 已确认的定位',start+'## 已确认的定位',1)
s=s.replace('## 已批准的完整提纲（15页主讲55分钟，另5分钟答疑）','## 最初批准的提纲（历史记录；当前主题以顶部表格为准）')
s=s.replace('## 当前制作状态','## 上一版制作状态（历史）',1)
s=s.replace('附录P16/P17通过；P18修订后待复审；P19–P21按序制作。','附录P16–P21也已全部修订并复审PASS。')
s+='\n- 2026-10-20：完成技术深化版21页逐页审查与推送，正在进行整套讲稿承接、输出文件与预览一致性验收。P19改为迟到Drain回调竞态；P20以PA本体说明两种方案都复用输入对象。\n'
p.write_text(s,encoding='utf-8')
