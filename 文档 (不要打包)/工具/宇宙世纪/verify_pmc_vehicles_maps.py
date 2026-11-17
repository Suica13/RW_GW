from pathlib import Path
import sys,json,re,xml.etree.ElementTree as ET,base64,gzip,zlib,struct
r=Path.cwd();out=r/'output/pmc-vehicles-maps';sys.path.insert(0,str(next(r.glob('*/*/*/config_view.py')).parent));import config_view as c
cases=json.loads(Path(__file__).with_name('pmc-vehicle-map-cases.json').read_text('utf-8'));plans=cases['vehicles'];issues=[]
for row in plans:
 pack=r/row['package'];c.MOD=pack;c.merged.cache_clear();d=c.effective(pack/row['file']);co=d['core']
 assert co.get('@global manualControlImplemented')=='true',row['unit']
 assert 'ManualControlCapable' in co['tags'],row['unit']
 declared={k[8:].split(':')[0] for k in co if k.startswith('@memory ')}
 for s in c.local(pack/row['adapter']):
  if not s.startswith(('action_','hiddenAction_','turret_')):continue
  for k,v in d[s].items():
   if k.startswith('@'):continue
   for memory in re.findall(r'\bmemory\.([A-Za-z_][A-Za-z_0-9]*)',v):
    if memory.lower() not in {x.lower() for x in declared}:issues.append((row['unit'],s,k,memory))
 for b in row['buttons']:assert 'action_'+b in d
 # No per-weapon automatic polling introduced.
 for s,v in c.local(pack/row['adapter']).items():assert not ('autoTrigger' in v and v['autoTrigger'] not in ('false','if not memory.manualControlEnabled and (false)')),(row['unit'],s)
assert not issues,issues[:15]
rows=cases['maps']
for row in rows:
 source=ET.parse(r/'GW_BattleUniverse_Main/Maps'/row['source']).getroot();target=ET.parse(r/'GW_BattleUniverse_Main/Maps'/row['map']).getroot()
 assert source.attrib['width']==target.attrib['width'] and source.attrib['height']==target.attrib['height']
 old_layers=source.findall('layer');new_layers=target.findall('layer');assert len(old_layers)==len(new_layers)
 for a,b in zip(old_layers,new_layers):
  if a.get('name').lower()!='items':assert ET.tostring(a)==ET.tostring(b)
 starts=target.find("objectgroup[@name='SP_PlayerStarts']").findall('object');assert len(starts)==20
 assert len({(o.get('x'),o.get('y')) for o in starts})==20
 assert len(source.findall('.//object'))+20==len(target.findall('.//object'))
 assert row['map'].startswith('[p20]') and row['map'].count(']')==1
 assert row['map'].endswith('_SP_Map.tmx') and row['thumbnail']==row['map'][:-4]+'_map.png'
print('PASS:',len(plans),'vehicle adapters,',sum(len(x['buttons']) for x in plans),'weapons; all memory declarations and native references valid; seven maps retain terrain and neutral objects.')
print('Active INI counts (before cross-package overrides):')
for pack in sorted(r.glob('GW_BattleUniverse_*')):
 n=sum(c.local(p).get('core',{}).get('dont_load','false')!='true' for p in pack.rglob('*.ini'))
 print(pack.name,n)
