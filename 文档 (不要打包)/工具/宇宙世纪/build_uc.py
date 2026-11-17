from pathlib import Path
import os
os.chdir(Path(__file__).resolve().parents[3])
from pathlib import Path
import json,re,collections,sys,hashlib,shutil
sys.path.insert(0,str(Path(__file__).resolve().parent));import config_view as cv
ROOT=Path.cwd();OUT=ROOT/'output/uc';DEST=ROOT/'GW_BattleUniverse_DLC_UC';DEST.mkdir(exist_ok=True)
from source_paths import packages
PACKS=packages()
INV=json.loads((OUT/'tech-inventory.json').read_text('utf-8'));ENT=json.loads((OUT/'source-entities.json').read_text('utf-8'));FAC=list(INV);TECHS={t for r in INV.values() for t in r['main']};BRANCH={t for r in INV.values() for t in r['branch']};FIDS=dict(zip(FAC,[1010101,1010201,1020101,1020201,1020301,1030101,1030201]));NAMES=dict(zip(FAC,['联邦军[0079]','吉翁军[0079]','奥古[0087]','提坦斯[0087]','新吉翁[0087]','联邦军[0093]','新吉翁[0093]']));ENAMES=dict(zip(FAC,['EFSF 0079','Zeon 0079','AEUG 0087','Titans 0087','Neo Zeon 0087','EFSF 0093','Neo Zeon 0093']))
DB={};CUSTOM={};ASSETS={};REMOVED_ACTIONS=set();KEEP_IDS=set();BATTLE_ALLOWED=set();BAD_IDS=set();SELECTED={};INCLUDED=set();FILE_QUEUE=[];ENTITY_QUEUE=[]
for era,pack in PACKS.items():
 for p in pack.rglob('*'):
  if p.is_file() and p.suffix in ['.ini','.gw','.template']:DB[(era,p.relative_to(pack).as_posix())]=p.read_text('utf-8-sig')
ORIGINAL=dict(DB)

def blocks(t):
 return list(re.finditer(r'(?ms)^\[([^\]\r\n]+)\][ \t]*\n(.*?)(?=^\[|\Z)',t))
def vals(b):
 d={};lines=iter(b.splitlines())
 for ln in lines:
  m=re.match(r'^([^#;:=]+?)\s*[:=]\s*(.*)',ln.strip())
  if not m:continue
  k,v=m.groups()
  if v.startswith('"""'):
   v=v[3:]
   while '"""' not in v:
    try:v+='\n'+next(lines)
    except StopIteration:break
   v=v.split('"""')[0]
  d[k.strip()]=v.strip()
 return d
def local(t):
 d={}
 for m in blocks(t):d.setdefault(m[1],{}).update(vals(m[2]))
 return d
def edit(t,s,k,value):
 matches=[m for m in blocks(t) if m[1]==s]
 if not matches:return t+f'\n[{s}]\n{k}:{value}\n'
 m=next((m for m in matches if k in vals(m[2])),matches[0]);b=m[2];pat=r'(?m)^'+re.escape(k)+r'\s*[:=](?:"""[\s\S]*?"""|[^\n]*)';line=k+':'+value
 b=re.sub(pat,lambda _:line,b,count=1) if re.search(pat,b) else line+'\n'+b
 return t[:m.start(2)]+b+t[m.end(2):]
def replace_section(t,s,body):
 found=False;out=[];last=0
 for m in blocks(t):
  if m[1]!=s:continue
  out.append(t[last:m.start()]);out.append(f'[{s}]\n{body}\n' if not found else '');last=m.end();found=True
 return ''.join(out)+t[last:] if found else t+f'\n[{s}]\n{body}\n'
def remove_sections(t,pred):
 out=[];last=0
 for m in blocks(t):
  if pred(m[1],vals(m[2])):
   out.append(t[last:m.start()]);last=m.end()
   if m[1].startswith(('action_','hiddenAction_')):REMOVED_ACTIONS.add(m[1].split('_',1)[1])
 return ''.join(out)+t[last:]
def calls(t,s):return [x.strip() for x in local(t).get(s,{}).get('alsoTriggerAction','').split(',') if x.strip()]
def choose(name):
 rs=ENT.get(name,[])
 if not rs:return None
 overrides=[r for r in rs if r['override'] and r['era']!='Main']
 return (overrides[-1] if overrides else next((r for r in rs if r['era']=='Main'),rs[0]))
