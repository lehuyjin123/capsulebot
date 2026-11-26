"""Plot Fluent thrust and moment against propeller RPM.

The input folder must contain directories named like ``3000rpm``.  Each
directory contains a Fluent report file for thrust (``thurst-rfile.out`` is
also accepted) and a moment report file.  The reported value is the mean of
the final iterations, which is more representative than one last, possibly
noisy, sample.

Example:
    python plot_fluent_loads.py "../Data"
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import matplotlib.pyplot as plt


RPM_DIR_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)\s*rpm$", re.IGNORECASE)
NUMBER_PATTERN = re.compile(
    r"^\s*\d+\s+([-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?)\s*$"
)


def read_report_values(path: Path) -> list[float]:
    """Read the value column from a Fluent report file, ignoring its header."""
    values: list[float] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = NUMBER_PATTERN.match(line)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError(f"No iteration/value rows found in {path}")
    return values


def find_report(folder: Path, quantity: str) -> Path:
    keywords = ("moment", "torque") if quantity == "moment" else ("thrust", "thurst", "force")
    candidates = [
        path for path in folder.glob("*.out")
        if any(word in path.name.lower() for word in keywords)
    ]
    if len(candidates) != 1:
        names = ", ".join(path.name for path in candidates) or "none"
        raise FileNotFoundError(
            f"Expected exactly one {quantity} .out report in {folder.name}; found: {names}"
        )
    return candidates[0]


def tail_mean(values: list[float], tail_count: int) -> float:
    return sum(values[-tail_count:]) / min(len(values), tail_count)


def save_chart(rpm: list[float], loads: list[float], label: str, unit: str, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")
    ax.plot(rpm, loads, "o-", linewidth=2, markersize=6, color="#0072B2")
    ax.set_xlabel("RPM")
    ax.set_ylabel(f"{label} ({unit})")
    ax.set_title(f"{label} vs RPM")
    ax.grid(True, alpha=0.3)
    ax.ticklabel_format(axis="y", style="sci", scilimits=(-3, 3))
    fig.savefig(output, dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create thrust and moment plots from Fluent .out reports.")
    parser.add_argument("data_dir", type=Path, help="Folder that contains the <RPM>rpm subfolders")
    parser.add_argument("--tail", type=int, default=100, help="Final iterations to average (default: 100)")
    parser.add_argument("--output", type=Path, default=Path("results/fluent_loads"), help="Output directory")
    args = parser.parse_args()
    if args.tail < 1:
        parser.error("--tail must be at least 1")

    cases = []
    for folder in args.data_dir.iterdir():
        if not folder.is_dir() or not (match := RPM_DIR_PATTERN.match(folder.name)):
            continue
        rpm = float(match.group(1))
        moment = tail_mean(read_report_values(find_report(folder, "moment")), args.tail)
        thrust = tail_mean(read_report_values(find_report(folder, "thrust")), args.tail)
        cases.append((rpm, thrust, moment))
    if not cases:
        raise SystemExit(f"No <RPM>rpm folders found in {args.data_dir}")

    cases.sort()
    args.output.mkdir(parents=True, exist_ok=True)
    csv_path = args.output / "fluent_loads_vs_rpm.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["rpm", "thrust_N", "moment_Nm"])
        writer.writerows(cases)

    rpm, thrust, moment = map(list, zip(*cases))
    save_chart(rpm, thrust, "Thrust", "N", args.output / "thrust_vs_rpm.png")
    save_chart(rpm, moment, "Moment", "N m", args.output / "moment_vs_rpm.png")
    print(f"Read {len(cases)} cases. Wrote: {args.output.resolve()}")


if __name__ == "__main__":
    main()
