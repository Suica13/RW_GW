"""Read-only port checks for Sazabi/Nu Gundam; gameplay must be checked separately."""
from pathlib import Path
import re,json,hashlib,itertools,collections
from 验证_0093骨架 import ROOT,DLC,ANALYSIS,text,blocks

def main():
 results=[]
 def check(n,v):
  results.append({'name':n,'passed':bool(v)})
  print(('PASS ' if v else 'FAIL ')+n)
 data=json.loads((ANALYSIS/'0093_沙扎比牛高达移植.json').read_text(encoding='utf-8-sig'))
 W=DLC/'Units/BattleUnits/Weapon';E=Path(data['source_mod'])
 units={uid:blocks(text(DLC/f'Units/BattleUnits/{uid}/{uid}.ini')) for uid in ['RX_93','MSN_04']}
 for uid,b in units.items():
  t=text(DLC/f'Units/BattleUnits/{uid}/{uid}.ini')
  check(uid+' uses a single native unit INI','BattleUnit_Framework_MS.ini' in b['core'] and '_Base.gw' not in b['core'] and '_Graphics.gw' not in b['core'])
  check(uid+' has no GM III body or weapon residue',not any(x in t for x in ['RGM_86R_0093_EFSF/Image','Weapon/Shell/EF_RGM_86R_','Weapon/Beam/EF_RGM_86R_','EF_GMRifle','EF_HypeBazookaKai_0087']))
  check(uid+' keeps initial base stats',hashlib.sha256(b['hiddenAction_InitializeStats'].encode()).hexdigest()==data['initial_stats_sha256'][uid])
  check(uid+' contains no weapon Fire_Step overrides',not any('_Fire_Step_' in n for n in b))
  check(uid+' keeps its faction pilot',('Pilot_0093_EFSF_N_C_A' if uid=='RX_93' else 'Pilot_0093_NZN_N_C_A') in b['hiddenAction_InitializeAddPilot_Default'])
 check('all imported body, shield, weapon and funnel artwork matches source bytes',all((E/x['source']).read_bytes()==(DLC/x['target']).read_bytes() for x in data['assets']))
 check('Nu Gundam has no I-field/barrier imports or active decals',not any(x in text(DLC/'Units/BattleUnits/RX_93/RX_93.ini') for x in ['GNField','IField','FieldShield','RX_93_FFS_']))
 def active(b,w,d,r):
  v=b['hiddenAction_'+w+'_Trigger'].split('requireConditional:',1)[1].replace(chr(34)*3,'').strip()[3:]
  v=' '.join(v.split())
  for old,new in [('distanceBetween(self,self.attacking)',str(d)),('eventData("RandomWeapon",type="float")',str(r)),('memory.finalAttackRange','600'),('false','False'),('true','True')]:v=v.replace(old,new)
  return bool(eval(v,{'__builtins__':{}},{}))
 ranges=[0,60,60.01,300,300.01,600,600.01];rolls=[0,5,5.01,15,15.01,25,25.01,35,35.01,100]
 for uid,ws in [('RX_93',['EF_RX_93_BR','EF_RX_93_BZ','EF_RX_93_ShieldBC','EF_RX_93_ShieldMS']),('MSN_04',['NZN_MSN_04_BSG','NZN_MSN_04_BR','NZN_MSN_04_HighBeamCannon','NZN_MSN_04_ShieldMS'])]:
  check(uid+' has complete exclusive ranged random branches',all(sum(active(units[uid],w,d,r) for w in ws)==int(60<d<=600) for d,r in itertools.product(ranges,rolls)))
 check('Sazabi axe and dual sabers use exclusive close-range branches',all(sum(active(units['MSN_04'],w,d,r) for w in ['NZN_MSN_04_BeamHawk_AF','NZN_MSN_04_DoubleSaber'])==int(d<=60) for d,r in itertools.product(ranges,rolls)))
 refs=[];missing_ids=[];ids=collections.Counter()
 for p in DLC.rglob('*.ini'):ids.update(m[1].strip() for m in re.finditer(r'(?m)^name:([^\r\n]+)',text(p)))
 files=[DLC/r for r in data['created']]+[DLC/f'Units/BattleUnits/{u}/{u}.ini' for u in units]
 for p in files:
  t=text(p)
  for m in re.finditer(r'ROOT:[/\\]?([A-Za-z0-9_./\\ -]+?\.(?:png|ogg|ini|gw))',t):
   if not (DLC/m[1].replace('\\','/')).is_file():refs.append([str(p),m[1]])
  for x in re.findall(r'(?ms)^spawnUnit:(?:"""(.*?)"""|([^\r\n]+))',t):
   for uid in re.findall(r'([A-Za-z_][A-Za-z_0-9]*)\*',x[0] or x[1]):
    if uid not in ids:missing_ids.append([str(p),uid])
 check('all source/resource/animation/file references resolve inside DLC0093',not refs)
 check('all spawned projectiles and funnels resolve to real entities',not missing_ids)
 for uid,prefix in [('RX_93','EF_RX_93'),('MSN_04','NZN_MSN_04')]:
  name=prefix+'_Funnel';launcher=blocks(text(W/f'Funnel/{name}.gw'));entity=blocks(text(DLC/f'Units/BattleUnits/{uid}/{uid}_Funnel.ini'));gun=blocks(text(W/f'Funnel/{name}_BeamGun.gw'))
  check(uid+' has one real funnel entity',ids[uid+'_Funnel']==1 and 'dont_load:false' in entity['core'])
  queue=launcher['hiddenAction_'+name+'_B10_Step_1']
  check(uid+' deploys exactly six funnels per native queue',queue.count(name+'_Fire_Step_1,')==1 and queue.count(name+'_Fire_Step_2,')==5)
  check(uid+' enforces active cap and backpack state for manual and AI launches',all('memory.'+name+'_Units.size==0' in b and 'memory.backpackBreaked==false' in b for b in [launcher['action_'+name+'_Trigger'],launcher['hiddenAction_'+name+'_Trigger_ByAI']]))
  check(uid+' records every funnel with a matching spawn callback',name+'_Units[memory.'+name+'_Units.size]' in launcher['hiddenAction_Get_FunnelSpawn_'+name] and 'FunnelSpawn_'+name in entity['hiddenAction_Send_FunnelSpawn'])
  check(uid+' prunes the owner active-funnel array','shrinkArrays:'+name+'_Units' in launcher['hiddenAction_Check_'+name+'_Units'])
  check(uid+' uses native target/attack/return lifecycle','Funnel_TypeA.gw' in entity['core'] and 'newMessage(withTag="Attack")' in entity['hiddenAction_'+name+'_BeamGun_Trigger'] and 'self.resource.EN>0' in gun['hiddenAction_'+name+'_BeamGun_Fire'])
  check(uid+' removes funnels when owner dies or changes team','customTarget1.hp<=0' in entity['hiddenAction_OrdinaryFunnel_InvalidOwner'] and 'self.teamId!=customTarget1.teamId' in entity['hiddenAction_OrdinaryFunnel_InvalidOwner'] and 'deleteSelf:true' in entity['hiddenAction_OrdinaryFunnel_InvalidOwner'])
  check(uid+' has no defensive barrier in its offensive funnel dependency',not any(x in text(W/f'Funnel/{name}.gw')+text(DLC/f'Units/BattleUnits/{uid}/{uid}_Funnel.ini') for x in ['GNField','FieldShield','IF_' ]))
  faction='0093_EFSF' if uid=='RX_93' else '0093_NZN';prod=blocks(text(DLC/f'Units/Buildings/Factory/UnitList/{faction}/Units/Land/{uid}.gw'))
  check(uid+' keeps standard-squad pilot queue and hides fake equipment squads',all('isVisible:false' in prod['action_Produce_'+uid+'_'+alias] for alias in ['MGSquad','BazookaSquad']) and all('produceUnits:' in prod['hiddenAction_Produce_'+uid+'_StandardSquad_'+str(n)] for n in [1,2,3]))
 native=text(W/'Funnel/Mod/Funnel_TypeA.gw')
 check('native funnel return has bounded lifetime and deletion',all(x in native for x in ['[hiddenAction_TimerOut]','[hiddenAction_TryGoBack]','[hiddenAction_TimerOutDel]','deleteSelf:true']))
 bc=blocks(text(W/'Beam/EF_RX_93_ShieldBC.gw'))
 check('Nu shield cannon AP projectile has finite hit count','|ProjectileAttackTimes:3' in bc['projectile_EF_RX_93_ShieldBC_Projectile'])
 check('funnel launch queues cannot be cancelled mid-volley',all('canPlayerCancel:false' in blocks(text(W/f'Funnel/{prefix}_Funnel.gw'))['action_'+prefix+'_Funnel_Trigger'] for prefix in ['EF_RX_93','NZN_MSN_04']))
 report={'checks':len(results),'passed':sum(x['passed'] for x in results),'results':results,'gameplay_tested':False}
 (ANALYSIS/'0093_沙扎比牛高达验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f"{report['passed']}/{report['checks']} checks passed")
 return int(report['passed']!=report['checks'])

if __name__=='__main__':raise SystemExit(main())
