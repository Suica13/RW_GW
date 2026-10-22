"""Headless load verification in isolated folders; never edits original game preferences.

Usage: python 验证_0093引擎加载.py --case main|0093|mixed|cr_p1|mixed_cr_p1
Requires the local game and Windows junction support.
"""
from pathlib import Path
import argparse,base64,hashlib,json,os,re,shutil,subprocess,time

ROOT=Path(__file__).resolve().parents[2]
GAME=ROOT.parents[1]
BASE=Path(__file__).resolve().parent/'0093_loadtest'
CASES={'main':['Main'],'0093':['Main','DLC_0093'],
       'mixed':['Main','DLC_0079','DLC_0087','DLC_SEED','DLC_0093'],
       'cr_p1':['Main','DLC_CR_P1'],
       'mixed_cr_p1':['Main','DLC_0079','DLC_0087','DLC_SEED','DLC_0093','DLC_CR_P1']}

def link(target,path):
    if path.exists():
        assert path.resolve()==target.resolve(),path
        return
    path.parent.mkdir(parents=True,exist_ok=True)
    quote=lambda p:"'"+str(p).replace("'","''")+"'"
    command='New-Item -ItemType Junction -Path '+quote(path)+' -Target '+quote(target)+' | Out-Null'
    subprocess.run(['powershell','-NoProfile','-EncodedCommand',base64.b64encode(command.encode('utf-16le')).decode()],check=True,capture_output=True)

def run(case):
    packs=['GW_BattleUniverse_'+p for p in CASES[case]]
    sandbox=BASE/('verify_'+case);sandbox.mkdir(parents=True,exist_ok=True)
    for name in ['assets','res','font','libs']:link(GAME/name,sandbox/name)
    for f in GAME.iterdir():
        if f.is_file() and (f.suffix=='.dll' or f.name in ['game-lib.jar','steam_appid.txt']):shutil.copy2(f,sandbox/f.name)
    for name in packs:link(ROOT/name,sandbox/'mods/units'/name)
    settings=','.join(name+'|'+hashlib.sha256(name.encode()).hexdigest().upper()+'|enabled' for name in packs)
    (sandbox/'preferences.ini').write_text('[settings]\nloadDisabledModData:false\nmodSettingsVersion:1\nlastModCount:'+str(len(packs)+1)+'\nmodSettings:'+settings+'\n',encoding='utf-8')
    log=sandbox/'engine.log';console=sandbox/'console.log'
    cmd=[str(GAME/'jvm64/bin/java.exe'),'-Xmx4096M','-Dfile.encoding=UTF-8','-Djava.library.path=.',
         '-cp','game-lib.jar;libs/*','com.corrodinggames.rts.java.Main','-nodisplay','-nosound','-nologfile','-log',str(log),'-printunits']
    start=time.time();timedout=False
    with console.open('wb') as output:
        process=subprocess.Popen(cmd,cwd=sandbox,stdout=output,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        while process.poll() is None and time.time()-start < 150:
            time.sleep(1)
            content=log.read_text('utf-8',errors='replace') if log.exists() else ''
            if 'Init completed' in content:
                time.sleep(1)
                if process.poll() is None:process.terminate()
                break
        if process.poll() is None:
            if 'Init completed' not in (log.read_text('utf-8',errors='replace') if log.exists() else ''):timedout=True
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:process.kill()
        code=process.wait()
    content=(log.read_text('utf-8',errors='replace') if log.exists() else '')+'\n'+console.read_text('utf-8',errors='replace')
    lines=content.splitlines()
    errors=list(dict.fromkeys(line for line in lines if re.search(r'Error while loading|Adding error for mod|alert:Error|java\.lang\..*(?:Exception|Error)|Exception:|Missing unit|Failed to open',line)))
    enabled={name:any("Mod: '"+name+"_V159' - Memory use:" in line and '(disabled)' not in line for line in lines) for name in packs}
    initialized='Init completed' in content
    summary={'case':case,'passed':initialized and all(enabled.values()) and not errors and not timedout,
             'initialized':initialized,'enabled':enabled,'errors':errors,'timed_out':timedout,
             'returncode':code,'elapsed_seconds':round(time.time()-start,1),
             'log':str(log.relative_to(ROOT))}
    (sandbox/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report=ROOT/'文档 (不要打包)/分析'/('0093_引擎加载_'+case+'.json')
    report.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
    return 0 if summary['passed'] else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--case',choices=CASES,required=True)
    raise SystemExit(run(parser.parse_args().case))