# Apply UC-specific unit roster changes before deriving allowed units and pruning.
from uc_technology_rules import additions_for, REMOVED_UNITS
TECH_ADDITIONS = {}
for faction, row in INV.items():
 key=(row['era'],f'Units/TechTree/Tech/Faction/{faction}/TechList_{faction}.ini')
 additions=additions_for(faction,local(ORIGINAL[key]))
 TECH_ADDITIONS[faction]=additions
 for tech, units in additions.items():
  assert tech in row['main'], (faction,tech)
  section='hiddenAction_'+tech+'_UnlockUnit'
  original_calls=calls(DB[key],section)
  combined=list(dict.fromkeys(original_calls+['Unlock_'+unit for unit in units]))
  DB[key]=edit(DB[key],section,'alsoTriggerAction',','.join(combined))
  marker=choose(tech)
  marker_key=(marker['era'],marker['path'])
  for unit in units:
   DB[marker_key]=replace_section(DB[marker_key],'action_UnlockInfo_'+unit,'@copyFromSection:template_UnlockInfo_Unit\n@define UnitID:'+unit)
 for tech in row['main']:
  section='hiddenAction_'+tech+'_UnlockUnit'
  kept=[call for call in calls(DB[key],section) if not(call.startswith('Unlock_') and call[7:] in REMOVED_UNITS)]
  DB[key]=edit(DB[key],section,'alsoTriggerAction',','.join(kept))
(OUT/'technology-additions.json').write_text(json.dumps(TECH_ADDITIONS,ensure_ascii=False,indent=2),encoding='utf-8')

# Preserve every middle-row main technology and derive the genuine unit production set.
UNLOCKS={}
for f,r in INV.items():
 era=r['era'];key=(era,f'Units/TechTree/Tech/Faction/{f}/TechList_{f}.ini');t=DB[key];unlocks=set()
 for tech in r['main']:
  unlocks.update(x[7:] for x in calls(t,'hiddenAction_'+tech+'_UnlockUnit') if x.startswith('Unlock_') and not x.startswith('Unlock_Tech_'))
 UNLOCKS[f]=sorted(unlocks);KEEP_IDS.update(unlocks);KEEP_IDS.update(r['main'])
for name,rs in ENT.items():
 if name in KEEP_IDS:
  for r in rs:
   if r['path'].startswith('Units/BattleUnits/') and not r['path'].startswith(('Units/BattleUnits/Weapon/','Units/BattleUnits/Pilot/')):
    folder=r['path'].split('/')[2]
    BATTLE_ALLOWED.update(n for n,records in ENT.items() if any(q['era']==r['era'] and q['path'].startswith('Units/BattleUnits/'+folder+'/') for q in records))
# Explicit ACE combat units are an intentional exception to the technology-only roster.
ACE_UNIT_IDS={name for name,records in ENT.items() if any('ACE_Unit' in record['tags'].split(',') and '/Pilot/' not in record['path'] for record in records)}
KEEP_IDS.update(ACE_UNIT_IDS)
# Starter vehicles and all normal/officer pilots remain supported. ACE pilots follow the main chain.
for n,rs in ENT.items():
 if any('/Pilot/' in r['path'] and '/ACE/' not in r['path'] for r in rs):KEEP_IDS.add(n)
for n in ['Type74','Type61','FF_S3','FF_4','Wappa','MTank','ZN_APC','MusaiClass','JiccoClass']:BATTLE_ALLOWED.add(n)
for n,rs in ENT.items():
 combat=any(r['path'].startswith('Units/BattleUnits/') and not any('/'+x+'/' in r['path'] for x in ['Weapon','Pilot','Shield']) and any(t in r['tags'].split(',') for t in ['MS','Ship','Unit','MA','Vehicle']) for r in rs)
 if combat and n not in BATTLE_ALLOWED:BAD_IDS.add(n)
 if '/ACE/' in ' '.join(r['path'] for r in rs) and n not in KEEP_IDS and not n.startswith('Pilot_CustomMarker'):BAD_IDS.add(n)
# Production with no surviving technology unlock must not create a combat root.
for (era,path),text in DB.items():
 if '/Factory/UnitList/' not in path or '/Units/' not in path.split('/Factory/UnitList/',1)[1]:continue
 for section,values in local(text).items():
  unit=values.get('@define UnitID')
  if unit in ENT and unit not in KEEP_IDS and any(record['path'].startswith('Units/BattleUnits/') for record in ENT[unit]):BAD_IDS.add(unit)
