from pathlib import Path
import os
os.chdir(Path(__file__).resolve().parents[3])
import json,re,sys,collections
sys.path.insert(0,str(Path(__file__).resolve().parent))
import config_view as c
from source_paths import package_root
from uc_technology_rules import additions_for, REMOVED_UNITS, REMOVED_TECHNOLOGIES

P=Path('GW_BattleUniverse_DLC_UC').resolve()
O=Path('output/uc')
c.MOD=P
inventory=json.loads((O/'tech-inventory.json').read_text('utf-8'))
progression=json.loads((O/'era-progression.json').read_text('utf-8'))
selected=set(json.loads((O/'selected-entities.json').read_text('utf-8')))
removed=set(json.loads((O/'removed-ids.json').read_text('utf-8')))
entities=json.loads((O/'source-entities.json').read_text('utf-8'))
origins=json.loads((P/'uc-source-map.json').read_text('utf-8'))
source_paths={(v['source_package'],v['source_path']):P/k for k,v in origins.items()}
errors=[]
report={}

def check(condition,message):
    if not condition:errors.append(message)

def source_file(era,relative):
    return source_paths[(package_root(era).name,relative)]

loaded={}
for path in P.rglob('*.ini'):
    own=c.local(path)
    if own.get('core',{}).get('dont_load')=='true':continue
    core=c.merged(path).get('core',{})
    name=re.sub(r'\$\{([^}]+)\}',lambda m:core.get('@global '+m[1],m[0]),core.get('name',''))
    check(name not in loaded,'Duplicate UC entity '+name)
    loaded[name]=path
check(not(selected&removed),'Excluded entities remain selected')
check(not(set(json.loads((O/'branch-exclusive-ids.json').read_text('utf-8')))&selected),'Branch-exclusive unit retained')
check({p.name for p in P.iterdir() if p.is_dir()}=={'Units','Template','Resource'},'Nonstandard runtime folder layout')
check(not any(re.fullmatch(r'[0-9a-f]{24}',p.stem) for p in P.rglob('*.png')),'Hashed asset names remain')

all_main=set()
metrics=[]
for faction,row in inventory.items():
    main=row['main']
    all_main.update(main)
    page=c.local(loaded['TechTree_UI_Page_UC_'+faction])
    nodes=[(v['onCreateSpawnUnitOf'],float(v['x']),float(v['y'])) for s,v in page.items() if s.startswith('attachment_Tech_Main_')]
    check([v[0] for v in nodes]==main,faction+' main node order changed')
    by_row=collections.defaultdict(list)
    for _,x,y in nodes:by_row[y].append(x)
    for xs in by_row.values():check(xs==sorted(xs) and len(set(xs))==len(xs),faction+' row not left to right')
    for s,v in page.items():
        if not s.startswith('decal_UC_MainLine_'):continue
        start=float(re.search(r'y=([\d.-]+)',v['basePosition'])[1])
        end=float(re.search(r'y=([\d.-]+)',v['drawLineTo'])[1])
        check(start==end,faction+' has a line crossing between rows')
    relative=f'Units/TechTree/Tech/Faction/{faction}/TechList_{faction}.ini'
    original=c.local(package_root(row['era'])/relative)
    merged=c.local(source_file(row['era'],relative))
    for tech in main:
        section='hiddenAction_'+tech+'_Awake'
        before=original[section]['setUnitMemory']
        after=merged[section]['setUnitMemory']
        def number(text,field):return float(re.search(r'\$\{TechID\}_'+field+r'=([\d.]+)',text)[1])
        old_tp=number(before,'TechPoint')
        new_tp=number(after,'TechPoint')
        check(new_tp==old_tp*.75,tech+' TP multiplier incorrect')
        check("+customTarget1.customTarget1.readUnitMemory('ucEraTechBase',type='float')" in after,tech+' lacks cumulative offset')
        for field in ['Time','Money','Resource']:check(number(before,field)==number(after,field),tech+' changed '+field)
        check(tech in loaded,tech+' missing marker')
        marker=c.local(loaded[tech])['core']
        index=main.index(tech)
        prerequisite='true' if index==0 else "self.globalTeamTags(includes='"+main[index-1]+"')"
        check(marker['@global Unlocked']==prerequisite,tech+' prerequisite changed')
        check(marker.get('@global AIUnlocked')=='true',tech+' AI prerequisite blocked')
        metrics.append({'technology':tech,'original_tp':old_tp,'local_tp':new_tp})
    for branch in row['branch']:check(not any(branch in s for s in merged),branch+' research action retained')

