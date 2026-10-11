"""Transparent callable timer on the actual generation model, no model hooks."""
from contextlib import contextmanager
from functools import wraps
import time


@contextmanager
def forward_timer(model, synchronize):
    target = model.get_base_model() if hasattr(model, 'get_base_model') else model
    had_instance_forward = 'forward' in target.__dict__
    original = target.forward
    measurement = dict(seconds=0.0, calls=0, target=type(target).__name__)
    @wraps(original)
    def timed(*args, **kwargs):
        synchronize()
        begin = time.perf_counter()
        try:
            return original(*args, **kwargs)
        finally:
            synchronize()
            measurement['seconds'] += time.perf_counter() - begin
            measurement['calls'] += 1
    target.forward = timed
    try:
        yield measurement
    finally:
        if had_instance_forward:
            target.forward = original
        else:
            del target.forward


def neutral_cpu_control():
    class Neutral:
        def forward(self, value):
            time.sleep(0.02)
            return value
    class PeftLike:
        def __init__(self): self.inner = Neutral()
        def get_base_model(self): return self.inner
        def generate(self, value): return self.inner.forward(value)
    model = PeftLike()
    sentinel = object()
    start = time.perf_counter()
    with forward_timer(model, lambda: None) as measured:
        assert model.generate(sentinel) is sentinel
    wall = time.perf_counter() - start
    assert measured['calls'] == 1 and 0.015 <= measured['seconds'] <= wall
    assert 'forward' not in model.inner.__dict__
    return dict(passed=True, wall_seconds=wall, forward=measured, return_identity_preserved=True, callable_restored=True)
