# Executed by build_uc.py with the parsed source configurations and editing helpers.
# Source era keys are internal to the builder; emitted paths follow ordinary DLC folders.
def ref(era, path):
    return 'ROOT:Source/' + era + '/' + path

TECH_POINTS = {}
for faction, row in INV.items():
    path = f'Units/TechTree/Tech/Faction/{faction}/TechList_{faction}.ini'
    source = local(ORIGINAL[(row['era'], path)])
    TECH_POINTS[faction] = {}
    for tech in row['main']:
        memory = source['hiddenAction_' + tech + '_Awake']['setUnitMemory']
        points = float(re.search(r'\$\{TechID\}_TechPoint=([\d.]+)', memory)[1])
        TECH_POINTS[faction][tech] = points * 0.75

reference = TECH_POINTS['EFSF_0079']
ERA_GAP = reference['Tech_EFSF_0079_T2_GPProject'] - reference['Tech_EFSF_0079_T2_GLineDevelopmentPlan']
ERA_END = {f: max(points.values()) for f, points in TECH_POINTS.items()}
EDGES = {
    'EFSF_0079': ['AEUG_0087', 'TITANS_0087'],
    'ZEON_0079': ['AEUG_0087', 'NEO_ZEON_0087'],
    'AEUG_0087': ['0093_EFSF'],
    'TITANS_0087': ['0093_NZN', '0093_EFSF'],
    'NEO_ZEON_0087': ['0093_NZN'],
}

