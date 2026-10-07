"""Current semantic and historical regression checks; exclusive publication."""
import datetime
import importlib.util
import json
from pathlib import Path
import sys
from concurrent.futures import ThreadPoolExecutor

OUT = Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location("checks106", OUT / "R5_105-verify.py")
prior = importlib.util.module_from_spec(s); s.loader.exec_module(prior)
checks = prior.checks
checks.COMMANDS.insert(0, ["-m", "unittest", "discover", "-s", "tests", "-p", "test_predicates.py", "-v"])


def main():
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with ThreadPoolExecutor(max_workers=2) as pool:
        rows = list(pool.map(checks.run, checks.COMMANDS))
    result = dict(utc_started=start, utc_finished=datetime.datetime.now(datetime.timezone.utc).isoformat(), commands=rows,
                  tests=sum(r["tests"] for r in rows), all_pass=all(r["exit"] == 0 for r in rows), scope="R5.106 semantic/pipeline/application/external checks")
    label = sys.argv[1] if len(sys.argv) > 1 else "GENERIC-VERIFICATION"
    assert checks.re.fullmatch(r"[A-Z0-9-]+", label)
    with (OUT / ("R5_106-" + label + ".json")).open("x", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, indent=2); f.write("\n")
    print(result["tests"], result["all_pass"], flush=True)
    return int(not result["all_pass"])


if __name__ == "__main__": sys.exit(main())
