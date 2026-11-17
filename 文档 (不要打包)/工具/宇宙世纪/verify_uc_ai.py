from pathlib import Path
import sys,json,re
r=Path.cwd();(r/'output/uc-perf').mkdir(parents=True,exist_ok=True);tool=next(r.glob('*/*/*/config_view.py')).parent;sys.path.insert(0,str(tool));import config_view as c
pack=r/'GW_BattleUniverse_DLC_UC';c.MOD=pack;origins=json.loads((pack/'uc-source-map.json').read_text('utf-8'));rows=[]
for file in sorted((pack/'Units/Buildings/Factory/Faction').rglob('*.ini')):
 relative=file.relative_to(pack).as_posix();origin=origins[relative];source=r/origin['source_package']/origin['source_path'];before=c.local(source);after=c.local(file);effective=c.effective(file);count=0
 assert not any('UC_AutoProduceFallback' in section or 'UC_TryAutoProduceFallback' in section for section in after),relative
 for section,values in after.items():
  if 'AutoProduce' not in section:continue
  assert section in before,(relative,section)
  for key,value in values.items():
   if key in {'alsoTriggerAction','alsoQueueAction'}:
    expected=[v.strip() for v in before[section].get(key,'').split(',') if v.strip() and ('hiddenAction_'+v.strip() in effective or 'action_'+v.strip() in effective)]
    actual=[] if value=='NONE' else [v.strip() for v in value.split(',') if v.strip()]
    assert actual==expected,(relative,section,key,actual,expected)
   else:assert value==before[section].get(key),(relative,section,key,value,before[section].get(key))
   count+=1
 rows.append({'factory':relative,'source':source.relative_to(r).as_posix(),'checked_fields':count})
relative='Template/Building/Common_AutoProduce.ini';origin=origins[relative];assert c.local(pack/relative)==c.local(r/origin['source_package']/origin['source_path'])
baseline=r/'output/uc-perf/user-mod-info-before.bin'
if baseline.exists():
 normalize=lambda b:re.sub(rb'V[0-9]+[A-Za-z0-9]*',b'V_RELEASE',b)
 assert normalize((pack/'mod-info.txt').read_bytes())==normalize(baseline.read_bytes())
report={'native_factory_count':len(rows),'checked_ai_fields':sum(row['checked_fields'] for row in rows),'native_hq_scheduler_exact_match':True,'factories':rows,'user_music_settings_preserved':True if baseline.exists() else None}
(r/'output/uc-perf/native-ai-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('Native AI audit PASS:',len(rows),'factories;',report['checked_ai_fields'],'fields; exact original HQ scheduler.')
