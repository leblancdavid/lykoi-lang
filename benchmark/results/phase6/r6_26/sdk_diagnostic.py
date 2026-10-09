"""Collect only MCP diagnostic log lines, with no inference or secret export."""
import json
import os
from common import HERE, save, now
from experiment import configuration, cmd, TEMP

def main():
    label = 'SDK-DIAGNOSTIC'
    assert not (HERE / label).exists()
    (HERE / label).mkdir()
    cfg = configuration(label, 'neutral')
    # The first diagnostic showed inherited MCP servers. Disable their connections
    # for this model-free probe; participant permissions had already denied them.
    for name in ('codegraphcontext','shadcn','pixellab'):
        cfg['mcp'][name] = {'enabled':False}
    env = os.environ.copy()
    env.update(OPENCODE_CONFIG_CONTENT=json.dumps(cfg), OPENCODE_DISABLE_PROJECT_CONFIG='1',
        OPENCODE_DISABLE_EXTERNAL_SKILLS='1', OPENCODE_DISABLE_CLAUDE_CODE_SKILLS='1', OPENCODE_PURE='1')
    out = cmd(['opencode','mcp','list','--pure','--print-logs','--log-level','DEBUG'], cwd=TEMP, env=env, timeout=60)
    lines = [s for s in out.stderr.splitlines() if 'service=mcp' in s or 'Failed to get tools' in s]
    save(label + '/DIAGNOSTIC.json', dict(timestamp=now(), model_calls=0, returncode=out.returncode,
        selected_log_lines=lines, config_override=cfg, cause='See exact SDK log; no schema or semantic changes'))
    print(json.dumps(lines, ensure_ascii=True, indent=2))

if __name__ == '__main__':
    main()