# A player entering 0087/0093 starts with one page, and only appends visited eras.
core = '''[core]
copyFrom:ROOT:Source/Main/Units/TechTree/Mod/TechTree_Core.gw
name:TechTree_Core_UC
tags:TechTree_Core
@memory ucPage:float
@memory ucPages:float
@memory ucStartEra:float

[hiddenAction_UC_Initialize]
autoTriggerOnEvent:created
setUnitMemory:ucPage=0,ucPages=0,ucStartEra=select(self.resource.FactionIndex>=1030000,2,select(self.resource.FactionIndex>=1020000,1,0))

[action_ShowTechTree_UC]
@copyFromSection:template_ShowTechTree
text:Universal Century research [%{memory.ucPages} pages]
text_zh:宇宙世纪科技树 [%{memory.ucPages}页]
isVisible:if not memory.showTechTree
isLocked:false
sendMessageTo:self
sendMessageWithTags:UC_ButtonPressed
alsoTriggerAction:UC_Open

[hiddenAction_UC_Next]
autoTriggerOnEvent:newMessage(withTag="UC_Next")
setUnitMemory:ucPage=min(memory.ucPages-1,memory.ucPage+1)
alsoQueueAction:UC_OpenDelayed

[hiddenAction_UC_Last]
autoTriggerOnEvent:newMessage(withTag="UC_Last")
setUnitMemory:ucPage=max(0,memory.ucPage-1)
alsoQueueAction:UC_OpenDelayed

[hiddenAction_UC_OpenDelayed]
buildSpeed:0.1s
alsoTriggerAction:UC_Open
'''
open_calls = []
close_calls = []
for faction, row in INV.items():
    era = row['era']
    era_index = ['0079', '0087', '0093'].index(era)
    base = row['main'][0]
    core += f'''
[attachment_{faction}]
@copyFromSection:template_TechTree_Main
onCreateSpawnUnitOf:NONE

[hiddenAction_UC_Visit_{faction}]
autoTrigger:if self.globalTeamTags(includes='Tech_{faction}_Start') and self.attachment(slot='{faction}').hp<=0
attachments_addNewUnits:TechTree_UI_Main_{faction}
attachments_onlyOnSlots:{faction}
addGlobalTeamTags:UC_Visited_{faction}
setUnitMemory:ucPages=max(memory.ucPages,{era_index}+1-memory.ucStartEra),ucPage={era_index}-memory.ucStartEra
alsoTriggerAction:UC_CloseOldPages
alsoQueueAction:UC_Bootstrap_{faction}

[hiddenAction_UC_Bootstrap_{faction}]
buildSpeed:0.25s
sendMessageTo:self.attachment(slot='{faction}')
sendMessageWithTags:Unlock_{base}
sendMessageWithData:byOther=1

[hiddenAction_UC_Open_{faction}]
requireConditional:if memory.ucPage=={era_index}-memory.ucStartEra and self.globalTeamTags(includes='UC_Visited_{faction}')
sendMessageTo:self.attachment(slot='{faction}')
sendMessageWithTags:ShowTechTree

[hiddenAction_UC_CloseOldPage_{faction}]
sendMessageTo:self.attachment(slot='{faction}')
sendMessageWithTags:UC_CloseOwnedPage
'''
    open_calls.append('UC_Open_' + faction)
    close_calls.append('UC_CloseOldPage_' + faction)
    key = (era, f'Units/TechTree/Core/Faction/{faction}/TechTree_UI_Main_{faction}.ini')
    text = DB[key]
    text = edit(text, 'core', '@memory ucTechBase', 'float')
    text = edit(text, 'hiddenAction_InitializeStats', 'setUnitMemory', 'pageMax=0,pageCount=0,ucTechBase=customTarget1.customTarget1.readUnitMemory(\'ucEraTechBase\',type=\'float\')')
    text = replace_section(text, 'hiddenAction_ShowTechTree', 'autoTriggerOnEvent:newMessage(withTag="ShowTechTree")\nalsoTriggerAction:ShowTechTree_Page0')
    text = replace_section(text, 'hiddenAction_ShowTechTree_Page0', f'attachments_addNewUnits:TechTree_UI_Page_UC_{faction}\nattachments_onlyOnSlots:Page')
    text = remove_sections(text, lambda s,v: s.startswith('hiddenAction_ShowTechTree_Page') and s != 'hiddenAction_ShowTechTree_Page0')
    text = replace_section(text, 'hiddenAction_GetNextPage', 'autoTriggerOnEvent:newMessage(withTag="NextPage")\nsendMessageTo:parent\nsendMessageWithTags:UC_Next')
    text = replace_section(text, 'hiddenAction_GetLastPage', 'autoTriggerOnEvent:newMessage(withTag="LastPage")\nsendMessageTo:parent\nsendMessageWithTags:UC_Last')
    text = remove_sections(text, lambda s,v: s.startswith('hiddenAction_AI_CheckPage'))
    text += f'''
[hiddenAction_UC_CloseOwnedPage]
autoTriggerOnEvent:newMessage(withTag="UC_CloseOwnedPage")
alsoTriggerAction:TryClosePage

[hiddenAction_UC_AI_Show]
autoTrigger:if self.isControlledByAI() and self.globalTeamTags(includes='{faction}') and self.attachment(slot='Page').hp<=0
alsoTriggerAction:ShowTechTree
'''
    DB[key] = text

    original_page = local(DB[(era, str(Path(row['pages'][0]['file'])).replace('\\', '/'))])
    page_number = f"{era_index}+1-parent.parent.readUnitMemory('ucStartEra',type='float')"
    page = f'''[core]
copyFrom:{ref(era, 'Units/TechTree/Mod/TechTree_UI_Page.gw')}
name:TechTree_UI_Page_UC_{faction}
displayText:{ENAMES[faction]} mainline research
displayText_zh:{NAMES[faction]} 主线科技

[action_UC_PageInfo]
displayType:infoOnly
pos:-1
text:{ENAMES[faction]} - Page %{{{page_number}}}/%{{parent.parent.readUnitMemory('ucPages',type='float')}}
text_zh:{NAMES[faction]} - 第%{{{page_number}}}/%{{parent.parent.readUnitMemory('ucPages',type='float')}}页
buildSpeed:0s
isVisible:true
'''
    for section in ['decal_Background', 'decal_Background2', 'decal_Faction_Icon', 'decal_Faction_Text']:
        values = original_page.get(section, {})
        if values:
            page += '\n[' + section + ']\n'
            page += '\n'.join(k + ':' + (ref(era, value[5:]) if value.startswith('ROOT:') else value) for k,value in values.items()) + '\n'
    first_row = [tech for tech in row['main'] if '_T2_' not in tech]
    second_row = [tech for tech in row['main'] if '_T2_' in tech]
    positions = []
    for technologies, y in [(first_row, 20 if second_row else -5), (second_row, -25)]:
        for index, tech in enumerate(technologies):
            x = -110 + 220 * index / max(1, len(technologies)-1)
            positions.append((tech, round(x,2), y))
    for index, (tech,x,y) in enumerate(positions):
        page += f'\n[attachment_Tech_Main_{index}]\n@copyFromSection:template_TechSlot\nx:{x}\ny:{y}\nonCreateSpawnUnitOf:{tech}\n'
        if index and positions[index-1][2]==y:
            _, px, py = positions[index-1]
            # Continue reading at the left of the next row; no reversed lower row.
            page += f'\n[decal_UC_MainLine_{index}]\n@copyFromSection:template_DrawLine\nbasePosition:self.getOffsetRelative(x={px},y={py})\ndrawLineTo:self.getOffsetRelative(x={x},y={y})\n'
    DB[('Main', f'UC/TechTree_UI_Page_UC_{faction}.ini')] = page
    CUSTOM['TechTree_UI_Page_UC_' + faction] = True