hq=c.local(P/'Units/Buildings/HQ/Mod/HQ_EraProgression.gw')
check(progression['gap']==3600,'Unexpected era gap')
edges=[]
for faction,targets in progression['edges'].items():
    gate=progression['era_end'][faction]+progression['gap']
    for target in targets:
        action='UC_Advance_'+faction+'_To_'+target
        values=hq['action_'+action]
        edges.append([faction,target])
        check('TechPoint' not in values['setResourcesWithLogic'],action+' resets or spends cumulative TP')
        check(f'ucEraTechBase=memory.ucEraTechBase+{gate:g}' in values['setUnitMemory'],action+' wrong next-era offset')
        check(f'self.resource.TechPoint>=memory.ucEraTechBase+{gate:g}' in values['requireConditional'],action+' lacks TP gate')
        for tech in inventory[faction]['main']:check(tech in values['requireConditional'],action+' missing research prerequisite')
        for terrain in ['Ground','Space']:
            expected='HQ_'+target+('_Space' if terrain=='Space' and 'HQ_'+target+'_Space' in entities else '')
            check(hq['hiddenAction_'+action+'_'+terrain]['convertTo']==expected,action+' wrong HQ')
    ai=hq['hiddenAction_UC_AI_Advance_'+faction]
    check('rnd(0,1)' in ai['setUnitMemory'] and 'ucAdvancePending=true' in ai['setUnitMemory'],faction+' AI does not draw once')
    check('self.resource.TechPoint>=' in ai['autoTrigger'],faction+' AI skips TP gate')
    check('ucAdvanceAt=self.timeAlive+0.1' in ai['setUnitMemory'] and 'self.timeAlive>memory.ucAdvanceAt' in hq['hiddenAction_UC_AI_Choose_'+faction]['autoTrigger'],faction+' AI lacks delayed independent choice')
    for i,target in enumerate(targets):
        values=hq['hiddenAction_UC_AI_Select_'+faction+'_'+str(i)]
        check(values['alsoTriggerAction']=='UC_Advance_'+faction+'_To_'+target,faction+' AI target mismatch')

master=c.local(loaded['TechTree_Core_UC'])
check('ucStartEra=' in master['hiddenAction_UC_Initialize']['setUnitMemory'],'Initial page era not normalized')
for era in ['0079','0087','0093']:
    mode=c.effective(loaded['HQ_VS_GE_UC'+era])
    spawns=[v.get('attachments_addNewUnits','') for s,v in mode.items()]
    check('TechTree_Core_UC' in spawns,era+' start lacks UC core')
    check('UnlockedListMarker_UC' in spawns,era+' start lacks UC unlock receiver')
    check(not any('TechTree_Core_'+other in x for x in spawns for other in ['0079','0087','0093']),era+' uses native era core')
host=c.local(loaded['HostOption_Core'])
for tile in ['Ground','Space']:
    check(host['hiddenAction_AddMain_VS_GE_'+tile]['setUnitMemory']=='nowStageUIPageMax=2',tile+' scenario page count wrong')
    for index,era in enumerate(['0079','0087','0093']):
        page=c.effective(loaded[f'HostOption_Main_VS_GE_{tile}_Page{index}'])
        stages=[v.get('onCreateSpawnUnitOf','') for s,v in page.items() if s.startswith('attachment_HostOption_VS_GE_Common_')]
        check(stages==['HostOption_VS_GE_Common_UC'+era+'*1'],tile+era+' wrong starting scenario')
        marker=c.effective(loaded['HostOption_VS_GE_Common_UC'+era])
        data=marker.get('action_SelectStage',{})
        # The native marker action name differs between eras; inspect its stage message.
        candidates=[v for v in marker.values() if v.get('sendMessageWithTags')=='VS_Stage']
        check(bool(candidates),era+' scenario lacks setting message')

