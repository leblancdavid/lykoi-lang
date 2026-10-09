"""Post-neutral, model-free SDK/schema diagnosis; no participant retry."""
import json
import os
import subprocess
from common import HERE, save, now, tools
from experiment import configuration, cmd, TEMP

def main():
    label = 'DIAGNOSTIC'
    assert not (HERE / label).exists()
    (HERE / label).mkdir()
    cfg = configuration(label, 'neutral')
    env = os.environ.copy()
    env.update(OPENCODE_CONFIG_CONTENT=json.dumps(cfg), OPENCODE_DISABLE_PROJECT_CONFIG='1',
        OPENCODE_DISABLE_EXTERNAL_SKILLS='1', OPENCODE_DISABLE_CLAUDE_CODE_SKILLS='1', OPENCODE_PURE='1')
    # Resolved config is inspected in memory only; never serialize credentials.
    resolved = cmd(['opencode','debug','config','--pure'], cwd=TEMP, env=env, timeout=60)
    config = json.loads(resolved.stdout)
    save(label + '/RESOLVED-SAFE.json', dict(model=config.get('model'), tools=config.get('tools'),
        permission=config.get('permission'), mcp_names=list(config.get('mcp',{})),
        enabled_mcp={n: x.get('enabled') for n,x in config.get('mcp',{}).items()},
        instructions=config.get('instructions'), agent=config.get('agent',{}).get('r626'),
        credentials_serialized=False))
    listing = cmd(['opencode','mcp','list','--pure','--print-logs','--log-level','ERROR'], cwd=TEMP, env=env, timeout=60)
    (HERE / label / 'MCP-STATUS.txt').write_text(listing.stdout, encoding='utf-8')
    (HERE / label / 'MCP-ERROR.txt').write_text(listing.stderr, encoding='utf-8')
    save(label + '/STATUS.json', dict(timestamp=now(), model_calls=0, returncode=listing.returncode,
        schemas={t['function']['name']: {'root_type':t['function']['parameters'].get('type'), 'keys':list(t['function']['parameters'])} for t in tools.definitions(['value','check','compose'])}))
    print(listing.stdout)
    print(listing.stderr)

if __name__ == '__main__':
    main()
