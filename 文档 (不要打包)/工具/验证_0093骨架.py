"""Static integration and regression checks for the UC0093 skeleton (no MOD writes)."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,subprocess,struct

ROOT=Path(__file__).resolve().parents[2]
DLC=ROOT/'GW_BattleUniverse_DLC_0093'
MAIN=ROOT/'GW_BattleUniverse_Main'
ANALYSIS=ROOT/'文档 (不要打包)/分析'
FACTIONS={'0093_EFSF':1030101,'0093_NZN':1030201}
EXT={'.ini','.gw','.template'}

def text(path):return path.read_text(encoding='utf-8-sig').replace('\r\n','\n')
def blocks(content):
 out={}
 for m in re.finditer(r'^\[([^\]]+)\]\s*\n(.*?)(?=^\[|\Z)',content,re.M|re.S):
  out.setdefault(m[1],[]).append(m[2])
 return {k:'\n'.join(v) for k,v in out.items()}
def norm(content):
 return re.sub(r'\s+','',re.sub(r'^\s*#.*$','',content,flags=re.M)).rstrip(',')
def without_calls(content,call):
 def clean(m):
  vals=[v.strip() for v in m[1].split(',') if v.strip() and v.strip()!=call]
  return 'alsoTriggerAction:"""'+','.join(vals)+'"""'
 return re.sub(r'alsoTriggerAction:\s*"""(.*?)"""',clean,content,flags=re.S)

def main():
 results=[]
 def check(label,cond,details=None):
  results.append({'check':label,'passed':bool(cond),'details':details})
  print(('PASS ' if cond else 'FAIL ')+label,flush=True)
 # Assets and copyFrom must be local to this MOD, regardless of other loaded packs.
 rx=re.compile(r'ROOT:[/\\]?([A-Za-z0-9_./\\ -]+?\.(?:png|ogg|ini|gw|template))',re.I)
 missing=[]
 for p in DLC.rglob('*'):
  if p.suffix.lower() not in EXT:continue
  for m in rx.finditer(text(p)):
   rel=m[1].replace('\\','/')
   if not (DLC/rel).is_file():missing.append([p.relative_to(DLC).as_posix(),rel])
 check('all concrete ROOT file references exist inside DLC0093',not missing,missing)
 manifest_content=json.loads((ANALYSIS/'0093_构建清单.json').read_text('utf-8')).get('base_content',{})
 check('BattleUnits contains only declared units and reusable Shield/Weapon trees',
       {p.name for p in (DLC/'Units/BattleUnits').iterdir()}=={'Shield','Weapon'}|set(manifest_content.get('battle_folders',[])))
 check('no duplicated background music',not list((DLC/'Resource/Music').rglob('*.ogg')))

 # Pure text texture updates keep identical local copies in the runtime Main pack.
 manifest_ui=json.loads((ANALYSIS/'0093_构建清单.json').read_text('utf-8')).get('ui_texture_update')
 if manifest_ui:
  for name in manifest_ui['text']:
   rel='Resource/Image/Text/Button/'+name
   data=(DLC/rel).read_bytes()
   check('UI texture 130x60 RGBA + synchronized: '+name,
         data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(130,60)
         and data[25]==6 and data==(MAIN/rel).read_bytes())
  check('UC0093 title is synchronized', (DLC/manifest_ui['title']).read_bytes()==(MAIN/manifest_ui['title']).read_bytes())
  check('UC0093 ground/space title and year text are wired',
        all('image:ROOT:'+manifest_ui['title'] in text(MAIN/f'Units/Buildings/HQ/HostOption/VS/HostOption_Main_VS_GE_{terrain}_Page3.ini') for terrain in ['Ground','Space'])
        and 'image:ROOT:Resource/Image/Text/Button/Button_UC0093.png' in text(MAIN/'Units/Buildings/HQ/HostOption/VS/Marker/Common/HostOption_VS_GE_Common_UC0093.ini'))

 # Main owns complete common pilots; the optional DLC has no cross-pack image dependencies.
 pilot_report=ANALYSIS/'0093_普通驾驶员接入.json'
 if pilot_report.exists():
  pilots=json.loads(pilot_report.read_text('utf-8'))
  pilot_files=list((MAIN/'Units/BattleUnits/Pilot/0093').rglob('*.ini'))
  check('0093 has four common pilots and three dispatch markers',len(pilot_files)==7)
  missing_pilot_refs=[]
  for p in pilot_files:
   for m in rx.finditer(text(p)):
    if not (MAIN/m[1].replace('\\','/')).is_file():missing_pilot_refs.append([str(p),m[1]])
  check('0093 pilot templates and images resolve entirely inside Main',not missing_pilot_refs,missing_pilot_refs)
  check('0087 pilot images copied without modification',all((ROOT/x['source']).read_bytes()==(ROOT/x['target']).read_bytes() and hashlib.sha256((ROOT/x['target']).read_bytes()).hexdigest()==x['sha256'] for x in pilots['images']))
  root_routes=blocks(text(MAIN/'Units/BattleUnits/Pilot/Pilot_CustomMarker_Common.ini'))
  era_routes=blocks(text(ROOT/pilots['era_marker']))
  check('created common marker dispatches to UC0093', 'Start_PilotCustomChange_Common_0093' in root_routes['hiddenAction_Start_PilotCustomChange'] and 'convertTo:Pilot_CustomMarker_Common_0093' in root_routes['hiddenAction_Start_PilotCustomChange_Common_0093'])
  for f,info in pilots['factions'].items():
   route=root_routes['hiddenAction_Start_PilotCustomChange_Common_0093']
   target=era_routes['hiddenAction_Start_PilotCustomChange_'+f]
   check(f+' faction routing matches HQ tags',"includes='"+f+"'" in route and "includes='"+f+"'" in target and 'convertTo:Pilot_CustomMarker_Common_'+f in target)
   bs=blocks(text(ROOT/info['marker']))
   start=bs['hiddenAction_Start_PilotCustomChange']
   check(f+' preserves message/skill-transfer chain','newMessage(withTag="PilotCustomChange")' in start and 'Send_TryTransform_PilotCustomChange_Step3' in start and 'changePilotSkillsBool=true' in bs['hiddenAction_Send_TryTransform_PilotCustomChange_Step3'])
   for kind,codes in [('N_C',[1001,1101]),('O_C',[2001,2101])]:
    branch=bs['hiddenAction_Start_PilotCustomChange_Pilot_'+f+'_'+kind]
    check(f+' '+kind+' PilotType resolves to real unit',all('PilotType=='+str(code) in branch for code in codes) and 'convertTo:Pilot_'+f+'_'+kind+'_A' in branch)
   for unit in info['units']:
    u=text(ROOT/unit);core=blocks(u)['core'];unit_id=(ROOT/unit).stem
    check(unit_id+' identity and era are isolated',('name:'+unit_id) in core and ('tags:'+unit_id+','+f+',') in core and ',0093,UC,' in core and '0087' not in u and '0079' not in u)
   for tier in [1,2]:
    action=blocks(text(MAIN/f'Units/Buildings/Academy/Common/Academy_Common_T{tier}.ini'))['action_Produce_Pilot_'+f+'_N_C_A']
    check(f+' Academy T'+str(tier)+' faction/production match',"includes='Tech_"+f+"_Start'" in action and 'Pilot_'+f+'_N_C_A*1' in action and '@define Money=100' in action and 'buildSpeed:3s' in action)

 mode=text(DLC/'Units/Buildings/HQ/HQ_VS_GE/HQ_VS_GE_UC0093.ini')
 check('no starting combat roster',not re.search(r'^\s*(spawnUnits|produceUnits):',mode,re.M))
 check('exactly two faction selection actions',
       set(re.findall(r'^\[action_ChoseFaction_(0093_[^\]]+)\]',mode,re.M))==set(FACTIONS))
 for f,index in FACTIONS.items():
  b=blocks(mode)['action_ChoseFaction_'+f]
  check(f+' has matching index/start tag',f'FactionIndex={index}' in b and f'Tech_{f}_Start' in b)
  b=blocks(mode)['hiddenAction_ConvertToFaction_'+f]
  check(f+' converts and attaches the UC0093 core',f'convertTo:HQ_{f}' in b and 'TechTree_Core_0093' in b and 'TechTreeMarkerSlot' in b)
  for group in ['Units/TechTree/Core/Faction','Units/TechTree/Tech/Faction','Units/Buildings/HQ/HQ_VS_GE/Faction','Units/Buildings/Factory/Faction','Units/Buildings/Factory/UnitList']:
   check(f+' directory '+group,(DLC/group/f).is_dir())
  for category in ['Land','Air','Aqua','Mega','Space','Space_Mega']:
   p=DLC/f'Units/Buildings/Factory/UnitList/{f}/{f}_UnitList_{category}.ini'
   expected=bool(manifest_content and category in ['Land','Space','Space_Mega'])
   has_content=p.is_file() and ('/Units/Land/' in text(p) or '/Units/Space_Mega/' in text(p))
   check(f+' '+category+' production registration',p.is_file() and has_content==expected)
 for suffix in ['Main','DLC_0079','DLC_0087','DLC_SEED','DLC_0093']:
  p=ROOT/('GW_BattleUniverse_'+suffix)
  for rel,target in [('Template/Building/Common_Buildings_Slot.gw','0093_BuildingSlot'),('Units/Buildings/StrategicLocation/Mod/StrategicLocation.ini','StrategicLocation_0093')]:
   bs=blocks(text(p/rel));route=bs.get('hiddenAction_ConvertTo_0093','')
   check(suffix+' '+target+' routing',all(str(i) in route for i in FACTIONS.values()) and 'convertTo:'+target in route and 'ConvertTo_0093' in bs['hiddenAction_ConvertToFaction'])
  q=p/'Units/Buildings/HQ/Mod/HQ_GetMode.ini'
  if q.exists():
   bs=blocks(text(q));route=bs.get('hiddenAction_SetGameMode_Setting_Get_GameMode_VS_GE_UC0093','')
   check(suffix+' HQ stage routing','stageIndex==1020' in route and 'convertTo:HQ_VS_GE_UC0093' in route and 'SetGameMode_Setting_Get_GameMode_VS_GE_UC0093' in bs['hiddenAction_SetGameMode_Setting_Get_GameMode_VS_GE'])
 host=text(MAIN/'Units/Buildings/HQ/HostOption/HostOption_Core.ini')
 marker=text(MAIN/'Units/Buildings/HQ/HostOption/VS/Marker/Common/HostOption_VS_GE_Common_UC0093.ini')
 gm=text(MAIN/'Units/GameManager/GameManager_Start.ini')
 check('marker to HostOption to GameManager stageIndex chain',all(x in marker for x in ['Index=1020','VS_Stage','DLCMarker_0093']) and 'stageIndex=eventData("Index",type="float")' in host and 'sendMessageWithTags:Setting_GameMode' in host and "stageIndex=eventData('stageIndex',type='float')" in gm and 'stageIndex=memory.stageIndex' in gm and 'sendMessageTo:memory.playersHQ[index]' in gm)
 check('HostOption pagination covers ground and space page3',host.count('nowStageUIPageMax=3')==2 and all(f'attachments_addNewUnits:HostOption_Main_VS_GE_{t}_Page3' in host for t in ['Ground','Space']))
 # Verify all new Main entry targets resolve before installing the DLC, too.
 for rel,id_ in [
 ('Units/Buildings/HQ/HQ_VS_GE/HQ_VS_GE_UC0093.ini','HQ_VS_GE_UC0093'),
 ('Units/Buildings/HQ/HQ_VS_GE/Faction/0093_EFSF/HQ_0093_EFSF.ini','HQ_0093_EFSF'),
 ('Units/Buildings/HQ/HQ_VS_GE/Faction/0093_NZN/HQ_0093_NZN.ini','HQ_0093_NZN'),
 ('Units/Buildings/BuildingSlot/Faction/0093_BuildingSlot.ini','0093_BuildingSlot'),
 ('Units/Buildings/StrategicLocation/Faction/StrategicLocation_0093.ini','StrategicLocation_0093'),
 ('Units/TechTree/Core/0093/TechTree_Core_0093.ini','TechTree_Core_0093'),
 ('Units/TechTree/UnlockedListMarker/UnlockedListMarker_0093.ini','UnlockedListMarker_0093')]:
  check('Main placeholder and DLC replacement: '+id_,(MAIN/rel).is_file() and re.search(r'^name:\s*'+re.escape(id_)+r'\s*$',text(MAIN/rel),re.M) and 'overrideAndReplace:'+id_ in text(DLC/rel))
 # Compare original files against saved pre-change hashes, not against a fabricated target.
 baseline=json.loads((ANALYSIS/'BU_四包基线_0093制作前.json').read_text('utf-8'))
 manifest=json.loads((ANALYSIS/'0093_构建清单.json').read_text('utf-8'))
 actual=[];deleted=[]
 for pack,files in baseline.items():
  root=ROOT/('GW_BattleUniverse_'+pack)
  for rel,meta in files.items():
   p=root/rel
   if not p.is_file():deleted.append(str(p));continue
   if hashlib.sha256(p.read_bytes()).hexdigest()!=meta['sha256']:actual.append(p.relative_to(ROOT).as_posix())
 check('only declared existing files changed',set(actual)==set(manifest['existing_modified']),actual)
 declared_deleted={str(ROOT/p) for p in manifest.get('preexisting_deleted',[])}
 check('no additional source-pack files deleted',set(deleted)==declared_deleted,deleted)
 check('GameManager files remain byte-identical',not any('/Units/GameManager/' in p for p in actual))
 # Old scene actions must remain semantically unchanged, apart from appending the new dispatch.
 regress=[]
 for rel in actual:
  if (ROOT/rel).suffix.lower() not in EXT:continue  # Asset bytes were checked in declared-change validation.
  old=subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),'show','HEAD:'+rel],cwd=ROOT).decode('utf-8-sig').replace('\r\n','\n')
  before=blocks(old);after=blocks(text(ROOT/rel))
  for sec,b in before.items():
   a=after.get(sec,'')

   if '/HostOption/VS/Marker/Common/' in rel:
    for old_image,new_image in manifest.get('ui_texture_renames',{}).items():
     a=a.replace('ROOT:'+new_image,'ROOT:'+old_image)
     b=b.replace('ROOT:'+new_image,'ROOT:'+old_image)

   if rel.endswith('HostOption_Core.ini'):
    a=a.replace('nowStageUIPageMax=3','nowStageUIPageMax=2')
    b=b.replace('nowStageUIPageMax=3','nowStageUIPageMax=2')
    for terrain in ['Ground','Space']:
     a=without_calls(a,'ShowVS_GE_'+terrain+'_Page3')
     b=without_calls(b,'ShowVS_GE_'+terrain+'_Page3')
   for call in ['ConvertTo_0093','SetGameMode_Setting_Get_GameMode_VS_GE_UC0093','Start_PilotCustomChange_Common_0093']:
    a=without_calls(a,call)
    b=without_calls(b,call)
   b=without_calls(b,'__nothing__')
   if norm(a)!=norm(b):regress.append([rel,sec])
 check('original scene sections preserved',not regress,regress)
 report={'checks':len(results),'passed':sum(x['passed'] for x in results),'results':results}
 (ANALYSIS/'0093_静态连携验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f"{report['passed']}/{report['checks']} checks passed",flush=True)
 return 0 if report['passed']==report['checks'] else 1

if __name__=='__main__':raise SystemExit(main())