menu=c.local(loaded['HostOption_Main_Menu_2'])
check(menu['attachment_HostOption_VS_CR']['onCreateSpawnUnitOf']=='HostOption_VS_CR*1','Cross Rays button hidden')
button=c.local(loaded['HostOption_VS_CR'])
check(button['action_VS_CR']['isLocked']=='true' and button['action_VS_CR']['requireConditional']=='false','Cross Rays WIP can be selected')
check('[开发中]' in button['action_VS_CR']['text_zh'],'Cross Rays lacks WIP label')
check('decal_UC_WIP' in button,'Cross Rays lacks WIP overlay')
warnings=[]
for path in P.rglob('*'):
    if path.suffix not in ['.ini','.gw','.template']:continue
    for section,values in c.local(path).items():
        if values.get('image')=='ROOT:Resource/Image/UI/UC_LoadWarning.png':warnings.append((path,section,values))
check(len(warnings)==1,'Warning image appears in multiple UI locations')
if warnings:
    path,section,values=warnings[0]
    check(path==loaded['HostOption_Main_VS'],'Warning not on pre-scenario submode panel')
    check(values['imageScale']=='0.25','Warning size is not halved')
    check(float(values['yOffsetRelative'])<-96.25,'Warning overlaps panel interior')
check(c.local(P/'mod-info.txt')['mod']['thumbnail']=='mod-thumbnail.png','Warning used as mod thumbnail')

factories={}
for faction in inventory:
    factories[faction]={}
    for name,path in loaded.items():
        if not name.startswith('Factory_'+faction+'_'):continue
        definitions=c.effective(path)
        production=[]
        for section,values in definitions.items():
            unit=values.get('@define UnitID','')
            if section.startswith('action_') and unit and unit not in ['Test','<UNIT>']:
                production.append(unit)
                check(unit not in removed,name+' exposes excluded unit '+unit)
        factories[faction][name]=sorted(set(production))
        check('hiddenAction_Get_AutoProduce' in definitions,name+' lacks AI production receiver')
    check(bool(factories[faction]),faction+' has no factories')

# Verify each requested fold all the way from research to UI, receiver and factory.
merges=[]
receiver=c.effective(loaded['UnlockedListMarker_UC'])
for faction,row in inventory.items():
    relative=f'Units/TechTree/Tech/Faction/{faction}/TechList_{faction}.ini'
    expected=additions_for(faction,c.local(package_root(row['era'])/relative))
    controller=c.effective(loaded['TechTree_UI_Main_'+faction])
    lists=c.local(source_file(row['era'],relative))
    for tech,units in expected.items():
        unlocks=lists['hiddenAction_'+tech+'_UnlockUnit']['alsoTriggerAction'].split(',')
        marker=c.effective(loaded[tech])
        for unit in units:
            check('Unlock_'+unit in unlocks,tech+' missing added unlock '+unit)
            check(marker.get('action_UnlockInfo_'+unit,{}).get('@define UnitID')==unit,tech+' missing added UI '+unit)
            check(controller.get('hiddenAction_Unlock_'+unit,{}).get('@define UnitID')==unit,faction+' missing sender '+unit)
            check(any(s.startswith('hiddenAction_Get_UnlockInfo_') and v.get('@define UnitID')==unit for s,v in receiver.items()),faction+' missing receiver '+unit)
            if not unit.startswith('Pilot_'):
                check(unit in loaded,'Added unit not loadable '+unit)
                check(any(unit in units for units in factories[faction].values()),faction+' no factory panel for '+unit)
        merges.append({'faction':faction,'technology':tech,'units':units})
check(not REMOVED_UNITS.intersection(loaded),'Explicitly removed unit remains loadable')
check(not REMOVED_TECHNOLOGIES.intersection(loaded),'Removed Gyan technology remains loadable')
for faction,lists in factories.items():
    for factory,units in lists.items():check(not REMOVED_UNITS.intersection(units),factory+' offers removed unit')

missing=[]
for path in P.rglob('*'):
    if path.suffix not in ['.ini','.gw','.template']:continue
    for line in path.read_text('utf-8-sig').splitlines():
        if line.lstrip().startswith(('#',';')):continue
        for reference in re.findall(r'ROOT:([^\s,\r\n"\x27]+)',line):
            reference=reference.split(':')[0]
            if '${' not in reference and '<UNIT>' not in reference and not (P/reference).is_file():missing.append([str(path.relative_to(P)),reference])
