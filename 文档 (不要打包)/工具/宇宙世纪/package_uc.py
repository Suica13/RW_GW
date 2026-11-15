from pathlib import Path
import json,zipfile,hashlib,os,re
root=Path(__file__).resolve().parents[3]
os.chdir(root)
source=root/'GW_BattleUniverse_DLC_UC'
static=json.loads((root/'output/uc/verification.json').read_text('utf-8'))
runtime=json.loads((root/'output/uc/runtime-check.json').read_text('utf-8'))
assert not static['errors'] and runtime['success'] and runtime['full_suite'] and not runtime['loading_errors']
version=re.search(r'V\d+[A-Za-z0-9]*',(source/'mod-info.txt').read_text('utf-8')).group()
build=root.parent/'build';build.mkdir(exist_ok=True)
artifact=build/('GW_BattleUniverse_DLC_UC_'+version+'.rwmod')
files=sorted(p for p in source.rglob('*') if p.is_file())
with zipfile.ZipFile(artifact,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for path in files:archive.write(path,path.relative_to(source).as_posix())
with zipfile.ZipFile(artifact) as archive:
    assert archive.testzip() is None
    assert len(archive.infolist())==len(files)
    assert 'mod-info.txt' in archive.namelist()
    for path in files:
        assert hashlib.sha256(archive.read(path.relative_to(source).as_posix())).digest()==hashlib.sha256(path.read_bytes()).digest(),path
report={'path':str(artifact),'files':len(files),'bytes':artifact.stat().st_size,'sha256':hashlib.sha256(artifact.read_bytes()).hexdigest(),'requires':'GW_BattleUniverse_Main','incompatible_with':'all other DLC packages','main_technologies':static['main_technology_count'],'era_gap':static['era_gap'],'factory_definitions':sum(len(v) for v in static['factories'].values()),'era_progression_edges':len(static['progression_edges']),'runtime_routes':len(runtime['routes']),'runtime_entries':len(runtime['entries']),'runtime_ai_tests':len(runtime['ai_development']),'runtime_ai_advances':len(runtime['ai_advances']),'runtime_assertions':runtime['assertions'],'loaded_unit_definitions':runtime['unit_count']}
(root/'output/uc/package-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'文档 (不要打包)/工具/宇宙世纪/verification-report.json').write_text(json.dumps({'artifact':report,'static':static,'runtime':runtime,'not_tested':['manual visual inspection in game','multiplayer synchronization','save and reload','full length match balance']},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
