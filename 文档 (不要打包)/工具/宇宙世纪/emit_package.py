# Executed by build_uc.py. Runtime files use the same layout as the source DLCs.
PRIORITY = {'Main':0, '0079':1, '0087':2, '0093':3}
CUSTOM_PATHS = {
    'UC/TechTree_Core_UC.ini': 'Units/TechTree/Core/TechTree_Core_UC.ini',
    'UC/UnlockedListMarker_UC.ini': 'Units/TechTree/UnlockedListMarker/UnlockedListMarker_UC.ini',
    'UC/HQ_EraProgression.gw': 'Units/Buildings/HQ/Mod/HQ_EraProgression.gw',
    'UC/DLCMarker_UC.ini': 'Units/DLCMarker/DLCMarker_UC.ini',
}
for faction in FAC:
    CUSTOM_PATHS[f'UC/TechTree_UI_Page_UC_{faction}.ini'] = f'Units/TechTree/Core/Faction/{faction}/TechTree_UI_Page_UC_{faction}.ini'
WARNING_PATH = 'Resource/Image/UI/UC_LoadWarning.png'

# Include the Main resource icons used by the common all-units.template.
for reference in re.findall(r'ROOT:([^\s,\r\n"\x27]+)', DB[('Main','all-units.template')]):
    reference = reference.replace('\\','/')
    source = PACKS['Main']/reference
    if source.is_file():
        ASSETS[('Main',reference)] = source

# Identical shared templates are emitted once. Dependencies and image/audio bytes are
# included in the signature, so same-text templates with different era resources stay separate.
import functools
active_keys={selected for name,selected in SELECTED.items() if name in KEEP_VISITED}
asset_bytes={key:source.read_bytes() for key,source in ASSETS.items()}
asset_signatures={(key[0],key[1].lower()):hashlib.sha256(data).hexdigest() for key,data in asset_bytes.items()}

def signature_reference(era,path,reference):
    reference=reference.replace('\\','/').strip()
    if reference.startswith('ROOT:UC/'):
        return ('Main',reference[5:])
    if reference.startswith('ROOT:Source/'):
        source_era,relative=reference[12:].split('/',1)
    elif reference.startswith('ROOT:'):
        source_era,relative=era,reference[5:].lstrip('/')
    else:
        source_era=era
        relative=(PACKS[era]/Path(path).parent/reference).resolve().relative_to(PACKS[era]).as_posix()
    return CANON.get((source_era,relative.lower()),(source_era,relative))

@functools.lru_cache(None)
def configuration_signature(key):
    era,path=key
    text=DB[key]
    inherited=local(text).get('core',{}).get('copyFrom')
    if inherited is not None:
        references=[]
        for reference in inherited.split(','):
            reference=reference.strip()
            if not reference:continue
            if reference.startswith(('CORE:','SHARED:')):
                references.append(reference)
            else:
                dependency=signature_reference(era,path,reference)
                references.append(configuration_signature(dependency) if dependency in INCLUDED else str(dependency))
        text=edit(text,'core','copyFrom','|'.join(references))
    def normalize(match):
        parts=match[1].split(':',1)
        reference=parts[0]
        suffix=':'+parts[1] if len(parts)>1 else ''
        dependency=signature_reference(era,path,'ROOT:'+reference)
        if dependency==key:return 'SELF_FILE'+suffix
        if dependency in INCLUDED:return 'CONFIG_'+configuration_signature(dependency)+suffix
        asset=asset_signatures.get((dependency[0],dependency[1].lower()))
        return 'ASSET_'+asset+suffix if asset else match[0]
    text=re.sub(r'ROOT:([^\s,\r\n"\x27]+)',normalize,text)
    load_role='active' if key in active_keys or path.startswith('UC/') else 'inheritance'
    return hashlib.sha256((load_role+'\n'+text).encode('utf-8')).hexdigest()

config_outputs={}
config_representatives={}
config_groups=collections.defaultdict(list)
for key in INCLUDED:
    era,path=key
    if path in CUSTOM_PATHS:
        relative=CUSTOM_PATHS[path]
        config_outputs[key]=relative
        config_representatives[relative]=key
    else:
        config_groups[path.lower()].append(key)
