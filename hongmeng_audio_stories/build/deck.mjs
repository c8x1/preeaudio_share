import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const SKILL='C:/Users/47156/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11127/skills/presentations';
process.env.RUNTIME_NODE_MODULES='C:/Users/47156/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const PY='C:/Users/47156/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const arg=process.argv[2]||'all';
const names=(await fs.readdir(path.join(ROOT,'pages'))).filter(n=>/^P\d\d.json$/.test(n)).sort();
const pages=await Promise.all(names.map(async n=>JSON.parse(await fs.readFile(path.join(ROOT,'pages',n),'utf8'))));
const active=arg==='all'?pages:pages.filter(p=>p.n===Number(arg));
const pres=Presentation.create({slideSize:{width:1280,height:720}});
const C={navy:'#12263B',blue:'#3379EB',teal:'#087F7A',purple:'#816C97',amber:'#B96320',gray:'#526679',light:'#DBE4EE',white:'#FFFFFF',bg:'#F8FAFD',pale:'#EFF4FA'};
const col=x=>C[x]||x||'none';let s,idx=0,svg=[];
const esc=x=>String(x).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
function rect(x,y,w,h,fill='none',stroke='none',sw=0){svg.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${col(fill)}" stroke="${col(stroke)}" stroke-width="${sw}"/>`);return s.shapes.add({geometry:'rect',name:'o'+idx++,position:{left:x,top:y,width:w,height:h},fill:col(fill),line:{fill:col(stroke),width:sw}})}
function text(x,y,w,h,t,size=24,c='navy',bold=false,align='left',face='Microsoft YaHei'){
 const q=rect(x,y,w,h);q.text=t;q.text.style={typeface:face,fontSize:Number(size),color:col(c),bold,alignment:align,verticalAlignment:'middle',wrap:'none'};q.text.insets=0;
 const lines=String(t).split('\n'),sy=y+(h-lines.length*Number(size)*1.25)/2+Number(size);
 lines.forEach((l,i)=>svg.push(`<text x="${align==='center'?x+w/2:align==='right'?x+w:x}" y="${sy+i*Number(size)*1.25}" fill="${col(c)}" font-family="${face}" font-size="${size}" font-weight="${bold?700:400}" text-anchor="${align==='center'?'middle':align==='right'?'end':'start'}">${esc(l)}</text>`));
}
function line(x1,y1,x2,y2,c='blue',width=2,dash=false){
 svg.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${col(c)}" stroke-width="${width}" ${dash?'stroke-dasharray="7 5"':''}/>`);
 const x=Math.min(x1,x2),y=Math.min(y1,y2),w=Math.max(1,Math.abs(x2-x1)),h=Math.max(1,Math.abs(y2-y1));
 s.shapes.add({geometry:'custom',name:'ln'+idx++,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:col(c),width,style:dash?'dashed':'solid'},customPaths:[{width:w,height:h,commands:[{moveTo:{x:x1-x,y:y1-y}},{lineTo:{x:x2-x,y:y2-y}}]}]});
}
function arrow(x,y,xx,yy,c='blue',dash=false){line(x,y,xx,yy,c,2.5,dash);const a=Math.atan2(yy-y,xx-x);line(xx-10*Math.cos(a-.45),yy-10*Math.sin(a-.45),xx,yy,c,2.5);line(xx-10*Math.cos(a+.45),yy-10*Math.sin(a+.45),xx,yy,c,2.5)}
function node(x,y,w,h,t,c='blue',size=23){rect(x,y,w,h,c);text(x+10,y+5,w-20,h-10,t,size,'white',true,'center')}
function table(x,y,w,h,values,widths=null,size=22){
 const rows=values.length,cols=values[0].length;
 const tb=s.tables.add({rows,columns:cols,left:x,top:y,width:w,height:h,values,columnWidths:widths||Array(cols).fill(w/cols)});
 tb.borders.assign({fill:col('light'),style:'solid',width:1});
 for(let r=0;r<rows;r++){tb.rows[r].height=h/rows;for(let c=0;c<cols;c++){
  const cell=tb.getCell(r,c);cell.fill=col(r===0?'navy':r%2?'white':'pale');cell.text.style={typeface:'Microsoft YaHei',fontSize:size,color:col(r===0?'white':'navy'),bold:r===0,verticalAlignment:'middle'};
 }}
 const cw=widths||Array(cols).fill(w/cols);let yy=y;
 for(let r=0;r<rows;r++){let xx=x;for(let c=0;c<cols;c++){
  svg.push(`<rect x="${xx}" y="${yy}" width="${cw[c]}" height="${h/rows}" fill="${col(r===0?'navy':r%2?'white':'pale')}" stroke="${col('light')}"/>`);
  String(values[r][c]).split('\n').forEach((v,j)=>svg.push(`<text x="${xx+12}" y="${yy+size+10+j*size*1.2}" fill="${col(r===0?'white':'navy')}" font-family="Microsoft YaHei" font-size="${size}">${esc(v)}</text>`));xx+=cw[c];
 }yy+=h/rows;}
}
for(const p of active){
 s=pres.slides.add();s.background.fill=col('bg');svg=[`<rect width="1280" height="720" fill="${col('bg')}"/>`];
 text(54,21,1150,24,p.chapter,16,'teal',true);
 text(54,62,1170,60,p.title,p.titleSize||42,'navy',true);
 text(54,132,1170,40,p.takeaway,25,'gray');
 for(const [type,...v] of p.elements){if(type==='text')text(...v);else if(type==='rect')rect(...v);else if(type==='line')line(...v);else if(type==='arrow')arrow(...v);else if(type==='node')node(...v);else if(type==='table')table(...v);else throw Error(type)}
 text(54,670,1080,29,p.condition,15,'gray');text(1158,670,66,29,p.label||String(p.n).padStart(2,'0'),18,'gray',false,'right');
 s.speakerNotes.text=`${p.title}\n本页学习结果：${p.outcome}\n备课预算：${p.minutes}分钟，需试讲校准\n\n${p.script}\n\n预测问题：${p.question}\n展开答案：${p.answer}\n演示：${p.cue||'无'}\n承接：${p.prev}\n转场：${p.next}\n条件：${p.condition}\n\n固定源码证据：\n${p.sources.join('\n')}`;
 await fs.writeFile(path.join(ROOT,`assets/diagrams/P${String(p.n).padStart(2,'0')}.svg`),`<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720">${svg.join('')}</svg>`);
 const blob=await pres.export({slide:s,format:'png',scale:1.5});await fs.writeFile(path.join(ROOT,`previews/P${String(p.n).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
}
await fs.mkdir(path.join(ROOT,'build/.private'),{recursive:true});
const candidate=path.join(ROOT,'build/.private',arg==='all'?'candidate.pptx':`P${String(Number(arg)).padStart(2,'0')}.pptx`);
await(await PresentationFile.exportPptx(pres)).save(candidate);console.log(`Rendered ${active.length} slide(s): ${arg}`);
if(arg==='all'){
 if(pages.length!==19)throw Error('Expected 15 main slides and 4 appendix slides');
 const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
 let finalPath=path.join(ROOT,'一段声音的旅程_三个设计故事.pptx');try{await fs.access(finalPath);finalPath=path.join(ROOT,`一段声音的旅程_三个设计故事_${Date.now()}.pptx`)}catch{}
 const owners=pages.filter(p=>p.elements.some(e=>e[0]==='table')).map(p=>p.n);
 const result=await finalizePresentation({workspaceDir:path.dirname(ROOT),candidatePath:candidate,finalPath,pythonExecutable:PY,integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...owners.flatMap(n=>['--require-native-table-slide',String(n)])],explicitTotalSlideCount:19,requiredNativeTableOwnerSlides:owners,requiredNativeChartOwnerSlides:[],fontPolicy:{basis:'design',families:['Microsoft YaHei']},verifyArtifactToolImport:true,receiptPath:path.join(ROOT,'..','.codex-finalizer',`stories-${Date.now()}.json`)});
 await fs.writeFile(path.join(ROOT,'build/final.json'),JSON.stringify({file:path.basename(finalPath),sha256:result.finalSha256,nativeTableSlides:owners},null,2));console.log(finalPath);
}
