"""Read-only checks for the RGZ_91 BWS -> MS conversion contract."""
from pathlib import Path
import json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from 验证_0093骨架 import ROOT,DLC,MAIN,ANALYSIS,text,blocks

def main():
 results=[]
 def check(name,value):
  results.append({'check':name,'passed':bool(value)})
  print(('PASS ' if value else 'FAIL ')+name,flush=True)
 root=DLC/'Units/BattleUnits/RGZ_91'
 ma=text(root/'RGZ_91_MA.ini');ms=text(root/'RGZ_91.ini');over=text(root/'RGZ_91_MA_OverLine.ini')
 m=blocks(ma);h=blocks(ms);o=blocks(over)
 exit_template=blocks(text(DLC/'Template/Unit/Skill/ExitUnit.gw'))
 framework=blocks(text(DLC/'Template/Unit/BattleUnit_Framework.ini'))
 core=blocks(text(DLC/'Template/Unit/BattleUnitCore.ini'))
 check('MSZ_006-style names resolve to distinct MS/MA/OverLine entities',all('name:'+uid in body['core'] for uid,body in [('RGZ_91',h),('RGZ_91_MA',m),('RGZ_91_MA_OverLine',o)]))
 check('MA forms retain the research/factory family tag',all('RGZ_91,' in body['core'] for body in [m,o]))
 check('MA has native AIR movement', 'FlyUnit_Fighter.gw' in ma and 'movementType: AIR' in text(DLC/'Template/Unit/Skill/FlyUnit_Fighter.gw'))
 check('MA sets flight stats and human explicitly clears flight state','flyUnit=1' in m['hiddenAction_InitializeStats'] and 'flyUnit=0' in h['hiddenAction_InitializeStats'] and 'baseHeight=1,' in h['hiddenAction_InitializeStats'])
 check('DedicatedMap adapter changes collision/movement without a new combat form','disableAllUnitCollisions:true' in o['core'] and 'movementType:OVER_CLIFF_WATER' in o['movement'] and 'convertTo:RGZ_91_MA_OverLine' in m['hiddenAction_TurnToOverLine_T'] and 'convertTo:RGZ_91_MA' in m['hiddenAction_TurnToOverLine_F'])
 check('aircraft has only requested BWS weapon templates and no inherited GM III armament','canAttack:true' in m['attack'] and 'EF_RGZ_91_BWS_DBC.gw' in m['core'] and 'EF_RGZ_91_BWS_DMS.gw' in m['core'] and 'HighBeamCannon' not in m['core'] and 'RGM_86R_0093_EFSF_Base.gw' not in m['core'])
 check('BWS sprite is on the reference arm15 anchor','RGZ_91_BWS_1.png' in m['decal_MA'] and 'basePositionFromLegEnd:arm15' in m['decal_MA'])
 check('all human body and shield layers are hidden on the aircraft',all('isVisible:false' in m['decal_'+part] for part in ['Crotch','Body','ArmL','ArmR','ShoulderL','ShoulderR','Head','Head_Close','Eye','LeftFoot','LeftLeg','RightFoot','RightLeg','Shield']))
 check('ExitUnit shared action and staged message path remain in use','ROOT:Template/Unit/Skill/ExitUnit.gw' in m['core'] and 'ExitUnit_Send' in exit_template['action_ExitUnit'] and 'sendMessageWithTags:TryExitUnit' in exit_template['hiddenAction_ExitUnit_Send'] and 'newMessage(withTag="TryExitUnit")' in exit_template['hiddenAction_ExitUnit_Step2'])
 check('purge converts the existing unit to the human form','convertTo:RGZ_91' in m['hiddenAction_ExitUnit_Step2'] and 'convertTo_keepCurrentTags:false' in exit_template['hiddenAction_ExitUnit_Step2'])
 check('purge clears queued actions and retains the core state-transfer path','Send_TryClearQueued,Send_TryTransform_ExitUnit' in exit_template['hiddenAction_ExitUnit_Step2'] and '@copyFromSection:hiddenAction_Send_TryTransform' in exit_template['hiddenAction_Send_TryTransform_ExitUnit'] and 'sendMessageTo:memory.battleUnitCore' in framework['hiddenAction_Send_TryTransform'])
 check('core forwards Transform and the destination recomputes stats','newMessage(withTag="TryTransform")' in core['hiddenAction_SetTransform'] and 'sendMessageWithTags:Transform' in core['hiddenAction_SetTransform_Step2'] and 'InitializeCommonStatsBefore,InitializeStats,InitializeCommonStatsAfter' in framework['hiddenAction_Get_Transform'])
 check('pilot initialization is not repeated by the transform path','InitializeAddPilot' not in framework['hiddenAction_Get_Transform'] and 'addUnitsIntoTransport' not in m['hiddenAction_ExitUnit_Step2'])
 check('recovery ratios match the FA_78_1 purge example',all(field in m['hiddenAction_Send_TryTransform_ExitUnit'] for field in ['RecoverHpPer=0.35','RecoverEnPer=0.35','RecoverShieldPer=0','ResetTags=1','ChangeType=0']))
 check('purge shows discarded BWS and a valid decoy','RGZ_91_BWS_2.png' in m['effect_breakedExitUnit0_A'] and 'Common_ExitDecoy*1' in m['action_ExitUnit'] and (MAIN/'Units/CommonUnit/SP/Common_ExitDecoy.ini').is_file())
 check('human has no reverse BWS action or template','Transform_LandFly' not in ms and not re.search(r'convertTo:RGZ_91_MA\b',ms) and 'ExitUnit.gw' not in ms)
 check('OverLine inherits the same one-way exit','copyFrom:ROOT:Units/BattleUnits/RGZ_91/RGZ_91_MA.ini' in o['core'])
 prod=text(DLC/'Units/Buildings/Factory/UnitList/0093_EFSF/Units/Land/RGZ_91.gw')
 check('production keeps the human family UI/unlock ID','@define UnitID=RGZ_91' in prod and 'RGZ_91_MA.gw' not in prod)
 check('all existing squad steps produce MA with original pilot/equipment data',prod.count('RGZ_91_MA*1(addResources=PilotType:1101|EquipmentIndex:')==9 and 'RGZ_91*1(' not in prod and len(re.findall(r'buildSpeed:1\.0s',prod))==6)
 for category in ['Land','Space']:
  content=text(DLC/f'Units/Buildings/Factory/UnitList/0093_EFSF/0093_EFSF_UnitList_{category}.ini')
  check(category+' continues to register the RGZ_91 family definition','Units/Land/RGZ_91.gw' in content)
 missing=[]
 for p in root.glob('*'):
  if p.suffix not in {'.ini','.gw'}:continue
  for match in re.finditer(r'ROOT:[/\\]?([A-Za-z0-9_./\\ -]+?\.(?:png|ogg|ini|gw))',text(p)):
   if not (DLC/match[1].replace('\\','/')).is_file():missing.append(match[1])
 check('all concrete RGZ body, BWS and template references resolve inside DLC0093',not missing)
 report={'checks':len(results),'passed':sum(x['passed'] for x in results),'results':results,'gameplay_tested':False}
 (ANALYSIS/'0093_灵格斯BWS验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f"{report['passed']}/{report['checks']} checks passed")
 return 0 if report['checks']==report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
