"""Verified fresh backend endpoint discovery; no cached endpoint is authoritative."""
import json
import re
import subprocess
import time
import urllib.request


def discover(logpath, owned_pid, loaded, digest, weight):
    begin = time.perf_counter()
    starts = []
    for line in logpath.read_text(errors='replace').splitlines():
        if 'msg="starting llama-server"' in line:
            match = re.search(r'--port (\d+) --host 127\.0\.0\.1.*? -c (\d+)', line)
            if match:
                starts.append((int(match[1]), int(match[2]), line))
    if not starts:
        raise RuntimeError('ENDPOINT_NO_START_RECORD')
    port, context, startup = starts[-1]
    script = (f'$owners = @(Get-NetTCPConnection -State Listen -LocalAddress "127.0.0.1" -LocalPort {port} -ErrorAction Stop); '
              'if ($owners.Count -ne 1) { throw "listener cardinality" }; '
              '$ownerId = $owners[0].OwningProcess; '
              'Get-CimInstance Win32_Process -Filter "ProcessId=$ownerId" | '
              'Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Compress')
    process = subprocess.run(['pwsh', '-NoProfile', '-Command', script], capture_output=True, text=True, timeout=30)
    if process.returncode:
        raise RuntimeError('ENDPOINT_LISTENER_UNVERIFIED: ' + process.stderr[:500])
    identity = json.loads(process.stdout)
    command = identity['CommandLine']
    if not (identity['ParentProcessId'] == owned_pid and identity['Name'].lower() == 'llama-server.exe' and
            ('--port ' + str(port)) in command and '--host 127.0.0.1' in command and
            '--offline' in command and ('sha256-' + weight) in command and
            ('-c ' + str(context)) in command):
        raise RuntimeError('ENDPOINT_PROCESS_IDENTITY_MISMATCH')
    models = loaded.get('models', [])
    if not (len(models) == 1 and models[0]['digest'] == digest and models[0]['context_length'] == context):
        raise RuntimeError('ENDPOINT_MODEL_CONTEXT_MISMATCH')
    base = 'http://127.0.0.1:' + str(port)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    def api(path):
        with opener.open(base + path, timeout=15) as response:
            return json.load(response)
    health = api('/health')
    if health.get('status') != 'ok':
        raise RuntimeError('ENDPOINT_HEALTH_UNVERIFIED')
    props = api('/props')
    if props.get('model_path') and ('sha256-' + weight) not in props['model_path']:
        raise RuntimeError('ENDPOINT_BACKEND_MODEL_MISMATCH')
    # Check owner again after HTTP checks to avoid trusting a vanished listener.
    again = subprocess.run(['pwsh', '-NoProfile', '-Command', script], capture_output=True, text=True, timeout=30)
    if again.returncode or json.loads(again.stdout)['ProcessId'] != identity['ProcessId']:
        raise RuntimeError('ENDPOINT_CHANGED_DURING_VERIFICATION')
    return dict(base=base, port=port, context=context, startup=startup, process=identity,
        health=health, props={k: props[k] for k in ('model_path', 'model_alias', 'total_slots') if k in props},
        loaded=loaded, verified=True, verification_seconds=time.perf_counter() - begin,
        verification='fresh log + active loopback listener owner/parent + pinned model path + loaded digest/context + backend health/props + owner recheck')
