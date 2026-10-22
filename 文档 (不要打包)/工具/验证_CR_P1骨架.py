"""Read-only structural checks and a limited menu-dispatch simulation, not an engine test.

Run: python -B '文档 (不要打包)/工具/验证_CR_P1骨架.py'
"""
from pathlib import Path
import re
import sys
from functools import lru_cache

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / 'GW_BattleUniverse_Main'
DLC = ROOT / 'GW_BattleUniverse_DLC_CR_P1'
FACTIONS = {'CR_Order': 9010101, 'CR_Resistance': 9010201, 'CR_Chaos': 9010301}
CATEGORIES = ('Land', 'Air', 'Aqua', 'Mega', 'Space', 'Space_Mega')
OPEN_CATEGORIES = ('Land', 'Mega', 'Space', 'Space_Mega')
COMMON = {'Refinery_Common_T3', 'Institute_Common_T2', 'SupplyDepot_Common_T2',
          'Academy_Common_T2', 'Turret_MG_B', 'Turret_AA_B', 'Turret_CN_B',
          'Turret_BM_B_Yellow', 'Turret_Radar_B', 'Turret_Space_MG_B',
          'Turret_Space_MS_B', 'Turret_Space_CN_B', 'Wall_T2_A', 'Wall_T2_B'}
EXTENSIONS = {'.ini', '.gw', '.template'}


def text(path):
    return path.read_text(encoding='utf-8-sig')


def sections(data):
    # Preserve RW repeated sections; do not rewrite files with a standard INI parser.
    result = {}
    for match in re.finditer(r'^\[([^\]]+)\]\s*\n(.*?)(?=^\[|\Z)', data, re.M | re.S):
        result[match[1]] = result.get(match[1], '') + match[2]
    return result


def fields(data):
    return {m[1]: (m[2] if m[2] is not None else m[3]).strip()
            for m in re.finditer(r'^([\w@]+):\s*(?:"""(.*?)"""|([^\r\n]*))', data, re.M | re.S)}


def config(path):
    return {key: fields(value) for key, value in sections(text(path)).items()}


def split(value):
    return [s.strip() for s in value.split(',') if s.strip()]


def literal_ids(pack):
    result = set()
    for path in pack.rglob('*.ini'):
        data = text(path)
        core = config(path).get('core', {})
        if core.get('dont_load', '').lower() == 'true':
            continue
        if 'name' in core and '${' not in core['name']:
            result.add(core['name'])
        result.update(re.findall(r'^@global TechID=(\w+)', data, re.M))
    return result


@lru_cache(None)
def inherited(path):
    """Resolve file inheritance for structural references, without expanding RW macros."""
    local = config(path)
    package = next(parent for parent in path.parents if parent.name.startswith('GW_BattleUniverse_'))
    merged = {}
    for ref in split(local.get('core', {}).get('copyFrom', '')):
        source = package / ref[5:] if ref.startswith('ROOT:') else path.parent / ref
        for name, values in inherited(source.resolve()).items():
            merged.setdefault(name, {}).update(values)
    for name, values in local.items():
        merged.setdefault(name, {}).update(values)
    return merged


