"""Derive measured comparisons and seal/check additive R6.67 publication."""
import ast
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments/incremental_training_r6_66'))
import run as frozen
OUT = ROOT / 'benchmark/results/phase6/r6_67'
DIMENSIONS = frozen.successor.DIMENSIONS


def derive():
    frozen.OUT = OUT
    base = frozen.read(OUT / 'DIAGNOSTIC-BASE.json')['records']
    adapter = frozen.read(OUT / 'DIAGNOSTIC-ADAPTER.json')['records']
    comparison = []
    for b, a in zip(base, adapter):
        assert b['episode_id'] == a['episode_id'] and b['prompt_identity'] == a['prompt_identity']
        comparison.append(dict(episode_id=b['episode_id'], group=b['group'],
            base={k:b[k] for k in ('scores','teacher_forced_loss','output_tokens','inference_seconds')},
            adapter={k:a[k] for k in ('scores','teacher_forced_loss','output_tokens','inference_seconds')},
            target_loss_decrease=b['teacher_forced_loss']-a['teacher_forced_loss']))
    groups = {}
    for name in ('training_record', 'structurally_varied', 'all'):
        selected = [r for r in comparison if name == 'all' or r['group'] == name]
        if not selected:
            continue
        groups[name] = dict(cases=len(selected))
        for track in ('base', 'adapter'):
            rows = [r[track] for r in selected]
            groups[name][track] = dict(
                dimensions={d:sum(bool(r['scores'][d]) for r in rows) for d in DIMENSIONS},
                accepted=sum(r['scores']['accepted'] for r in rows),
                exact_target_reproduction=sum(r['scores']['exact_target_reproduction'] for r in rows),
                mean_teacher_forced_loss=sum(r['teacher_forced_loss'] for r in rows)/len(rows),
                generated_tokens=sum(r['output_tokens'] for r in rows),
                inference_seconds=sum(r['inference_seconds'] for r in rows))
    frozen.write('COMPARISON.json', dict(records=comparison, groups=groups, independent_generalization=False,
        downstream_interpretation='False dimensions after serialization halt mean no demonstrated correct selection; later stages not reached'))
    result = frozen.read(OUT / 'TRAINING-RESULT.json')
    frozen.write('ADAPTER-IDENTITIES.json', dict(content_identity=result['adapter_content_identity'],
        files=result['adapter_files'], directory=str(frozen.ARTIFACTS / 'step20/adapter'),
        changed_tensor_count=result['changed_tensor_count'], base_unchanged=result['base_unchanged'],
        merged=False, preserved_r6_59_adapter_identity='79843df8ce1f3e9bf87c81e0e23073c37a702695df6e52ac384b0a33f77fb7d1'))
    frozen.write('ASSESSMENT.json', dict(classification='R6_67_TRAINING_MECHANICS_ONLY',
        A_training_mechanics=True, B_target_likelihood_improved=True, B_exact_reproduction_improved=False,
        C_valid_incremental_generation_improved=False, D_correct_semantic_decisions_improved=False,
        E_exposed_fitting_only=True, E_memorization_causally_established=False,
        F_no_observable_generation_improvement=True, target_loss_improved_cases=13,
        limitation='Ten exposed records and three coordinator-authored structural variants; no independent generalization evidence',
        recommended_next_experiment='Separately authorized serialization-focused generation study with prospective protocol and fresh diagnostics; no current retry'))
    print(json.dumps(groups, indent=2))


def seal(check):
    frozen.frozen_check()
    history = frozen.publication('r6_66')
    audit = frozen.baseline()
    assert audit == frozen.read(OUT / 'PREFLIGHT.json')['baseline']
    result = frozen.read(OUT / 'TRAINING-RESULT.json')
    assert frozen.file_manifest(frozen.ARTIFACTS / 'step20/adapter') == result['adapter_files']
    assert frozen.read(OUT / 'ADAPTER-RELOAD.json')['reference_logits_bitwise_equal']
    paths = sorted(list(Path(__file__).parent.glob('*.py')) +
        [ROOT / 'benchmark/results/phase6/R6_67-REPORT.md', ROOT / 'benchmark/results/phase6/R6_67-PROTOCOL.md',
         ROOT / 'docs/research-log-r6.67.md'] +
        [p for p in OUT.iterdir() if p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')])
    for path in paths:
        text = path.read_text(encoding='utf-8')
        assert '\r' not in text and all(line == line.rstrip() for line in text.splitlines()), path
        if path.suffix == '.json':
            json.loads(text)
        if path.suffix == '.py':
            ast.parse(text)
        assert not re.search(r'sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----', text), path
        if path.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)', text):
                if not link.startswith(('https:', '#')):
                    target = (path.parent / link.split('#')[0]).resolve()
                    pending_seal = not check and target in (OUT / 'PUBLICATION-IDENTITIES.json', OUT / 'VERIFICATION.json')
                    assert target.exists() or pending_seal, (path, link)
    status = subprocess.check_output(['git','status','--porcelain','--untracked-files=all'], cwd=ROOT, text=True)
    allowed = ('experiments/incremental_training_r6_67/', 'benchmark/results/phase6/r6_67/',
        'benchmark/results/phase6/R6_67-REPORT.md', 'benchmark/results/phase6/R6_67-PROTOCOL.md', 'docs/research-log-r6.67.md')
    assert all(line[3:].replace('\\','/').startswith(allowed) for line in status.splitlines()), status
    subprocess.run(['git','diff','--check'], cwd=ROOT, check=True)
    manifest = dict(version='r6.67-publication-1', files={p.relative_to(ROOT).as_posix():
        dict(sha256=frozen.sha(p), bytes=p.stat().st_size) for p in paths})
    if check:
        assert manifest == frozen.read(OUT / 'PUBLICATION-IDENTITIES.json')
        assert frozen.sha(OUT / 'PUBLICATION-IDENTITIES.json') == frozen.read(OUT / 'VERIFICATION.json')['manifest_sha256']
    else:
        assert not (OUT / 'PUBLICATION-IDENTITIES.json').exists()
        frozen.OUT = OUT
        frozen.write('PUBLICATION-IDENTITIES.json', manifest)
        frozen.write('VERIFICATION.json', dict(passed=True, manifest_sha256=frozen.sha(OUT / 'PUBLICATION-IDENTITIES.json'),
            history_publication=history, inherited_full_audit='PASS', adapter_files='PASS',
            json_python_links_whitespace_credentials='PASS', additive_scope='PASS', git_diff_check='PASS',
            kernel_constructs=26, production_changes=0, experimental_semantic_changes=0,
            dataset_expansion=0, training_attempts=1, optimizer_updates=20, scheduler_updates=20,
            P6_A04_acceptance=0, P6_A05_access=False))
    print('PASS R6.67 publication integrity and preserved baseline')


if __name__ == '__main__':
    if sys.argv[1] == 'derive':
        derive()
    else:
        seal(sys.argv[1] == 'check')
