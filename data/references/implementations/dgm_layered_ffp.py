#!/usr/bin/env python3
"""Stable direct-global-matrix (DGM) wavenumber-integration reference.

Point source in a pressure-release waveguide made of horizontally stratified,
lossless fluid layers over a downward-radiating fluid half-space. Time
convention: e^{-iwt}; source normalisation: free-field e^{ikR}/(4 pi R) for
``source_strength=1`` (identical to the legacy ``layered_ffp.py``).

Differences from ``src/.../layered_ffp.py`` (kept untouched):

* Each finite layer uses the stable DGM parameterisation
  ``A exp(iq (z - z_top)) + B exp(iq (z_bot - z))`` so no exponential grows
  inside a layer (the legacy ``exp(-iq (z - z_top))`` term overflows for
  evanescent wavenumbers).
* The direct source term is removed from the spectral integrand and added
  analytically in the range domain, so the integrand decays even when the
  receiver is at the source depth.
* Trapezoid rule on a contour shifted by ``gamma = contour_decay * dk / (2 pi)``
  below the real axis. With lossless trapped-mode poles on the real axis the
  wrap-around (alias) error of the J0 representation is ~exp(-contour_decay)
  relative to each modal term; the legacy value contour_decay=3 leaves ~5 %
  per-mode errors, while 15-20 makes them negligible. Because the Bessel kernel
  is evaluated at the complex argument exactly, no exp(+gamma r) correction is
  needed.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import numpy as np
from scipy.special import jv


def _radiating_sqrt(value: np.ndarray) -> np.ndarray:
    out = np.sqrt(np.asarray(value, dtype=np.complex128))
    return np.where(np.imag(out) < 0.0, -out, out)


@dataclass(frozen=True)
class DGMSettings:
    """Numerical settings of one reference level."""

    range_window_m: float = 4.0e5
    contour_decay: float = 20.0
    k_extra_rad_per_m: float = 0.8

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


class StableLayeredFFP:
    """DGM point-source field for fluid layers over a fluid half-space."""

    def __init__(
        self,
        *,
        freq_hz: float,
        interfaces_m: list[float] | tuple[float, ...],
        c_mps: list[float] | tuple[float, ...],
        rho_kg_m3: list[float] | tuple[float, ...],
        source_depth_m: float,
        settings: DGMSettings = DGMSettings(),
        source_strength: complex = 1.0 + 0.0j,
    ) -> None:
        interfaces = np.asarray(interfaces_m, dtype=float)
        if interfaces.ndim != 1 or interfaces.size < 1 or np.any(np.diff(interfaces) <= 0):
            raise ValueError("interfaces_m must be increasing finite-layer bottoms")
        if len(c_mps) != interfaces.size + 1 or len(rho_kg_m3) != interfaces.size + 1:
            raise ValueError("need one sound speed/density per finite layer plus half-space")
        self.freq_hz = float(freq_hz)
        self.settings = settings
        self.omega = 2.0 * math.pi * self.freq_hz
        self.ztop = np.r_[0.0, interfaces]
        self.zbot = np.r_[interfaces, np.inf]
        self.c = np.asarray(c_mps, dtype=float)
        self.rho = np.asarray(rho_kg_m3, dtype=float)
        self.n_finite = int(interfaces.size)
        self.zs = float(source_depth_m)
        self.strength = complex(source_strength)
        self.k_layer = self.omega / self.c
        dk = 2.0 * math.pi / float(settings.range_window_m)
        kmax = float(np.max(self.k_layer)) + float(settings.k_extra_rad_per_m)
        self.nk = int(kmax / dk) + 1
        self.k_real = np.arange(self.nk, dtype=float) * dk
        self.dk = dk
        self.gamma = float(settings.contour_decay) * dk / (2.0 * math.pi)
        self.kr = self.k_real - 1j * self.gamma
        self.q = np.asarray([_radiating_sqrt(k**2 - self.kr**2) for k in self.k_layer])
        self.source_layer = self.layer_of(self.zs)
        if self.source_layer >= self.n_finite:
            raise ValueError("a source in the half-space is not supported")
        self._solve()

    # ------------------------------------------------------------------
    def layer_of(self, z_m: float) -> int:
        z = float(z_m)
        for j in range(self.n_finite):
            if self.ztop[j] - 1e-9 <= z <= self.zbot[j] + 1e-9:
                return j
        if z < 0.0:
            raise ValueError("receiver above the pressure-release surface")
        return self.n_finite

    def _direct(self, j: int, z: float) -> tuple[np.ndarray | float, np.ndarray | float]:
        if j != self.source_layer:
            return 0.0, 0.0
        q = self.q[j]
        e = np.exp(1j * q * abs(z - self.zs))
        value = self.strength * 1j * e / (4.0 * math.pi * q)
        sign = 1.0 if z >= self.zs else -1.0
        derivative = -self.strength * sign * e / (4.0 * math.pi)
        return value, derivative

    def _solve(self) -> None:
        n_fin = self.n_finite
        n_unknown = 2 * n_fin + 1
        nk = self.kr.size
        matrix = np.zeros((nk, n_unknown, n_unknown), dtype=np.complex128)
        rhs = np.zeros((nk, n_unknown), dtype=np.complex128)

        def add_pressure(row: int, j: int, z: float, sign: float) -> None:
            q = self.q[j]
            if j < n_fin:
                matrix[:, row, 2 * j] += sign * np.exp(1j * q * (z - self.ztop[j]))
                matrix[:, row, 2 * j + 1] += sign * np.exp(1j * q * (self.zbot[j] - z))
            else:
                matrix[:, row, 2 * n_fin] += sign * np.exp(1j * q * (z - self.ztop[j]))

        def add_velocity(row: int, j: int, z: float, sign: float) -> None:
            q = self.q[j]
            rho = self.rho[j]
            if j < n_fin:
                matrix[:, row, 2 * j] += sign * (1j * q / rho) * np.exp(1j * q * (z - self.ztop[j]))
                matrix[:, row, 2 * j + 1] += sign * (-1j * q / rho) * np.exp(1j * q * (self.zbot[j] - z))
            else:
                matrix[:, row, 2 * n_fin] += sign * (1j * q / rho) * np.exp(1j * q * (z - self.ztop[j]))

        row = 0
        add_pressure(row, 0, 0.0, 1.0)
        g0, _ = self._direct(0, 0.0)
        rhs[:, row] = -g0
        row += 1
        for j in range(n_fin):
            zi = float(self.zbot[j])
            add_pressure(row, j, zi, 1.0)
            add_pressure(row, j + 1, zi, -1.0)
            g_up, dg_up = self._direct(j, zi)
            g_dn, dg_dn = self._direct(j + 1, zi)
            rhs[:, row] = -g_up + g_dn
            row += 1
            add_velocity(row, j, zi, 1.0)
            add_velocity(row, j + 1, zi, -1.0)
            rhs[:, row] = -dg_up / self.rho[j] + dg_dn / self.rho[j + 1]
            row += 1
        self.amplitudes = np.linalg.solve(matrix, rhs[..., np.newaxis])[..., 0]

    def homogeneous_spectrum(self, z_m: float) -> np.ndarray:
        z = float(z_m)
        j = self.layer_of(z)
        q = self.q[j]
        if j < self.n_finite:
            return self.amplitudes[:, 2 * j] * np.exp(1j * q * (z - self.ztop[j])) + self.amplitudes[
                :, 2 * j + 1
            ] * np.exp(1j * q * (self.zbot[j] - z))
        return self.amplitudes[:, 2 * self.n_finite] * np.exp(1j * q * (z - self.ztop[j]))

    def _weights(self) -> np.ndarray:
        weights = np.full(self.k_real.size, self.dk)
        weights[0] *= 0.5
        weights[-1] *= 0.5
        return weights

    def _direct_range(self, r: np.ndarray, z: float) -> np.ndarray:
        if self.layer_of(z) != self.source_layer:
            return np.zeros_like(r, dtype=np.complex128)
        big_r = np.sqrt(r**2 + (z - self.zs) ** 2)
        k = self.k_layer[self.source_layer]
        return self.strength * np.exp(1j * k * big_r) / (4.0 * math.pi * big_r)

    def pressure_range_line(self, range_m: np.ndarray, receiver_depth_m: float, *, chunk: int = 32) -> np.ndarray:
        r = np.asarray(range_m, dtype=float)
        if np.any(r <= 0.0):
            raise ValueError("ranges must be positive")
        integrand = self.homogeneous_spectrum(receiver_depth_m) * self.kr * self._weights()
        out = np.empty(r.size, dtype=np.complex128)
        for start in range(0, r.size, chunk):
            rr = r[start : start + chunk]
            out[start : start + chunk] = jv(0, np.outer(rr, self.kr)) @ integrand
        return out + self._direct_range(r, float(receiver_depth_m))

    def pressure_vertical_line(self, range_m: float, depths_m: np.ndarray) -> np.ndarray:
        depths = np.asarray(depths_m, dtype=float)
        kernel = jv(0, self.kr * float(range_m)) * self.kr * self._weights()
        out = np.empty(depths.size, dtype=np.complex128)
        for idx, z in enumerate(depths):
            if z <= 0.0:
                out[idx] = 0.0
                continue
            value = np.dot(self.homogeneous_spectrum(float(z)), kernel)
            out[idx] = value + self._direct_range(np.asarray([float(range_m)]), float(z))[0]
        return out

    def metadata(self) -> dict[str, object]:
        return {
            "method": "stable_dgm_wavenumber_integration_trapezoid_shifted_contour",
            "time_convention": "e^{-iwt}",
            "source_normalisation": "free-field exp(ikR)/(4 pi R)",
            "frequency_hz": self.freq_hz,
            "layer_tops_m": self.ztop.tolist(),
            "c_mps": self.c.tolist(),
            "rho_kg_m3": self.rho.tolist(),
            "source_depth_m": self.zs,
            "settings": self.settings.as_dict(),
            "nk": int(self.nk),
            "dk_rad_per_m": float(self.dk),
            "kmax_rad_per_m": float(self.k_real[-1]),
            "contour_offset_gamma": float(self.gamma),
        }