class MenuModel:
    """Interpret only the literal assignments and dispatch conditions used by this menu.

    This deliberately does not simulate RW events, attachment lifetime or network timing.
    """
    def __init__(self, tile=0, installed=True):
        self.memory = {}
        self.tile = tile
        self.installed = installed
        self.page = None
        self.converted = []
        self.config = config(MAIN / 'Units/Buildings/HQ/HostOption/Mod/HostOption_Core.gw')
        self.config.update(config(MAIN / 'Units/Buildings/HQ/HostOption/HostOption_Core.ini'))

    def condition(self, expression):
        expression = re.sub(r'^if\s+', '', expression)
        expression = expression.replace('customTarget1.resource().tileMode', str(self.tile))
        expression = expression.replace('self.numberOfUnitsInAllTeams(withTag="DLCMarker_CR_P1")', str(int(self.installed)))
        expression = re.sub(r'memory\.(\w+)', lambda m: str(self.memory.get(m[1], 0)), expression)
        # Accept only arithmetic, bool operators and numeric literals from the above substitutions.
        assert re.fullmatch(r'[\d\s().=<>+\-*/]+|[\d\s().=<>+\-*/andor]+', expression), expression
        return bool(eval(expression, {'__builtins__': {}}, {}))

    def run(self, action):
        data = self.config['hiddenAction_' + action]
        if 'requireConditional' in data and not self.condition(data['requireConditional']):
            return
        for assignment in split(data.get('setUnitMemory', '')):
            key, value = assignment.split('=', 1)
            self.memory[key.strip()] = float(value)
        if 'attachments_deleteNumUnits' in data:
            self.page = None
        if 'attachments_addNewUnits' in data:
            self.page = data['attachments_addNewUnits']
        if 'convertTo' in data:
            self.converted.append(data['convertTo'])
        for child in split(data.get('alsoTriggerAction', '')):
            self.run(child)


