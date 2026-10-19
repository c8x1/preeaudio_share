from pathlib import Path
import json,re,zipfile,html,wave,hashlib,os,shutil
from xml.etree import ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
import numpy as np
from author import sync
R=Path(__file__).resolve().parents[1];sync()
pages=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((R/'pages').glob('P??.json'))]
assert len(pages)==21 and sum(p['minutes'] for p in pages)==55
for p in pages:
 review=(R/'reviews'/f"P{p['n']:02}.md").read_text(encoding='utf-8')
 assert re.search(r'状态[：:]\s*PASS',review),f"Review pending: P{p['n']:02}"
 for n in ['title','objective','script','next','boundary']:assert p[n]
 assert (R/'previews'/f"P{p['n']:02}.png").exists()
final=json.loads((R/'build/final.json').read_text(encoding='utf-8'));ppt=R/final['file']
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
with zipfile.ZipFile(ppt) as z:
 slides=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml',n)];assert len(slides)==21
 shape_count=0
 for p in pages:
  n=p['n'];t=ET.fromstring(z.read(f'ppt/slides/slide{n}.xml'));shape_count+=len(t.findall('.//p:sp',ns))
  notes=''.join(e.text or '' for e in ET.fromstring(z.read(f'ppt/notesSlides/notesSlide{n}.xml')).findall('.//a:t',ns))
  assert re.sub(r'\s+','',p['script']) in re.sub(r'\s+','',notes),f'Notes mismatch {n}'
 media=[n for n in z.namelist() if n.startswith('ppt/media/')];assert not media
def notes(p):return f"## {p.get('label',str(p['n']).zfill(2))} {p['title']}\n\n时间：{p['minutes']}分钟\n\n{p['script']}\n\n演示 cue：{p['cue'] or '无'}\n讲述安排：{p['pacing']}\n转场：{p['next']}\n技术边界：{p['boundary']}\n\n依据：\n"+'\n'.join('- '+s for s in p['sources'])
(R/'speaker_notes.md').write_text('# 一段声音的旅程：鸿蒙音频底座的协同与自研演进\n\n15页主讲55分钟，另5分钟答疑。A1–A6按需。分钟数含试听、互动和停顿。\n\n'+'\n\n---\n\n'.join(notes(p) for p in pages),encoding='utf-8')
evidence='# 页面与证据\n\n当前框架3a2688e805df970739e3b0cebf9cc05d8cb24e9b；5.1框架c42a228d60b64a90d6b05cf26278a89253e5310b；5.1PA bc6e4fe58232dbad60ae6ee5d83cf46d0fe9b3ca。源码说明限定实现。时延/性能/功耗及抗抖动定性结论由用户团队提供，未补造幅度。\n'
for p in pages:evidence+=f"\n## P{p['n']:02} {p['title']}\n\n{p['takeaway']}\n\n边界：{p['boundary']}\n\n"+'\n'.join('- '+s for s in p['sources'])+'\n'
(R/'sources_and_claims.md').write_text(evidence,encoding='utf-8')
esc=html.escape
css='body{margin:0;background:#edf2f7;color:#12263b;font:17px/1.65 "Microsoft YaHei",sans-serif}header,main,footer{max-width:1250px;margin:auto;padding:24px}nav a{margin-right:24px}section{background:white;padding:20px;margin:28px 0}img{width:100%;height:auto}pre{white-space:pre-wrap;font:16px/1.8 "Microsoft YaHei",sans-serif}audio{width:100%;max-width:650px}summary{cursor:pointer;color:#3379eb}figcaption{font-size:21px;font-weight:600}a{color:#2465b9}'
nav='<nav><a href="全部页面预览.html">全部页面</a><a href="演示台.html">音频演示</a><a href="speaker_notes.md">完整讲稿</a><a href="'+esc(final['file'])+'">PPTX</a></nav>'
doc=f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>{css}</style><title>鸿蒙音频底座·全部页面</title><header><h1>一段声音的旅程</h1><p>鸿蒙音频底座的协同与自研演进 · 15页主讲 + 6页答疑附录</p>{nav}</header><main>'
for p in pages:
 n=p['n'];doc+=f'<section id="p{n}"><figcaption>{p.get("label",str(n).zfill(2))} {esc(p["title"])}</figcaption><a href="previews/P{n:02}.png"><img src="previews/P{n:02}.png" alt="{esc(p["title"])}"></a><details><summary>讲稿、cue与源码依据</summary><pre>{esc(notes(p))}</pre></details><p><a href="reviews/P{n:02}.md">本页subagent评审</a></p></section>'
