import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const SKILL='C:/Users/47156/.codex/plugins/cache/openai-primary-runtime/presentations/26.1015.12040/skills/presentations';
const PY='C:/Users/47156/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
process.env.RUNTIME_NODE_MODULES='C:/Users/47156/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const arg=process.argv[2]||'all',selected=arg==='all'?null:Number(arg);
const names=(await fs.readdir(path.join(ROOT,'pages'))).filter(n=>/^P\d\d.json$/.test(n)).sort();
const pages=await Promise.all(names.map(async n=>JSON.parse(await fs.readFile(path.join(ROOT,'pages',n),'utf8'))));
const pres=Presentation.create({slideSize:{width:1280,height:720}});
const C={navy:'#12263B',blue:'#3379EB',teal:'#119A92',purple:'#887798',gray:'#62768A',light:'#DCE5EE',white:'#FFFFFF',bg:'#F7F9FC',amber:'#C97835'};
const color=x=>C[x]||x||'none';let s,idx=0,svg=[];
const esc=x=>String(x).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
function rect(x,y,w,h,fill='none',stroke='none',sw=0){svg.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${color(fill)}" stroke="${color(stroke)}" stroke-width="${sw}"/>`);return s.shapes.add({geometry:'rect',name:'object-'+idx++,position:{left:x,top:y,width:w,height:h},fill:color(fill),line:{fill:color(stroke),width:sw,style:'solid'}})}
function text(x,y,w,h,t,size=28,c='navy',bold=false,align='left'){
 const q=rect(x,y,w,h);q.text=t;q.text.style={typeface:'Microsoft YaHei',fontSize:Number(size),color:color(c),bold,alignment:align,verticalAlignment:'middle',wrap:'none'};q.text.insets=0;const lines=String(t).split('\n');const sy=y+(h-lines.length*Number(size)*1.25)/2+Number(size);lines.forEach((l,i)=>svg.push(`<text x="${align==='center'?x+w/2:align==='right'?x+w:x}" y="${sy+i*Number(size)*1.25}" fill="${color(c)}" font-family="Microsoft YaHei, sans-serif" font-size="${size}" font-weight="${bold?700:400}" text-anchor="${align==='center'?'middle':align==='right'?'end':'start'}">${esc(l)}</text>`));return q;
}
function line(x1,y1,x2,y2,c='blue',width=3){svg.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color(c)}" stroke-width="${width}"/>`);
 const x=Math.min(x1,x2),y=Math.min(y1,y2),w=Math.max(1,Math.abs(x2-x1)),h=Math.max(1,Math.abs(y2-y1));
 s.shapes.add({geometry:'custom',name:'line-'+idx++,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:color(c),width,style:'solid'},customPaths:[{width:w,height:h,commands:[{moveTo:{x:x1-x,y:y1-y}},{lineTo:{x:x2-x,y:y2-y}}]}]});
}
function arrow(x1,y1,x2,y2,c='blue',dash=false){if(dash){for(let j=0;j<12;j+=2)line(x1+(x2-x1)*j/12,y1+(y2-y1)*j/12,x1+(x2-x1)*(j+1)/12,y1+(y2-y1)*(j+1)/12,c,2)}else line(x1,y1,x2,y2,c);const a=Math.atan2(y2-y1,x2-x1);line(x2-10*Math.cos(a-.45),y2-10*Math.sin(a-.45),x2,y2,c);line(x2-10*Math.cos(a+.45),y2-10*Math.sin(a+.45),x2,y2,c)}
function node(x,y,w,h,t,c='blue',size=26){rect(x,y,w,h,c);text(x+12,y+6,w-24,h-12,t,size,'white',true,'center')}
const notes=p=>`${p.title}\n时间：${p.minutes}分钟\n本页目标：${p.objective}\n承接：${p.from}\n\n${p.script}\n\n演示：${p.cue||'无'}\n讲述安排：${p.pacing}\n转场：${p.next}\n技术边界：${p.boundary}\n源码与依据：\n${p.sources.join('\n')}`;
for(const p of pages.filter(p=>selected===null||p.n===selected)){
 s=pres.slides.add();s.background.fill=color(p.dark?'navy':'bg');svg=[`<rect width="1280" height="720" fill="${color(p.dark?'navy':'bg')}"/>`];const fg=p.dark?'white':'navy';
 text(64,30,1150,31,p.section,19,p.dark?'#A4C5E8':'blue',true);
 text(64,87,1150,70,p.title,p.titleSize||44,fg,true);
 text(64,169,1150,48,p.takeaway,27,p.dark?'#C5D9EB':'gray');
 for(const e of p.elements){const [type,...v]=e;if(type==='text')text(...v);else if(type==='rect')rect(...v);else if(type==='line')line(...v);else if(type==='arrow')arrow(...v);else if(type==='node')node(...v);else throw new Error(type)}
 text(64,665,1070,30,p.footer,17,p.dark?'#A4BDD1':'gray');text(1157,665,57,30,p.label||String(p.n).padStart(2,'0'),19,p.dark?'#A4BDD1':'gray',false,'right');s.speakerNotes.text=notes(p);
 await fs.mkdir(path.join(ROOT,'assets/diagrams'),{recursive:true});await fs.writeFile(path.join(ROOT,`assets/diagrams/P${String(p.n).padStart(2,'0')}.svg`),`<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">${svg.join('')}</svg>`);
 const blob=await pres.export({slide:s,format:'png',scale:1.5});await fs.writeFile(path.join(ROOT,`previews/P${String(p.n).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
}
await fs.mkdir(path.join(ROOT,'build/.private'),{recursive:true});
const candidate=path.join(ROOT,'build/.private',selected?`P${String(selected).padStart(2,'0')}.pptx`:'candidate.pptx');
await(await PresentationFile.exportPptx(pres)).save(candidate);console.log(`Built ${pres.slides.items.length} slide(s), rendered ${arg}`);
if(selected===null){
 const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
 let finalPath=path.join(ROOT,'鸿蒙音频底座_技术深化版.pptx');try{await fs.access(finalPath);finalPath=path.join(ROOT,'鸿蒙音频底座_技术深化版_'+Date.now()+'.pptx')}catch{}
 const r=await finalizePresentation({workspaceDir:path.dirname(ROOT),candidatePath:candidate,finalPath,pythonExecutable:PY,integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],explicitTotalSlideCount:pages.length,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],fontPolicy:{basis:'design',families:['Microsoft YaHei']},verifyArtifactToolImport:true,receiptPath:path.join(ROOT,'..','.codex-finalizer','foundation-'+Date.now()+'.json')});
 await fs.writeFile(path.join(ROOT,'build/final.json'),JSON.stringify({file:path.basename(finalPath),sha256:r.finalSha256},null,2));console.log('Finalized '+finalPath);
}
