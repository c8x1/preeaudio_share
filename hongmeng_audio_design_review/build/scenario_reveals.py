"""Add native click-to-appear builds to named shapes in the staged PPTX."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as ET
import re,sys

P='http://schemas.openxmlformats.org/presentationml/2006/main'
NS={'p':P}
def e(parent,name,**attrs):return ET.SubElement(parent,'{'+P+'}'+name,attrib={k:str(v) for k,v in attrs.items()})
def patch(data):
    root=ET.fromstring(data)
    groups={}
    for node in root.findall('.//p:spTree//p:cNvPr',NS):
        m=re.match(r'reveal(\d+)-',node.get('name',''))
        if m:groups.setdefault(int(m[1]),[]).append(node.get('id'))
    if not groups:return data,0
    old=root.find('p:timing',NS)
    if old is not None:root.remove(old)
    timing=ET.Element('{'+P+'}timing')
    ext=root.find('p:extLst',NS)
    root.insert(list(root).index(ext) if ext is not None else len(root),timing)
    ids=iter(range(1,100000))
    top=e(e(timing,'tnLst'),'par')
    rt=e(top,'cTn',id=next(ids),dur='indefinite',restart='never',nodeType='tmRoot')
    seq=e(e(rt,'childTnLst'),'seq',concurrent=1,nextAc='seek')
    main=e(seq,'cTn',id=next(ids),dur='indefinite',nodeType='mainSeq')
    children=e(main,'childTnLst')
    for stage,spids in sorted(groups.items()):
        outer=e(e(children,'par'),'cTn',id=next(ids),fill='hold')
        e(e(outer,'stCondLst'),'cond',delay='indefinite')
        inner=e(e(e(outer,'childTnLst'),'par'),'cTn',id=next(ids),fill='hold')
        e(e(inner,'stCondLst'),'cond',delay=0)
        effects=e(inner,'childTnLst')
        for j,spid in enumerate(spids):
            ct=e(e(effects,'par'),'cTn',id=next(ids),presetID=1,presetClass='entr',presetSubtype=0,
                 fill='hold',grpId=stage,nodeType='clickEffect' if j==0 else 'withEffect')
            e(e(ct,'stCondLst'),'cond',delay=0)
            setter=e(e(ct,'childTnLst'),'set')
            bh=e(setter,'cBhvr')
            behavior=e(bh,'cTn',id=next(ids),dur=1,fill='hold')
            e(e(behavior,'stCondLst'),'cond',delay=0)
            e(e(bh,'tgtEl'),'spTgt',spid=spid)
            e(e(bh,'attrNameLst'),'attrName').text='style.visibility'
            e(e(setter,'to'),'strVal',val='visible')
    for name,event in [('prevCondLst','onPrev'),('nextCondLst','onNext')]:
        e(e(e(seq,name),'cond',evt=event,delay=0),'tgtEl').append(ET.Element('{'+P+'}sldTgt'))
    builds=e(timing,'bldLst')
    for stage,spids in sorted(groups.items()):
        for spid in spids:e(builds,'bldP',spid=spid,grpId=stage)
    return ET.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True),len(groups)

src=Path(sys.argv[1]);dst=Path(sys.argv[2]);counts=[]
with ZipFile(src) as zin, ZipFile(dst,'w',ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data=zin.read(item.filename)
        if re.fullmatch(r'ppt/slides/slide\d+\.xml',item.filename):
            data,count=patch(data);counts.append(count)
        zout.writestr(item,data)
assert counts and all(n in (1,2) for n in counts),counts
print('Native reveal steps per slide:',counts)
