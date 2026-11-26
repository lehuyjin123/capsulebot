"""Run a multi-RPM BEMT performance sweep for the propeller."""

from bemt import BEMTSolver
from report import write_csv, write_plots
import config


def main():
    solver = BEMTSolver(config)
    results = solver.sweep(config.RPM_SWEEP, config.ADVANCE_VELOCITIES_MPS)
    csv_path = write_csv(results, config.RESULTS_DIR)
    plot_path = write_plots(results, config.RESULTS_DIR)

    print("BEMT sweep completed")
    print(f"Results CSV : {csv_path}")
    print(f"Plot        : {plot_path}")
    print("\nStatic operating points")
    print(" RPM       T [mN]     Q [uN m]      P [mW]    KT")
    for p in results:
        if p.advance_velocity == 0.0:
            print(f"{p.rpm:6.0f}  {p.thrust_n * 1e3:10.4f}  {p.torque_nm * 1e6:10.4f}"
                  f"  {p.power_w * 1e3:10.4f}  {p.kt:7.4f}")


if __name__ == "__main__":
    main()
