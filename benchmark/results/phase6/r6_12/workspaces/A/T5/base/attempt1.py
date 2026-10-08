import json
import re
import sys


def ident(value):
    return type(value) is str and re.fullmatch(r"[A-Z]", value) is not None


def run(request):
    if type(request) is not dict or set(request) != {"candidates", "ballots"}:
        return {"error": "shape"}
    candidates, ballots = request["candidates"], request["ballots"]
    if (type(candidates) is not list or not 1 <= len(candidates) <= 6
            or not all(ident(i) for i in candidates)
            or type(ballots) is not list or len(ballots) > 12):
        return {"error": "shape"}
    for ballot in ballots:
        if type(ballot) is not dict or set(ballot) != {"ranks", "weight"}:
            return {"error": "shape"}
        ranks, weight = ballot["ranks"], ballot["weight"]
        if (type(ranks) is not list or len(ranks) > 6 or not all(ident(i) for i in ranks)
                or type(weight) is not int or not 1 <= weight <= 9):
            return {"error": "shape"}
        if len(set(ranks)) != len(ranks):
            return {"error": "shape"}
    active = set(candidates)
    if len(active) != len(candidates):
        return {"error": "duplicate_candidate"}
    if any(i not in active for ballot in ballots for i in ballot["ranks"]):
        return {"error": "unknown_candidate"}
    rounds = []
    while active:
        totals = dict.fromkeys(sorted(active), 0)
        exhausted = 0
        for ballot in ballots:
            choice = next((i for i in ballot["ranks"] if i in active), None)
            if choice is None:
                exhausted += ballot["weight"]
            else:
                totals[choice] += ballot["weight"]
        nonexhausted = sum(totals.values())
        winner = next((i for i, votes in totals.items() if 2 * votes > nonexhausted), None)
        eliminated = None
        if nonexhausted and winner is None:
            lowest = min(totals.values())
            eliminated = max(i for i, votes in totals.items() if votes == lowest)
        rounds.append({"totals": [{"id": i, "votes": votes} for i, votes in totals.items()],
                       "exhausted": exhausted, "eliminated": eliminated})
        if eliminated is None:
            return {"winner": winner, "rounds": rounds}
        active.remove(eliminated)


if __name__ == "__main__":
    print(json.dumps(run(json.load(sys.stdin))))
