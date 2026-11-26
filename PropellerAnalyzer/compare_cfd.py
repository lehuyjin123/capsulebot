"""Compare CFD integrated loads with BEMT at matching operating points.

Create ``results/cfd_performance_map.csv`` with columns:
rpm,advance_velocity_mps,thrust_N,torque_Nm,power_W
The rpm and advance velocity must match BEMT sweep inputs (within a small
floating-point tolerance).
"""

import csv
from pathlib import Path
import config


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def f(row, name):
    return float(row[name])


def main():
    bemt_path = config.RESULTS_DIR / "bemt_performance_map.csv"
    cfd_path = config.RESULTS_DIR / "cfd_performance_map.csv"
    if not bemt_path.exists():
        raise SystemExit("Run `python main.py` first.")
    if not cfd_path.exists():
        raise SystemExit(f"Missing {cfd_path}. See this file's header for the required columns.")

    bemt = read_csv(bemt_path)
    cfd = read_csv(cfd_path)
    output = []
    for c in cfd:
        rpm, va = f(c, "rpm"), f(c, "advance_velocity_mps")
        matches = [b for b in bemt if abs(f(b, "rpm") - rpm) < 1e-6
                   and abs(f(b, "advance_velocity_mps") - va) < 1e-8]
        if not matches:
            print(f"Skipped CFD point: rpm={rpm:g}, Va={va:g} m/s (no BEMT match)")
            continue
        b = matches[0]
        row = {"rpm": rpm, "advance_velocity_mps": va}
        for key, label in (("thrust_N", "T"), ("torque_Nm", "Q"), ("power_W", "P")):
            theory, simulated = f(b, key), f(c, key)
            row[f"bemt_{key}"] = theory
            row[f"cfd_{key}"] = simulated
            row[f"error_{label}_percent"] = 100.0 * (simulated - theory) / theory if theory else float("nan")
        output.append(row)

    out_path = config.RESULTS_DIR / "bemt_vs_cfd.csv"
    if not output:
        raise SystemExit("No CFD rows matched the BEMT map.")
    with out_path.open("w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)
    print(f"Wrote comparison: {out_path}")


if __name__ == "__main__":
    main()
