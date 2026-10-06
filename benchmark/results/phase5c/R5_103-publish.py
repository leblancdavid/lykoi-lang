"""Publish fresh candidate copies and mechanically derived matrix/progression."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
GAPS={
 'B02':('missing semantic family','Ordered writable string values, repeated inputs, strip/map and stable first deduplication'),
 'B03':('backend/store gap','Current model lacks tags; read-only membership already works, persisted-list prerequisite does not'),
 'B06':('missing semantic family','Presence-aware write-time trimming/validation; query equality exists'),
 'B07':('missing semantic family','Persisted ordered arrays and append/strip transformation'),
 'B08':('backend/store gap','Writable boolean absent from v0.3 field algebra/store; read view is insufficient'),
 'B09':('missing semantic family','Inclusive temporal range, two operands and cross-input validation, plus archive prerequisite'),
 'B10':('missing semantic family','Supplied-versus-omitted validation and write-time trimming; query equality exists'),
 'B11':('missing semantic family','OR permission composition and archived-store prerequisite'),
 'B12':('missing semantic family','Scalar-in-constant-set conjunction and archive store; clock/null-before selection now integrated'),
 'B13':('backend/store gap','Typed equality guard now reaches model binding, which lacks archived and append-note/notes; B11 prerequisite remains'),
 'B14':('missing semantic family','Writable identity edges, graph reachability/acyclicity and inverse-reference guards'),
 'B15':('missing semantic family','Quantified related-record predicates and dependency store'),
 'B16':('missing semantic family','Multiple durable entities, referential existence and conditional relation-aware migration'),
 'B17':('ambiguity','Old non-system-user migration role remains unresolved'),
 'B18':('BDI gap','External-effect decision family undiscovered; durable events/atomic effects also missing downstream'),
 'B19':('missing semantic family','Nullable positive integer, temporal arithmetic, successor creation and atomic multi-effects'),
 'B20':('ambiguity','Nonexistent member-user rejection authority remains unresolved'),
}


def write_json(name,value):
    with (OUT/name).open('x',encoding='utf-8',newline='\n') as stream: json.dump(value,stream,indent=2); stream.write('\n')


def main():
    fresh=json.loads((OUT/'R5_103-FINAL-EVIDENCE.json').read_text(encoding='utf-8'))
    initial={r['case']:r for r in json.loads((OUT/'R5_103-INITIAL-EVIDENCE.json').read_text(encoding='utf-8'))['cases']}
    old101={r['case']:r for r in json.loads((OUT/'R5_101-CURRENT-EVIDENCE.json').read_text(encoding='utf-8'))['cases']}
    old102={r['case']:r for r in json.loads((OUT/'R5_102-TRANSFER-EVIDENCE.json').read_text(encoding='utf-8'))['cases']}
    matrix=['# R5.103 — fresh typed current-system capability matrix','','**Exposed requirement-local development/regression evidence; no held-out or cumulative claim.**',
        '', '| Case | Fresh formalization | Structural | BDI | Adequacy | V1 | Author/compile | Behavioral verification | First blocker |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    progression=['# R5.101 → R5.102 → R5.103 progression','','First-blocker classes, preserving the original records. R5.102 has nineteen old-capture rows; every R5.103 input is a fresh current source interpretation.', '',
        '| Case | R5.101 | R5.102 | R5.103 | Cause of changed result / current diagnosis |', '| --- | --- | --- | --- | --- |']
    analysis=[]
    for r in fresh['cases']:
        case=r['case']; s=r['stages']
        write_json(f'R5_103-{case}-CANDIDATE.json',dict(case=case,producer_capture=r['candidate'],exact_frc=r['formalization']['contract'],source_sha256=r['formalization']['contract']['source']['sha256']))
        values=[s[k] for k in ('FORMALIZATION','STRUCTURAL','BDI','ADEQUACY','REPRESENTATION')]
        if case=='B18': values[1]='PASS_BOUNDED_EFFECT_CHANNEL'
        author_compile=s['AUTHORING']+'/'+s['COMPILATION']
        matrix.append('| '+' | '.join([case,*values,author_compile,s['BEHAVIORAL_VERIFICATION'],r['first_blocker']])+' |')
        changed=old102[case]['first_blocker']!=r['first_blocker']
        cause='FRESH_TYPED_FORMALIZATION_EXISTING_SUPPORT' if changed and initial[case]['first_blocker']==r['first_blocker'] else 'GENERIC_INTEGRATION_REPAIR' if changed else 'UNCHANGED_FIRST_BLOCKER'
        cls,reason=GAPS.get(case,('success','Author/compile/runtime/external behavior executed'))
        newly=[k for k in s if old102[case]['stages'][k]=='NOT_REACHED' and s[k]!='NOT_REACHED']
        analysis.append(dict(case=case,primary_cluster=cls,diagnosis=reason,result_change_cause=cause,newly_reached=newly,external_invocations=r.get('external_invocations',0),candidate_ref=f'R5_103-{case}-CANDIDATE.json'))
        progression.append('| '+' | '.join([case,old101[case]['first_blocker'],old102[case]['first_blocker'],r['first_blocker'],cause+'; '+reason])+' |')
    clusters={c:sum(r['primary_cluster']==c for r in analysis) for c in ('existing-semantic integration gap','missing semantic family','backend/store gap','BDI gap','representation gap','ambiguity','success')}
    summary=dict(classification='R5_103_FRESH_TYPED_CORPUS_REBASELINED',distribution=fresh['distribution'],primary_clusters=clusters,stale_capture_result_changes=sum(r['result_change_cause']=='FRESH_TYPED_FORMALIZATION_EXISTING_SUPPORT' for r in analysis),repair_result_changes=sum(r['result_change_cause']=='GENERIC_INTEGRATION_REPAIR' for r in analysis),external_invocations=sum(r['external_invocations'] for r in analysis),cases=analysis,limitations=['Requirement-local precursor demands, not cumulative achieved features','Same-agent source capture/inventory/oracles; synthetic owner approvals','Backend/store primary classes may have missing writable algebra prerequisites','B18 structural pass only carries an external-effect channel, not full event semantics'])
    write_json('R5_103-SUMMARY.json',summary)
    for name,lines in [('R5_103-CAPABILITY-MATRIX.md',matrix),('R5_103-PROGRESSION.md',progression)]:
        with (OUT/name).open('x',encoding='utf-8',newline='\n') as stream: stream.write('\n'.join(lines)+'\n')
    # Publish source/oracle/controller/native/external evidence for bounded closure.
    sys.path.insert(0,str(ROOT/'tests'))
    from test_existing_composition import fixture, evaluation
    rows=[]
    for label,kwargs in [('scalar-guard',dict(guards=True)),('scalar-clock',dict(clock=True)),('scalar-query',dict(composed=True)),('scalar-query-clock',dict(composed=True,clock=True))]:
        _,candidate,plan=fixture(**kwargs); result=evaluation.evaluate(candidate,plan)
        assert result['first_blocker']=='SUCCESS',result.get('terminal')
        rows.append(dict(label=label,result=result)); print(label,result['external_invocations'],flush=True)
    write_json('R5_103-SYNTHETIC-EVIDENCE.json',dict(scope='Bounded existing-semantic integration, same-agent source-side external plans',cases=rows,external_invocations=sum(r['result']['external_invocations'] for r in rows)))
    print(json.dumps(summary['distribution']), 'external invocations',summary['external_invocations'])


if __name__=='__main__': main()
