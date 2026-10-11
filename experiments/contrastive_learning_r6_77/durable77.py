"""Synchronous, fail-closed experiment-local case journal and tracked launcher."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.pending')
    with temporary.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            assert key not in result, 'DUPLICATE_JSON_KEY'
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique)


class Journal:
    def __init__(self, root, binding):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.binding = binding

    def recover(self):
        assert not list(self.root.glob('*.pending')), 'INCOMPLETE_ATOMIC_WRITE'
        records = []
        starts = sorted(self.root.glob('*.start.json'))
        seen = set()
        for index, start in enumerate(starts):
            claim = load(start)
            assert claim['index'] == index and claim['binding'] == self.binding, 'ORDER_OR_BINDING_DRIFT'
            assert claim['case_id'] not in seen, 'DUPLICATE_CASE'
            seen.add(claim['case_id'])
            assert claim['case_id'] == self.binding['case_ids'][index], 'CASE_ORDER_DRIFT'
            commit = self.root / f'{index:03d}.commit.json'
            assert commit.exists(), 'AMBIGUOUS_INFLIGHT_NO_RETRY'
            closed = load(commit)
            raw = self.root / f'{index:03d}.raw.json'
            assert closed['start_sha256'] == digest(start), 'START_CORRUPTION'
            assert closed['raw_sha256'] == digest(raw), 'RAW_CORRUPTION'
            assert closed['case_id'] == claim['case_id'], 'CASE_DRIFT'
            records.append(load(raw))
        assert len(list(self.root.glob('*.commit.json'))) == len(starts), 'ORPHAN_COMMIT'
        assert len(list(self.root.glob('*.raw.json'))) == len(starts), 'ORPHAN_RAW'
        return records

    def begin(self, case_id):
        index = len(self.recover())
        assert index < len(self.binding['case_ids']), 'ALL_CASES_COMMITTED'
        assert self.binding['case_ids'][index] == case_id, 'CASE_ORDER_DRIFT'
        start = self.root / f'{index:03d}.start.json'
        with start.open('x', encoding='utf-8') as stream:
            json.dump(dict(index=index, case_id=case_id, binding=self.binding,
                           pid=os.getpid(), time_ns=time.time_ns()), stream)
            stream.flush()
            os.fsync(stream.fileno())
        return index

    def commit(self, index, raw):
        start = self.root / f'{index:03d}.start.json'
        assert load(start)['case_id'] == raw['id']
        destination = self.root / f'{index:03d}.raw.json'
        assert not destination.exists()
        atomic(destination, raw)
        atomic(self.root / f'{index:03d}.commit.json', dict(case_id=raw['id'],
               start_sha256=digest(start), raw_sha256=digest(destination)))


def launch(command, output, resource, ceiling, timeout, expected_interpreter, nonce):
    """No detached processes; flushed external samples survive launcher interruption."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    began = time.perf_counter()
    worker_pid = None
    failure = None
    with (output/'stdout.txt').open('x') as stdout, (output/'stderr.txt').open('x') as stderr:
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr)
        atomic(output/'LAUNCH.json', dict(command=command, launcher_pid=os.getpid(),
               redirector_pid=process.pid, timeout_seconds=timeout, nonce=nonce))
        try:
            with (output/'resources.jsonl').open('x', encoding='utf-8') as samples:
                while process.poll() is None:
                    handshake = output/'HANDSHAKE.json'
                    if worker_pid is None and handshake.exists():
                        record = load(handshake)
                        assert record['nonce'] == nonce and record['parent_pid'] == process.pid
                        assert Path(record['interpreter']).resolve() == Path(expected_interpreter).resolve()
                        worker_pid = record['worker_pid']
                        assert isinstance(worker_pid, int) and worker_pid > 0
                    sample = resource.measure(worker_pid or process.pid)
                    if not sample['available'] and process.poll() is not None:
                        break
                    resource.validate(sample, worker_pid or process.pid, ceiling)
                    sample.update(elapsed_seconds=time.perf_counter()-began,
                                  attribution='worker' if worker_pid else 'redirector')
                    samples.write(json.dumps(sample, allow_nan=False)+'\n')
                    samples.flush()
                    os.fsync(samples.fileno())
                    assert time.perf_counter()-began <= timeout, 'PROCESS_WALL_LIMIT'
                    time.sleep(0.1)
        except BaseException as exc:
            failure = str(exc)
        finally:
            if process.poll() is None:
                subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                               capture_output=True, timeout=30)
                if worker_pid:
                    subprocess.run(['taskkill', '/PID', str(worker_pid), '/T', '/F'],
                                   capture_output=True, timeout=30)
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=30)
    result = dict(worker_pid=worker_pid, redirector_pid=process.pid,
                  returncode=process.returncode, seconds=time.perf_counter()-began,
                  failure=failure, complete=True)
    atomic(output/'EXIT.json', result)
    return result
