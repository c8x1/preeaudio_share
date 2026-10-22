from pathlib import Path
from zipfile import ZipFile
from lxml import etree as ET
import json,hashlib,re,html,os

BASE=Path(__file__).resolve().parents[2]
_env=os.environ.get('SCENARIO_ROOT')
ROOT=(BASE/_env) if _env else (BASE/'audio_scenario')
TITLE=os.environ.get('SCENARIO_TITLE','一首歌，三个操作')
meta=json.loads((ROOT/'build/final.json').read_text(encoding='utf8'))
ppt=ROOT/meta['file']
assert hashlib.sha256(ppt.read_bytes()).hexdigest()==meta['sha256']
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
names=sorted((ROOT/'pages').glob('P*.json'))
assert names,'no pages found'
expected=[]
for pth in names:
    page=json.loads(pth.read_text(encoding='utf8'))
    groups=[e[1] for e in page['elements'] if e[0]=='reveal']
    expected.append(max(groups) if groups else 0)
checks=[]
with ZipFile(ppt) as z:
    for i in range(1,len(names)+1):
        root=ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
        ids={n.get('id') for n in root.findall('.//p:spTree//p:cNvPr',ns)}
        targets=root.findall('.//p:timing//p:spTgt',ns)
        assert targets and all(n.get('spid') in ids for n in targets)
        timing=root.findall('.//p:timing//p:cTn',ns)
        tid=[n.get('id') for n in timing]
        assert len(tid)==len(set(tid))
        clicks=sum(n.get('nodeType')=='clickEffect' for n in timing)
        assert clicks==expected[i-1],(i,clicks,expected[i-1])
        slide_text=''.join(root.xpath('.//a:t/text()',namespaces=ns))
        assert not any(x in slide_text for x in ['HpaeRendererManager','OnFadeDone','SetSessionFade','.cpp'])
        checks.append({'slide':i,'click_steps':clicks,'animation_shape_targets':len(targets)})

sections=[]
for idx,pth in enumerate(names,1):
    page=json.loads(pth.read_text(encoding='utf8'))
    svg=(ROOT/f'assets/diagrams/P{idx:02}.svg').read_text(encoding='utf8')
    # Keep the full diagram editable in PPT; web version reveals the same groups.
    svg=svg.replace('viewBox="0 0 1280 720">','viewBox="0 0 1280 720"><g data-stage="0">',1)
    svg=re.sub(r'<!-- reveal (\d+) -->',lambda m:'</g><g data-stage="'+m.group(1)+'">',svg)
    svg=svg.replace('</svg>','</g></svg>')
    sections.append(f'<section data-step="0" data-max="{expected[idx-1]}"><div class="bar"><strong>{idx:02}　{html.escape(page["title"])}</strong><span class="progress"></span><button data-action="prev">上一步</button><button data-action="next">下一步</button><button data-action="all">全部展开</button></div>{svg}</section>')
head='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'''+html.escape(TITLE)+'''</title>
<style>body{margin:0;background:#182638;font-family:"Microsoft YaHei",sans-serif}main{max-width:1280px;margin:auto}section{margin:24px 0 48px}svg{width:100%;height:auto;display:block}.bar{display:flex;align-items:center;gap:12px;padding:16px;color:white;flex-wrap:wrap}.bar strong{margin-right:auto}.progress{font-size:14px;color:#ced7e3}button{background:#f7f9fc;border:0;border-radius:3px;padding:8px 14px;cursor:pointer;font:inherit}button:disabled{opacity:.4;cursor:default}header{padding:24px;color:white}a{color:#b8d1ff}</style>
<header>按“下一步”依次揭示。<a href="'''+meta['file']+'''">下载可编辑 PPT</a>　<a href="speaker_notes.md">逐页讲稿</a></header><main>'''
tail='''</main><script>
function update(s){const step=+s.dataset.step,max=+s.dataset.max;s.querySelectorAll('[data-stage]').forEach(g=>g.style.visibility=+g.dataset.stage<=step?'visible':'hidden');s.querySelector('.progress').textContent=`${step} / ${max}`;s.querySelector('[data-action=prev]').disabled=step===0;s.querySelector('[data-action=next]').disabled=step===max}
document.querySelectorAll('section').forEach(s=>{update(s);s.querySelectorAll('button').forEach(b=>b.onclick=()=>{s.dataset.step=b.dataset.action==='all'?s.dataset.max:Math.max(0,Math.min(+s.dataset.max,+s.dataset.step+(b.dataset.action==='next'?1:-1)));update(s)})});
</script></html>'''
(ROOT/'全部页面预览.html').write_text(head+''.join(sections)+tail,encoding='utf8')
(ROOT/'build/.private/revision_checks.json').write_text(json.dumps({'sha256':meta['sha256'],'slides':checks},indent=2),encoding='utf8')
print(json.dumps(checks))
