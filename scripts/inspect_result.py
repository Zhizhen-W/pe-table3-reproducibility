#!/usr/bin/env python3
"""Show matching Table III scores, native inputs, parameters and references."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def entries(obj, names):
    if isinstance(obj, list):
        return obj
    for name in names:
        if isinstance(obj.get(name), list):
            return obj[name]
    raise ValueError("Unrecognized manifest structure")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True)
    parser.add_argument("--frequency", type=float)
    parser.add_argument("--method")
    parser.add_argument("--depth", type=float)
    parser.add_argument("--mode")
    args = parser.parse_args()
    configs = entries(json.loads((ROOT / "manifests/configurations.json").read_text(encoding="utf-8")), ["configurations"])
    config_map = {x["config_id"]: x for x in configs}
    scores = entries(json.loads((ROOT / "manifests/pe_scores.json").read_text(encoding="utf-8")), ["scores", "records", "runs"])
    selected = []
    for score in scores:
        if score.get("case") != args.case: continue
        if args.frequency is not None and float(score.get("frequency_hz", score.get("frequency", -1))) != args.frequency: continue
        if args.method and score.get("method") != args.method: continue
        if args.depth is not None and float(score.get("depth_m", score.get("depth", -1))) != args.depth: continue
        if args.mode and score.get("mode", "").replace("×", "x") != args.mode.replace("×", "x"): continue
        selected.append({"score": score, "configuration": config_map.get(score.get("config_id"))})
    refs = entries(json.loads((ROOT / "manifests/reference_checks.json").read_text(encoding="utf-8")), ["rows", "checks"])
    selected_refs = [x for x in refs if x.get("case") == args.case and (args.frequency is None or float(x.get("frequency_hz", -1)) == args.frequency)]
    if not selected and not selected_refs:
        parser.error("No matching Table III record")
    print(json.dumps({"results": selected, "reference_checks": selected_refs}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
