"""
Parse Fluent Report File (.out) outputs across multiple RPM case folders,
take the converged value at the final iteration (2500), and plot:
  1) Thrust vs RPM
  2) Moment vs RPM

Assumed folder layout (edit ROOT_DIR / filenames below to match yours):

    ROOT_DIR/
        3000rpm/
            thurst-rfile.out
            moment-rfile.out
        4000rpm/
            thurst-rfile.out
            moment-rfile.out
        ...

Each .out file looks like:

    "thurst-rfile"
    "Iteration" "thurst"
    ("Iteration" "thurst")
    1 -6.984715020059072e-05
    2 -0.0001318170752501128
    ...
    2500 -0.0007151788630627254

We take the LAST line's value as the converged result for that case.
"""

import re
import glob
import os
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- USER CONFIG ----------------
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")
THRUST_FILENAME = "thurst-rfile.out"
MOMENT_FILENAME = "moment-rfile.out"
DRAG_FILENAME = "report-def-0-rfile.out"   # drag force report file
OUTPUT_XLSX = "thrust_moment_vs_rpm.xlsx"
OUTPUT_PNG_THRUST = "thrust_vs_rpm.png"
OUTPUT_PNG_MOMENT = "moment_vs_rpm.png"
OUTPUT_PNG_DRAG = "drag_vs_rpm.png"
# ----------------------------------------------


def read_final_value(filepath):
    """Read a Fluent report-file (.out): 3 header lines, then 'iter value' rows.
    Returns (final_iteration, final_value), or (None, None) if unreadable."""
    if not os.path.exists(filepath):
        return None, None
    last_iter, last_val = None, None
    with open(filepath, encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('"') or line.startswith('('):
                continue
            parts = line.split()
            if len(parts) != 2:
                continue
            try:
                it = int(parts[0])
                val = float(parts[1])
            except ValueError:
                continue
            last_iter, last_val = it, val  # keep overwriting -> ends on last row
    return last_iter, last_val


def extract_rpm(folder_name):
    m = re.search(r'(\d+)\s*rpm', folder_name, re.IGNORECASE)
    return int(m.group(1)) if m else None


def main():
    case_dirs = sorted(
        [d for d in glob.glob(os.path.join(ROOT_DIR, "*rpm")) if os.path.isdir(d)],
        key=lambda d: extract_rpm(os.path.basename(d)) or 0
    )
    if not case_dirs:
        raise SystemExit(f"No '*rpm' folders found under {ROOT_DIR}")

    records = []
    for d in case_dirs:
        rpm = extract_rpm(os.path.basename(d))
        thrust_path = os.path.join(d, THRUST_FILENAME)
        moment_path = os.path.join(d, MOMENT_FILENAME)

        t_iter, t_val = read_final_value(thrust_path)
        m_iter, m_val = read_final_value(moment_path)
        drag_path = os.path.join(d, DRAG_FILENAME)
        g_iter, g_val = read_final_value(drag_path)

        if t_val is None or m_val is None:
            print(f"[WARN] {os.path.basename(d)}: thrust={t_val} (iter {t_iter}), "
                  f"moment={m_val} (iter {m_iter}) -- files present: {os.listdir(d)}")
        if g_val is None:
            print(f"[WARN] {os.path.basename(d)}: drag file missing/unreadable "
                  f"({DRAG_FILENAME}) -- files present: {os.listdir(d)}")

        records.append({
            "RPM": rpm,
            "Thrust_N": t_val,
            "Thrust_final_iter": t_iter,
            "Moment_Nm": m_val,
            "Moment_final_iter": m_iter,
            "Drag_N": g_val,
            "Drag_final_iter": g_iter,
        })

    df = pd.DataFrame(records).sort_values("RPM").reset_index(drop=True)

    if df["Thrust_N"].dropna().empty:
        raise SystemExit(
            "\nNo case had a readable thrust value -- check the [WARN] lines above "
            "and confirm THRUST_FILENAME/MOMENT_FILENAME match the real filenames."
        )

    print(df)

    # Sign was just a consequence of how the axis/direction vector was defined in Fluent
    # (not physically meaningful here) -- report magnitudes instead.
    df["Thrust_N"] = df["Thrust_N"].abs()
    df["Moment_Nm"] = df["Moment_Nm"].abs()
    df["Drag_N"] = df["Drag_N"].abs()

    print("\nAfter taking absolute value:")
    print(df[["RPM", "Thrust_N", "Moment_Nm", "Drag_N"]])

    # Flag any case that didn't actually reach iteration 2500 (didn't finish/converge)
    incomplete = df[(df["Thrust_final_iter"] != 2500) | (df["Moment_final_iter"] != 2500)]
    if not incomplete.empty:
        print("\n[NOTE] These cases did not reach iteration 2500 -- check them:")
        print(incomplete[["RPM", "Thrust_final_iter", "Moment_final_iter"]])

    # ---- Save Excel ----
    df.to_excel(OUTPUT_XLSX, index=False)
    print(f"\nSaved table -> {OUTPUT_XLSX}")

    # ---- Plot Thrust vs RPM ----
    plt.figure(figsize=(7, 5))
    plt.plot(df["RPM"], df["Thrust_N"], marker='o')
    plt.xlabel("RPM")
    plt.ylabel("Thrust [N] (converged, iter 2500)")
    plt.title("Thrust vs RPM")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG_THRUST, dpi=200)
    print(f"Saved plot -> {OUTPUT_PNG_THRUST}")

    # ---- Plot Moment vs RPM ----
    plt.figure(figsize=(7, 5))
    plt.plot(df["RPM"], df["Moment_Nm"], marker='o', color='darkorange')
    plt.xlabel("RPM")
    plt.ylabel("Moment [N·m] (converged, iter 2500)")
    plt.title("Moment vs RPM")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG_MOMENT, dpi=200)
    print(f"Saved plot -> {OUTPUT_PNG_MOMENT}")

    # ---- Plot Drag vs RPM ----
    plt.figure(figsize=(7, 5))
    plt.plot(df["RPM"], df["Drag_N"], marker='o', color='green')
    plt.xlabel("RPM")
    plt.ylabel("Drag force [N] (converged, iter 2500)")
    plt.title("Drag vs RPM")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG_DRAG, dpi=200)
    print(f"Saved plot -> {OUTPUT_PNG_DRAG}")


if __name__ == "__main__":
    main()