BAD_IDS.update(BRANCH)
BAD_IDS.update(REMOVED_UNITS)
if (OUT/'branch-exclusive-ids.json').is_file():BAD_IDS.update(json.loads((OUT/'branch-exclusive-ids.json').read_text('utf-8')))
for n in ENT:
 if any(s in n for s in ['SEED','CE71','CR_P1','CR_Order','CR_Chaos','CR_Resistance','VS_CR']):BAD_IDS.add(n)
BAD_IDS.discard('HostOption_VS_CR')
BAD_TOKEN_RE=re.compile(r'\b(?:'+'|'.join(re.escape(x) for x in sorted(BAD_IDS,key=len,reverse=True))+r')\b')
# Prefer a retained derived ID to an excluded parent prefix (RX_121_2A vs RX_121).
BAD_UNIT_IDS={name for name in BAD_IDS if not name.startswith('Tech_')}
retained_derived={name for name in ENT if name not in BAD_IDS and any(name.startswith(parent+'_') for parent in BAD_UNIT_IDS)}
derived_guard=(r'(?!(?:'+'|'.join(re.escape(name) for name in sorted(retained_derived,key=len,reverse=True))+r')(?:_|$))') if retained_derived else ''
BAD_ACTION_RE=re.compile(r'(?:^|_)'+derived_guard+r'(?:'+'|'.join(re.escape(name) for name in sorted(BAD_UNIT_IDS,key=len,reverse=True))+r')(?:_|$)')
BRANCH_ACTION_RE=re.compile(r'^(?:hiddenAction|action)_(?:'+'|'.join(re.escape(x) for x in BRANCH)+r')(?:_|$)')
print('Preprocessing',len(DB),'source configs;',len(BAD_IDS),'excluded IDs',flush=True)
# Remove branch registrations, production chains, spawn/upgrade actions and incompatible menus.
for key,t in list(DB.items()):
 era,path=key
 def drop(s,v):
  if s.startswith('template_'):return False
  if BRANCH_ACTION_RE.search(s):return True
  if v.get('@define UnitID') in BAD_IDS:return True
  if s!='core' and any(x in s for x in ['SEEDCE71','_CE71','_CR_P1','VS_CR','AddMain_CR']):return True
  if BAD_TOKEN_RE.search(v.get('convertTo','')+' '+v.get('onCreateSpawnUnitOf','')+' '+v.get('produceUnits','')+' '+v.get('spawnUnits','')):return True
  if s.startswith(('action_','hiddenAction_')) and BAD_ACTION_RE.search(s):return True
  return False
 t=remove_sections(t,drop)
 t=re.sub(r'(?m)^@memory (?:'+ '|'.join(re.escape(x) for x in BRANCH)+r')(?:_\w+)?:[^\n]*\n','',t)
 if '/TechList_' in path:
  for tech in INV.get(path.split('/')[-2],{}).get('main',[]):
   pat=r'(\b'+re.escape(tech)+r'_TechPoint=|\$\{TechID\}_TechPoint=)([\d.]+)'
   s='hiddenAction_'+tech+'_Awake';d=local(t)
   if s in d:
    memory=d[s].get('setUnitMemory','');memory=re.sub(r'(\$\{TechID\}_TechPoint=)([\d.]+)',lambda m:m[1]+str(float(m[2])*0.5625).removesuffix('.0')+"+customTarget1.customTarget1.readUnitMemory('ucEraTechBase',type='float')",memory)
    t=edit(t,s,'setUnitMemory','"""\n'+memory+'\n"""')
  # Do not allow old skip-T1 entry points to invoke deleted side technologies.
  t=remove_sections(t,lambda s,v:s.startswith('hiddenAction_Tech_') and s.endswith('_PassT1'))
 if path.endswith('HQ_GetMode.ini'):
  t=remove_sections(t,lambda s,v:s.startswith('hiddenAction_SetGameMode_Setting_Get_GameMode_VS_GE_') and not s.endswith(('_UC0079','_UC0087','_UC0093')))
  t=edit(t,'hiddenAction_SetGameMode_Setting_Get_GameMode_VS_GE','alsoTriggerAction','SetGameMode_Setting_Get_GameMode_VS_GE_UC0079,SetGameMode_Setting_Get_GameMode_VS_GE_UC0087,SetGameMode_Setting_Get_GameMode_VS_GE_UC0093')
 if re.search(r'HQ_VS_GE_UC(0079|0087|0093)\.ini$',path):
  for source_era in ['0079','0087','0093']:
   t=t.replace('TechTree_Core_'+source_era,'TechTree_Core_UC').replace('UnlockedListMarker_'+source_era,'UnlockedListMarker_UC')
 DB[key]=t
