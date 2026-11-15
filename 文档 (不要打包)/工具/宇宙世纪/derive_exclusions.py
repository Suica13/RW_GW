from pathlib import Path
import os,json
os.chdir(Path(__file__).resolve().parents[3])
import config_view as c
from source_paths import package_root
from uc_technology_rules import additions_for, REMOVED_UNITS
O=Path('output/uc');inv=json.loads((O/'tech-inventory.json').read_text('utf-8'));ent=json.loads((O/'source-entities.json').read_text('utf-8'));main=set();branch=set()
for f,row in inv.items():
 p=package_root(row['era'])/f'Units/TechTree/Tech/Faction/{f}/TechList_{f}.ini';d=c.local(p)
 for units in additions_for(f,d).values():main.update(units)
 for role,target in [('main',main),('branch',branch)]:
  for tech in row[role]:
   for call in d.get('hiddenAction_'+tech+'_UnlockUnit',{}).get('alsoTriggerAction','').split(','):
    call=call.strip()
    if call.startswith('Unlock_'):target.add(call[7:])
main.difference_update(REMOVED_UNITS)
exclusive={n for n in branch-main if any(a['path'].startswith('Units/BattleUnits/') for a in ent.get(n,[]))}
exclusive.update(REMOVED_UNITS)
(O/'branch-exclusive-ids.json').write_text(json.dumps(sorted(exclusive),indent=2),encoding='utf-8')
print('Excluded branch-exclusive entities:',len(exclusive))
