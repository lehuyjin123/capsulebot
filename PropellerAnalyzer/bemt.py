"""A small, transparent blade-element/momentum (BEMT) solver.

It is intended for preliminary comparison against CFD.  It uses an annular
momentum balance, hence it also remains defined for the static condition
(advance velocity equal to zero).
"""

from dataclasses import dataclass
import math
import numpy as np


@dataclass
class OperatingPoint:
    rpm: float
    advance_velocity: float


@dataclass
class Performance:
    rpm: float
    advance_velocity: float
    thrust_n: float
    torque_nm: float
    power_w: float
    kt: float
    kq: float
    kp: float
    j: float
    efficiency: float
    converged: bool
    iterations: int
    reynolds_075r: float


class BEMTSolver:
    def __init__(self, cfg):
        self.cfg = cfg
        self.radius = cfg.DIAMETER_M / 2.0
        table = np.asarray(cfg.SECTIONS, dtype=float)
        self.r = table[:, 0] * self.radius
        self.c = table[:, 1] * 1e-3
        self.beta = np.deg2rad(table[:, 2])
        if len(self.r) < 3 or np.any(np.diff(self.r) <= 0):
            raise ValueError("SECTIONS must contain at least 3 increasing r/R values")
        self.dr = self._annulus_widths(self.r)

    @staticmethod
    def _annulus_widths(r):
        edges = np.empty(len(r) + 1)
        edges[1:-1] = 0.5 * (r[:-1] + r[1:])
        edges[0] = r[0] - 0.5 * (r[1] - r[0])
        edges[-1] = r[-1] + 0.5 * (r[-1] - r[-2])
        return np.diff(edges)

    def _polar(self, alpha):
        cl = self.cfg.LIFT_CURVE_SLOPE * (alpha - math.radians(self.cfg.ALPHA_ZERO_DEG))
        cl = np.clip(cl, self.cfg.CL_MIN, self.cfg.CL_MAX)
        cd = self.cfg.CD0 + self.cfg.CD2 * cl * cl
        return cl, cd

    def solve(self, op: OperatingPoint) -> Performance:
        omega = op.rpm * 2.0 * math.pi / 60.0
        va = max(0.0, op.advance_velocity)
        # Initial induced velocity gives stable convergence at static thrust.
        vi = np.full_like(self.r, max(0.02, 0.10 * omega * self.radius))
        vtheta = np.zeros_like(self.r)
        converged = False

        for iteration in range(1, self.cfg.MAX_ITERATIONS + 1):
            wt = np.maximum(omega * self.r - vtheta, 1e-8)
            wa = va + vi
            w = np.hypot(wt, wa)
            phi = np.arctan2(wa, wt)
            cl, cd = self._polar(self.beta - phi)
            lift = 0.5 * self.cfg.RHO * w * w * self.c * cl
            drag = 0.5 * self.cfg.RHO * w * w * self.c * cd
            d_thrust = self.cfg.BLADES * (lift * np.cos(phi) - drag * np.sin(phi)) * self.dr
            d_torque = self.cfg.BLADES * (lift * np.sin(phi) + drag * np.cos(phi)) * self.r * self.dr

            # Annular axial and angular-momentum balance.  A negative local
            # thrust is allowed to decay its induced velocity to zero.
            discriminant = va * va + np.maximum(d_thrust, 0.0) / (
                math.pi * self.cfg.RHO * self.r * self.dr
            )
            vi_target = 0.5 * (-va + np.sqrt(discriminant))
            vd = np.maximum(va + vi_target, 1e-7)
            vt_target = np.maximum(
                d_torque / (4.0 * math.pi * self.cfg.RHO * self.r**2 * vd * self.dr), 0.0
            )
            next_vi = (1.0 - self.cfg.RELAXATION) * vi + self.cfg.RELAXATION * vi_target
            next_vtheta = (1.0 - self.cfg.RELAXATION) * vtheta + self.cfg.RELAXATION * vt_target
            error = max(np.max(np.abs(next_vi - vi)), np.max(np.abs(next_vtheta - vtheta)))
            vi, vtheta = next_vi, next_vtheta
            if error < self.cfg.CONVERGENCE_TOL:
                converged = True
                break

        # Re-evaluate at the final induced velocities for reported loads.
        wt = np.maximum(omega * self.r - vtheta, 1e-8)
        wa = va + vi
        w = np.hypot(wt, wa)
        phi = np.arctan2(wa, wt)
        cl, cd = self._polar(self.beta - phi)
        lift = 0.5 * self.cfg.RHO * w * w * self.c * cl
        drag = 0.5 * self.cfg.RHO * w * w * self.c * cd
        thrust = float(np.sum(self.cfg.BLADES * (lift * np.cos(phi) - drag * np.sin(phi)) * self.dr))
        torque = float(np.sum(self.cfg.BLADES * (lift * np.sin(phi) + drag * np.cos(phi)) * self.r * self.dr))
        power = torque * omega
        n = op.rpm / 60.0
        d = self.cfg.DIAMETER_M
        kt = thrust / (self.cfg.RHO * n**2 * d**4)
        kq = torque / (self.cfg.RHO * n**2 * d**5)
        kp = power / (self.cfg.RHO * n**3 * d**5)
        j = va / (n * d)
        efficiency = va * thrust / power if power > 0.0 else float("nan")
        re_075 = self._reynolds_at(0.75 * self.radius, omega, va, vi, vtheta)
        return Performance(op.rpm, va, thrust, torque, power, kt, kq, kp, j,
                           efficiency, converged, iteration, re_075)

    def _reynolds_at(self, radius, omega, va, vi, vtheta):
        chord = np.interp(radius, self.r, self.c)
        induced_a = np.interp(radius, self.r, vi)
        induced_t = np.interp(radius, self.r, vtheta)
        relative_speed = math.hypot(omega * radius - induced_t, va + induced_a)
        return self.cfg.RHO * relative_speed * chord / self.cfg.MU

    def sweep(self, rpms, advance_velocities):
        return [self.solve(OperatingPoint(rpm, velocity))
                for rpm in rpms for velocity in advance_velocities]
