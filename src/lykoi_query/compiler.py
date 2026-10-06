"""Faithful query-document lowering through the existing adequacy mechanism."""
from air_compiler.collection_query import QueryError, generate
from benchmark.evaluation import formal_requirements_r5_80 as frc
from . import contracts


def compile_document(document):
    contract = contracts.recover(document)
    frc.validate(contract)
    projection = contracts.structural(contract, document["source_frc"])
    discovered = contracts.bdi(contract, projection)
    adequacy = contracts.adequate(contract, discovered)
    if adequacy["outcome"] != "IMPLEMENTATION_ADEQUATE":
        raise QueryError("Implementation not adequate: " + adequacy["outcome"])
    return {q["id"]: generate({k: v for k, v in q.items() if k != "origins"}) for q in projection["queries"]}
