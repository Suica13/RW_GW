from pathlib import Path
import sys,json,os
os.chdir(Path(__file__).resolve().parents[3])
folder=Path(__file__).resolve().parent;sys.path.insert(0,str(folder));import config_view as c
root=Path('GW_BattleUniverse_DLC_UC').resolve();c.MOD=root
v=json.loads(Path('output/uc/verification.json').read_text('utf-8'))
loaded={}
for p in root.rglob('*.ini'):
 if c.local(p).get('core',{}).get('dont_load')!='true':
  d=c.merged(p)['core'];n=d.get('name','');
  if '${' not in n:loaded[n]=p
cases=[];productions=[];forms=set();ent=json.loads(Path('output/uc/source-entities.json').read_text('utf-8'));selected=set(json.loads(Path('output/uc/selected-entities.json').read_text('utf-8')))
for row in v['technology_merges']:
 f=row['faction'];tech=row['technology'];units=row['units'];cases.append('\t'.join([f,tech,','.join(units)]))
 for unit in units:
  if unit.startswith('Pilot_'):continue
  records=[r for r in ent[unit] if r['era']==('0079' if f.endswith('0079') else '0087')]
  prefix=records[0]['path'].split('/')[2]
  for name,rs in ent.items():
   if name in selected and any(r['era']==records[0]['era'] and r['path'].startswith('Units/BattleUnits/'+prefix+'/') and ('MS' in r['tags'].split(',') or 'MA' in r['tags'].split(',')) for r in rs):forms.add(name)
  for tile in [0,1]:
   choices=[]
   for factory,roster in v['factories'][f].items():
    if unit not in roster or ('_Space' in factory)!=(tile==1):continue
    d=c.effective(loaded[factory]);actions=[s[7:] for s,a in d.items() if s.startswith('action_Produce_') and a.get('@define UnitID')==unit]
    if actions:choices.append((factory,actions[0]))
   if choices:
    factory,action=sorted(choices,key=lambda item:('_Land' not in item[0] and '_Space' not in item[0],item[0]))[0]
    productions.append('\t'.join([f,str(tile),tech,unit,factory,action]))
   else:
    # Some units are legitimately confined to one terrain's native production lists.
    assert not any(unit in roster and ('_Space' in factory)==(tile==1) for factory,roster in v['factories'][f].items()),(unit,tile)
Path('output/uc/tech-merge-cases.txt').write_text('\n'.join(cases),encoding='utf-8')
Path('output/uc/tech-merge-production.txt').write_text('\n'.join(productions),encoding='utf-8')
Path('output/uc/tech-merge-forms.txt').write_text('\n'.join(sorted(forms)),encoding='utf-8')
print('Research groups',len(cases),'factory cases',len(productions),'MS/MA forms',len(forms))
