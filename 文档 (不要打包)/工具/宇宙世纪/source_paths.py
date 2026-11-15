from pathlib import Path
import os
ROOT = Path(__file__).resolve().parents[3]
ERAS = ('Main', '0079', '0087', '0093')

def package_root(era):
    name = 'GW_BattleUniverse_Main' if era == 'Main' else 'GW_BattleUniverse_DLC_' + era
    for base in (ROOT, ROOT.parent):
        candidate = base / name
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError(f'Missing source package: {name}; checked {ROOT} and {ROOT.parent}')

def packages():
    return {era: package_root(era) for era in ERAS}
