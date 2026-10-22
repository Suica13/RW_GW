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
 check('BattleUnits contains only reusable Shield and Weapon trees',
       {p.name for p in (DLC/'Units/BattleUnits').iterdir()}=={'Shield','Weapon'})
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
   check(f+' empty '+category+' production list',p.is_file() and not re.search(r'^\[(?:action_|hiddenAction_AutoProduce)',text(p),re.M))
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
 check('no existing source-pack files deleted',not deleted,deleted)
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

   if rel.endswith('HostOption_Core.ini'):
    a=a.replace('nowStageUIPageMax=3','nowStageUIPageMax=2')
    for terrain in ['Ground','Space']:a=without_calls(a,'ShowVS_GE_'+terrain+'_Page3')
   for call in ['ConvertTo_0093','SetGameMode_Setting_Get_GameMode_VS_GE_UC0093']:
    a=without_calls(a,call)
   b=without_calls(b,'__nothing__')
   if norm(a)!=norm(b):regress.append([rel,sec])
 check('original scene sections preserved',not regress,regress)
 report={'checks':len(results),'passed':sum(x['passed'] for x in results),'results':results}
 (ANALYSIS/'0093_静态连携验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f"{report['passed']}/{report['checks']} checks passed",flush=True)
 return 0 if report['passed']==report['checks'] else 1

if __name__=='__main__':raise SystemExit(main())