def main():
    results = []
    def check(label, condition, detail=None):
        results.append((label, bool(condition)))
        if not condition:
            print('FAIL:', label, detail if detail is not None else '')

    # Exact package-local paths, including case, and copyFrom relative paths.
    bad = []
    root_ref = re.compile(r'ROOT:[/\\]?([A-Za-z0-9_./\\ -]+?\.(?:png|ogg|ini|gw|template))', re.I)
    for path in DLC.rglob('*'):
        if path.suffix not in EXTENSIONS:
            continue
        data = text(path)
        for match in root_ref.finditer(data):
            if not (DLC / match[1].replace('\\', '/')).is_file():
                bad.append((str(path.relative_to(DLC)), match[1]))
        for match in re.finditer(r'^\s*copyFrom:\s*(?:"""(.*?)"""|([^\r\n]+))', data, re.M | re.S):
            for ref in split(match[1] or match[2]):
                if not ref.startswith('ROOT:') and '${' not in ref and not (path.parent / ref).is_file():
                    bad.append((str(path.relative_to(DLC)), ref))
    check('CR P1 concrete local assets and inheritance resolve', not bad, bad)
    check('no combat unit roster copied', {p.name for p in (DLC / 'Units/BattleUnits').iterdir()} == {'Shield', 'Weapon'})
    check('no duplicated music', not list((DLC / 'Resource/Music').rglob('*.ogg')))

    menu = text(MAIN / 'Units/Buildings/HQ/HostOption/Main/HostOption_Main_Menu_2.ini')
    sub = text(MAIN / 'Units/Buildings/HQ/HostOption/Main/HostOption_Main_VS.ini')
    check('main menu contains Genesis and Cross Rays attached buttons', all('onCreateSpawnUnitOf:HostOption_VS_' + m + '*1' in menu for m in ['GE', 'CR']))
    check('submode menu contains VS and scenario attached buttons', all('onCreateSpawnUnitOf:HostOption_' + m + '*1' in sub for m in ['VS', 'Stage']))
    stage = config(MAIN / 'Units/Buildings/HQ/HostOption/Main/Marker/HostOption_Stage.ini')
    check('scenario stays locked and visibly WIP', stage['action_Stage']['isLocked'] == 'true' and '[WIP]' in stage['action_Stage']['text_zh'] and stage['decal_WIP']['isVisible'] == 'true')
    marker = config(MAIN / 'Units/Buildings/HQ/HostOption/Main/Marker/HostOption_VS_CR.ini')
    check('CR entry and overlay require the P1 DLC marker', all('DLCMarker_CR_P1' in value for value in [marker['action_VS_CR']['isLocked'], marker['decal_NeedDLC']['isVisible']]))
    for tile in [0, 1]:
        for mode, index in [('GE', 1), ('CR', 2)]:
            model = MenuModel(tile)
            model.run('AddMain_Menu')
            model.run('Get_VS_' + mode)
            check(f'{mode}/{tile} opens submode choice without starting a game', model.page == 'HostOption_Main_VS' and model.memory['gameSubMode'] == 0 and model.memory['gameMainMode'] == index)
            snapshot = (dict(model.memory), model.page)
            model.run('Get_Stage')
            check(f'{mode}/{tile} WIP event cannot start a scenario', snapshot == (model.memory, model.page))
            model.run('Get_VS')
            wanted = 'HostOption_Main_VS_Setting' if mode == 'CR' else 'HostOption_Main_VS_GE_' + ('Ground' if tile == 0 else 'Space') + '_Page0'
            check(f'{mode}/{tile} VS route reaches its correct page', model.page == wanted and model.memory['gameSubMode'] == 1)
            if mode == 'CR':
                check(f'CR/{tile} phase and initial resources', model.memory['stageIndex'] == 2000 and model.memory['resStart'] == 12000)
            model.run('BackToMenuPage')
            check(f'{mode}/{tile} back resets mode, phase and settings', model.memory['gameMainMode'] == 0 and model.memory['gameSubMode'] == 0 and model.memory['stageIndex'] == 0 and model.memory['resStart'] == 6000)
    model = MenuModel(installed=False)
    model.run('AddMain_Menu')
    before = (dict(model.memory), model.page)
    model.run('Get_VS_CR')
    check('Main alone cannot enter CR even through its event', before == (model.memory, model.page))

    host = config(MAIN / 'Units/Buildings/HQ/HostOption/HostOption_Core.ini')
    gm = config(MAIN / 'Units/GameManager/GameManager_Start.ini')
    # Compare assignments literally rather than interpreting broadcast/network behavior.
    check('host and manager broadcast exactly the same setting names', set(re.findall(r'(\w+)\s*=', host['hiddenAction_StartGame']['sendMessageWithData'])) == set(re.findall(r'(\w+)\s*=', gm['hiddenAction_SetGameMode_Setting_Get_GameMode_Step_2_SendToAllPlayers']['sendMessageWithData'])))
    check('all player HQs receive the broadcast', gm['hiddenAction_SetGameMode_Setting_Get_GameMode_Step_2']['alsoTriggerActionRepeat'] == 'memory.playersHQ.size' and gm['hiddenAction_SetGameMode_Setting_Get_GameMode_Step_2_SendToAllPlayers']['sendMessageTo'] == 'memory.playersHQ[index]')
    for main_mode, sub_mode, stage_index, target in [(1, 1, 1020, 'GameManager_VS'), (2, 1, 2000, 'GameManager_CR_VS'), (1, 2, 0, None), (2, 2, 0, None)]:
        model = MenuModel()
        model.config = gm
        model.memory = dict(gameMainMode=main_mode, gameSubMode=sub_mode, stageIndex=stage_index)
        model.run('SetGameMode_Setting_Get_GameMode_Step_3')
        check(f'manager dispatch {main_mode}/{sub_mode}', model.converted == ([target] if target else []))

    main_ids, dlc_ids = literal_ids(MAIN), literal_ids(DLC)
    # Check complete INI compositions, not standalone .gw fragments whose templates
    # are deliberately supplied by their final consumer (e.g. TechTree_Core).
    for path in DLC.rglob('*.ini'):
        if 'CR_' not in path.relative_to(DLC).as_posix():
            continue
        resolved = inherited(path.resolve())
        missing = []
        for section_name, values in resolved.items():
            for key in ['alsoTriggerAction', 'alsoQueueAction', 'takeResources_triggerActionForEach']:
                for action in split(values.get(key, '')):
                    if '${' not in action and action.lower() != 'none' and 'action_' + action not in resolved and 'hiddenAction_' + action not in resolved:
                        missing.append((section_name, key, action))
            for parent in split(values.get('@copyFromSection', '')):
                if '${' not in parent and parent not in resolved:
                    missing.append((section_name, '@copyFromSection', parent))
            if section_name.startswith('template_'):
                continue
            for key in ['convertTo', 'attachments_addNewUnits', 'onCreateSpawnUnitOf', 'produceUnits', 'spawnUnits', 'addUnitsIntoTransport']:
                value = values.get(key, '')
                if '${' in value:
                    continue
                for unit in re.findall(r'(?:^|,)\s*([A-Za-z0-9_]+)(?=\*|\(|,|$)', value):
                    if unit.lower() != 'none' and unit not in main_ids | dlc_ids:
                        missing.append((section_name, key, unit))
        check('resolved actions, sections and entities: ' + path.relative_to(DLC).as_posix(), not missing, missing)
    placeholders = {'HQ_VS_CR_P1', 'TechTree_Core_CR_P1', 'UnlockedListMarker_CR_P1', 'CR_P1_BuildingSlot', 'StrategicLocation_CR_P1'} | {'HQ_' + f for f in FACTIONS}
    for entity in placeholders:
        check('Main placeholder + P1 override: ' + entity, entity in main_ids and entity in dlc_ids and any('overrideAndReplace:' + entity in text(p) for p in DLC.rglob('*.ini')))
    for pack in [MAIN] + sorted(ROOT.glob('GW_BattleUniverse_DLC_*')):
        for rel, target in [('Template/Building/Common_Buildings_Slot.gw', 'CR_P1_BuildingSlot'), ('Units/Buildings/StrategicLocation/Mod/StrategicLocation.ini', 'StrategicLocation_CR_P1')]:
            data = config(pack / rel)
            branch = data['hiddenAction_ConvertTo_CR_P1']
            check(pack.name + ' routes ' + target, 'ConvertTo_CR_P1' in data['hiddenAction_ConvertToFaction']['alsoTriggerAction'] and branch['convertTo'] == target and all(str(i) in branch['requireConditional'] for i in FACTIONS.values()))
        path = pack / 'Units/Buildings/HQ/Mod/HQ_GetMode.ini'
        if not path.exists():
            continue
        routes = config(path)
        for mode, stage_id, wanted in [(1, 1020, 'HQ_VS_GE_UC0093'), (2, 2000, 'HQ_VS_CR_P1')]:
            model = MenuModel()
            model.config = routes | {'hiddenAction_AddCV_Core': {}}
            model.memory = dict(gameMainMode=mode, gameSubMode=1, stageIndex=stage_id)
            model.run('SetGameMode_Setting_Get_GameMode_VS')
            check(pack.name + f' HQ dispatch mode {mode}', model.converted == [wanted])

    lobby = config(DLC / 'Units/Buildings/HQ/HQ_VS_CR/HQ_VS_CR_P1.ini')
    core = config(DLC / 'Units/TechTree/Core/CR_P1/TechTree_Core_CR_P1.ini')
    build = config(DLC / 'Units/Buildings/BuildingSlot/Faction/CR_P1_MainBuildList.ini')
    slots = config(DLC / 'Units/Buildings/BuildingSlot/Faction/CR_P1_BuildingSlot.ini')
    common_get = config(DLC / 'Units/TechTree/Tech/Faction/Common/Common_Building_Get.ini')
    common_send = config(DLC / 'Units/TechTree/Tech/Faction/Common/Common_Building_Send.ini')
    check('exactly three faction choices', {k.removeprefix('action_ChoseFaction_') for k in lobby if k.startswith('action_ChoseFaction_CR_')} == set(FACTIONS))
    check('no starting combat spawns', not re.search(r'^\s*(spawnUnits|produceUnits):', text(DLC / 'Units/Buildings/HQ/HQ_VS_CR/HQ_VS_CR_P1.ini'), re.M))
    for faction, index in FACTIONS.items():
        selected = lobby['action_ChoseFaction_' + faction]
        check(faction + ' HQ selection and startup tags', selected['setResourcesWithLogic'] == 'FactionIndex=' + str(index) and 'Tech_' + faction + '_Start' in selected['addGlobalTeamTags'] and 'PassT0' in selected['addGlobalTeamTags'])
        conversion = lobby['hiddenAction_ConvertToFaction_' + faction]
        check(faction + ' HQ and core attachment', conversion['convertTo'] == 'HQ_' + faction and conversion['attachments_addNewUnits'] == 'TechTree_Core_CR_P1' and conversion['attachments_onlyOnSlots'] == 'TechTreeMarkerSlot')
        start = core['hiddenAction_Start_Set_Tech_' + faction]
        check(faction + ' automatic Base message', start['sendMessageTo'] == "self.attachment(slot='" + faction + "')" and start['sendMessageWithTags'] == 'Unlock_Tech_' + faction + '_BaseTech' and 'byOther=1' in start['sendMessageWithData'])
        base_dir = DLC / 'Units/TechTree/Tech/Faction' / faction
        tech = config(base_dir / ('TechList_' + faction + '.ini'))
        base_id = 'Tech_' + faction + '_BaseTech'
        wanted = COMMON | {'Factory_' + faction + '_' + c for c in OPEN_CATEGORIES}
        unlocked = {a.removeprefix('Unlock_') for a in split(tech['hiddenAction_' + base_id + '_UnlockUnit']['alsoTriggerAction'])}
        check(faction + ' Base unlocks buildings only', unlocked == wanted, sorted(unlocked ^ wanted))
        check(faction + ' full Base lifecycle', all('hiddenAction_' + base_id + '_' + s in tech for s in ['Awake', 'Start', 'Stop', 'Done', 'UnlockUnit', 'NotByOther', 'SendAlly', 'SendAlly_Step2', 'SendAlly_Step3']))
        sends = common_send | config(base_dir / (faction + '_Send.ini'))
        gets = common_get | config(base_dir / (faction + '_Get.ini'))
        marker = config(base_dir / 'Common' / (base_id + '.ini'))
        for unit in wanted:
            check(faction + ' unlock chain: ' + unit, unit in main_ids | dlc_ids and 'hiddenAction_Unlock_' + unit in sends and 'hiddenAction_Get_UnlockInfo_' + unit in gets and 'action_UnlockInfo_' + unit in marker and 'canBuild_' + unit in build)
        for category in CATEGORIES:
            factory = 'Factory_' + faction + '_' + category
            check(factory + ' slot route', 'action_Build_' + factory in slots and faction in slots['action_Build_' + factory].get('@define OtherVisible', sections(text(DLC / 'Units/Buildings/BuildingSlot/Faction/CR_P1_BuildingSlot.ini'))['action_Build_' + factory]))
            listing = DLC / 'Units/Buildings/Factory/UnitList' / faction / (faction + '_UnitList_' + category + '.ini')
            check(factory + ' empty valid production list', 'dont_load:true' in text(listing) and '/Units/' not in text(listing) and 'produceUnits:' not in text(listing))
        page = text(DLC / 'Units/TechTree/Core/Faction' / faction / ('TechTree_UI_Page_' + faction + '_00.ini'))
        check(faction + ' first page only contains Base', re.findall(r'onCreateSpawnUnitOf:([^\s*]+)', page) == [base_id])
    for team in range(20):
        chosen = []
        for faction in FACTIONS:
            expr = lobby['hiddenAction_ChoseFaction_ByAI_' + faction]['requireConditional'].removeprefix('if ')
            expr = expr.replace('self.resource().FactionIndex', str(0 if not chosen else FACTIONS[chosen[0]])).replace('self.teamID', str(team))
            if eval(expr, {'__builtins__': {}, 'int': int}, {}):
                chosen.append(faction)
        check(f'AI team {team} picks exactly one faction', chosen == [list(FACTIONS)[team % 3]])

    print(f'{sum(ok for _, ok in results)}/{len(results)} checks passed')
    print('Static only: game loading, UI rendering, network timing and gameplay are not tested.')
    return int(not all(ok for _, ok in results))


if __name__ == '__main__':
    sys.exit(main())
