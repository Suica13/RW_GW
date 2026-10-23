"""Read-only checks for Jegan/Geara Doga native weapon wiring; not a gameplay simulation."""
from pathlib import Path
import itertools,json,re,hashlib
from 验证_0093骨架 import ROOT,DLC,ANALYSIS,text,blocks

def main():
 results=[]
 def check(n,v):
  results.append({'name':n,'passed':bool(v)})
  print(('PASS ' if v else 'FAIL ')+n)
 report=json.loads((ANALYSIS/'0093_杰刚基拉多加武装接入.json').read_text(encoding='utf-8-sig'))
 W=DLC/'Units/BattleUnits/Weapon'
 units={uid:blocks(text(DLC/f'Units/BattleUnits/{uid}/{uid}.ini')) for uid in ['RGM_89','AMS_119']}
 for uid,b in units.items():
  check(uid+' uses one standalone native unit INI','BattleUnit_Framework_MS.ini' in b['core'] and '_Base.gw' not in b['core'] and '_Graphics.gw' not in b['core'])
  check(uid+' has no leftover GM III weapons',not any(x in b['core'] for x in ['EF_RGM_86R_','EF_GMRifle','EF_HypeBazookaKai_0087']))
  check(uid+' contains no weapon Fire_Step overrides',not any('_Fire_Step_' in n for n in b))
  check(uid+' preserves initial base stats',hashlib.sha256(b['hiddenAction_InitializeStats'].encode()).hexdigest()==report['initialize_stats_sha256_before'][uid])
  check(uid+' keeps its faction pilot',('Pilot_0093_EFSF_N_C_A' if uid=='RGM_89' else 'Pilot_0093_NZN_N_C_A') in b['hiddenAction_InitializeAddPilot_Default'])
 def active(b,w,d,r,e=0):
  v=b['hiddenAction_'+w+'_Trigger'].split('requireConditional:',1)[1].replace(chr(34)*3,'').strip()[3:]
  v=' '.join(v.split())
  for old,new in [('distanceBetween(self,self.attacking)',str(d)),('eventData("RandomWeapon",type="float")',str(r)),('memory.finalAttackRange','600'),('self.resource().EquipmentIndex',str(e)),('false','False'),('true','True')]:v=v.replace(old,new)
  return bool(eval(v,{'__builtins__':{}},{}))
 ranges=[0,60,60.01,299.99,300,300.01,600,600.01];rolls=[0,10,10.01,15,15.01,30,30.01,35,35.01,100]
 jw=['EF_RGM_89_BR','EF_RGM_89_BZ','EF_RGM_89_ShieldMS','EF_RGM_89_CrotchGL_L','EF_RGM_89_Decoy']
 gw=['NZN_AMS_119_BR_WGL','NZN_AMS_119_BR_GL','NZN_AMS_119_SeaSerpent','NZN_AMS_119_Panzerfaust']
 check('Jegan random intervals and both equipment sets are complete/exclusive',all(sum(active(units['RGM_89'],w,d,r,e) for w in jw)==int(60<d<=600) for d,r,e in itertools.product(ranges,rolls,[0,1,2])))
 check('Geara Doga random intervals are complete/exclusive at the sea-serpent range boundary',all(sum(active(units['AMS_119'],w,d,r,e) for w in gw)==int(60<d<=600) for d,r,e in itertools.product(ranges,rolls,[0,1,2])))
 check('sea serpent is selected only at 60 < distance <= 300 and roll <= 10',all(active(units['AMS_119'],'NZN_AMS_119_SeaSerpent',d,r)==(60<d<=300 and r<=10) for d,r in itertools.product(ranges,rolls)))
 check('Jegan uses real BR/BZ equipment options',all('action_Set_Equipment'+str(n) in units['RGM_89'] for n in [0,1]) and 'action_Set_Equipment2' not in units['RGM_89'])
 check('Geara Doga has no inherited Federation equipment switch',not any(n.startswith('action_Set_Equipment') for n in units['AMS_119']))
 refs=[];missing_ids=[];ids=set()
 for p in DLC.rglob('*.ini'):
  ids.update(m[1].strip() for m in re.finditer(r'(?m)^name:([^\r\n]+)',text(p)))
 for rel in report['weapons_created']:
  p=W/rel;t=text(p)
  for m in re.finditer(r'ROOT:[/\\]?([A-Za-z0-9_./\\ -]+?\.(?:png|ogg|ini|gw))',t):
   if not (DLC/m[1].replace('\\','/')).is_file():refs.append([rel,m[1]])
  for value in re.findall(r'(?ms)^spawnUnit:(?:"""(.*?)"""|([^\r\n]+))',t):
   for uid in re.findall(r'([A-Za-z_][A-Za-z_0-9]*)\*',value[0] or value[1]):
    if uid not in ids:missing_ids.append([rel,uid])
 check('all weapon file references resolve inside DLC0093',not refs)
 check('all spawned projectile entity IDs exist',not missing_ids)
 guards=[('Beam/EF_RGM_89_BR.gw','EF_RGM_89_BR','armRBreaked'),('Shell/EF_RGM_89_BZ.gw','EF_RGM_89_BZ','armRBreaked'),('Shell/EF_RGM_89_ShieldMS.gw','EF_RGM_89_ShieldMS','armLBreaked'),('Cqb/EF_RGM_89_BeamSaber_AF.gw','EF_RGM_89_BeamSaber_AF','armRBreaked'),('Beam/NZN_AMS_119_BR_WGL.gw','NZN_AMS_119_BR_WGL','armRBreaked'),('Shell/NZN_AMS_119_BR_GL.gw','NZN_AMS_119_BR_GL','armRBreaked'),('Cqb/NZN_AMS_119_BeamHawk_AF.gw','NZN_AMS_119_BeamHawk_AF','armRBreaked'),('Cqb/NZN_AMS_119_SeaSerpent.gw','NZN_AMS_119_SeaSerpent','armLBreaked'),('Shell/NZN_AMS_119_Panzerfaust.gw','NZN_AMS_119_Panzerfaust','armLBreaked')]
 for rel,w,part in guards:
  b=blocks(text(W/rel))
  check(w+' keeps component guards inside weapon Fire/shot steps','memory.'+part+'==false' in b['hiddenAction_'+w+'_Fire'] and all('memory.'+part+'==false' in body or '@copyFromSection:' in body for n,body in b.items() if n.startswith('hiddenAction_'+w+'_Fire_Step_') and not n.endswith('_Final')))
 source=Path(report['source_mod'])
 check('imported artwork matches source bytes',all((source/a['source']).read_bytes()==(DLC/a['target']).read_bytes() for a in report['artwork']))
 sea=blocks(text(W/'Cqb/NZN_AMS_119_SeaSerpent.gw'));projectile=blocks(text(W/'Cqb/Projectile/Projectile_NZN_AMS_119_SeaSerpent.ini'))
 check('sea serpent uses native left-arm animation and left launch anchor','Common_Melee_B_L.gw' in sea['core'] and 'barrelX:-11' in sea['turret_NZN_AMS_119_SeaSerpent'] and 'basePositionFromLegEnd:arm3' in sea['decal_DrawLineTo_NZN_AMS_119_SeaSerpent_Unit'])
 check('sea serpent red image and callback are wired consistently','NZN_AMS_119_SeaSerpent_Red.png' in projectile['decal_Projectile_Image'] and 'RodSpawn_NZN_AMS_119_SeaSerpent' in projectile['hiddenAction_Send_RodSpawn'] and 'RodSpawn_NZN_AMS_119_SeaSerpent' in sea['hiddenAction_Get_Spawn_NZN_AMS_119_SeaSerpent'])
 check('sea serpent native hit pipeline carries stun and slow','|StunDamage=3' in sea['projectile_NZN_AMS_119_SeaSerpent_Projectile'] and '|SpeedDownDamage=3' in sea['projectile_NZN_AMS_119_SeaSerpent_Projectile'] and 'alsoTriggerAction:' in blocks(text(W/'Template/Shoot_RodProjectile_Cqb.ini'))['hiddenAction_AttackTarget'])
 panzer=blocks(text(W/'Shell/NZN_AMS_119_Panzerfaust.gw'))
 check('Panzerfaust queues both left-hand shots','NZN_AMS_119_Panzerfaust_Fire_Step_3,' in panzer['hiddenAction_NZN_AMS_119_Panzerfaust_B1_Step_1'] and '@copyFromSection:hiddenAction_NZN_AMS_119_Panzerfaust_Fire_Step_2' in panzer['hiddenAction_NZN_AMS_119_Panzerfaust_Fire_Step_3'])
 for uid,f in [('RGM_89','0093_EFSF'),('AMS_119','0093_NZN')]:
  prod=blocks(text(DLC/f'Units/Buildings/Factory/UnitList/{f}/Units/Land/{uid}.gw'))
  check(uid+' preserves three-step pilot rolls and real squad production',all('produceUnits:' in prod['hiddenAction_Produce_'+uid+'_StandardSquad_'+str(n)] for n in [1,2,3]) and all('buildSpeed:1.0s' in prod['hiddenAction_Produce_'+uid+'_StandardSquad_'+str(n)] for n in [2,3]))
  check(uid+' hides invalid old MG squad','isVisible:false' in prod['action_Produce_'+uid+'_MGSquad'])
 check('beam machine gun and underbarrel grenade use the external weapon muzzle',all('barrelX:12' in blocks(text(W/rel))['turret_'+name] and 'barrelY:28' in blocks(text(W/rel))['turret_'+name] for rel,name in [('Beam/NZN_AMS_119_BR_WGL.gw','NZN_AMS_119_BR_WGL'),('Shell/NZN_AMS_119_BR_GL.gw','NZN_AMS_119_BR_GL')]))
 check('Geara Doga body has no old GM III image references', 'RGM_86R_0093_EFSF/Image' not in text(DLC/'Units/BattleUnits/AMS_119/AMS_119.ini'))
 check('all Geara Doga body image references resolve',all((DLC/m[1].replace('\\','/')).is_file() for m in re.finditer(r'ROOT:[/\\]?([A-Za-z0-9_./\\ -]+?\.png)',text(DLC/'Units/BattleUnits/AMS_119/AMS_119.ini'))))
 report={'checks':len(results),'passed':sum(x['passed'] for x in results),'results':results,'gameplay_tested':False}
 (ANALYSIS/'0093_杰刚基拉多加武装验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f"{report['passed']}/{report['checks']} checks passed")
 return int(report['checks']!=report['passed'])

if __name__=='__main__':raise SystemExit(main())
