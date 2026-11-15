from pathlib import Path
import re
from functools import lru_cache
ROOT=Path.cwd();MOD=ROOT/'GW_BattleUniverse_DLC_0093'
@lru_cache(None)
def local(p):
 result={};s='';lines=iter(Path(p).read_text(encoding='utf-8-sig').splitlines())
 for line in lines:
  line=line.strip()
  if not line or line.startswith(('#',';')):continue
  if line.startswith('[') and line.endswith(']'):s=line[1:-1];result.setdefault(s,{});continue
  m=re.match(r'([^:=]+?)\s*[:=]\s*(.*)',line)
  if not m:continue
  k,v=m.groups()
  if v.startswith('"""'):
   v=v[3:]
   while '"""' not in v:v+=next(lines)
   v=v.split('"""')[0]
  result.setdefault(s,{})[k.strip()]=v.strip()
 return result
def ref(p,name):
 name=name.strip().replace('\\','/')
 return (MOD/name[5:].lstrip('/') if name.startswith('ROOT:') else Path(p).parent/name).resolve()
@lru_cache(None)
def merged(p):
 d={};own=local(p)
 for name in own.get('core',{}).get('copyFrom','').split(','):
  if name.strip():
   for s,v in merged(ref(p,name)).items():d.setdefault(s,{}).update(v)
 for s,v in own.items():d.setdefault(s,{}).update(v)
 return d
def effective(p):
 data=merged(p);cache={}
 def sec(s,trail=()):
  if s in cache:return cache[s]
  assert s not in trail,(s,trail)
  v=data.get(s,{});d={}
  for parent in v.get('@copyFromSection','').split(','):
   if parent.strip():d.update(sec(parent.strip(),trail+(s,)))
  d.update(v);cache[s]=d;return d
 return {s:sec(s) for s in data}
def roster():
 return [p for p in sorted((MOD/'Units/BattleUnits').glob('*/*.ini')) if 'MS' in [t.strip() for t in merged(p).get('core',{}).get('tags','').split(',')] and '_Turret' not in p.stem and 'Funnel' not in p.stem]
if __name__=='__main__':
 for p in roster()+[MOD/'Units/BattleUnits/SalamisClassKai_0093_EFSF/SalamisClassKai_0093_EFSF.ini']:
  if '_OverLine' in p.stem:continue
  print('\n'+p.stem)
  for s,v in effective(p).items():
   if s.startswith('action_') and float(v.get('pos','9999'))<990:print(s,v.get('pos'),v.get('text_zh'),v.get('iconImage'),v.get('isVisible','true'))
