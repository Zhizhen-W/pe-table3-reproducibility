#!/usr/bin/env python3
"""Check paths, manifest links and Python syntax; never execute numerical code."""
from __future__ import annotations
import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read_json(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))

def require_file(name):
    p = (ROOT / name).resolve()
    if not p.is_relative_to(ROOT.resolve()) or not p.is_file():
        raise ValueError(f"Missing or unsafe packaged path: {name}")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checksums", action="store_true", help="Also verify packaged file bytes against checksums.sha256")
    args = parser.parse_args()
    configurations = read_json("manifests/configurations.json")["configurations"]
    by_config = {x["config_id"]: x for x in configurations}
    if len(by_config) != len(configurations):
        raise ValueError("Duplicate config_id")
    for item in configurations:
        names = set()
        for asset in item["files"]:
            require_file(asset["path"])
            if asset["work_name"] in names:
                raise ValueError(f"Duplicate staged file in {item['config_id']}: {asset['work_name']}")
            names.add(asset["work_name"])
        for asset in item.get("starter_sources", []):
            if "path" in asset: require_file(asset["path"])
    scores = read_json("manifests/pe_scores.json")["scores"]
    by_score = {x["score_id"]: x for x in scores}
    if len(by_score) != len(scores): raise ValueError("Duplicate score_id")
    for item in scores:
        if item["config_id"] not in by_config: raise ValueError(f"Missing configuration: {item['config_id']}")
        for name in ["points_path", "test_pressure_path", "reference_pressure_path"]: require_file(item[name])
        for key in ["case", "frequency_hz", "method", "mode"]:
            left, right = item[key], by_config[item["config_id"]][key]
            if key == "mode": left, right = left.replace("×", "x"), right.replace("×", "x")
            if left != right:
                raise ValueError(f"Configuration metadata mismatch: {item['score_id']} {key}")
    with (ROOT / "manifests/table3_cells.csv").open(newline="", encoding="utf-8") as handle:
        cells = list(csv.DictReader(handle))
    for item in cells:
        for name in filter(None, item["score_ids"].split(";")):
            if name not in by_score: raise ValueError(f"Missing score: {name}")
        for name in filter(None, item["config_ids"].split(";")):
            if name not in by_config: raise ValueError(f"Missing config: {name}")
    references = read_json("manifests/reference_checks.json")["rows"]
    ref_keys = {(x["case"], int(x["frequency_hz"])) for x in references}
    for item in cells:
        if (item["case"], int(item["frequency_hz"])) not in ref_keys: raise ValueError("Missing reference-check row")
    for item in references:
        for asset in item.get("datasets", []) + item.get("input_files", []): require_file(asset["path"])
        if item.get("implementation"): require_file(item["implementation"])
    pyfiles = [p for p in ROOT.rglob("*.py") if not any(x in p.parts for x in [".git", ".venv", "work", "results"])]
    for path in pyfiles: ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    checksum_count = 0
    if args.checksums:
        for line in (ROOT / "manifests/checksums.sha256").read_text().splitlines():
            digest, name = line.split("  ", 1)
            require_file(name)
            if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest: raise ValueError(f"File-byte checksum mismatch: {name}")
            checksum_count += 1
    print(json.dumps({"configurations": len(configurations), "scalar_scores": len(scores), "table_cells": len(cells),
                      "reference_rows": len(references), "python_syntax_files": len(pyfiles), "file_checksums": checksum_count,
                      "numerical_computation_executed": False}, indent=2))

if __name__ == "__main__":
    main()
