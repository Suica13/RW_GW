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

cases=json.loads((O/'ace-conversion-cases.json').read_text('utf-8'))
(O/'ace-cases.tsv').write_text('\n'.join(row['pilot']+'\t'+str(row['pilot_type']) for row in cases),encoding='utf-8')

# Special-map starts are ordinary native unit objects, with an explicit p20 name.
import xml.etree.ElementTree as _map_xml
_map_cases=[]
for _map in sorted(Path('GW_BattleUniverse_Main/Maps').glob('[[]p20]*(10v10)_PVP_*_SP_Map.tmx')):
    _root=_map_xml.parse(_map).getroot()
    _starts={}
    for _obj in _root.findall("objectgroup[@name='SP_PlayerStarts']/object"):
        _props={p.get('name'):p.get('value') for p in _obj.findall('properties/property')}
        _starts[int(_props['team'])]=str(float(_obj.get('x'))+float(_obj.get('width'))/2)+','+str(float(_obj.get('y'))+float(_obj.get('height'))/2)
    assert set(_starts)==set(range(20)),_map
    _map_cases.append('\t'.join(['mods/units/GW_BattleUniverse_Main/Maps/'+_map.name]+[_starts[i] for i in range(20)]))
(O/'sp-map-cases.tsv').write_text('\n'.join(_map_cases)+'\n',encoding='utf-8')
