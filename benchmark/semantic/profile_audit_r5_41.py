"""Prospective audit uses the same compatible-path model as readiness."""

from benchmark.semantic import application_boundary_r5_41 as boundary
from benchmark.semantic import profile_audit_r5_40 as historical
from benchmark.semantic.refined_generator_r5_28 import canonical, sha

structure = historical.structure
contamination = historical.contamination
traceability = historical.traceability
leaves = historical.leaves


def inspect(application, configuration):
    manifest = {'application': sha(canonical(application)), 'generation': 'static-audit-r541'}
    path = boundary.support_report(application, configuration['transport'], configuration['state'],
                                   configuration['launch'], manifest)
    return {'status': path['status'], 'findings': path['findings'],
            'structure': structure(configuration), 'contamination': contamination(configuration)}