core += '\n[hiddenAction_UC_Open]\nalsoTriggerAction:' + ','.join(open_calls) + '\n'
core += '\n[hiddenAction_UC_CloseOldPages]\nalsoTriggerAction:' + ','.join(close_calls) + '\n'
DB[('Main', 'UC/TechTree_Core_UC.ini')] = core
CUSTOM['TechTree_Core_UC'] = True

imports = [ref('Main', 'Units/TechTree/UnlockedListMarker/Mod/Common_UnlockedListMarker.ini')]
for faction, row in INV.items():
    era = row['era']
    imports.append(ref(era, 'Units/TechTree/Tech/Faction/Common/Common_Building_Get.ini'))
    for role in ['Get','ACE_Get']:
        path = f'Units/TechTree/Tech/Faction/{faction}/{faction}_{role}.ini'
        if (era,path) in DB:
            imports.append(ref(era,path))
DB[('Main','UC/UnlockedListMarker_UC.ini')] = '[core]\ncopyFrom:"""\n' + ',\n'.join(dict.fromkeys(imports)) + '\n"""\nname:UnlockedListMarker_UC\n'
CUSTOM['UnlockedListMarker_UC'] = True

# [ORDER_DEPENDENT] Native HQs already keep attachments. Do not redeclare slots here.
hq = '''[core]
dont_load:true
@memory ucEraTechBase:float
@memory ucAdvancePending:bool
@memory ucAdvanceRoll:float
@memory ucAdvanceAt:float
'''
for faction, targets in EDGES.items():
    complete = ' and '.join("self.globalTeamTags(includes='" + tech + "')" for tech in INV[faction]['main'])
    local_gate = ERA_END[faction] + ERA_GAP
    gate = f'memory.ucEraTechBase+{local_gate:g}'
    for target in targets:
        action = 'UC_Advance_' + faction + '_To_' + target
        era = INV[target]['era']
        stage = 1010 if era == '0087' else 1020
        hq += f'''
[action_{action}]
pos:90
text:Advance to {ENAMES[target]} [TP %{{{gate}}}]
text_zh:进入{NAMES[target]}时代 [科技点 %{{{gate}}}]
description:Complete all current-era mainline research and reach the required cumulative research points. Research points, credits, materials, units and completed research are retained.
description_zh:完成本时代全部主线科技后，仍需累计{ERA_GAP:g}点科技。科技点不清零，后续时代门槛继续累加；保留资金、资源、现役部队与已完成研究。
displayType:action
buildSpeed:0s
ai_isDisabled:true
isVisible:if self.resource.FactionIndex=={FIDS[faction]}
isLocked:if not ({complete}) or self.resource.TechPoint<{gate} or not self.hasTags(includes='HQ_NotCaptured')
isLockedMessage:Complete current-era research and accumulate the required research points.
isLockedMessage_zh:需完成本时代全部主线，并达到显示的累计科技点门槛。
requireConditional:if self.resource.FactionIndex=={FIDS[faction]} and ({complete}) and self.resource.TechPoint>={gate} and self.hasTags(includes='HQ_NotCaptured')
temporarilyRemoveTags:{','.join(f for f in FAC if f != target)}
temporarilyAddTags:{target}
removeGlobalTeamTags:{','.join(f for f in FAC if f != target)}
addGlobalTeamTags:{target},Tech_{target}_Start,PassT0
setResourcesWithLogic:FactionIndex={FIDS[target]}
setUnitMemory:ucEraTechBase={gate},autoTechTimer=0,stageIndex={stage},ucAdvancePending=false
alsoTriggerAction:{action}_Ground,{action}_Space

[hiddenAction_{action}_Ground]
requireConditional:if self.resource.tileMode==0
convertTo:HQ_{target}

[hiddenAction_{action}_Space]
requireConditional:if self.resource.tileMode==1
convertTo:HQ_{target}{'_Space' if 'HQ_'+target+'_Space' in ENT else ''}
'''
    # [TICK_DEPENDENT] Draw once and resolve on a later tick, avoiding repeated rerolls.
    hq += f'''
[hiddenAction_UC_AI_Advance_{faction}]
autoTrigger:if self.isControlledByAI() and self.resource.FactionIndex=={FIDS[faction]} and ({complete}) and self.resource.TechPoint>={gate} and self.hasTags(includes='HQ_NotCaptured') and not memory.ucAdvancePending
setUnitMemory:ucAdvancePending=true,ucAdvanceRoll=rnd(0,1),ucAdvanceAt=self.timeAlive+0.1

[hiddenAction_UC_AI_Choose_{faction}]
autoTrigger:if memory.ucAdvancePending and self.resource.FactionIndex=={FIDS[faction]} and self.timeAlive>memory.ucAdvanceAt
setUnitMemory:ucAdvancePending=false
alsoTriggerAction:{','.join('UC_AI_Select_'+faction+'_'+str(i) for i in range(len(targets)))}
'''
    for index,target in enumerate(targets):
        choice = 'true' if len(targets)==1 else ('memory.ucAdvanceRoll<0.5' if index==0 else 'memory.ucAdvanceRoll>=0.5')
        hq += f'''
[hiddenAction_UC_AI_Select_{faction}_{index}]
requireConditional:if self.resource.FactionIndex=={FIDS[faction]} and ({choice})
alsoTriggerAction:UC_Advance_{faction}_To_{target}
'''
DB[('Main','UC/HQ_EraProgression.gw')] = hq
for key,text in list(DB.items()):
    era,path = key
    if '/HQ/Mod/HQ_Faction.ini' in path:
        original = local(text)['core'].get('copyFrom','')
        DB[key] = edit(text,'core','copyFrom','"""\n' + original + ',\nROOT:UC/HQ_EraProgression.gw\n"""')

