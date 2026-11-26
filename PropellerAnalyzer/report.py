"""Write BEMT results to portable CSV and PNG plots."""

import csv
from pathlib import Path
import matplotlib.pyplot as plt


FIELDS = [
    "rpm", "advance_velocity_mps", "J", "thrust_N", "torque_Nm", "power_W",
    "KT", "KQ", "KP", "efficiency", "Re_0.75R", "converged", "iterations",
]


def write_csv(results, directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "bemt_performance_map.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for p in results:
            writer.writerow({
                "rpm": p.rpm, "advance_velocity_mps": p.advance_velocity,
                "J": p.j, "thrust_N": p.thrust_n, "torque_Nm": p.torque_nm,
                "power_W": p.power_w, "KT": p.kt, "KQ": p.kq, "KP": p.kp,
                "efficiency": p.efficiency, "Re_0.75R": p.reynolds_075r,
                "converged": p.converged, "iterations": p.iterations,
            })
    return path


def write_plots(results, directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    rpms = sorted({p.rpm for p in results})
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
    for rpm in rpms:
        items = sorted((p for p in results if p.rpm == rpm), key=lambda p: p.j)
        j = [p.j for p in items]
        axes[0].plot(j, [p.kt for p in items], marker="o", label=f"{rpm:g} rpm")
        axes[1].plot(j, [p.kq for p in items], marker="o", label=f"{rpm:g} rpm")
        axes[2].plot(j, [p.efficiency for p in items], marker="o", label=f"{rpm:g} rpm")
    axes[0].set(ylabel="$K_T$", xlabel="Advance coefficient, J")
    axes[1].set(ylabel="$K_Q$", xlabel="Advance coefficient, J")
    axes[2].set(ylabel="Propulsive efficiency, η", xlabel="Advance coefficient, J", ylim=(0, 1))
    for ax in axes:
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    fig.tight_layout()
    path = directory / "bemt_coefficients.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path
