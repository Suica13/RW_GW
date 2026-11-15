from pathlib import Path
import os
os.chdir(Path(__file__).resolve().parents[3])
from pathlib import Path
import json,sys,re
sys.path.insert(0,str(Path(__file__).resolve().parent));import config_view as c
from source_paths import package_root
O=Path('output/uc');e=json.loads((O/'source-entities.json').read_text('utf-8'));out={}
for records in e.values():
 for r in records:
  if '${' in r['name']:
   pack=package_root(r['era']);c.MOD=pack;c.merged.cache_clear();core=c.merged(pack/r['path'])['core'];r['name']=re.sub(r'\$\{([^}]+)\}',lambda m:core.get('@global '+m[1],core.get('@define '+m[1],m[0])),r['name'])
  out.setdefault(r['name'],[]).append(r)
(O/'source-entities.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print('Entity IDs after macro resolution:',len(out))
t=json.loads((O/'tech-inventory.json').read_text('utf-8'))
for f,row in t.items():
 if row['era']=='0093':row['main']=row['branch'];row['branch']=[]
(O/'tech-inventory.json').write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['HostOption_Core','HostOption_Main','HostOption_Main_VS','HostOption_Main_VS_GE_Ground','UnlockedListMarker_0079','UnlockedListMarker_0087','GameManager','GameManager_Start','GameManager_VS','HQ_EFSF_0079_Space','HQ_0093_EFSF']:
 print(name,out.get(name,[]))