for group in config_groups.values():
    group.sort(key=lambda key:PRIORITY[key[0]],reverse=True)
    primary=group[0][1]
    equivalents={}
    for index,key in enumerate(group):
        signature=configuration_signature(key)
        if signature in equivalents:
            relative=equivalents[signature]
        else:
            path=Path(primary)
            relative=primary if index==0 else str(path.with_name(path.stem+'_'+key[0]+path.suffix)).replace('\\','/')
            equivalents[signature]=relative
            config_representatives[relative]=key
        config_outputs[key]=relative

def canonical_key(key):
    return CANON.get((key[0],key[1].lower()),key)

def config_path(key):
    key = canonical_key(key)
    return config_outputs[key]

def source_key(era,path,reference):
    reference = reference.replace('\\','/').strip()
    if reference.startswith('ROOT:UC/'):
        return ('Main',reference[5:])
    if reference.startswith('ROOT:Source/'):
        mod,relative = reference[12:].split('/',1)
        return canonical_key((mod,relative))
    if reference.startswith('ROOT:'):
        return canonical_key((era,reference[5:].lstrip('/')))
    relative = (PACKS[era]/Path(path).parent/reference).resolve().relative_to(PACKS[era]).as_posix()
    return canonical_key((era,relative))

outputs = {}
asset_outputs = {}
asset_groups = collections.defaultdict(list)
for key in ASSETS:
    asset_groups[key[1].lower()].append(key)
for group in asset_groups.values():
    group.sort(key=lambda key: PRIORITY[key[0]], reverse=True)
    primary = group[0][1]
    same_content = {}
    for index,key in enumerate(group):
        data = asset_bytes[key]
        digest = hashlib.sha256(data).hexdigest()
        if digest in same_content:
            relative = same_content[digest]
        else:
            path = Path(primary)
            relative = primary if index==0 else str(path.with_name(path.stem+'_'+key[0]+path.suffix)).replace('\\','/')
            same_content[digest] = relative
            assert relative not in outputs or outputs[relative]==data, relative
            outputs[relative] = data
        asset_outputs[(key[0],key[1].lower())] = relative

# Keep file names recognizable. Only actual same-path collisions receive era suffixes.
def rewrite_references(text,era):
    def replace(match):
        reference = match[1].replace('\\','/').lstrip('/')
        suffix = ''
        if ':' in reference:
            reference,volume = reference.split(':',1)
            suffix = ':'+volume
        source_era = era
        if reference.startswith('Source/'):
            source_era,reference = reference[7:].split('/',1)
        if reference=='UC/ExclusiveLoadWarning.png':
            return 'ROOT:'+WARNING_PATH+suffix
        if reference in CUSTOM_PATHS:
            return 'ROOT:'+CUSTOM_PATHS[reference]+suffix
        key = canonical_key((source_era,reference))
        if key in config_outputs:
            return 'ROOT:'+config_outputs[key]+suffix
        asset = asset_outputs.get((source_era,reference.lower()))
        if asset:
            return 'ROOT:'+asset+suffix
        # Only inactive legacy comments should reach this fallback; the verifier checks active lines.
        return 'ROOT:'+reference+suffix
    return re.sub(r'ROOT:([^\s,\r\n"\x27]+)',replace,text)

