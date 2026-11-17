#!/usr/bin/env python3
"""Recompute Table III reference differences from paired fields or the C3 DGM inputs.

Loads archived paired fields and generates the C3 DGM fields from their settings.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np


def _read_pair(root, row):
    asset = row["datasets"][0]
    with np.load(root / asset["path"], allow_pickle=False) as data:
        ranges = data["r_m"].copy()
        depths = data["z_m"].copy()
        if row["kind"] == "archived_pair":
            coarse, fine = data["p_coarse"].copy(), data["p_fine"].copy()
        else:
            coarse = fine = None
    if row["kind"] == "dgm_regenerate_pair":
        # The archived fine CSV was rounded on export and no coarse field was saved.
        # Rebuild both levels using the exact original implementation and settings.
        source = root / row["implementation"]
        spec = importlib.util.spec_from_file_location("table3_dgm_reference", source)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        config = json.loads((root / row["input_files"][0]["path"]).read_text(encoding="utf-8"))
        values = []
        for level in ("coarse_settings", "fine_settings"):
            model = module.StableLayeredFFP(
                freq_hz=config["frequency_hz"],
                interfaces_m=config["interfaces_m"],
                c_mps=config["c_mps"],
                rho_kg_m3=config["rho_kg_m3"],
                source_depth_m=config["source_depth_m"],
                settings=module.DGMSettings(**config[level]),
            )
            values.append(np.stack([model.pressure_range_line(ranges, z) for z in depths]))
        coarse, fine = values
    shape = (len(depths), len(ranges))
    if coarse.shape != shape or fine.shape != shape or coarse.size != asset["n_points"]:
        raise ValueError(f"Unexpected field shape or point count: {row['id']}")
    if not np.isfinite(coarse).all() or not np.isfinite(fine).all():
        raise ValueError(f"Nonfinite pressure at prescribed evaluation points: {row['id']}")
    return depths, coarse, fine


def compute_reference_checks(root=None, case=None):
    """Return reference differences calculated on the prescribed evaluation points."""
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "manifests/reference_checks.json").read_text(encoding="utf-8"))
    results = []
    for row in manifest["rows"]:
        if case is not None and row["case"] != case:
            continue
        result = {key: row[key] for key in ("id", "case", "frequency_hz", "reference", "aggregation")}
        if row["kind"] in ("analytical", "unverified"):
            result.update(D_SPL_db=None, display="Analytical" if row["kind"] == "analytical" else "Unverified", n_points=0, line_rms_db={})
        else:
            depths, coarse, fine = _read_pair(root, row)
            difference = 20 * np.log10(np.maximum(np.abs(coarse), 1e-30) / np.maximum(np.abs(fine), 1e-30))
            if row["aggregation"] == "max_receiver_line_rms":
                line_rms = np.sqrt(np.mean(difference ** 2, axis=1))
                value = float(np.max(line_rms))
                by_line = {str(float(z)): float(v) for z, v in zip(depths, line_rms)}
            else:
                value = float(np.sqrt(np.mean(difference ** 2)))
                by_line = {}
            display = f"{value:.2e}" if row["case"] in ("C3", "C4") else f"{value:.2f}"
            result.update(D_SPL_db=value, display=display, n_points=int(coarse.size), line_rms_db=by_line)
        results.append(result)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=[f"C{i}" for i in range(1, 10)] + ["N1"])
    parser.add_argument("--output", default="results/reference_checks.csv")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    results = compute_reference_checks(root, args.case)
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    columns = ["id", "case", "frequency_hz", "reference", "aggregation", "D_SPL_db", "display", "n_points", "line_rms_db"]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for result in results:
            writer.writerow({**result, "line_rms_db": json.dumps(result["line_rms_db"], sort_keys=True)})
    print(f"Wrote {len(results)} reference rows to {output}")


if __name__ == "__main__":
    main()
