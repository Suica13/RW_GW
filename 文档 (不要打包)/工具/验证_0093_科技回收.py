"""Read-only recovery-plan wiring, migration and pricing regression checks."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[2]
D=R/'GW_BattleUniverse_DLC_0093'
S=R/'GW_BattleUniverse_DLC_0087'
def rd(p):return p.read_text(encoding='utf-8-sig')
def sections(s):
 ms=list(re.finditer(r'^\[([^\r\n]+)\]\n',s,re.M))
 return {m[1]:s[m.end():ms[i+1].start() if i+1<len(ms) else len(s)] for i,m in enumerate(ms)}
def field(s,k):
 m=re.search(r'^'+re.escape(k)+r'[:=](?:"""([\s\S]*?)"""|([^\r\n]*))',s,re.M)
 return (m[1] if m[1] is not None else m[2]).strip() if m else ''
def ids(s):return [x.strip() for x in s.split(',') if x.strip()]
def reachable_actions(blocks_by_name, start):
 pending=[start];visited=set()
 while pending:
  name=pending.pop()
  if name in visited:continue
  visited.add(name)
  pending.extend(ids(field(blocks_by_name.get('hiddenAction_'+name,''),'alsoTriggerAction')))
 return visited
def main():
 checks=[]
 def ck(label,ok):
  checks.append(bool(ok));print(('PASS ' if ok else 'FAIL ')+label)
 for f,moved,units in [('0093_EFSF','RGZ_91',['MSZ_006A1_0093_EFSF','MSZ_006C1_0093_EFSF']),('0093_NZN','MSN_03',['AMX_107_0093_NZN','AMX_006_0093_NZN'])]:
  t='Tech_'+f+'_Recovery';folder=D/f'Units/TechTree/Tech/Faction/{f}'
  b=sections(rd(folder/f'TechList_{f}.ini'))
  award=b[f'hiddenAction_{t}_UnlockUnit']
  ck(f+' awards exactly recovered units',ids(field(award,'alsoTriggerAction'))==['Unlock_'+u for u in [moved]+units])
  ck(f+' old plan no longer awards moved unit','Unlock_'+moved not in field(b[f'hiddenAction_Tech_{f}_Mid03_UnlockUnit'],'alsoTriggerAction'))
  ck(f+' full research and ally lifecycle',all('hiddenAction_'+t+'_'+suffix in b for suffix in ['Awake','Start','Stop','Done','UnlockUnit','NotByOther','SendAlly','SendAlly_Step2','SendAlly_Step3']))
  marker=rd(folder/'Common'/f'{t}.ini')
  ck(f+' recovery follows mass-production plan',f"includes='Tech_{f}_Mid02'" in marker)
  ck(f+' main-unit plan follows recovery',f"includes='{t}'" in rd(folder/'Common'/f'Tech_{f}_Mid03.ini'))
  ck(f+' all recovery unit info buttons',all(f'[action_UnlockInfo_{u}]' in marker for u in units+[moved]))
  page=rd(D/f'Units/TechTree/Core/Faction/{f}/TechTree_UI_Page_{f}_00.ini')
  ck(f+' page order and six unique nodes',re.findall(r'onCreateSpawnUnitOf:([^*\r\n]+)',page)==[f'Tech_{f}_BaseTech',f'Tech_{f}_Mid02',t,f'Tech_{f}_Mid03',f'Tech_{f}_Mid04',f'Tech_{f}_Mid05'])
  gift=b[f'hiddenAction_{t}_NotByOther']
  expected=[u if u!='RGZ_91' else 'RGZ_91_MA' for u in [moved]+units]
  actual=re.findall(r'([A-Za-z_0-9]+)\*1\(',field(gift,'spawnUnits'))
  if f=='0093_EFSF':
   ground=b['hiddenAction_Tech_0093_EFSF_Recovery_Gift_Ground'];space=b['hiddenAction_Tech_0093_EFSF_Recovery_Gift_Space']
   ck(f+' map-specific recovery gifts',actual==['RGZ_91_MA'] and 'TileMode==0' in ground and 'MSZ_006A1_0093_EFSF*1(' in ground and 'TileMode==1' in space and 'MSZ_006C1_0093_EFSF*1(' in space and 'template_Tech_NotByOther' in gift)
  else:ck(f+' own research grants each recovered unit once',actual==expected and 'template_Tech_NotByOther' in gift)
  for u in units:
   old=u.split('_0093_')[0]
   for suffix in ['','_MA','_MA_OverLine']:
    p=D/f'Units/BattleUnits/{old}/{u+suffix}.ini';s=rd(p)
    ck(u+suffix+' has independent ID',bool(re.search(r'^name:'+u+suffix+r'$',s,re.M)))
    if suffix!='_MA_OverLine':
     ck(u+suffix+' uses 0093 faction/pilot',f',{f},0093,UC' in s and f'Pilot_{f}_N_C_A' in s)
     ck(u+suffix+' transforms only within own family',set(re.findall(r'^convertTo:([^\r\n]+)',s,re.M))<=set(u+x for x in ['','_MA','_MA_OverLine']))
   base=sections(rd(D/f'Units/BattleUnits/{old}/{u}.ini'))
   source=sections(rd(S/f'Units/BattleUnits/{old}/{old}.ini'))
   ck(u+' preserves source combat stats',base['hiddenAction_InitializeStats']==source['hiddenAction_InitializeStats'])
   sent=sections(rd(folder/f'{f}_Send.ini'));got=sections(rd(folder/f'{f}_Get.ini'))
   ck(u+' matching unlock send/receive',field(sent['hiddenAction_Unlock_'+u],'@define UnitID')==u and field(got['hiddenAction_Get_UnlockInfo_'+u],'@define UnitID')==u)
   production=D/f'Units/Buildings/Factory/UnitList/{f}/Units/Land/{u}.gw';pb=sections(rd(production))
   ck(u+' all spawn targets belong to 0093',set(re.findall(r'^([A-Za-z_0-9]+)\*\d+\(addResources=PilotType:1101',rd(production),re.M))=={u})
   for category in ['Land','Space']:
    listing=rd(D/f'Units/Buildings/Factory/UnitList/{f}/{f}_UnitList_{category}.ini')
    fb=sections(rd(D/f'Units/Buildings/Factory/Faction/{f}/Factory_{f}_{category}.ini'))
    expected_ai = not ((old=='MSZ_006A1' and category=='Space') or (old=='MSZ_006C1' and category=='Land'))
    ck(u+' '+category+' player/AI entry',production.relative_to(D).as_posix() in listing and (not expected_ai or ('AutoProduce_'+u in reachable_actions(fb,'Get_AutoProduce') and 'hiddenAction_AutoProduce_'+u in fb)))
   # Check the reachable squad queues retain distinct pilot creation ticks.
   orders=[(n,b) for n,b in pb.items() if n.startswith('action_Produce_')]
   for n,b in orders:
    queue=ids(field(b,'alsoQueueAction'));steps=[pb['hiddenAction_'+x] for x in queue]
    ck(n+' pilot queue',len(steps) in [1,3] and all('PilotType:1101' in x for x in steps))
    if len(steps)==3:ck(n+' delayed pilot spawns',[field(x,'buildSpeed') for x in steps]==['0.0s','1.0s','1.0s'])
    ck(n+' cost above zero',int(field(b,'@define Money'))>0 and int(field(b,'@define Resource'))>0)
 m=json.loads(next(R.glob('*/*/0093_recovery_plans.json')).read_text(encoding='utf8'))
 missing=[]
 for rel in m['changed_files']:
  p=R/rel
  if p.suffix not in ['.ini','.gw']:continue
  for ref in re.findall(r'ROOT:[/\\]*([^\s,\r\n"\)]+?\.(?:ini|gw|png|ogg))',rd(p),re.I):
   if not (D/ref.replace('\\','/')).is_file():missing.append((rel,ref))
 ck('all migrated file dependencies remain inside DLC0093',not missing)
 if missing:print(missing)
 plans=json.loads(next(R.glob('*/*/0093_factory_pricing.json')).read_text(encoding='utf8'))['plans']
 z=rd(S/'Units/Buildings/Factory/UnitList/AEUG_0087/Units/Land/MSZ_006.gw')
 zz=rd(S/'Units/Buildings/Factory/UnitList/AEUG_0087/Units/Land/MSZ_010.gw')
 zprice=sections(z)['action_Produce_MSZ_006_StandardSquad'];zzprice=sections(zz)['action_Produce_MSZ_010_StandardSquad']
 for u in ['RX_93','MSN_04']:
  ck(u+' priced above Z and ten percent above previous ZZ-tier cost',all(plans[u][key]==int(field(zzprice,'@define '+fieldname))*110//100 and plans[u][key]>int(field(zprice,'@define '+fieldname)) for key,fieldname in [('money','Money'),('resource','Resource')]))
 print(f'{sum(checks)}/{len(checks)} checks passed; production, transformations and interception still need gameplay verification.')
 return int(not all(checks))
if __name__=='__main__':raise SystemExit(main())