# Keep prerequisites as the complete original main-chain order, irrespective of old side-branch gates.
for f,r in INV.items():
 for i,tech in enumerate(r['main']):
  record=choose(tech)
  key=(record['era'],record['path']) if record else None
  if key not in DB:continue
  DB[key]=re.sub(r'(?m)^@global Unlocked=.*$',"@global Unlocked="+('true' if i==0 else "self.globalTeamTags(includes='"+r['main'][i-1]+"')"),DB[key])
  DB[key]=edit(DB[key],'core','@global AIUnlocked','true')
print('Source filtering complete; generating era framework',flush=True)
# Custom era framework, one-page trees and compatibility patches are generated here.
exec(Path(__file__).with_name('uc_custom.py').read_text('utf-8-sig'))
# Remove references to actions/units that were deliberately excluded. Preserve multiline separators.
for key,t in list(DB.items()):
 # Action names are local to a unit/template. A deleted action in another unit must not remove a valid generic hook here.
 before_names={s.split('_',1)[1] for s in local(ORIGINAL.get(key,'')) if s.startswith(('action_','hiddenAction_'))}
 after_names={s.split('_',1)[1] for s in local(t) if s.startswith(('action_','hiddenAction_'))}
 removed_here=before_names-after_names
 def clean_list(m):
  k=m[1];v=m[2];items=[x.strip() for x in v.split(',') if x.strip()];items=[x for x in items if x not in removed_here and not BAD_ACTION_RE.search(x) and not BRANCH_ACTION_RE.search('hiddenAction_'+x) and not (x.startswith('Unlock_') and x[7:] in BAD_IDS)]
  return k+':'+(','.join(items) if items else 'NONE')
 t=re.sub(r'(?m)^(alsoTriggerAction|alsoQueueAction):"""([\s\S]*?)"""',clean_list,t)
 t=re.sub(r'(?m)^(alsoTriggerAction|alsoQueueAction):([^\n]*)',clean_list,t)
 # Import only production definitions whose units are retained; registrations for other stages are removed too.
 def clean_copy(m):
  body=m[1];refs=[x.strip() for x in body.split(',') if x.strip()];kept=[]
  for ref in refs:
   if '/Factory/UnitList/' in ref and '/Units/' in ref:
    stem=Path(ref.replace('\\','/')).stem
    if stem in BAD_IDS:continue
   if any(x in ref for x in ['SEEDCE71','/CE71/','/CR_P1/','/CR_Order/','/CR_Resistance/','/CR_Chaos/']):continue
   kept.append(ref)
  return 'copyFrom:"""\n'+',\n'.join(kept)+'\n"""'
 t=re.sub(r'(?m)^copyFrom:"""([\s\S]*?)"""',clean_copy,t)
 DB[key]=t
exec(Path(__file__).with_name('uc_factory_ai.py').read_text('utf-8-sig'))
exec(Path(__file__).with_name('uc_runtime_optimizations.py').read_text('utf-8-sig'))
# A single concrete definition wins per entity ID; modules retain local template/resource semantics.
for n in ENT:
 r=choose(n)
 if r:SELECTED[n]=(r['era'],r['path'])
ENTITY_REASONS=collections.defaultdict(list)
def add_entity(n,reason=None):
 if n in CUSTOM:return
 if n in BAD_IDS:return
 key=SELECTED.get(n)
 # Main supplies the engine/system units. Only the restricted era-selection UI overrides it.
 if key and key[0]=='Main' and n!='Pilot_CustomMarker_ACE' and not key[1].startswith('Units/Buildings/HQ/HostOption/'):return
 if key:
  evidence=reason or {'kind':'root'}
  if evidence not in ENTITY_REASONS[n]:ENTITY_REASONS[n].append(evidence)
 if key and n not in KEEP_VISITED:
  KEEP_VISITED.add(n);ENTITY_QUEUE.append(n);add_file(key)
def add_file(key):
 if key in INCLUDED:return
 if key not in DB:return
 INCLUDED.add(key);FILE_QUEUE.append(key)
