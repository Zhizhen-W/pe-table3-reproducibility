#!/usr/bin/env python3
"""Recompute Table III PE errors from the packaged complex pressures.

No solver is called. Expected values are never used as calculation inputs.
Only the Python standard library is required.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, ROUND_HALF_UP
import json
import math
from pathlib import Path


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def safe_path(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path escapes the repository: {relative}")
    return path


def complex_values(rows, label):
    values = []
    for index, row in enumerate(rows, 1):
        real, imag = float(row["real"]), float(row["imag"])
        if not math.isfinite(real) or not math.isfinite(imag):
            raise ValueError(f"Nonfinite pressure: {label}, row {index}")
        values.append(complex(real, imag))
    return values


def compute_scores(repo_root, case=None):
    """Return one dict per scalar score, including each N1 angle separately.

    ``case`` may be C1...C9 or N1. All archived sample coordinates are retained;
    no interpolation, gain fitting, phase fitting or post-hoc filtering occurs.
    """
    root = Path(repo_root).resolve()
    manifest = json.loads((root / "manifests/pe_scores.json").read_text(encoding="utf-8"))
    floor = float(manifest["amplitude_floor"])
    if not math.isfinite(floor) or floor <= 0:
        raise ValueError("The amplitude floor must be finite and positive")
    configurations = manifest["scores"]
    if case is not None:
        configurations = [item for item in configurations if item["case"] == case]
        if not configurations:
            raise ValueError(f"No packaged score for case {case}")
    output = []
    for item in configurations:
        points = read_csv(safe_path(root, item["points_path"]))
        tests = read_csv(safe_path(root, item["test_pressure_path"]))
        references = read_csv(safe_path(root, item["reference_pressure_path"]))
        n = int(item["n_points"])
        if not n or any(len(a) != n for a in (points, tests, references)):
            raise ValueError(f"Missing or extra samples for {item['score_id']}; expected {n}")
        coordinates = [tuple(float(row[k]) for k in ("r_m", "y_m", "z_m")) for row in points]
        if any(not math.isfinite(value) for xyz in coordinates for value in xyz):
            raise ValueError(f"Nonfinite coordinate for {item['score_id']}")
        if len(set(coordinates)) != n:
            raise ValueError(f"Duplicate coordinates for {item['score_id']}")
        test = complex_values(tests, item["score_id"] + ":test")
        reference = complex_values(references, item["score_id"] + ":reference")
        differences = [20.0 * math.log10(max(abs(p), floor) / max(abs(q), floor))
                       for p, q in zip(test, reference)]
        rmse = math.sqrt(math.fsum(value * value for value in differences) / n)
        if not math.isfinite(rmse):
            raise ValueError(f"Nonfinite RMSE for {item['score_id']}")
        output.append({key: item[key] for key in
                       ("score_id", "config_id", "case", "frequency_hz", "depth_m",
                        "mode", "method", "theta_cut_deg", "n_points")}
                      | {"rmse_db": rmse})
    return output


def format_db(value):
    """Preserve the published two-decimal ROUND_HALF_UP display rule."""
    number = Decimal(str(value))
    if not number.is_finite() or number < 0:
        raise ValueError("Invalid nonnegative SPL RMS value")
    return "<0.01" if number < Decimal("0.005") else str(number.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def table_cells(repo_root, scores):
    """Map computed scores to Table III cells, retaining dashes and N1 ranges.

    ``reported_value`` is not consulted to produce the returned display value.
    For partial calculations, only cases represented in ``scores`` are returned.
    """
    root = Path(repo_root).resolve()
    by_id = {item["score_id"]: item for item in scores}
    if len(by_id) != len(scores):
        raise ValueError("Duplicate score IDs")
    cases = {item["case"] for item in scores}
    output = []
    for item in read_csv(root / "manifests/table3_cells.csv"):
        if item["case"] not in cases:
            continue
        identifiers = [value for value in item["score_ids"].split(";") if value]
        if item["kind"] == "unreported":
            value, low, high = "—", "", ""
        else:
            values = [float(by_id[key]["rmse_db"]) for key in identifiers]
            if item["kind"] == "scalar":
                if len(values) != 1:
                    raise ValueError(f"A scalar cell needs one score: {item['cell_id']}")
                low = high = values[0]
                value = format_db(low)
            elif item["kind"] == "interval":
                if len(values) != 6:
                    raise ValueError(f"An N1 cell needs six cutoffs: {item['cell_id']}")
                low, high = min(values), max(values)
                value = format_db(low) + "–" + format_db(high)
            else:
                raise ValueError(f"Unknown cell kind: {item['kind']}")
        output.append({key: item[key] for key in
                       ("cell_id", "data_row", "case", "frequency_hz", "depth_m", "mode", "method", "kind")}
                      | {"value": value, "rmse_min_db": low, "rmse_max_db": high})
    return output


def write_csv(path, rows):
    if not rows:
        raise ValueError("Cannot write an empty result table")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--case", choices=[f"C{i}" for i in range(1, 10)] + ["N1"])
    parser.add_argument("--output", type=Path, default=Path("results/pe_scores.csv"))
    parser.add_argument("--cells-output", type=Path, default=Path("results/table3_pe_cells.csv"))
    args = parser.parse_args(argv)
    root = args.repo_root.resolve()
    scores = compute_scores(root, args.case)
    cells = table_cells(root, scores)
    for name, content in ((args.output, scores), (args.cells_output, cells)):
        destination = name if name.is_absolute() else root / name
        write_csv(destination, content)
    print(f"Computed {len(scores)} scalar scores and {len(cells)} displayed PE cells.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
