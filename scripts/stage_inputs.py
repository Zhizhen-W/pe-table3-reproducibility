#!/usr/bin/env python3
"""Restore one archived native input set without running a solver."""
import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def stage(config_id, output):
    records = json.loads((ROOT / "manifests/configurations.json").read_text(encoding="utf-8"))["configurations"]
    matches = [x for x in records if x["config_id"] == config_id]
    if len(matches) != 1:
        raise ValueError(f"Expected one configuration for {config_id}; found {len(matches)}")
    record = matches[0]
    dest = Path(output).resolve()
    dest.mkdir(parents=True, exist_ok=False)
    for entry in record["files"]:
        relative = Path(entry["work_name"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Unsafe work name: {relative}")
        target = dest / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        source = (ROOT / entry["path"]).resolve()
        if not source.is_relative_to(ROOT.resolve()):
            raise ValueError(f"Input path outside repository: {entry['path']}")
        if target.exists():
            raise ValueError(f"Duplicate staged target: {target}")
        shutil.copyfile(source, target)
    (dest / "configuration.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Inputs staged to {dest}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config_id")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    stage(args.config_id, args.output)
