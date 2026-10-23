"""Read-only checks for Re-GZ weapon integration; does not simulate a battle."""
from pathlib import Path
import itertools,json,re
from 验证_0093骨架 import ROOT,DLC,ANALYSIS,text,blocks

def main():
 results=[]
 def check(name,ok):
  results.append({'name':name,'passed':bool(ok)})
  print(('PASS ' if ok else 'FAIL ')+name)
 unit=DLC/'Units/BattleUnits/RGZ_91';weapons=DLC/'Units/BattleUnits/Weapon'
 human=blocks(text(unit/'RGZ_91.ini'));plane=blocks(text(unit/'RGZ_91_MA.ini'))
 check('human no longer inherits GM III weapon/equipment definitions','RGM_86R_0093_EFSF_Base.gw' not in human['core'])
 check('human uses native framework, inline graphics and yellow saber',all(x in human['core'] for x in ['BattleUnit_Framework_MS.ini','EF_RGZ_91_BeamSaber_AF_Yellow.gw']) and 'RGZ_91_Body_1.png' in human['decal_Body'])
 check('deferred weapons remain absent',not any(x in human['core']+plane['core'] for x in ['ChargetFI','HighBeamCannon']))
 check('plane uses only BWS ranged weapons',all(x in plane['core'] for x in ['EF_RGZ_91_BWS_DBC.gw','EF_RGZ_91_BWS_DMS.gw']) and '/Cqb/' not in plane['core'])
 check('low EN behavior resets across ejection','lowEnDoNotAutoCqb=true' in plane['hiddenAction_InitializeStats'] and 'lowEnDoNotAutoCqb=false' in human['hiddenAction_InitializeStats'])
 def active(body,weapon,distance,roll,right=False,left=False,back=False):
  s=body['hiddenAction_'+weapon+'_Trigger'].split('requireConditional:',1)[1].replace(chr(34)*3,'').strip()[3:].strip()
  s=' '.join(s.split()).replace('${onAttacking}','False')
  for a,b in [('distanceBetween(self,self.attacking)',repr(distance)),('memory.finalAttackRange','600'),('eventData("RandomWeapon",type="float")',repr(roll)),('memory.armRBreaked',str(right)),('memory.armLBreaked',str(left)),('memory.backpackBreaked',str(back)),('false','False'),('true','True')]:s=s.replace(a,b)
  return bool(eval(s,{'__builtins__':{}},{}))
 human_ranged=['EF_RGZ_91_BR','Common_ArmGL_L','EF_RGZ_91_CrotchGL_L','EF_RGZ_91_Decoy']
 coverage=True
 for d,r,ar,al in itertools.product([0,60,60.01,300,600,600.01],[0,10,15,15.01,35,35.01,100],[False,True],[False,True]):
  picks=[w for w in human_ranged if active(human,w,d,r,ar,al)]
  coverage &= len(picks)<=int(60<d<=600)
  if not(ar or al):coverage &= len(picks)==int(60<d<=600)

 check('unit ranged rolls are exclusive and independent of weapon firing guards',coverage)
 check('melee saber selection uses the reference close range',all(active(human,'EF_BeamSaber_AF_Yellow',d,0)==(d<=60) for d in [0,60,60.01,600]))
 check('BWS unit random rolls cover both weapons without overlap',all(sum(active(plane,w,d,r,back=b) for w in ['EF_RGZ_91_BWS_DBC','EF_RGZ_91_BWS_DMS'])==int(60<d<=600) for d,r,b in itertools.product([0,60,60.01,600,601],[0,35,35.01,100],[False,True])))
 files=[weapons/p for p in ['Beam/EF_RGZ_91_BR.gw','Beam/EF_RGZ_91_BWS_DBC.gw','Shell/EF_RGZ_91_BWS_DMS.gw','Shell/EF_RGZ_91_CrotchGL_L.gw','Shell/EF_RGZ_91_Decoy.gw','Shell/Projectile/Projectile_Decoy_RGZ_91.ini']]
 missing=[]
 for f in files+list(unit.glob('*.ini'))+list(unit.glob('*.gw')):
  for m in re.finditer(r'ROOT:[/\\]?([A-Za-z0-9_./\\ -]+?\.(?:png|ogg|ini|gw))',text(f)):
   if not (DLC/m[1].replace('\\','/')).is_file():missing.append((str(f),m[1]))
 check('weapon/body/effect/sound/animation file references resolve inside DLC0093',not missing)
 br=blocks(text(files[0]));dbc=blocks(text(files[1]));dms=blocks(text(files[2]));decoy=blocks(text(files[-1]))
 check('beam rifle and BWS beams use yellow native projectiles','Projectile_AP_BeamRifle_Yellow' in br['projectile_EF_RGZ_91_BR_Projectile'] and 'Projectile_BeamGun_Yellow' in dbc['projectile_EF_RGZ_91_BWS_DBC_Projectile'])
 check('BWS fires paired missiles from the reference wing positions','barrelX:35' in dms['turret_EF_RGZ_91_BWS_DMS'] and 'barrelX:-37' in dms['turret_EF_RGZ_91_BWS_DMS_L'])
 check('queued BWS shots stop if the backpack breaks',all('memory.backpackBreaked==false' in b['hiddenAction_'+w+'_Fire_Step_'+str(n)] for b,w in [(dbc,'EF_RGZ_91_BWS_DBC'),(dms,'EF_RGZ_91_BWS_DMS')] for n in [1,2,3]))
 check('queued rifle shots stop if the right arm breaks',all('memory.armRBreaked==false' in br['hiddenAction_EF_RGZ_91_BR_Fire_Step_'+str(n)] for n in [1,2,3]))
 check('human launcher and saber queues guard their own arms',all('memory.armLBreaked==false' in blocks(text(weapons/'Shell/EF_RGZ_91_ArmGL_L.gw'))['hiddenAction_Common_ArmGL_L_Fire_Step_'+str(n)] for n in [1,2,3]) and all('memory.armRBreaked==false' in blocks(text(weapons/'Cqb/EF_RGZ_91_BeamSaber_AF_Yellow.gw'))['hiddenAction_EF_BeamSaber_AF_Yellow_Fire_Step_'+str(n)] for n in range(1,6)))
 check('decoy intercept resolves the projectile and bursts using native handshake','newMessage(withTag="TryDamage")' in decoy['hiddenAction_Decoy_Intercept'] and 'sendMessageWithTags:DoDamage' in decoy['hiddenAction_Decoy_Intercept'] and 'alsoTriggerAction:AttackTarget' in decoy['hiddenAction_Decoy_Intercept'])
 check('decoy uses a native explosive lifecycle and no foreign memory framework','Shoot_ExplosionProjectile_Shell.ini' in decoy['core'] and 'Common_GetDamage.ini' not in text(files[-1]))
 source=Path(r'E:/RustedWarfare_Reunion/mods/GundamWars_BattleOperation2_V5')
 check('imported rifle/shield/decoy PNG files are byte identical to references',all((source/a).read_bytes()==(DLC/b).read_bytes() for a,b in [('Units/BattleUnits/Weapon/Beam/Image/EF_RGZ_91_BR.png','Units/BattleUnits/Weapon/Beam/Image/EF_RGZ_91_BR.png'),('Units/BattleUnits/Shield/EF_RGZ_91_Shield_B.png','Units/BattleUnits/Shield/EF_RGZ_91_Shield_B.png'),('Resource/Image/Bullet/Sp/EF_Decoy_RGM_89.png','Resource/Image/Bullet/Sp/EF_Decoy_RGZ_91.png')]))
 prod=blocks(text(DLC/'Units/Buildings/Factory/UnitList/0093_EFSF/Units/Land/RGZ_91.gw'))
 check('factory offers only the real loadout while keeping old queued IDs',all('isVisible:false' in prod['action_Produce_RGZ_91_'+n] for n in ['MGSquad','BazookaSquad']) and all('alsoQueueAction:Produce_RGZ_91_StandardSquad' in prod['hiddenAction_AutoProduce_RGZ_91_Random_'+n] for n in ['A','B','C']))
 check('all nine new units use standalone INIs without Base/Graphics wrappers',all('BattleUnit_Framework_MS.ini' in blocks(text(DLC/f'Units/BattleUnits/{uid}/{uid}.ini'))['core'] and '_Base.gw' not in blocks(text(DLC/f'Units/BattleUnits/{uid}/{uid}.ini'))['core'] and '_Graphics.gw' not in blocks(text(DLC/f'Units/BattleUnits/{uid}/{uid}.ini'))['core'] for uid in ['RGM_89','RGC_90','RGZ_91','RX_93','RX_93_Test','AMS_119','AMS_119H','MSN_03','MSN_04']))
 decoy_weapon=blocks(text(weapons/'Shell/EF_RGZ_91_Decoy.gw'))
 check('decoy follows normal SetAttacking/queue/final-unlock firing pattern','fireTurretXAtGround:' not in decoy_weapon['hiddenAction_EF_RGZ_91_Decoy_Fire'] and 'SetAttackingOn,' in decoy_weapon['hiddenAction_EF_RGZ_91_Decoy_Fire'] and 'alsoQueueAction:' in decoy_weapon['hiddenAction_EF_RGZ_91_Decoy_B2_Step_1'] and 'SetAttackingOff' in decoy_weapon['hiddenAction_EF_RGZ_91_Decoy_Fire_Step_Final'])
 reference=blocks(text(ROOT/'GW_BattleUniverse_DLC_0087/Units/BattleUnits/MSZ_006/MSZ_006.ini'))
 check('rifle uses MSZ_006 primary-weapon random threshold', 'eventData("RandomWeapon",type="float")>25' in human['hiddenAction_EF_RGZ_91_BR_Trigger'] and 'eventData("RandomWeapon",type="float")>25' in reference['hiddenAction_AEUG_MSZ_006_BR_Trigger'])
 check('unit INIs have no weapon Fire Step overrides',not any(re.search(r'^\[hiddenAction_.*_Fire_Step_',text(f),re.M) for f in unit.glob('*.ini')))
 check('component firing requirements live in weapon Fire sections',all('memory.'+part+'==false' in blocks(text(weapons/rel))['hiddenAction_'+name+'_Fire'] for rel,name,part in [('Beam/EF_RGZ_91_BR.gw', 'EF_RGZ_91_BR', 'armRBreaked'), ('Shell/EF_RGZ_91_ArmGL_L.gw', 'Common_ArmGL_L', 'armLBreaked'), ('Cqb/EF_RGZ_91_BeamSaber_AF_Yellow.gw', 'EF_BeamSaber_AF_Yellow', 'armRBreaked'), ('Shell/EF_RGZ_91_Decoy.gw', 'EF_RGZ_91_Decoy', 'armLBreaked'), ('Beam/EF_RGZ_91_BWS_DBC.gw', 'EF_RGZ_91_BWS_DBC', 'backpackBreaked'), ('Shell/EF_RGZ_91_BWS_DMS.gw', 'EF_RGZ_91_BWS_DMS', 'backpackBreaked')]))
 report={'checks':len(results),'passed':sum(x['passed'] for x in results),'results':results,'runtime_combat_tested':False}
 (ANALYSIS/'0093_灵格斯武装验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f"{report['passed']}/{report['checks']} checks passed")
 return int(report['passed']!=report['checks'])

if __name__=='__main__':raise SystemExit(main())
