import itertools
import json
import re
import sys


def ident(value):
    return type(value) is str and re.fullmatch(r"[A-Z]", value) is not None


def integer(value, low, high):
    return type(value) is int and low <= value <= high


def run(request):
    if type(request) is not dict or set(request) != {"jobs"}:
        return {"error": "shape"}
    jobs = request["jobs"]
    if type(jobs) is not list or len(jobs) > 7:
        return {"error": "shape"}
    for job in jobs:
        if type(job) is not dict or set(job) != {"id", "duration", "weight", "deadline", "deps"}:
            return {"error": "shape"}
        if not (ident(job["id"]) and integer(job["duration"], 1, 9)
                and integer(job["weight"], 0, 9) and integer(job["deadline"], 0, 63)):
            return {"error": "shape"}
        deps = job["deps"]
        if type(deps) is not list or len(deps) > 7 or not all(ident(d) for d in deps):
            return {"error": "shape"}
        if len(set(deps)) != len(deps):
            return {"error": "shape"}
    by_id = {j["id"]: j for j in jobs}
    if len(by_id) != len(jobs):
        return {"error": "duplicate_id"}
    if any(d not in by_id for j in jobs for d in j["deps"]):
        return {"error": "unknown_dep"}
    remaining, done = set(by_id), set()
    while remaining:
        ready = {i for i in remaining if set(by_id[i]["deps"]) <= done}
        if not ready:
            return {"error": "cycle"}
        remaining -= ready
        done |= ready
    best = None
    for order in itertools.permutations(sorted(by_id)):
        done, completion, elapsed, cost = set(), [], 0, 0
        for i in order:
            job = by_id[i]
            elapsed += job["duration"]
            if not set(job["deps"]) <= done or elapsed > job["deadline"]:
                break
            completion.append(elapsed)
            cost += job["weight"] * elapsed
            done.add(i)
        else:
            if best is None or (cost, order) < best[:2]:
                best = (cost, order, completion)
    if best is None:
        return {"error": "infeasible"}
    return {"order": list(best[1]), "completion": best[2], "cost": best[0]}


if __name__ == "__main__":
    print(json.dumps(run(json.load(sys.stdin))))
