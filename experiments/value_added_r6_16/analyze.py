"""Aggregate frozen results and actual telemetry without new scoring."""
from evidence import HERE, OUT, ROOT, load, now, save, sha, verify


def main():
    for s in range(3):
        verify(load(OUT / f'SUBMISSION-FREEZE-{s}.json')['files'])
    summary = {}
    for track in ('A', 'B', 'C'):
        phases = []
        for stage in range(3):
            details = []
            for domain in ('kiln', 'custody'):
                r = load(OUT / f'results/{track}-{domain}-{stage}.json')
                first = load(OUT / f'results/{track}-{domain}-{stage}-first.json')
                old = load(OUT / f'results/{track}-{domain}-{stage - 1}.json') if stage else None
                old_index = {(o['group'], o['case'], o['step']): o for o in old['observations']} if old else {}
                prior = [o for o in r['observations'] if (o['group'], o['case'], o['step']) in old_index]
                regressions = sum(old_index[(o['group'], o['case'], o['step'])]['pass_result'] and not o['pass_result'] for o in prior)
                changes = sum(old_index[(o['group'], o['case'], o['step'])].get('observed') != o.get('observed') for o in prior)
                phase = 'base' if stage == 0 else f's{stage}'
                author = load(OUT / f'submissions/{track}/{domain}/{phase}/authoring.json')
                details.append(dict(domain=domain, accepted=r['accepted'], first_accepted=first['accepted'],
                    first_status=first['status'], final_status=r['status'], groups=r['groups'],
                    regressions=regressions, changed_prior_observations=changes,
                    authored_bytes=r.get('authored_bytes'), generated_bytes=r.get('source_bytes'),
                    generation_validation_seconds=r['validation_seconds'], author_record=author))
            phases.append(dict(stage=stage, full_applications_accepted=sum(d['accepted'] for d in details),
                application_denominator=2, observations_passed=sum(sum(g['passed'] for g in d['groups'].values()) for d in details),
                observation_denominator=sum(sum(g['total'] for g in d['groups'].values()) for d in details), applications=details))
        summary[track] = phases
    telemetry = [r for s in range(3) for r in load(OUT / f'TELEMETRY-{s}.json')['sessions']]
    efforts = {}
    for track in ('A', 'B', 'C'):
        chosen = [r for r in telemetry if r['scope'].startswith(track)]
        efforts[track] = dict(
            usage={k: sum(r['usage'][k] for r in chosen) for k in chosen[0]['usage']} if all(r['usage'] for r in chosen) else None,
            model_calls=sum(r['model_calls'] for r in chosen) if all(r['model_calls'] is not None for r in chosen) else None,
            development_wall_seconds=sum(r['development_wall_seconds'] for r in chosen) if all(r['development_wall_seconds'] is not None for r in chosen) else None,
            tool_seconds=sum(r['tool_seconds'] for r in chosen) if all(r['tool_seconds'] is not None for r in chosen) else None,
            tools=sum(r['tool_calls'] for r in chosen) if all(r['tool_calls'] is not None for r in chosen) else None,
            api_cost_usd=None)
    infra = load(OUT / 'INFRASTRUCTURE-FREEZE.json')['files']
    sizes = {n: dict(bytes=(ROOT / n).stat().st_size,
                     lines=len((ROOT / n).read_text(encoding='utf-8').splitlines())) for n in infra}
    save(OUT / 'COMPARISON.json', dict(utc=now(), classification='R6_16_ARCHITECTURAL_COMPARISON_INCONCLUSIVE',
        outcomes=summary, effort_totals=efforts, telemetry_sessions=telemetry,
        shared_pre_author_setup=sizes, setup_bytes=sum(x['bytes'] for x in sizes.values()),
        setup_lines=sum(x['lines'] for x in sizes.values()), setup_ai_usage=None,
        coordinator_wall_basis='timestamps protocol/baseline/infra freeze/reveals/publication; not isolated development time',
        billing_usd=None, staged_results='CONTAMINATED_UNENFORCED',
        matched_success_comparison='B versus C only; A is executable but fails exact blank-label error',
        recommendation='For this bounded slice shared intent plus ordinary generation is sufficient; no measured C-specific behavioral advantage. Keep Lykoi as optional semantic research, not mandatory layer; broader architectural choice remains unresolved.'))
    print('Totals:', efforts)
    print('Setup:', sum(x['bytes'] for x in sizes.values()), 'bytes;', sum(x['lines'] for x in sizes.values()), 'lines')
    print('All phase summaries:', {t: [(p['observations_passed'], p['observation_denominator']) for p in phases] for t, phases in summary.items()})


if __name__ == '__main__':
    main()
