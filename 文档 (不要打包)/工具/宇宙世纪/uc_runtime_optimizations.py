# UC-only: reuse an identical spatial query inside one atomic stat calculation.
# The cache is local to each core and recomputed whenever Check_AttackRange runs.
import re as _range_re

def optimize_range_query(text):
    query='self.numberOfUnitsInAllTeams(withTag="MinovskyParticle",withinrange=200)>0'
    match=_range_re.search(r'(?ms)^\[hiddenAction_Check_AttackRange\]\n(.*?)(?=^\[|\Z)',text)
    if not match or query not in match[1]:
        return text
    if match[1].count(query)==1 and '@memory rangeMinovskyNearby:bool' in text:
        return text
    assert match[1].count(query)==3
    body=match[1].replace(query,'memory.rangeMinovskyNearby')
    body=body.replace('setUnitMemory:"""\n','setUnitMemory:"""\nrangeMinovskyNearby='+query+',\n',1)
    text=text[:match.start(1)]+body+text[match.end(1):]
    return text.replace('[core]\n','[core]\n@memory rangeMinovskyNearby:bool\n',1)

for key,text in list(DB.items()):
    if key[1]=='Template/Unit/BattleUnitCore.ini':
        DB[key]=optimize_range_query(text)
