"""Read-only production/unlock/upgrade checks; not an in-game economy or AI test."""
from pathlib import Path
import hashlib, json, re

ROOT = Path(__file__).resolve().parents[2]
DLC = ROOT / 'GW_BattleUniverse_DLC_0093'
FACTORY = DLC / 'Units/Buildings/Factory'
LIST = FACTORY / 'UnitList'
TECH = DLC / 'Units/TechTree/Tech/Faction/0093_EFSF'

def read(p):
    return p.read_text(encoding='utf-8-sig')

def blocks(text):
    ms = list(re.finditer(r'^\[([^\r\n]+)\]\n', text, re.M))
    return {m[1]:text[m.end():ms[i+1].start() if i+1 < len(ms) else len(text)] for i,m in enumerate(ms)}

def field(block, key):
    m = re.search(r'^' + re.escape(key) + r'[:=](?:"""(.*?)"""|([^\r\n]*))', block, re.M | re.S)
    return (m[1] if m[1] is not None else m[2]).strip() if m else ''

def refs(value):
    return [s.strip() for s in value.split(',') if s.strip()]

def reachable_actions(blocks_by_name, start):
    pending = [start]; visited = set()
    while pending:
        name = pending.pop()
        if name in visited: continue
        visited.add(name)
        node = blocks_by_name.get('hiddenAction_'+name, blocks_by_name.get('action_'+name, ''))
        pending.extend(refs(field(node,'alsoTriggerAction')))
    return visited

