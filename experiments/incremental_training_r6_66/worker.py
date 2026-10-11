"""Freeze inherited training mechanics plus R6.64 diagnostics using R6.65 scoring."""
import ast
import os
import sys
import run


def effective_source():
    source = (run.ROOT/'benchmark/results/phase6/r6_59/EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8')
    source = source[:source.index('def diagnostic(track, index):')]
    assert source.count("'round': 'R6.59'") == 1
    source = source.replace("'round': 'R6.59'", "'round': 'R6.66'")
    start = source.index('    lora = LoraConfig(')
    end = source.index('    model = get_peft_model', start)
    source = source[:start] + "    lora = LoraConfig(**read(OUT/'TRAINING-CONFIGURATION.json')['configuration']['adapter_configuration'])\n" + source[end:]
    text = (run.ROOT/'experiments/incremental_training_r6_64/worker.py').read_text(encoding='utf-8')
    function = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == 'diagnostics')
    diagnostics = ast.get_source_segment(text, function)
    source = source + diagnostics + '\n'
    precision = """    precision = read(OUT/'TRAINING-CONFIGURATION.json')['configuration']['precision_runtime']
    torch.backends.cuda.matmul.allow_tf32 = precision['allow_tf32_matmul']
    torch.backends.cudnn.allow_tf32 = precision['allow_tf32_cudnn']
    torch.set_float32_matmul_precision(precision['float32_matmul_precision'])
    torch.use_deterministic_algorithms(precision['deterministic_algorithms'])
"""
    assert source.count('    q52.seed()\n') == 3
    return source.replace('    q52.seed()\n', precision + '    q52.seed()\n')


if __name__ == '__main__':
    assert os.environ.get('LYKOI_R6_66_AUTHORIZED') == '1', 'worker requires separate authorized dispatch'
    run.frozen_check()
    # Execute the frozen file, never dynamically patch a worker after qualification.
    source = (run.OUT/'EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8')
    assert source == effective_source()
    exec(compile(source, 'R6.66-effective-worker', 'exec'), globals())
    mode = sys.argv[1]
    if mode == 'train':
        train()
    elif mode == 'reload':
        reload()
    elif mode in ('base', 'adapter'):
        diagnostics(mode)
    else:
        raise ValueError(mode)
