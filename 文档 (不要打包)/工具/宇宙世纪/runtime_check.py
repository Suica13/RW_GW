from pathlib import Path
import json
import os
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
os.chdir(ROOT)
ENGINE = ROOT / 'output/uc/engine'
LOG = ENGINE / 'runtime.log'
LOG.write_text('', encoding='utf-8')
preferences = ENGINE / 'preferences.ini'
settings = preferences.read_text('utf-8').replace('|disabled', '|enabled').replace('loadDisabledModData:false', 'loadDisabledModData:true')
settings = re.sub(r'(?m)^(numIncompleteLoadAttempts|numLoadsSinceRunningGameOrNormalExit):.*$', r'\1:0', settings)
preferences.write_text(settings, encoding='utf-8')
command = [str(ROOT.parents[1] / 'jvm64/bin/java.exe'), '-Xmx3072M', '-Dfile.encoding=UTF-8', '-Djava.library.path=.', '-cp', 'game-lib.jar;libs/*;../classes', 'UCTestMain', '-nodisplay', '-nosound', '-nologfile', '-log', str(LOG)]
started = time.time()
console = ENGINE / 'runtime-console.log'
with console.open('wb') as sink:
    process = subprocess.Popen(command, cwd=ENGINE, stdout=sink, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        code = process.wait(timeout=900)
    except subprocess.TimeoutExpired:
        process.kill()
        code = process.wait()
text = console.read_text('utf-8', errors='replace') + '\n' + LOG.read_text('utf-8', errors='replace')
lines = text.splitlines()
def matching(marker):
    return [line for line in lines if marker in line]
loading_errors = list(dict.fromkeys(line[:500] for line in lines if any(marker in line for marker in ['Error while loading', 'Adding error for mod:', 'Failed to open'])))
unit_counts = re.findall(r'UC_UNIT_COUNT (\d+)', text)
result = {
    'exit_code': code,
    'elapsed': round(time.time() - started, 1),
    'loaded': matching('Loading units from mod:'),
    'unit_count': int(unit_counts[-1]) if unit_counts else None,
    'assertions': len(matching('UC_ASSERT_PASS')),
    'technology_merges': matching('UC_TECH_MERGE_PASS'),
    'production_cases': matching('UC_PRODUCTION_PASS'),
    'unit_forms': matching('UC_FORM_PASS'),
    'pmc_entries': matching('UC_PMC_PASS'),
    'pmc_borrow': matching('UC_PMC_BORROW_PASS'),
    'routes': matching('UC_ROUTE_PASS'),
    'entries': matching('UC_ENTRY_PASS'),
    'ai_development': matching('UC_AI_PASS'),
    'ai_advances': matching('UC_AI_ADVANCE_PASS'),
    'failures': [line[:1000] for line in lines if 'UC_ASSERT_FAIL' in line or 'UC_RUNTIME_FAILURE' in line],
    'initialized': 'Init completed' in text,
    'loading_errors': loading_errors,
    'success': 'UC_RUNTIME_SUCCESS' in text,
}
fixture_names = [('technology_merges', 'tech-merge-cases.txt', 2), ('production_cases', 'tech-merge-production.txt', 1), ('unit_forms', 'tech-merge-forms.txt', 1)]
result['technology_suite'] = all((ROOT / 'output/uc' / filename).is_file() and len(result[field]) == len((ROOT / 'output/uc' / filename).read_text('utf-8').splitlines()) * multiplier for field, filename, multiplier in fixture_names)
result['pmc_suite'] = len(result['pmc_entries']) == 6 and len(result['pmc_borrow']) == 1
result['full_suite'] = result['pmc_suite'] and len(result['entries']) == 14 and len(result['routes']) == 10 and len(result['ai_development']) == 9
(ROOT / 'output/uc/runtime-check.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
assert result['success'] and not result['failures'] and not loading_errors
assert result['unit_count'] < 3000
assert len([line for line in result['loaded'] if 'GW_BattleUniverse' in line]) == 2
