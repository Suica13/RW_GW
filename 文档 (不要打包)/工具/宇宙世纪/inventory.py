from pathlib import Path
import os
os.chdir(Path(__file__).resolve().parents[3])
from pathlib import Path
import sys,json,re,collections
sys.path.insert(0,str(Path(__file__).resolve().parent));import config_view as c
O=Path('output/uc');O.mkdir(exist_ok=True)
from source_paths import packages
packs=packages();factions={'0079':['EFSF_0079','ZEON_0079'],'0087':['AEUG_0087','TITANS_0087','NEO_ZEON_0087'],'0093':['0093_EFSF','0093_NZN']};data={};entities={};allentities=[]
for era,pack in packs.items():
 c.MOD=pack;c.local.cache_clear();c.merged.cache_clear();count=0
 for p in pack.rglob('*.ini'):
  try:
   d=c.merged(p);core=d.get('core',{});name=core.get('name','').strip()
   if name and c.local(p).get('core',{}).get('dont_load','false').lower()!='true':
    record={'era':era,'path':str(p.relative_to(pack)).replace('\\','/'),'name':name,'override':core.get('overrideAndReplace',''),'tags':core.get('tags','')};entities.setdefault(name,[]).append(record);allentities.append(record);count+=1
  except Exception as e:print('PARSE',str(p.relative_to(pack)),str(e)[:100])
 print(era,count,'loadable entity definitions')
 for fac in factions.get(era,[]):
  pages=[]
  for p in sorted((pack/f'Units/TechTree/Core/Faction/{fac}').glob('TechTree_UI_Page*ini')):
   d=c.local(p);nodes=[]
   for s,v in d.items():
    if s.startswith('attachment_Tech_') and 'onCreateSpawnUnitOf' in v:
     nodes.append({'slot':s,'id':v['onCreateSpawnUnitOf'].split('*')[0],'x':v.get('x'),'y':v.get('y'),'main':s.startswith('attachment_Tech_Mid_')})
   pages.append({'file':str(p.relative_to(pack)),'nodes':nodes})
  data[fac]={'era':era,'pages':pages,'main':[n['id'] for p in pages for n in p['nodes'] if n['main']],'branch':[n['id'] for p in pages for n in p['nodes'] if not n['main']]}
  print(fac,'MAIN',data[fac]['main'],'BRANCH',data[fac]['branch'])
(O/'source-entities.json').write_text(json.dumps(entities,ensure_ascii=False,indent=2),encoding='utf-8');(O/'tech-inventory.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('unique entity IDs',len(entities),'duplicates',sum(len(v)>1 for v in entities.values()));print('core structure examples')
