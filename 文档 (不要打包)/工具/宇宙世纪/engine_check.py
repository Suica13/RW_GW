from pathlib import Path
import os
os.chdir(Path(__file__).resolve().parents[3])
from pathlib import Path
import subprocess,time,re,json
root=Path.cwd();game=root/'output/uc/engine'
for p in (game/'mods/units').iterdir():
 assert p.resolve()==(root/p.name).resolve(),p
log=game/'control-fix-engine.log';console=game/'control-fix-console.log'
cmd=[str(Path.cwd().parents[1]/'jvm64/bin/java.exe'),'-Xmx3072M','-Dfile.encoding=UTF-8','-Djava.library.path=.','-cp','game-lib.jar;libs/*','com.corrodinggames.rts.java.Main','-nodisplay','-nosound','-nologfile','-log',str(log),'-printunits']
prefs=game/'preferences.ini'
settings=prefs.read_text('utf-8').replace('|disabled','|enabled').replace('loadDisabledModData:false','loadDisabledModData:true')
settings=re.sub(r'(?m)^(numIncompleteLoadAttempts|numLoadsSinceRunningGameOrNormalExit):.*$',r'\1:0',settings)
prefs.write_text(settings,encoding='utf-8')
log.write_text('',encoding='utf-8')
start=time.time();initialized=False;timedout=False
with console.open('wb') as sink:
 p=subprocess.Popen(cmd,cwd=game,stdout=sink,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 try:
  while p.poll() is None:
   t=log.read_text('utf-8',errors='replace') if log.exists() else ''
   if 'Init completed' in t:initialized=True;time.sleep(1);break
   if time.time()-start>240:timedout=True;break
   time.sleep(1)
 finally:
  if p.poll() is None:p.terminate()
  try:p.wait(timeout=8)
  except subprocess.TimeoutExpired:p.kill();p.wait()
t=(log.read_text('utf-8',errors='replace') if log.exists() else '')+'\n'+console.read_text('utf-8',errors='replace')
errors=list(dict.fromkeys(x for x in t.splitlines() if re.search(r'Error while loading|Adding error for mod|alert:Error|java\.lang\..*(?:Exception|Error)|Exception:|Missing unit|Failed to open',x)))
summary={'initialized':initialized,'timed_out':timedout,'elapsed':round(time.time()-start,1),'loaded':[x for x in t.splitlines() if 'Loading units from mod:' in x],'errors':errors}
(root/'output/uc/engine-check.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2),flush=True)
assert 'starting game in safe mode' not in t and not re.search(r'Disabled mod at:.*GW_BattleUniverse',t)
assert len([line for line in summary['loaded'] if 'GW_BattleUniverse' in line])==2 and initialized and all(any(pack.name in line for line in summary['loaded']) for pack in (game/'mods/units').iterdir()) and not errors and not timedout, 'Engine load failed'
