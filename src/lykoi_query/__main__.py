"""python -m lykoi_query validate|compile CONTRACT [OUTPUT_DIRECTORY]."""
import argparse
import json
from pathlib import Path

from benchmark.evaluation import formal_requirements_r5_80 as frc
from . import contracts
from .compiler import compile_document


def main():
    parser = argparse.ArgumentParser(description="Lykoi prospective collection-query profile")
    parser.add_argument("action", choices=("validate", "compile"))
    parser.add_argument("contract", type=Path)
    parser.add_argument("output", nargs="?", type=Path)
    args = parser.parse_args()
    c = json.loads(args.contract.read_text(encoding="utf-8"))
    p = contracts.structural(c, frc.validate(c))
    coverage = contracts.coverage(c, p)
    b = contracts.bdi(c, p)
    a = contracts.adequate(c, b)
    print(json.dumps({"coverage": coverage, "bdi": b["outcome"], "adequacy": a["outcome"]}))
    if args.action == "compile":
        if args.output is None or not args.output.is_dir():
            parser.error("compile requires an existing output directory")
        targets = compile_document(contracts.document(c, p))
        # Filenames are hash-derived, never interpreted from semantic IDs.
        import hashlib
        for identity, target in targets.items():
            name = hashlib.sha256(identity.encode()).hexdigest() + ".py"
            (args.output / name).write_text(target, encoding="utf-8")


if __name__ == "__main__":
    main()