for key in sorted(INCLUDED):
    era,path = key
    if config_representatives[config_path(key)]!=key:
        continue
    text = DB[key]
    values = local(text)
    named = [name for name,selected_key in SELECTED.items() if selected_key==key and name in KEEP_VISITED]
    if path.endswith('.ini'):
        text = edit(text,'core','dont_load','false' if named or path.startswith('UC/') else 'true')
    text = re.sub(r'(?m)^overrideAndReplace:([^\n]+)',lambda m:m[0] if any(r['era']=='Main' for r in ENT.get(m[1].strip(),[])) or m[1].strip() not in ENT else '',text)
    if named and era=='Main':
        text = edit(text,'core','overrideAndReplace',named[0])
    if 'copyFrom' in values.get('core',{}):
        references = []
        for old_reference in values['core']['copyFrom'].split(','):
            old_reference = old_reference.strip()
            if not old_reference:
                continue
            if old_reference.startswith(('CORE:','SHARED:')):
                references.append(old_reference)
            else:
                references.append('ROOT:'+config_path(source_key(era,path,old_reference)))
        text = edit(text,'core','copyFrom','"""\n'+',\n'.join(references)+'\n"""')
    # copyFrom has already been resolved; protect those mapped references from a second era lookup.
    copy_value = local(text).get('core',{}).get('copyFrom')
    if copy_value is not None:
        text = edit(text,'core','copyFrom','UC_COPY_FROM_SENTINEL')
    text = rewrite_references(text,era)
    if copy_value is not None:
        text = edit(text,'core','copyFrom','"""\n'+copy_value+'\n"""')
    relative = config_path(key)
    data = text.replace('\n','\r\n').encode('utf-8')
    assert relative not in outputs, relative
    outputs[relative] = data

outputs['all-units.template'] = rewrite_references(DB[('Main','all-units.template')],'Main').replace('\n','\r\n').encode('utf-8')
outputs[WARNING_PATH] = (OUT/'ExclusiveLoadWarning.png').read_bytes()
outputs['mod-thumbnail.png'] = (PACKS['Main']/'mod-thumbnail.png').read_bytes()
release_version=re.search(r'V\d+[A-Za-z0-9]*',(PACKS['Main']/'mod-info.txt').read_text('utf-8-sig'))[0]
outputs['mod-info.txt'] = '''[mod]
title: 高达战争_宇宙世纪包 UC_RELEASE_VERSION / Universal Century DLC
description:0079 / 0087 / 0093主线战役。必须启用Main，请勿与其他DLC同时加载。\\nRequires Main. Do not enable any other DLC.
minVersion:1.15p11
thumbnail:mod-thumbnail.png
'''.replace('UC_RELEASE_VERSION',release_version).replace('\n','\r\n').encode('utf-8')
outputs['uc-source-map.json'] = json.dumps({config_path(key):{'source_package':PACKS[key[0]].name,'source_path':key[1]} for key in sorted(INCLUDED) if config_representatives[config_path(key)]==key},ensure_ascii=False,indent=2).encode('utf-8')

manifest = OUT/'generated-manifest.json'
if manifest.exists():
    for relative in json.loads(manifest.read_text('utf-8')):
        target = DEST/relative
        assert target.resolve().is_relative_to(DEST.resolve())
        if relative not in outputs and target.is_file():
            target.unlink()
for relative,data in outputs.items():
    target = DEST/relative
    assert target.resolve().is_relative_to(DEST.resolve())
    target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists() or target.read_bytes()!=data:
        target.write_bytes(data)
for directory in sorted((p for p in DEST.rglob('*') if p.is_dir()),key=lambda p:len(p.parts),reverse=True):
    assert directory.resolve().is_relative_to(DEST.resolve())
    if not any(directory.iterdir()):
        directory.rmdir()
manifest.write_text(json.dumps(sorted(outputs),ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'main-unlocks.json').write_text(json.dumps(UNLOCKS,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'removed-ids.json').write_text(json.dumps(sorted(BAD_IDS),indent=2),encoding='utf-8')
(OUT/'selected-entities.json').write_text(json.dumps(sorted(KEEP_VISITED),indent=2),encoding='utf-8')
(OUT/'build-report.json').write_text(json.dumps({'entities':len(KEEP_VISITED)+len(CUSTOM),'configs':len(INCLUDED),'files':len(outputs),'missing_copyFrom':missing,'size_bytes':sum(len(data) for data in outputs.values()),'main_technologies':len(TECHS),'source_roots':{era:str(path) for era,path in PACKS.items()}},ensure_ascii=False,indent=2),encoding='utf-8')
print('UC package generated:',len(outputs),'files;',len(KEEP_VISITED)+len(CUSTOM),'entities; missing inheritance:',len(missing))
