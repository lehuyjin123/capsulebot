"""Inputs for the propeller-performance calculation.

Units in this file are SI unless the variable name explicitly ends in ``_MM``.
The section table is intentionally kept here: replace its provisional values
with chord and pitch-angle measurements exported from SolidWorks.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEP_FILE = "C:/Users/Jindo/Downloads/capsulerobot/chanvit_bitstep.STEP"
RESULTS_DIR = ROOT / "results"

# Operating fluid: fresh water at approximately 20 degC.
RHO = 998.2                 # kg/m^3
MU = 0.001003               # Pa s

# CAD-derived global geometry (the program may read these from STEP as well).
DIAMETER_M = 4.049711e-3
HUB_RADIUS_M = 0.60e-3
BLADES = 2

# A performance map is calculated at every combination of these inputs.
RPM_SWEEP = [3_000, 6_000, 9_000, 12_000, 15_000]
ADVANCE_VELOCITIES_MPS = [0.0, 0.10, 0.20, 0.30, 0.40, 0.50]

# Blade sections, from root to tip.  beta_deg is measured from the plane of
# rotation. These are PROVISIONAL values, selected only to make the project
# executable.  They are not measurements of the STEP model and must be
# replaced before using the numerical results as design/validation data.
#
#  r/R, chord [mm], beta [deg]
SECTIONS = [
    (0.30, 1.30, 44.0),
    (0.40, 1.42, 37.0),
    (0.50, 1.48, 32.0),
    (0.60, 1.43, 28.0),
    (0.70, 1.30, 24.5),
    (0.80, 1.10, 21.5),
    (0.90, 0.82, 19.0),
    (0.96, 0.45, 17.0),
]

# Low-Reynolds-number section polar.  Replace these constants with measured
# or XFOIL/CFD-derived polars for the real section if available.
LIFT_CURVE_SLOPE = 4.8      # 1/rad, deliberately lower than 2*pi at low Re
ALPHA_ZERO_DEG = 0.0
CL_MIN = -0.70
CL_MAX = 0.90
CD0 = 0.035
CD2 = 0.090

# Numerical controls for BEMT's annular induction iteration.
MAX_ITERATIONS = 250
RELAXATION = 0.20
CONVERGENCE_TOL = 1e-7
