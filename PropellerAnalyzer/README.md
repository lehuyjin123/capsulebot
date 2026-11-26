# PropellerAnalyzer

Preliminary BEMT performance-map generator for the 4.05 mm, two-bladed
underwater propeller. It is designed to put theory and CFD into the same
non-dimensional form, not to replace CFD or experiment.

## Run

```powershell
python main.py
```

The command writes these files into `results/`:

- `bemt_performance_map.csv` — thrust, torque, power, (J), (K_T), (K_Q),
  (K_P), efficiency, and Reynolds number for every operating point;
- `bemt_coefficients.png` — (K_T(J)), (K_Q(J)), and efficiency curves.

Change the desired cases in `config.py`:

```python
RPM_SWEEP = [3_000, 6_000, 9_000, 12_000, 15_000]
ADVANCE_VELOCITIES_MPS = [0.0, 0.10, 0.20, 0.30]
```

## Important: replace provisional blade geometry

`SECTIONS` in `config.py` is an executable *initial assumption*, not a
measurement of the CAD model. For a valid comparison, take 8–20 sections in
SolidWorks and replace every row with:

```python
(r_over_R, chord_mm, beta_deg)
```

Here `beta_deg` is the blade/pitch angle from the plane of rotation, measured
at that radius. The rotation axis of the supplied STEP geometry is Y.

The low-Re section-polar constants (`LIFT_CURVE_SLOPE`, `CD0`, etc.) are also
assumptions. Replace them with polar data from a section CFD/XFOIL run or an
experiment if possible. At this propeller's scale, the Reynolds number is only
roughly (10^3\) to (10^4), so ordinary high-Re airfoil polars are not valid.

## CFD comparison

## Vẽ tải Fluent theo RPM

Với thư mục có dạng `3000rpm`, `4000rpm`, ... và bên trong mỗi thư mục có
hai report `.out` của Fluent cho thrust và moment, chạy:

```powershell
python plot_fluent_loads.py "../Data"
```

Kết quả nằm trong `results/fluent_loads/`:

- `thrust_vs_rpm.png` — thrust theo RPM;
- `moment_vs_rpm.png` — moment theo RPM;
- `fluent_loads_vs_rpm.csv` — số liệu dùng để vẽ.

Script tự nhận cả tên file `thurst-rfile.out` hiện có. Giá trị cho mỗi RPM là
trung bình 100 iteration cuối. Có thể đổi thành 1 iteration cuối bằng
`--tail 1`.

Export integrated blade + hub loads from CFD at matching operating points into
`results/cfd_performance_map.csv`:

```csv
rpm,advance_velocity_mps,thrust_N,torque_Nm,power_W
12000,0.0,0.0030,0.0000015,0.0019
12000,0.2,0.0025,0.0000014,0.0018
```

Then run:

```powershell
python compare_cfd.py
```

It creates `results/bemt_vs_cfd.csv` with percent differences in thrust,
torque, and shaft power. Use water properties and the same RPM / advance
velocity in both calculations.

The comparison coefficients are:

\[
J=\frac{V_a}{nD},\quad
K_T=\frac{T}{\rho n^2D^4},\quad
K_Q=\frac{Q}{\rho n^2D^5},\quad
K_P=2\pi K_Q
\]
