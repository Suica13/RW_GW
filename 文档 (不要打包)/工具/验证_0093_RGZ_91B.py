"""Read-only integration checks for RGZ_91B. Does not simulate combat."""
from pathlib import Path
import hashlib,itertools,json,re,subprocess
from 验证_0093骨架 import ROOT,DLC,ANALYSIS,text,blocks

def main():
 out=[]
 def check(n,v):
  out.append({'name':n,'passed':bool(v)});print(('PASS ' if v else 'FAIL ')+n)
 data=json.loads(text(ANALYSIS/'0093_RGZ_91B移植来源.json'));E=Path(data['source_mod'])
 U=DLC/'Units/BattleUnits/RGZ_91B';W=DLC/'Units/BattleUnits/Weapon'
 h=blocks(text(U/'RGZ_91B.ini'));m=blocks(text(U/'RGZ_91B_MA.ini'));over=blocks(text(U/'RGZ_91B_MA_OverLine.ini'))
 paths=[DLC/p for p in data['created_config']]
 check('all imported body images retain source bytes and use underscores',len(data['assets'])==17 and all((E/a['source']).read_bytes()==(DLC/a['target']).read_bytes() and 'RGZ-91B' not in a['target'] for a in data['assets']))
 check('all new runtime identifiers and paths use underscores',all('RGZ-91' not in text(p) and 'RGZ-91' not in p.name for p in paths))
 check('MS has its own ID, tags and 0093 faction',all(x in h['core'] for x in ['name:RGZ_91B','tags:RGZ_91B,Unit,MS,EFSF,0093,UC,0093_EFSF']))
 check('MS and MA use standalone native framework with inline graphics',all('BattleUnit_Framework_MS.ini' in b['core'] and '_Base.gw' not in b['core'] and '_Graphics.gw' not in b['core'] for b in [h,m]))
 check('unit INIs never override weapon firing steps',not any('_Fire_Step_' in k for b in [h,m,over] for k in b))
 check('MS is editor selectable and uses independent placeholder icon','showInEditor:false' not in h['core'] and 'Resource/Image/Units/Icon/RGZ_91B.png' in h['graphics'] and (DLC/'Resource/Image/Units/Icon/RGZ_91B.png').is_file())
 check('only MS appears in editor',all('showInEditor:false' in b['core'] for b in [m,over]))
 check('both forms retain existing native 0093 ordinary pilot',all('Pilot_0093_EFSF_N_C_A' in b['hiddenAction_InitializeAddPilot_Default'] for b in [h,m]))
 check('MS body has source backpack and stowed sabers',all('RGZ_91B_'+n+'.png' in h['decal_'+n.replace('_1','')] for n in ['Backpack_BeamSaberL_1','Backpack_BeamSaberR_1']) and 'RGZ_91B_Backpack_1.png' in h['decal_Backpack_1'] and 'RGZ_91B_Backpack_2.png' in h['decal_Backpack_2'])
 check('waist cannon opens the alternate crotch sprite','nowSubWeaponIndex!=1' in h['decal_Crotch'] and 'nowSubWeaponIndex==1' in h['decal_Crotch_2'] and 'nowSubWeaponIndex=1' in h['hiddenAction_EF_RGZ_91B_CrotchBeamCannon_SetWeaponIndex'])
 check('other selected MS weapons close the waist cannon',all('nowSubWeaponIndex=0' in h[k] for k in ['hiddenAction_EF_RGZ_91B_BR_SetWeaponIndex','hiddenAction_Common_ArmGL_L_SetWeaponIndex','hiddenAction_EF_RGZ_91B_MS_SetWeaponIndex','hiddenAction_EF_RGZ_91B_BeamSaber_AF_Large_Yellow_A_SetWeaponIndex']))
 check('MA hides all human body parts and hand rifle',all('isVisible:false' in m['decal_'+n] for n in ['Crotch','Body','ArmL','ArmR','ShoulderL','ShoulderR','Head','Head_Close','LeftFoot','LeftLeg','RightFoot','RightLeg','Shield','EF_RGZ_91B_BR','EF_RGZ_91B_BR_NotUsing']))
 check('MA uses dedicated aircraft sprite and paired source exhausts','RGZ_91B_MA_1.png' in m['decal_MA'] and 'xOffsetRelative:10' in m['decal_Boost'] and 'xOffsetRelative:-10' in m['decal_Boost_MA'])
 check('both forms have reciprocal native transform targets',all('convertTo:RGZ_91B\n' in b['action_Transform_LandFlyA'] and 'convertTo:RGZ_91B_MA\n' in b['action_Transform_LandFlyB'] and 'Transform_LandFly_SFS_OFF.gw' in b['core'] for b in [h,m]))
 check('transform preserves HP/shield instead of BWS ejection','ExitUnit.gw' not in m['core'] and 'maxShield:8500' in h['core'] and 'maxShield:8500' in m['core'] and not any('RecoverHpPer=' in text(p) for p in U.glob('*.ini')))
 check('MS resets flight and MA resets aircraft state','flyUnit=0' in h['hiddenAction_InitializeStats'] and 'flyUnit=1' in m['hiddenAction_InitializeStats'] and 'lowEnDoNotAutoCqb=false' in h['hiddenAction_InitializeStats'] and 'lowEnDoNotAutoCqb=true' in m['hiddenAction_InitializeStats'])
 check('MA DedicatedMap routing remains bidirectional','convertTo:RGZ_91B_MA_OverLine' in m['hiddenAction_TurnToOverLine_T'] and 'convertTo:RGZ_91B_MA\n' in m['hiddenAction_TurnToOverLine_F'] and 'styleIndex=96' in m['hiddenAction_TurnToOverLine_F'] and 'movementType:OVER_CLIFF_WATER' in over['movement'])
 def active(b,w,d,r):
  s=b['hiddenAction_'+w+'_Trigger'].split('requireConditional:',1)[1].replace(chr(34)*3,'').strip()[3:];s=' '.join(s.split())
  for a,v in [('distanceBetween(self,self.attacking)',str(d)),('memory.finalAttackRange','600'),('eventData("RandomWeapon",type="float")',str(r))]:s=s.replace(a,v)
  return bool(eval(s,{'__builtins__':{}},{}))
 for label,b,weapons in [('MS',h,['EF_RGZ_91B_BR','Common_ArmGL_L','EF_RGZ_91B_CrotchBeamCannon','EF_RGZ_91B_MS']),('MA',m,['EF_RGZ_91B_HighBeamCannon','EF_RGZ_91_BWS_DBC','EF_RGZ_91B_MS'])]:
  check(label+' ranged random partitions are complete and exclusive',all(sum(active(b,w,d,r) for w in weapons)==int(60<d<=600) for d,r in itertools.product([0,60,60.01,300,600,600.01],[0,10,10.01,25,25.01,35,35.01,65,65.01,100])))
  check(label+' weapon selection defers firing requirements to weapons',all(not any(s in b['hiddenAction_'+w+'_Trigger'] for s in ['Breaked','_CDTimer','_Fire_Step_']) for w in weapons))
 names=['EF_RGZ_91B_BR','EF_RGZ_91B_CrotchBeamCannon','EF_RGZ_91B_HighBeamCannon','EF_RGZ_91B_MS']
 check('both forms import all shared cooldown declarations',all(n+'.gw' in b['core'] for n in names for b in [h,m]))
 br=blocks(text(W/'Beam/EF_RGZ_91B_BR.gw'));ms=blocks(text(W/'Shell/EF_RGZ_91B_MS.gw'));bc=blocks(text(W/'Beam/EF_RGZ_91B_CrotchBeamCannon.gw'));high=blocks(text(W/'Beam/EF_RGZ_91B_HighBeamCannon.gw'));saber=blocks(text(W/'Cqb/EF_RGZ_91B_BeamSaber_AF_Large_Yellow.gw'))
 check('rifle fires five shots with source burst spacing',br['hiddenAction_EF_RGZ_91B_BR_B2_Step_1'].count('Fire_Step_2')+br['hiddenAction_EF_RGZ_91B_BR_B2_Step_1'].count('Fire_Step_3')==5 and 'buildSpeed:0.075s' in br['hiddenAction_EF_RGZ_91B_BR_Fire_Step_3'])
 check('missiles fire twelve alternating left/right shots',ms['hiddenAction_EF_RGZ_91B_MS_B2_Step_1'].count('Fire_Step_2')==6 and ms['hiddenAction_EF_RGZ_91B_MS_B2_Step_1'].count('Fire_Step_3')==6 and 'barrelX:16' in ms['turret_EF_RGZ_91B_MS'] and 'barrelX:-17' in ms['turret_EF_RGZ_91B_MS_L'])
 check('waist cannon fires both source positions','barrelX:12' in bc['turret_EF_RGZ_91B_CrotchBeamCannon'] and 'barrelX:-12' in bc['turret_EF_RGZ_91B_CrotchBeamCannon_L'] and 'alsoTriggerAction:EF_RGZ_91B_CrotchBeamCannon_Fire_Step_Sub' in bc['hiddenAction_EF_RGZ_91B_CrotchBeamCannon_Fire_Step_3'])
 for b,n,part in [(br,names[0],'armRBreaked'),(bc,names[1],'backpackBreaked'),(high,names[2],'backpackBreaked'),(ms,names[3],'backpackBreaked'),(saber,'EF_RGZ_91B_BeamSaber_AF_Large_Yellow','armRBreaked')]:
  check(n+' guards its component during firing',all('memory.'+part+'==false' in v for k,v in b.items() if k=='hiddenAction_'+n+'_Fire' or k.startswith('hiddenAction_'+n+'_Fire_Step_') and not k.endswith('Final')))
 check('high cannon recreates its native charge attachment after conversion','UnitTurretSpawn' in high['hiddenAction_EF_RGZ_91B_HighBeamCannon_ChargeEffect_1_AwakeSet'] and 'Beam_Charge_1_EffectUnit' in high['hiddenAction_EF_RGZ_91B_HighBeamCannon_ChargeEffect_1_AwakeSet'] and 'requireConditional:false' in h['hiddenAction_EF_RGZ_91B_HighBeamCannon_ChargeEffect_1_AwakeSet'])
 check('high cannon uses native yellow beam and paired effect projectile','Projectile_HighBeamCannon_Yellow*1' in high['projectile_EF_RGZ_91B_HighBeamCannon_Projectile'] and 'Projectile_HighBeamCannon_Yellow_Effect*1' in high['projectile_EF_RGZ_91B_HighBeamCannon_Projectile'])
 check('charge queue releases turning and attack locks','SetAttackingCantTurnOn,' in high['hiddenAction_EF_RGZ_91B_HighBeamCannon_B1_Step_1'] and 'SetAttackingCantTurnOff,' in high['hiddenAction_EF_RGZ_91B_HighBeamCannon_B1_Step_1'] and 'SetAttackingOff' in high['hiddenAction_EF_RGZ_91B_HighBeamCannon_Fire_Step_Final'])
 check('large yellow saber uses native large melee projectiles and yellow effects','Projectile_Saber_L_A*1' in saber['projectile_EF_RGZ_91B_BeamSaber_AF_Large_Yellow_A_Projectile'] and 'Cqb_Fire_1_Yellow_R.gw' in saber['core'] and 'imageScaleY:1.35' in saber['decal_EF_RGZ_91B_BeamSaber_AF_Large_Yellow'])
 missing=[]
 for p in paths:
  for a in re.findall(r'ROOT:[/\\]?([^\n,\r]+?\.(?:gw|ini|png|ogg))',text(p)):
   if not (DLC/a.replace('\\','/')).is_file():missing.append([str(p),a])
 check('all concrete file references resolve in this DLC',not missing)
 check('source rifle artwork is already byte identical',(E/'Units/BattleUnits/Weapon/Beam/Image/EF_RGZ_91B_BR.png').read_bytes()==(W/'Beam/Image/EF_RGZ_91B_BR.png').read_bytes())
 check('no RGZ_91B tech or factory registrations exist',not any('RGZ_91B' in text(p) for folder in ['Units/TechTree','Units/Buildings/Factory'] for p in (DLC/folder).rglob('*') if p.suffix in ['.ini','.gw']))
 report={'checks':len(out),'passed':sum(i['passed'] for i in out),'results':out,'gameplay_tested':False}
 (ANALYSIS/'0093_RGZ_91B验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(str(report['passed'])+'/'+str(report['checks'])+' checks passed')
 return int(report['passed']!=report['checks'])

if __name__=='__main__':raise SystemExit(main())
