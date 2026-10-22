"""Check the Base -> unlock marker -> building/factory -> requested-unit chain."""
from pathlib import Path
import json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from 验证_0093骨架 import ROOT,DLC,MAIN,ANALYSIS,text,blocks

FACTIONS={'0093_EFSF':['RGM_86R_0093_EFSF','SalamisClassKai_0093_EFSF'],
          '0093_NZN':['AMX_101_0093_NZN','MusaiClassFinalType_0093_NZN']}
COMMON={'Refinery_Common_T3','Institute_Common_T2','SupplyDepot_Common_T2','Academy_Common_T2',
        'Turret_MG_B','Turret_AA_B','Turret_CN_B','Turret_BM_B_Yellow','Turret_Radar_B',
        'Turret_Space_MG_B','Turret_Space_MS_B','Turret_Space_CN_B','Wall_T2_A','Wall_T2_B','HLV_0093_Build'}
CATEGORIES=['Land','Mega','Space','Space_Mega']

def main():
 results=[]
 def check(label,ok,details=None):
  results.append({'check':label,'passed':bool(ok),'details':details})
  print(('PASS ' if ok else 'FAIL ')+label,flush=True)
 def read(rel):return text(DLC/rel)
 # Resolve loaded entity IDs from Main and DLC, independent of file names.
 registry={}
 for pack in [MAIN,DLC]:
  for p in pack.rglob('*.ini'):
   t=text(p)
   for m in re.finditer(r'^name:\s*([A-Za-z0-9_]+)\s*$',t,re.M):registry.setdefault(m[1],[]).append(p)
 common_get=blocks(read('Units/TechTree/Tech/Faction/Common/Common_Building_Get.ini'))
 common_send=blocks(read('Units/TechTree/Tech/Faction/Common/Common_Building_Send.ini'))
 buildlist=blocks(read('Units/Buildings/BuildingSlot/Faction/0093_MainBuildList.ini'))
 slots=blocks(read('Units/Buildings/BuildingSlot/Faction/0093_BuildingSlot.ini'))
 unlocked=read('Units/TechTree/UnlockedListMarker/UnlockedListMarker_0093.ini')
 check('unlocked marker includes shared building receiver','Faction/Common/Common_Building_Get.ini' in unlocked)
 core=blocks(read('Units/TechTree/Core/0093/TechTree_Core_0093.ini'))
 core_mod=blocks(read('Units/TechTree/Mod/TechTree_Core.gw'))
 ui_mod=blocks(read('Template/UI/Common_UI.gw'))
 check('created event reaches the core startup tech dispatcher',
       'autoTriggerOnEvent:created' in ui_mod['hiddenAction_InitializeStats']
       and 'Start_Set_Tech' in core_mod['hiddenAction_InitializeStats'])
 check('startup dispatch covers both 0093 factions',all('Start_Set_Tech_'+f in core['hiddenAction_Start_Set_Tech'] for f in FACTIONS))
 for f in FACTIONS:
  start=core['hiddenAction_Start_Set_Tech_'+f]
  check(f+' startup addresses its actual attached tech UI',
        "sendMessageTo:self.attachment(slot='"+f+"')" in start
        and 'attachment_'+f in blocks(read(f'Units/TechTree/Core/Faction/{f}/TechTree_{f}.gw')))
  check(f+' startup sends Base completion via the existing event path',
        'sendMessageWithTags:Unlock_Tech_'+f+'_BaseTech' in start and 'byOther=1' in start
        and 'autoTriggerOnEvent:newMessage(withTag="Unlock_${TechID}")' in read('Units/TechTree/Mod/TechList.gw'))
  tags=re.findall(r"self.globalTeamTags\(includes='([^']+)'\)",start)
  check(f+' startup is gated by its start tag and PassT0',set(tags)=={'Tech_'+f+'_Start','PassT0'} and ' and ' in start)
  lobby=blocks(read('Units/Buildings/HQ/HQ_VS_GE/HQ_VS_GE_UC0093.ini'))
  check(f+' faction selection grants the startup prerequisites',all(tag in lobby['action_ChoseFaction_'+f] for tag in tags))

 for f,units in FACTIONS.items():
  base='Tech_'+f+'_BaseTech';folder=f'Units/TechTree/Tech/Faction/{f}'
  project=read(folder+'/TechList_'+f+'.ini');sections=blocks(project)
  expected=set(units)|COMMON|{'Factory_'+f+'_'+c for c in CATEGORIES}
  actual=set(re.findall(r'\bUnlock_([A-Za-z0-9_]+)',sections['hiddenAction_'+base+'_UnlockUnit']))
  check(f+' Base unlocks exactly two combat units and baseline infrastructure',actual==expected,sorted(actual^expected))
  check(f+' Base lifecycle is complete',all('hiddenAction_'+base+'_'+s in sections for s in ['Awake','Start','Stop','Done','UnlockUnit','NotByOther','SendAlly','SendAlly_Step2','SendAlly_Step3']))
  check(f+' zero-cost Base matches 0087',all('${TechID}_'+x+'=0' in sections['hiddenAction_'+base+'_Awake'] for x in ['Time','Money','Resource','TechPoint']))
  check(f+' only one research project',set(re.findall(r'@define TechID=([^\s]+)',project))=={base})
  send=blocks(read(folder+'/'+f+'_Send.ini'))|common_send
  get=blocks(read(folder+'/'+f+'_Get.ini'))|common_get
  marker=blocks(read(folder+'/Common/'+base+'.ini'))
  for uid in sorted(expected):
   ok=uid in registry and ('hiddenAction_Unlock_'+uid) in send and ('hiddenAction_Get_UnlockInfo_'+uid) in get and ('action_UnlockInfo_'+uid) in marker
   check(f+' unlock resolves through Send/Get and real entity: '+uid,ok)
  page=read(f'Units/TechTree/Core/Faction/{f}/TechTree_UI_Page_{f}_00.ini')
  check(f+' first page contains only the Base node',re.findall(r'onCreateSpawnUnitOf:([^\s*]+)',page)==[base])
  ui=read(f'Units/TechTree/Core/Faction/{f}/TechTree_UI_Main_{f}.ini')
  check(f+' single-page UI and AI research opening','pageMax=0' in ui and 'hiddenAction_AI_CheckPage_ShowTechTree' in ui)
  for category in CATEGORIES:
   uid='Factory_'+f+'_'+category
   factory=read(f'Units/Buildings/Factory/Faction/{f}/{uid}.ini')
   check(uid+' has HQ/SL and slot construction routes',('canBuild_'+uid) in buildlist and ('action_Build_'+uid) in slots and "includes='"+f+"'" in slots['action_Build_'+uid])
   check(uid+' retains construction completion tag','temporarilyAddTags:Factory_T1' in factory)
   if category=='Mega':continue
   unit=units[1] if category=='Space_Mega' else units[0]
   unitlist=read(f'Units/Buildings/Factory/UnitList/{f}/{f}_UnitList_{category}.ini')
   check(uid+' registers correct production and AI action',unit+'.gw' in unitlist and 'alsoTriggerAction:AutoProduce_'+unit in factory)
  for uid in units:
   check(uid+' has no cross-DLC duplicate ID',len(registry.get(uid,[]))==1)
   p=registry[uid][0];t=text(p)
   pilot_kind='O_C_A' if uid==units[1] else 'N_C_A'
   check(uid+' defaults to correct 0093 pilot','Pilot_'+f+'_'+pilot_kind in t)
   category='Space_Mega' if uid==units[1] else 'Land'
   prod=read(f'Units/Buildings/Factory/UnitList/{f}/Units/{category}/{uid}.gw')
   targets=re.findall(r'^\s*([A-Za-z0-9_]+)\*1\(addResources=PilotType:',prod,re.M)
   check(uid+' production creates only itself',bool(targets) and set(targets)=={uid})
   if category=='Land':
    check(uid+' squad spacing preserves separate pilot rolls',len(re.findall(r'buildSpeed:1\.0s',prod))==2*(len(targets)//3))
 # Shared Main entities need unlocks and construction routes, not duplicate DLC copies.
 for uid in sorted(COMMON):
  check(uid+' has HQ/SL canBuild entry','canBuild_'+uid in buildlist)
  check(uid+' remains Main infrastructure',any(p.is_relative_to(MAIN) for p in registry.get(uid,[])) and not any(p.is_relative_to(DLC) for p in registry.get(uid,[])))
 check('core economy buildings have building-slot actions',all('action_Build_'+uid in slots for uid in ['Refinery_Common_T3','Institute_Common_T2','SupplyDepot_Common_T2','Academy_Common_T2']))
 check('HLV construction creates the 0093 transport','spawnUnits:HLV_0093*1' in text(MAIN/'Units/Buildings/HLV_Build/Unit/HLV_0093_Build.ini') and 'HLV_0093' in registry)
 # Check concrete local references and inherited relative copyFrom for the newly migrated files.
 migration=json.loads((ANALYSIS/'0093_Base科技接入.json').read_text('utf-8'))
 bad=[]
 for item in migration['migrations']:
  p=DLC/item['target'];t=text(p)
  for match in re.finditer(r'ROOT:[/\\]?([A-Za-z0-9_./\\ -]+?\.(?:png|ogg|ini|gw|template))',t,re.I):
   if not (DLC/match[1].replace('\\','/')).is_file():bad.append([str(p),match[1]])
  for value in re.findall(r'copyFrom:\s*(?:"""(.*?)"""|([^\r\n]+))',t,re.S):
   for ref in (value[0] or value[1]).split(','):
    ref=ref.strip()
    if ref and not ref.startswith('ROOT:') and not (p.parent/ref).is_file():bad.append([str(p),ref])
 check('migrated file references and relative inheritance resolve',not bad,bad)
 # All ship attachment entities must have distinct 0093 IDs, also when 0087 is enabled.
 source_ids=set()
 for p in (ROOT/'GW_BattleUniverse_DLC_0087/Units/BattleUnits').rglob('*.ini'):
  m=re.search(r'^name:([^\r\n]+)',text(p),re.M)
  if m:source_ids.add(m[1].strip())
 migrated_ids=[]
 for x in migration['migrations']:
  if x['target'].endswith('.gw'):continue
  t=text(DLC/x['target']);m=re.search(r'^name:([^\r\n]+)',t,re.M)
  if m:migrated_ids.append(m[1].strip())
 check('all migrated unit and turret IDs are unique across 0087',not set(migrated_ids)&source_ids and len(migrated_ids)==len(set(migrated_ids)))
 report={'checks':len(results),'passed':sum(x['passed'] for x in results),'results':results}
 (ANALYSIS/'0093_Base科技验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f"{report['passed']}/{report['checks']} checks passed")
 return 0 if report['checks']==report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