for path,reference in missing:errors.append(path+' missing '+reference)
# Adding and removing the destination tag in one action removes it in the engine.
for source,targets in progression['edges'].items():
    for target in targets:
        action=c.local(P/'Units/Buildings/HQ/Mod/HQ_EraProgression.gw')['action_UC_Advance_'+source+'_To_'+target]
        check(target not in action['removeGlobalTeamTags'].split(','),'Advance removes destination global tag '+target)
        check(target not in action['temporarilyRemoveTags'].split(','),'Advance removes destination unit tag '+target)

# Combat roots must come from a real technology/start roster; shared folders are not roots.
retention=json.loads((O/'entity-retention.json').read_text('utf-8'))
main_units={unit for units in json.loads((O/'main-unlocks.json').read_text('utf-8')).values() for unit in units}
starter_units={'Type74','Type61','FF_S3','FF_4','Wappa','MTank','ZN_APC','MusaiClass','JiccoClass'}
for faction,lists in factories.items():
    for factory,units in lists.items():check(set(units).issubset(main_units),factory+' has production without a retained technology unlock')
ace_units={name for name,records in entities.items() if any('ACE_Unit' in record['tags'].split(',') and '/Pilot/' not in record['path'] for record in records)}
era_labels={}
for name,path in loaded.items():
    relative=path.relative_to(P).as_posix()
    if not relative.startswith('Units/BattleUnits/') or any('/'+part+'/' in relative for part in ['Weapon','Pilot','Shield']):continue
    reasons=retention.get(name,[])
    check(bool(reasons),'Combat unit has no retention evidence '+name)
    if any(reason['kind']=='root' for reason in reasons):
        check(name in main_units|starter_units|ace_units,'Combat unit is an unauthorized folder root '+name)
    origin=origins[relative]['source_package'].rsplit('_',1)[-1]
    core=c.merged(path)['core']
    tags={tag.strip() for tag in core.get('tags','').split(',')}
    if origin in {'0079','0087','0093'} and 'Unit' in tags and tags.intersection({'MS','MA','Ship','Vehicle','Aircraft'}):
        for field in ['displayText','displayText_zh']:
            if core.get(field):check(core[field].endswith('['+origin+']'),name+' lacks era suffix in '+field)
        era_labels[name]=origin
for relative,origin in origins.items():
    if relative.startswith('Units/BattleUnits/') and relative.endswith('_Base.gw'):
        check(c.local(P/relative).get('core',{}).get('dont_load')=='true','Inheritance-only unit template not disabled '+relative)

# Every UC start exposes the shared PMC selection and keeps its no-ally requirement.
pmc_eras=[]
for year in ['0079','0087','0093']:
    definitions=c.effective(loaded['HQ_VS_GE_UC'+year])
    selection=definitions.get('action_ChoseFaction_PMC',{})
    check(selection.get('isVisible')!='false',year+' hides PMC')
    check(selection.get('setResourcesWithLogic')=='FactionIndex=9900101',year+' wrong PMC faction index')
    check('self.numberOfUnitsInAllyNotOwnTeam' in selection.get('isLocked',''),year+' PMC missing ally lock')
    check('self.numberOfUnitsInAllyNotOwnTeam' in selection.get('requireConditional',''),year+' PMC allows selection without an ally')
    conversion=definitions.get('hiddenAction_ConvertToFaction_PMC',{})
    check(conversion.get('convertTo')=='HQ_PMC',year+' missing shared PMC HQ route')
    check(conversion.get('attachments_addNewUnits')=='TechTree_Core_PMC',year+' wrong PMC technology tree')
    check('spawnUnits' not in conversion,year+' PMC gives starting units')
    pmc_eras.append(year)

report={'technology_merges':merges,'main_technology_count':len(all_main),'technology_metrics':metrics,'progression_edges':edges,'era_gap':progression['gap'],'factories':factories,'warning_locations':[str(p.relative_to(P)) for p,_,_ in warnings],'loaded_uc_entities':len(loaded),'era_labels':era_labels,'combat_roots_from_folders':False,'pmc_available_eras':pmc_eras,'missing_active_file_refs':missing,'errors':errors}
(O/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'main':len(all_main),'edges':len(edges),'factories':sum(len(v) for v in factories.values()),'errors':errors},ensure_ascii=False,indent=2))
assert not errors