KEEP_VISITED=set()
# Systems, common buildings and era factories are retained; combat roots come only from main unlocks.
for n,key in SELECTED.items():
 era,path=key
 if n in BAD_IDS:continue
 if era=='Main' and path.startswith('Units/') and not path.startswith(('Units/BattleUnits/','Units/TechTree/','Units/Buildings/HQ/','Units/Buildings/Factory/')) and 'GameManager_CR' not in path:add_entity(n)
 if path.startswith('Units/Buildings/') and not ('/HQ/' in path or '/Factory/' in path or '/Beacon_ACE/' in path):add_entity(n)
for n in KEEP_IDS|{'Pilot_CustomMarker_ACE','Type74','Type61','FF_S3','FF_4','Wappa','MTank','ZN_APC','MusaiClass','JiccoClass'}:add_entity(n)
for n in ['HQ_Start','HQ_Start_Host','HQ_VS_GE_UC0079','HQ_VS_GE_UC0087','HQ_VS_GE_UC0093','HostOption_Core','GameManager_Start','GameManager_VS']+[('HQ_'+f) for f in FAC]+[('HQ_'+f+'_Space') for f in FAC]:add_entity(n)
for n,key in SELECTED.items():
 if key[1].startswith('Units/Buildings/Factory/Faction/') and any('/'+f+'/' in key[1] for f in FAC):add_entity(n)
for key in list(DB):
 if key[1].startswith('UC/'):add_file(key)
for f in FAC:add_file((INV[f]['era'],f'Units/TechTree/Tech/Faction/{f}/TechList_{f}.ini'))
CANON={(e,p.lower()):(e,p) for e,p in DB}
ASSET_EXT=r'(?:png|ogg|tmx|dat|txt)';ID_FIELDS={'produceUnits','spawnUnits','spawnUnit','convertTo','attachments_addNewUnits','onCreateSpawnUnitOf','addUnitsIntoTransport','unitShownInUI','textAddUnitName','descriptionAddFromUnit','@define UnitID','fireTurretXAtGround_withProjectile'}
missing=[]
print('Resolving dependency closure',flush=True)
while FILE_QUEUE:
 era,path=FILE_QUEUE.pop();t=DB[(era,path)]
 for s,v in local(t).items():
  for k,val in v.items():
   if k=='copyFrom':
    for ref in val.split(','):
     ref=ref.strip().replace('\\','/')
     if not ref or ref.startswith(('CORE:','SHARED:')):continue
     if ref.startswith('ROOT:UC/'):add_file(('Main',ref[5:]));continue
     if ref.startswith('ROOT:Source/'):
      pieces=ref[12:].split('/',1);add_file((pieces[0],pieces[1]));continue
     dep=ref[5:].lstrip('/') if ref.startswith('ROOT:') else str((Path(path).parent/ref)).replace('\\','/')
     dep=str((PACKS[era]/dep).resolve().relative_to(PACKS[era])).replace('\\','/')
     if (era,dep) in DB:add_file((era,dep))
     elif (era,dep.lower()) in CANON:add_file(CANON[(era,dep.lower())])
     else:missing.append((era,path,ref))
   if k in ID_FIELDS:
    # Get/Send registrations only manipulate tags; they are not a unit acquisition path.
    if k=='@define UnitID' and 'TechTree/Tech/Faction/' in path and path.endswith(('_Get.ini','_Send.ini')):continue
    for token in re.findall(r'[A-Za-z][A-Za-z0-9_]*',val):
     if token in ENT:add_entity(token,{'kind':k,'era':era,'path':path,'section':s})
 for ref in re.findall(r'ROOT:([A-Za-z0-9_ ./\\\[\]()-]+?\.'+ASSET_EXT+r')',t):
  ref=ref.replace('\\','/').lstrip('/')
  if ref.startswith('UC/'):continue
  assetera=era
  if ref.startswith('Source/'):
   assetera,ref=ref[7:].split('/',1)
  p=PACKS[assetera]/ref
  if p.is_file():ASSETS[(assetera,ref)]=p
(OUT/'entity-retention.json').write_text(json.dumps(ENTITY_REASONS,ensure_ascii=False,indent=2),encoding='utf-8')
print('Closure complete:',len(INCLUDED),'configs;',len(KEEP_VISITED),'entities',flush=True)
# Preserve the source DLC directory conventions; resolve only real name collisions.
exec(Path(__file__).with_name('emit_package.py').read_text('utf-8-sig'))
