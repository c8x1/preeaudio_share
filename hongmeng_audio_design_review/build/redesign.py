from pathlib import Path
import json,sys
from author import refs,S,CUR,OLD
R=Path(__file__).resolve().parents[1]
def t(x,y,w,h,s,z=23,c='navy',b=False,a='left'):return ['text',x,y,w,h,s,z,c,b,a]
def l(x,y,xx,yy,c='light',z=2):return ['line',x,y,xx,yy,c,z]
def a(x,y,xx,yy,c='blue',dash=False):return ['arrow',x,y,xx,yy,c,dash]
def box(x,y,w,h,s,c='blue',z=23):return ['node',x,y,w,h,s,c,z]
def lanes(names,xs,top=245,bottom=593):
 e=[]
 for name,x in zip(names,xs):e += [t(x-115,top,230,48,name,23,'navy',True,'center'),l(x,top+55,x,bottom)]
 return e
def msg(x,xx,y,s,c='blue',size=22):return [a(x,y,xx,y,c),t(min(x,xx)+10,y-33,abs(xx-x)-15,30,s,size,c)]
def save(n,title,take,els,script,keys,footer='',boundary='',next='继续沿实际调用展开。'):
 p=json.loads((R/'pages'/f'P{n:02}.json').read_text(encoding='utf-8'))
 p.update(title=title,titleSize=40,takeaway=take,elements=els,script=script,objective=take,footer=footer,boundary=boundary or footer,next=next,dark=False,section=('源码设计 · 主讲' if n<=15 else '源码设计 · 条件与边界'),sources=refs(keys),cue='',pacing='先按图走一次调用，再解释条件与设计理由。',revision='technical-design-v2')
 (R/'pages'/f'P{n:02}.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
 for k in keys:
  sha,f,st,en,fn=S[k]; src=R.parent/('source_gitcode' if sha==CUR else 'source_audio_5_1')/f
  lines=src.read_text(encoding='utf-8').splitlines();(R/'appendix/source_evidence'/f'{k}.txt').write_text(refs([k])[0]+'\n'+'\n'.join(f'{i+1}: {lines[i]}' for i in range(st-1,min(en,len(lines)))),encoding='utf-8')
 print('Revised',n)
