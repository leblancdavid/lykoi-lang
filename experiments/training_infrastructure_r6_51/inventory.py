"""Read-only host probes; writes only the round-local inventory, no model loading."""
import importlib.util
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from convert import OUT, write


def command(args):
    try:
        proc = subprocess.run(args, capture_output=True, timeout=60)
        def decode(data):
            return data.decode('utf-16-le' if b'\x00' in data else 'utf-8', errors='replace').strip()
        return {'argv': args, 'returncode': proc.returncode,
                'stdout': decode(proc.stdout), 'stderr': decode(proc.stderr)}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'argv': args, 'error': type(exc).__name__ + ': ' + str(exc)}


def main():
    ps = "Get-CimInstance Win32_Processor | Select-Object Name,Architecture,NumberOfCores,NumberOfLogicalProcessors | ConvertTo-Json; Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory | ConvertTo-Json; Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,OSArchitecture,FreePhysicalMemory | ConvertTo-Json; Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | Select-Object DeviceID,Size,FreeSpace | ConvertTo-Json"
    packages = {}
    for name, module in [('torch', 'torch'), ('transformers', 'transformers'), ('peft', 'peft'),
                         ('trl', 'trl'), ('accelerate', 'accelerate'), ('bitsandbytes', 'bitsandbytes'),
                         ('datasets', 'datasets'), ('safetensors', 'safetensors'), ('tokenizers', 'tokenizers'),
                         ('jsonschema', 'jsonschema')]:
        try:
            version = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            version = None
        packages[name] = {'version': version, 'module_discoverable': importlib.util.find_spec(module) is not None,
                          'training_tested': False}
    probes = [command(['pwsh', '-NoProfile', '-Command', ps]),
              command(['nvidia-smi', '--query-gpu=name,memory.total,memory.free,driver_version', '--format=csv']),
              command(['nvcc', '--version']), command(['py', '--list']),
              command(['wsl', '--status']), command(['wsl', '--list', '--verbose']),
              command(['ollama', 'list']), command(['ollama', '--version']),
              command(['ollama', 'show', 'qwen2.5-coder:1.5b-base'])]
    # Conventional cache locations only; not an exhaustive all-disk search.
    cache = Path.home() / '.cache/huggingface/hub'
    cache_names = sorted(p.name for p in cache.glob('models--*')) if cache.exists() else []
    result = {'round': 'R6.51', 'utc': datetime.now(timezone.utc).isoformat(),
        'python': {'version': platform.python_version(), 'executable': sys.executable,
                   'machine': platform.machine(), 'prefix': sys.prefix, 'base_prefix': sys.base_prefix},
        'libraries': packages, 'probes': probes, 'huggingface_cache_model_directories': cache_names,
        'weight_inventory_scope': 'Ollama list, conventional user HF cache, repository venv search; other external environments and custom weight directories not exhaustively inspected',
        'trainable_candidate_checkpoint_verified_local': False,
        'cuda_tensor_allocation_test': 'NOT_RUN: torch absent', 'bf16_allocation_test': 'NOT_RUN',
        'software_changes': 0, 'weight_downloads': 0, 'training_runs': 0}
    write(OUT / 'INVENTORY.json', result)
    print(json.dumps({'python': result['python'], 'libraries': packages, 'probes': probes}, indent=2))


if __name__ == '__main__':
    main()