for name,records in ENT.items():
    record = choose(name)
    if not record:
        continue
    for faction in FAC:
        prefix = 'Factory_' + faction + '_'
        if not name.startswith(prefix):
            continue
        category = name[len(prefix):]
        if category not in ['Land','Air','Aqua','Mega','Space','Space_Mega']:
            continue
        key = (record['era'],record['path'])
        text = DB[key]
        for target in FAC:
            destination = 'Factory_' + target + '_' + category
            if target==faction or destination not in ENT:
                continue
            text += f"\n[hiddenAction_UC_Factory_{target}]\nautoTrigger:if self.resource.FactionIndex=={FIDS[target]} and self.globalTeamTags(includes='Unlock_{destination}') and self.queueSize()==0\nconvertTo:{destination}\n"
        DB[key] = text

# Keep the familiar three scenario pages, each containing one starting era.
host_key = ('Main','Units/Buildings/HQ/HostOption/HostOption_Core.ini')
text = DB[host_key]
for tile in ['Ground','Space']:
    text = edit(text,'hiddenAction_AddMain_VS_GE_'+tile,'setUnitMemory','nowStageUIPageMax=2')
    text = edit(text,'hiddenAction_ShowVS_GE_'+tile,'alsoTriggerAction',','.join('ShowVS_GE_'+tile+'_Page'+str(i) for i in range(3)))
