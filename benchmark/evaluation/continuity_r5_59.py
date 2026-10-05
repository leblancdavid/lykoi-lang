"""Prospective continuity adapter; historical physical locks are untouched."""

from benchmark.evaluation import checkout_r5_52 as checkout

VERSION = 'repository-continuity-r5.59-v1'


def verify(repository, physical, *, repository_sha256, kind, exact_bytes=False):
    """The caller supplies independently qualified repository bytes and classification.

    Only declared UTF-8 LF text permits CRLF materialization. Exact-byte protocol
    authority overrides text eligibility. No recovery or reinterpretation of a
    historical physical pin occurs here.
    """
    if checkout.sha(repository) != repository_sha256:
        raise ValueError('repository authority mismatch')
    eligible = (kind == 'utf8-lf-text' and not exact_bytes and
                checkout.text(repository) and b'\r' not in repository)
    selected = physical.replace(b'\r\n', b'\n') if eligible else physical
    if selected != repository:
        raise ValueError('implementation continuity mismatch')
    return {'version': VERSION, 'continuity_identity': repository_sha256,
            'comparison': 'repository-text' if eligible else 'exact-bytes',
            'checkout_sha256': checkout.sha(physical),
            'checkout_representation': checkout.endings(physical),
            'relationship': 'BYTE_IDENTICAL' if physical == repository else 'LF_CRLF_ONLY'}
