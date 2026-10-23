"""Read-only checks: dedicated icons, conventional Nu Test and Bruno heavy loadout."""
from pathlib import Path
import re,json,hashlib,itertools
from 验证_0093骨架 import ROOT,DLC,ANALYSIS,text,blocks

def main():
 out=[]
 def check(n,v):
  out.append({'name':n,'passed':bool(v)});print(('PASS ' if v else 'FAIL ')+n)
 data=json.loads((ANALYSIS/'0093_占位图标_Test与重装基拉多加.json').read_text(encoding='utf-8-sig'));E=Path(data['source_mod']);W=DLC/'Units/BattleUnits/Weapon'
 icons=[]
 for a in data['icons']:
  p=DLC/a['target'];uid=a['unit'];b=blocks(text(DLC/f'Units/BattleUnits/{uid}/{uid}.ini'));icons.append(p)
  check(uid+' owns a dedicated PNG icon',p.is_file() and p.name==uid+'.png' and p.read_bytes().startswith(b'\x89PNG'))
  check(uid+' references its own icon','icon_build:ROOT:'+a['target'] in b['graphics'] and 'RGM_86R.png' not in b['graphics'])
 check('all nine placeholder icons are independent files and distinct images',len(set(icons))==9 and len({hashlib.sha256(p.read_bytes()).hexdigest() for p in icons})==9)
 check('Re-GZ MA uses its family icon','Resource/Image/Units/Icon/RGZ_91.png' in text(DLC/'Units/BattleUnits/RGZ_91/RGZ_91_MA.ini'))
 testpath=DLC/'Units/BattleUnits/RX_93_Test/RX_93_Test.ini';test=blocks(text(testpath));t=text(testpath)
 check('Nu Test retains its own name and tags','name:RX_93_Test' in test['core'] and 'tags:RX_93_Test,' in test['core'])
 check('Nu Test has no funnel imports/actions/backpack decal','/Funnel/' not in test['core'] and not any('Funnel' in n or n=='decal_Body_FF' for n in test))
 check('Nu Test has no barrier runtime','GNField' not in t and 'FieldShield' not in t and 'RX_93_FFS_' not in t)
 check('Nu Test keeps Nu conventional weapons',all(w in test['core'] for w in ['EF_RX_93_BR.gw','EF_RX_93_BZ.gw','EF_RX_93_ShieldBC.gw','EF_RX_93_ShieldMS.gw','EF_RX_93_BeamSaber_BF.gw','Common_DoubleVulcan_MS_Lv3.gw']))
 check('Nu Test uses Nu body without duplicate bazooka stow','RX_93_Body_1.png' in test['decal_Body'] and 'decal_Body_BZ' in test and 'decal_EF_RX_93_BZ_NotUsing' not in test)
 hpath=DLC/'Units/BattleUnits/AMS_119H/AMS_119H.ini';h=blocks(text(hpath))
 for uid,b in [('RX_93_Test',test),('AMS_119H',h)]:
  check(uid+' preserves initial stats',hashlib.sha256(b['hiddenAction_InitializeStats'].encode()).hexdigest()==data['initial_stats'][uid])
  check(uid+' keeps standalone layout with no weapon Step overrides','BattleUnit_Framework_MS.ini' in b['core'] and '_Base.gw' not in b['core'] and not any('_Fire_Step_' in n for n in b))
 check('heavy unit matches source HWT body and weapons','AMS_119_Body_2.png' in h['decal_Body'] and all(w in h['core'] for w in ['NZN_AMS_119H_BrunoGun.gw','NZN_AMS_119H_BR.gw','NZN_AMS_119H_BeamSaber_AF.gw','NZN_AMS_119H_Panzerfaust.gw']))
 check('heavy unit has no sea serpent or underbarrel GL','SeaSerpent' not in h['core'] and '_BR_GL.gw' not in h['core'])
 check('heavy unit uses imported body and source eye offsets','RGM_86R_0093_EFSF/Image' not in text(hpath) and 'yOffsetRelative:2.5' in h['decal_Eye'])
 name='NZN_AMS_119H_BrunoGun';gun=blocks(text(W/f'Shell/{name}.gw'));shell=blocks(text(W/'Shell/Projectile/Projectile_NZN_AMS_119H_BrunoShell.ini'))
 check('Bruno uses original two-handed animation, cannon flash and source muzzle', 'Common_Shoot_Two_Handed_A.gw' in gun['core'] and 'Cannon_Fire_1.gw' in gun['core'] and 'barrelX:14' in gun['turret_'+name] and 'barrelY:38' in gun['turret_'+name] and 'shoot_flame:Cannon_Fire_1' in gun['turret_'+name])
 check('Bruno prefire flash and full attack queue remain in weapon','spawnEffects:Flash_1_S' in gun['hiddenAction_'+name+'_B1_Step_1'] and 'SetAttackingOn,' in gun['hiddenAction_'+name+'_Fire'] and 'alsoTriggerAction:SetAttackingOff' in gun['hiddenAction_'+name+'_Fire_Step_Final'])
 check('Bruno checks both arms/backpack inside weapon Fire and shot steps',all(all('memory.'+part+'==false' in b for part in ['armLBreaked','armRBreaked','backpackBreaked']) for b in [gun['hiddenAction_'+name+'_Fire'],gun['hiddenAction_'+name+'_Fire_Step_1'],gun['hiddenAction_'+name+'_Fire_Step_2']]))
 check('Bruno holds still for windup, shot and recovery',all('whenBuilding_cannotMove:true' in gun['hiddenAction_'+name+'_Fire_Step_'+step] for step in ['1','2','Final']))
 check('Bruno launches the dedicated large rail shell','Projectile_NZN_AMS_119H_BrunoShell*1' in gun['projectile_'+name+'_Projectile'])
 check('large shell keeps native explosion/trail/rail image/push',all(x in shell['core'] for x in ['Shoot_ExplosionProjectile_Shell.ini','RocketTrailLine_1.gw','Explosion_Hit_2.gw']) and 'RailShell_1.png' in shell['decal_Projectile_Image'] and 'imageScale:1.35' in shell['decal_Projectile_Image'] and 'pushForce:2250' in shell['projectile_Hit_Effect'])
 check('Bruno uses real OGG audio',(DLC/'Resource/Sound/SE/Weapon/Fire/RailGun_2.ogg').read_bytes().startswith(b'OggS'))
 check('green saber sprite and effects are real native assets','EF_BeamSaber_Green.png' in text(W/'Cqb/NZN_AMS_119H_BeamSaber_AF.gw') and 'Cqb_Fire_1_Green_R.gw' in text(W/'Cqb/NZN_AMS_119H_BeamSaber_AF.gw'))
 check('Bruno gun and plain machine gun artwork match source bytes',all((E/a['source']).read_bytes()==(DLC/a['target']).read_bytes() for a in data['assets']))
 fximgs=['Resource/Image/Fx/Weapon/Shell/Image/Explosion_Hit_2.png','Resource/Image/Fx/Weapon/Shell/Image/RocketTrailLine_1.png','Resource/Image/Bullet/Shell/RailShell_1.png']
 check('reused large explosion, trail and rail projectile match the external source',all((E/a).read_bytes()==(DLC/a).read_bytes() for a in fximgs))
 def active(w,d,r):
  s=h['hiddenAction_'+w+'_Trigger'].split('requireConditional:',1)[1].replace(chr(34)*3,'').strip()[3:];s=' '.join(s.split())
  for a,b in [('distanceBetween(self,self.attacking)',str(d)),('memory.finalAttackRange','600'),('eventData("RandomWeapon",type="float")',str(r))]:s=s.replace(a,b)
  return bool(eval(s,{'__builtins__':{}},{}))
 check('heavy ranged random branches are complete and exclusive',all(sum(active(w,d,r) for w in ['NZN_AMS_119H_BrunoGun','NZN_AMS_119H_BR','NZN_AMS_119H_Panzerfaust'])==int(60<d<=600) for d,r in itertools.product([0,60,60.01,600,601],[0,15,15.01,35,35.01,100])))
 paths=[DLC/a for a in data['created']]+[testpath,hpath];bad=[]
 for p in paths:
  for m in re.finditer(r'ROOT:[/\\]?([A-Za-z0-9_./\\ -]+?\.(?:png|ogg|ini|gw))',text(p)):
   if not (DLC/m[1].replace('\\','/')).is_file():bad.append([str(p),m[1]])
 check('all concrete new unit/weapon references resolve in DLC0093',not bad)
 report={'checks':len(out),'passed':sum(i['passed'] for i in out),'results':out,'gameplay_tested':False}
 (ANALYSIS/'0093_占位图标_Test与重装型验证.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(f"{report['passed']}/{report['checks']} checks passed")
 return int(report['passed']!=report['checks'])

if __name__=='__main__':raise SystemExit(main())