text = remove_sections(text,lambda s,v: bool(re.search(r'ShowVS_GE_(Ground|Space)_Page[3-9]$',s)))
DB[host_key] = text
for tile in ['Ground','Space']:
    for index,era in enumerate(['0079','0087','0093']):
        key = ('Main',f'Units/Buildings/HQ/HostOption/VS/HostOption_Main_VS_GE_{tile}_Page{index}.ini')
        text = DB[key]
        text = remove_sections(text,lambda s,v: s.startswith('attachment_') and '_T2' in s)
        section = 'attachment_HostOption_VS_GE_Common_UC'+era
        text = edit(text,section,'x','0')
        DB[key] = text

# Cross Rays stays visible, but it is explicitly WIP and cannot change game mode.
menu_key = ('Main','Units/Buildings/HQ/HostOption/Main/HostOption_Main_Menu_2.ini')
DB[menu_key] = ORIGINAL[menu_key]
button_key = ('Main','Units/Buildings/HQ/HostOption/Main/Marker/HostOption_VS_CR.ini')
text = ORIGINAL[button_key]
for field,value in {
    'text':'Cross Rays Mode [WIP]', 'text_zh':'火线纵横模式 [开发中]',
    'description':'Work in progress. This mode is not available in the Universal Century DLC.',
    'description_zh':'开发中，宇宙世纪包暂不提供火线纵横玩法。',
    'isLocked':'true', 'requireConditional':'false',
    'isLockedMessage':'Work in progress', 'isLockedMessage_zh':'开发中',
}.items():
    text = edit(text,'action_VS_CR',field,value)
text = edit(text,'decal_NeedDLC','isVisible','false')
text += '''
[decal_UC_WIP]
layer:beforeUI
order:5
onlyWhileAlive:true
isVisible:true
image:ROOT:Resource/Image/System/Button/HostOption/HostOption_WIP_1.png
imageScale:0.2
'''
DB[button_key] = text

# Display the warning image only on the submode panel before scenario selection.
record = choose('HostOption_Main_VS')
key = (record['era'],record['path'])
DB[key] += '''
[decal_UC_ExclusiveWarning]
layer:beforeUI
order:100
onlyTeam:own
isVisible:true
image:ROOT:UC/ExclusiveLoadWarning.png
imageScale:0.25
yOffsetRelative:-108
'''

DB[('Main','UC/DLCMarker_UC.ini')] = '''[core]
copyFrom:ROOT:Source/0079/Units/DLCMarker/Mod/DLCMarker.ini
name:DLCMarker_UC
tags:DLCMarker_UC,DLCMarker_0079,DLCMarker_0087,DLCMarker_0093

[hiddenAction_StartShowMessage]
showMessageToAllPlayers:Universal Century DLC loaded. Main is REQUIRED. Do not enable any other DLC.
showMessageToAllPlayers_zh:已加载宇宙世纪包。必须同时启用Main，请勿与其他任何DLC同时加载！
'''
CUSTOM['DLCMarker_UC'] = True
BAD_IDS.update(['DLCMarker_0079','DLCMarker_0087','DLCMarker_0093'])
(OUT/'era-progression.json').write_text(json.dumps({'technology_points':TECH_POINTS,'gap':ERA_GAP,'era_end':ERA_END,'edges':EDGES},ensure_ascii=False,indent=2),encoding='utf-8')
