#!/usr/bin/env python3
"""Recalculate Table III from packaged pressures and reference inputs."""
from __future__ import annotations
import argparse
import csv
from pathlib import Path
from score_pe import compute_scores, table_cells, write_csv

ROOT = Path(__file__).resolve().parents[1]
METHODS = ["SSP", "LSS-FD", "CT-S", "SSF", "WAMPE"]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=[f"C{i}" for i in range(1, 10)] + ["N1"])
    parser.add_argument("--pe-only", action="store_true", help="Skip the reference-check column, including C3 DGM regeneration")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    dest = args.output_dir.resolve()
    dest.mkdir(parents=True, exist_ok=True)
    scores = compute_scores(ROOT, case=args.case)
    cells = table_cells(ROOT, scores)
    write_csv(dest / "pe_scores.csv", scores)
    write_csv(dest / "table3_pe_cells.csv", cells)
    checks = {}
    if not args.pe_only:
        from score_references import compute_reference_checks
        print("Reference checks: C3 regenerates its two DGM levels; other numerical checks use archived paired fields.", flush=True)
        reference_rows = compute_reference_checks(ROOT, case=args.case)
        write_csv(dest / "reference_checks.csv", reference_rows)
        checks = {(x["case"], int(x["frequency_hz"])): x for x in reference_rows}
    groups = {}
    for cell in cells:
        number = int(cell["data_row"])
        if number not in groups:
            key = (cell["case"], int(cell["frequency_hz"]))
            ref = checks.get(key)
            groups[number] = {"data_row": number, "case": cell["case"], "frequency_hz": int(cell["frequency_hz"]),
                              "depth_m": cell["depth_m"], "mode": cell["mode"],
                              "reference_solution": ref["reference"] if ref else "not_computed",
                              "D_SPL": ref["display"] if ref else "not_computed"}
        groups[number][cell["method"]] = cell["value"]
    rows = []
    for number in sorted(groups):
        row = groups[number]
        missing = [name for name in METHODS if name not in row]
        if missing:
            raise ValueError(f"Incomplete table row {number}: {missing}")
        rows.append({k: row[k] for k in ["data_row", "case", "frequency_hz", "depth_m", "mode", "reference_solution", "D_SPL"] + METHODS})
    write_csv(dest / "table3.csv", rows)
    header = list(rows[0])
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    lines.extend("| " + " | ".join(str(row[name]) for name in header) + " |" for row in rows)
    (dest / "table3.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} table rows to {dest}.")

if __name__ == "__main__":
    main()