doc+='</main><footer>全部页面已独立评审。PPTX保持原生文字与技术图可编辑，工具渲染不等同PowerPoint/WPS现场放映验收。</footer></html>'
(R/'全部页面预览.html').write_text(doc,encoding='utf-8')
doc=f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><style>{css}</style><title>离线音频演示</title><header><h1>原创音频演示台</h1>{nav}</header><main><p>非产品录音或实测。首次播放从低音量开始。每段10秒，48kHz/16bit/双声道。</p>'
for file,label in [('01_scene_mix','P01/P15：音乐、游戏与提醒'),('02_continuous','P08：连续版本'),('03_simulated_dropout','P08：人为模拟断音')]:doc+=f'<section><h2>{label}</h2><audio controls preload="metadata" src="assets/audio/{file}.wav"></audio></section>'
doc+='</main></html>';(R/'演示台.html').write_text(doc,encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
for group in range(3):
 sheet=Image.new('RGB',(1632,1990),'#E7EEF5');draw=ImageDraw.Draw(sheet)
 for k,n in enumerate(range(group*7+1,group*7+8)):
  x=16+(k%2)*808;y=16+(k//2)*492
  im=Image.open(R/'previews'/f'P{n:02}.png');assert im.size==(1920,1080);sheet.paste(im.resize((792,446)),(x,y))
  caption_title=pages[n-1]['title'];caption_label=pages[n-1].get('label',str(n).zfill(2));caption_title=re.sub(r'^A[1-6]\s+','',caption_title);label=f"{caption_label} {caption_title}";draw.text((x,y+451),label[:31],font=font,fill='#12263b')
 sheet.save(R/'previews'/f'contact-{group+1}.jpg',quality=94)
audio=[]
for p in sorted((R/'assets/audio').glob('*.wav')):
 with wave.open(str(p),'rb') as w:
  assert (w.getframerate(),w.getnchannels(),w.getsampwidth(),w.getnframes())==(48000,2,2,480000)
  x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768;assert np.max(np.abs(x))<.501
 audio.append(p.name)
assert len(audio)==3
for name in ['全部页面预览.html','演示台.html']:
 for ref in re.findall(r'(?:src|href)="([^"#]+)"',(R/name).read_text(encoding='utf-8')):assert (R/ref).exists(),ref
summary='# 逐页评审汇总\n\n每一页先完成内容和PNG，再由subagent独立审查，解决必须改项后进入下一页。原reviewer完成P01–P12，续接reviewer完成P13–P21。\n\n'
for p in pages:
 n=p['n'];summary+=f'- P{n:02} {p["title"]}：PASS，见[记录](reviews/P{n:02}.md)。\n'
summary+='\n已修复：P09标题过长；P10管理器控制连线悬空；P17将原子摘取与随后执行分开表达。P07措辞和P08图折叠说明按可选建议优化。\n'
(R/'REVIEW_SUMMARY.md').write_text(summary,encoding='utf-8')
qa=f'''# 验收与使用说明

2026-10-18。21页，15页主讲55分钟，另5分钟Q&A，6页技术附录。原生可编辑对象{shape_count}个，21份演讲者备注与脚本正文一致，21张1920×1080预览，21份subagent评审均PASS。页数、尺寸、字体、包结构及Artifact Tool再导入通过。P09/P10/P17的评审问题已修复。

源码依据使用固定commit并保留行号摘录。没有编译/板端测试或声学时延测量。团队定性成果采用用户说明，未虚构量化结果。P14是拟议验证设计，非已执行实验。

3个原创WAV已解码、格式和峰值检查。未进行真人耳听、现场扬声器或声压验收。PPTX未嵌入音频，打开演示台.html手动播放，P01/P15为场景音，P08为连续/模拟断音对照。

没有在原生PowerPoint或WPS中打开验证。字体为Microsoft YaHei，未嵌入，跨机器应确认字体并课前检查放映。

## 待人工补充

- 讲师与团队正式信息、目标产品及内部commit对应。
- 可披露量化成果：平台、基线、负载、测量边界、数据和时间。
- 真实内部项目协同案例及贡献归属。
- 最终现场放映与音响试听。

最终PPTX SHA256：{hashlib.sha256(ppt.read_bytes()).hexdigest()}。
''';(R/'QA_REPORT.md').write_text(qa,encoding='utf-8')
hand='# 交付入口\n\n'+f'授课文件：{final["file"]}\n\n打开全部页面预览.html查看原图、完整讲稿与每页review。打开演示台.html播放离线音频。主讲结束停在P15，答疑进入A1–A6。\n\n'
hand+='| 页 | 主题 | 分钟 |\n|---|---|---|\n'
for p in pages:hand+=f'| {p.get("label",str(p["n"]).zfill(2))} | {p["title"]} | {p["minutes"]} |\n'
hand+='\n构建：build/rebuild.ps1。文案以pages/Pxx.json为准，内容作者脚本在build/pageXX.py。若修改JSON，请同步对应作者脚本。notes主记录位于交付包根目录IMPLEMENTATION_NOTES.md，后续先读该文件。所有技术图为可编辑对象；未使用外部插画或生成式技术截图。\n'
(R/'交付说明.md').write_text(hand,encoding='utf-8')
if (R.parent/'source_gitcode/LICENSE').exists():shutil.copyfile(R.parent/'source_gitcode/LICENSE',R/'appendix/OpenHarmony_LICENSE.txt')
(R/'appendix/NOTICE.md').write_text('框架源码摘录来自OpenHarmony multimedia_audio_framework，保留固定位置与原有版权归属，按Apache-2.0使用。PA版本声明只作版本核验，PA上游及集成仓库许可证为LGPL-2.1。未将三方源码用于音频生成。\n',encoding='utf-8')
report={'pages':21,'speaker_notes':21,'review_pass':21,'native_shapes':shape_count,'raster_media':len(media),'wav':len(audio),'main_minutes':55,'pass':True}
(R/'build/package_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
out=R.parent/'鸿蒙音频底座_全套交付.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 z.write(R.parent/'IMPLEMENTATION_NOTES.md','IMPLEMENTATION_NOTES.md')
 for folder,dirs,files in os.walk(R):
  dirs[:]=[d for d in dirs if d not in ['node_modules','.private','__pycache__']]
  for name in files:
   p=Path(folder)/name
   if name.startswith('.private') or (p.suffix=='.pptx' and p.name!=final['file']):continue
   z.write(p,p.relative_to(R.parent))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print(json.dumps(report));print(out)
