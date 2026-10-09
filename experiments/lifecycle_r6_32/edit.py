"""Pinned copy-on-write application revision and explicit local installation."""
import copy
import hashlib
import os
from pathlib import Path
import sys
import time
from lifecycle import ROOT, digest, publish, reject

sys.path.insert(0, str(ROOT / 'experiments/value_added_r6_16'))
from generate import generate


def revise(original, modified, expected_intent, selected, retained):
    """Require a total explicit disposition of the fixture's existing consumers.

    This is a bounded edit facade, not an inferred refactor or new semantic engine.
    Compilation is delegated entirely to the unchanged production-backed generator.
    """
    if digest(original) != expected_intent:
        reject('STALE_APPLICATION', 'exact predecessor intent required')
    consumers = {'ignite', 'set_gate', 'invariant:0'}
    if (type(selected) is not list or type(retained) is not list
            or len(set(selected)) != len(selected) or len(set(retained)) != len(retained)
            or set(selected) & set(retained) or set(selected) | set(retained) != consumers):
        reject('PARTIAL_MIGRATION', 'explicit disposition of both operations and shared invariant required')
    changed = set()
    for name in ('ignite', 'set_gate'):
        if original['operations'][name] != modified['operations'][name]:
            changed.add(name)
    if original['invariants'][0] != modified['invariants'][0]:
        changed.add('invariant:0')
    if changed != set(selected):
        reject('INVALID_MIGRATION', 'selected set must equal actual changed consumers')
    before, after = copy.deepcopy(original), copy.deepcopy(modified)
    for value in (before, after):
        for name in selected:
            if name == 'invariant:0':
                value['invariants'][0] = None
            else:
                value['operations'][name] = None
    if before != after:
        reject('UNAUTHORIZED_MUTATION', 'change outside selected consumer definitions')
    source, ir = generate(modified, 'C')
    source_again, ir_again = generate(copy.deepcopy(modified), 'C')
    if source != source_again or ir != ir_again:
        reject('NONDETERMINISM', 'generation mismatch')
    return dict(predecessor=expected_intent, identity=digest(modified), intent=modified,
                selected=sorted(selected), retained=sorted(retained), source=source, ir=ir,
                source_sha256=hashlib.sha256(source.encode()).hexdigest())


def install(revision, target, expected_source, journal):
    """One cooperating installer, atomic replace, predecessor archive before write."""
    target = Path(target)
    start = time.perf_counter()
    if hashlib.sha256(target.read_bytes()).hexdigest() != expected_source:
        reject('STALE_APPLICATION', 'installed source precondition mismatch')
    with journal.stage('install-' + revision['identity'], dict(predecessor_source=expected_source,
                     successor_source=revision['source_sha256'], successor_intent=revision['identity'])):
        archive = target.with_name(expected_source + '.predecessor')
        with archive.open('xb') as stream:
            stream.write(target.read_bytes())
            stream.flush()
            os.fsync(stream.fileno())
        pending = target.with_name(target.name + '.pending')
        with pending.open('xb') as stream:
            stream.write(revision['source'].encode('utf-8'))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(pending, target)
        journal.record('application_install', dict(predecessor=expected_source,
            successor=revision['source_sha256'], archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
            tool_seconds=time.perf_counter() - start))
