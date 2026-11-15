from pathlib import Path
import os,json
os.chdir(Path(__file__).resolve().parents[3])
O=Path('output/uc')
inventory=json.loads((O/'tech-inventory.json').read_text('utf-8'))
progression=json.loads((O/'era-progression.json').read_text('utf-8'))
for faction,row in inventory.items():
    (O/('tech-'+faction+'.txt')).write_text('\n'.join(row['main']),encoding='utf-8')
    (O/('end-'+faction+'.txt')).write_text(str(progression['era_end'][faction]),encoding='utf-8')
print('Runtime research fixtures prepared')