def main():
    data = json.loads((Path(__file__).resolve().parent.parent / '\u5206\u6790/0093_factory_pricing.json').read_text(encoding='utf-8'))
    results = []
    def check(name, value):
        results.append(bool(value)); print(('PASS ' if value else 'FAIL ') + name)

    for uid, spec in data['plans'].items():
        path = LIST / spec['faction'] / 'Units/Land' / (uid + '.gw')
        text = read(path); b = blocks(text)
        check(uid + ' registers its own panel, memory and close action', '@memory '+uid+':bool' in text and 'action_Pannel_'+uid in b and 'hiddenAction_Pannel_Close_'+uid in b)
        check(uid + ' has no empty action IDs', not any(n in {'action_','hiddenAction_'} for n in b))
        prod = b['action_Produce_'+uid+'_StandardSquad']
        auto = b['hiddenAction_AutoProduce_'+uid+'_Step2']
        check(uid + ' player/AI price declarations agree', all(int(field(v,'@define Money')) == spec['money'] and int(field(v,'@define Resource')) == spec['resource'] for v in [prod,auto]))
        check(uid + ' has intended build time', field(prod,'buildSpeed') == str(spec['time'])+'s')
        def expand(name, stack=()):
            assert name not in stack, name
            node = b.get('action_'+name, b.get('hiddenAction_'+name)); assert node is not None, name
            units = re.findall(r'([A-Za-z_][A-Za-z0-9_]*)\*(\d+)', field(node,'produceUnits'))
            return [(name,u,int(count)) for u,count in units] + [item for child in refs(field(node,'alsoQueueAction')) for item in expand(child,stack+(name,))]
        entries = [(n,v) for n,v in b.items() if n.startswith('action_Produce_'+uid+'_') and field(v,'isVisible') != 'false']
        outputs = {n:expand(n.removeprefix('action_')) for n,_ in entries}
        check(uid + ' each visible order produces the correct unit count', all(sum(count for _,_,count in units) == spec['count'] and all(u == spec['target'] for _,u,_ in units) for units in outputs.values()))
        check(uid + ' production always assigns a pilot', all('PilotType:1101' in field(b['hiddenAction_'+step],'produceUnits') for units in outputs.values() for step,_,_ in units))
        if spec['count'] == 3:
            check(uid + ' squad keeps delayed per-pilot spawns', all([field(b['hiddenAction_'+step],'buildSpeed') for step,_,_ in units] == ['0.0s','1.0s','1.0s'] for units in outputs.values()))
        else:
            check(uid + ' panel visibly indicates single-unit production', 'SingleUnit_1.png' in b['action_Pannel_'+uid] and field(prod,'text') == 'Standard Armament')
        for kind in ['Land','Space']:
            listing = LIST / spec['faction'] / (spec['faction']+'_UnitList_'+kind+'.ini')
            factory = FACTORY / 'Faction' / spec['faction'] / ('Factory_'+spec['faction']+'_'+kind+'.ini')
            ft = read(factory); fb = blocks(ft)
            check(uid + ' '+kind+' factory includes list, definition and AI entry', listing.name in ft and path.relative_to(DLC).as_posix() in read(listing) and 'AutoProduce_'+uid in reachable_actions(fb,'Get_AutoProduce') and field(fb['hiddenAction_AutoProduce_'+uid],'@define Number') == str(spec['limit']))
        local_actions = {n.split('_',1)[1] for n in b if n.startswith(('action_','hiddenAction_'))}
        calls = [x for v in b.values() for key in ['alsoTriggerAction','alsoQueueAction'] for x in refs(field(v,key))]
        check(uid + ' all local production actions resolve', all(x in local_actions for x in calls))
        if uid != 'RX_93_Test':
            old = data['legacy_queue_sections'][path.relative_to(ROOT).as_posix()]
            check(uid + ' keeps historical queue step IDs', all(name in b for name in old))

    jegan = blocks(read(LIST/'0093_EFSF/Units/Land/RGM_89.gw'))
    check('Jegan retains a real bazooka squad with its equipment discount', field(jegan['action_Produce_RGM_89_BazookaSquad'],'@define Money') == '3900' and field(jegan['action_Produce_RGM_89_BazookaSquad'],'@define Resource') == '5700' and 'EquipmentIndex:1' in jegan['hiddenAction_Produce_RGM_89_BazookaSquad_1'])
    check('deferred units and their production definitions are unchanged', all(hashlib.sha256((DLC/p).read_bytes()).hexdigest() == digest for p,digest in data['excluded'].items()))
    tech = blocks(read(TECH/'TechList_0093_EFSF.ini'))
    unlocked = field(tech['hiddenAction_Tech_0093_EFSF_Mid03_UnlockUnit'],'alsoTriggerAction')
    check('TEST shares the Nu plan; Re-GZ moved to recovery', all('Unlock_'+uid in refs(unlocked) for uid in ['RX_93_Test','RX_93']) and 'Unlock_RGZ_91' not in refs(unlocked))
    send = blocks(read(TECH/'0093_EFSF_Send.ini')); get = blocks(read(TECH/'0093_EFSF_Get.ini'))
    check('TEST unlock send and receive registrations match', field(send['hiddenAction_Unlock_RX_93_Test'],'@define UnitID') == 'RX_93_Test' and field(get['hiddenAction_Get_UnlockInfo_RX_93_Test'],'@define UnitID') == 'RX_93_Test')
    marker = read(DLC/'Units/TechTree/UnlockedListMarker/UnlockedListMarker_0093.ini')
    check('real unlock marker inherits TEST receiver and research UI lists TEST', '0093_EFSF_Get.ini' in marker and 'action_UnlockInfo_RX_93_Test' in blocks(read(TECH/'Common/Tech_0093_EFSF_Mid03.ini')))
    restore = get['hiddenAction_RestoreUnlock_RX_93_Test']
    check('researched saves can restore TEST unlock without new research', "includes='Tech_0093_EFSF_Mid03'" in restore and "not self.globalTeamTags(includes='Unlock_RX_93_Test')" in restore and field(restore,'addGlobalTeamTags') == 'Unlock_RX_93_Test')
    check('Nu own-research gift excludes TEST; restore grants nothing', 'template_Tech_NotByOther' in tech['hiddenAction_Tech_0093_EFSF_Mid03_NotByOther'] and 'RX_93*1(' in tech['hiddenAction_Tech_0093_EFSF_Mid03_NotByOther'] and 'RX_93_Test*' not in tech['hiddenAction_Tech_0093_EFSF_Mid03_NotByOther'] and 'spawnUnits:' not in restore and 'produceUnits:' not in restore)
    unit = blocks(read(DLC/'Units/BattleUnits/RX_93/RX_93_Test.ini')); upgrade = unit['action_CustomUnit_RX_93']
    check('TEST upgrades through native resupply conversion with correct target unlock', 'CustomUnit.gw' in unit['core'] and field(upgrade,'@copyFromSection') == 'template_CustomUnit' and field(upgrade,'@define UnitID') == 'RX_93' and "includes='Unlock_RX_93'" in field(upgrade,'@define CustomRule'))
    check('upgrade cost is exactly the production price difference', int(field(upgrade,'@define Money')) + data['plans']['RX_93_Test']['money'] == data['plans']['RX_93']['money'] and int(field(upgrade,'@define Resource')) + data['plans']['RX_93_Test']['resource'] == data['plans']['RX_93']['resource'])
    native = blocks(read(DLC/'Template/Unit/Skill/CustomUnit.gw'))
    check('upgrade retains native supply gate, duration and reset handshake', 'memory.canSupply==true' in native['template_CustomUnit'] and field(native['template_CustomUnit'],'buildSpeed') == '20s' and 'Send_TryTransform_CustomUnit' in native['template_CustomUnit'])
    check('upgrade resets equipment and displayed weapon index', field(upgrade,'setResourcesWithLogic') == 'EquipmentIndex=0' and field(upgrade,'setUnitMemory') == 'nowWeaponIndex=0')
    target = blocks(read(DLC/'Units/BattleUnits/RX_93/RX_93.ini'))
    framework = read(DLC/'Template/Unit/BattleUnit_Framework.ini')
    check('new and upgraded Nu Gundams have independent stats and native reinitialization', bool(field(target['hiddenAction_InitializeStats'],'setUnitMemory')) and 'EF_RX_93_Funnel.gw' in target['core'] and 'alsoTriggerAction:InitializeCommonStatsBefore,InitializeStats,InitializeCommonStatsAfter,Send_EquipmentChange,TransformRecover' in framework)
    changed = [DLC/p for p in data['updated']+data['created']]
    missing=[]
    for path in changed:
        for ref in re.findall(r'ROOT:[/\\]?([A-Za-z0-9_./\\ -]+?\.(?:png|ogg|ini|gw))',read(path)):
            if not (DLC/ref.replace('\\','/')).is_file(): missing.append((path.name,ref))
    check('all changed runtime file references resolve within DLC0093', not missing)
    if missing: print(missing)
    print(str(sum(results))+'/'+str(len(results))+' checks passed; real production/AI/save/upgrade gameplay not tested')
    return int(not all(results))

if __name__ == '__main__':
    raise SystemExit(main())
