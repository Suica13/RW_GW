"""Run using rw-modding-mcp/.venv/Scripts/python.exe; MOD files are read only."""
import asyncio
import json
import os
from pathlib import Path
import tempfile
import tomllib
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[2]
TOOL = Path(__file__).resolve().parent / 'rw-modding-mcp'

def payload(result):
    assert not getattr(result, 'is_error', getattr(result, 'isError', False)), result
    structured = getattr(result, 'structured_content', getattr(result, 'structuredContent', None))
    if structured is not None:
        return structured
    return json.loads(next(c.text for c in result.content if c.type == 'text'))

async def main():
    with (ROOT / '.codex' / 'config.toml').open('rb') as f:
        config = tomllib.load(f)['mcp_servers']['rusted-warfare']
    params = StdioServerParameters(command=config['command'], args=config['args'],
        cwd=config['cwd'], env={**os.environ, **config.get('env', {})})
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as s:
            await s.initialize()
            names = {t.name for t in (await s.list_tools()).tools}
            assert names == {'lookup_key', 'get_ref', 'search_source', 'lint', 'explain_actions'}, names
            print('PASS initialize + five tools')
            data = payload(await s.call_tool('lookup_key', {'key': 'canAttack'}))
            assert data['ok'] and data['found'] and data['sources']['jar'], data
            print('PASS lookup_key: tables + game JAR')
            data = payload(await s.call_tool('lookup_key',
                {'keys': ['canAttack', 'maxHp', '_definitely_missing_key_']}))
            assert data['ok'] and data['count'] == 3 and data['found'] == 2, data
            assert data['missing'] == ['_definitely_missing_key_'], data
            assert data['results']['canAttack']['found'], data
            print('PASS lookup_key: batch lookup + missing key')
            data = payload(await s.call_tool('get_ref', {}))
            assert data['ok'] and data['counts']['events'] == 18, data
            print('PASS get_ref')
            data = payload(await s.call_tool('search_source',
                {'pattern': 'addBooleanType', 'max_results': 1}))
            assert data['ok'] and data['files_scanned'] > 0 and data['total_matches'] > 0, data
            print('PASS search_source: local source index')
            explained = payload(await s.call_tool('explain_actions', {'path': str(TOOL / 'tests' / 'fixtures' / 'explain_loop_no_reset.ini')}))
            assert explained['ok'], explained
            print('PASS explain_actions: action graph')
            fixture = TOOL / 'tests' / 'fixtures' / 'good_minimal.ini'
            data = payload(await s.call_tool('lint', {'path': str(fixture)}))
            assert data['ok'] and data['files'] == 1 and data['errors'] == 0, data
            print('PASS lint: valid INI fixture')
            data = payload(await s.call_tool('lint', {'paths': [str(fixture),
                str(TOOL / 'tests' / 'fixtures' / 'bad_event_name.ini')], 'max_issues': 10}))
            assert data['ok'] and data['files'] == 2 and data['errors'] > 0, data
            assert data['issues'] and all(0 <= i['f'] < len(data['issue_files'])
                and 'file' not in i for i in data['issues']), data
            print('PASS lint: batch paths + compact issue file indexes')
            with tempfile.TemporaryDirectory(prefix='rw-mcp-gw-') as temp:
                (Path(temp) / 'sample.gw').write_bytes(fixture.read_bytes())
                data = payload(await s.call_tool('lint', {'path': temp}))
                assert data['ok'] and data['files'] == 1 and data['errors'] == 0, data
            print('PASS lint: .gw directory scan')
            target = ROOT / 'GW_BattleUniverse_DLC_0079' / 'Units' / 'BattleUnits' / 'RGM_79'
            data = payload(await s.call_tool('lint', {'path': str(target), 'max_issues': 3}))
            assert data['ok'] and data['files'] > 0, data
            print('PASS project read: files=%s errors=%s warnings=%s (diagnostics only)' %
                  (data['files'], data['errors'], data['warnings']))

if __name__ == '__main__':
    asyncio.run(asyncio.wait_for(main(), timeout=150))
