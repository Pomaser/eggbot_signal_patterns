"""Spirograph individual — compound trochoid rosettes tiled across the canvas.

Each cell draws one or two overlapping trochoid curves. The curve type is
determined by k = R/r (can be fractional p/q), d (pen distance), and whether
the small circle rolls inside (hypo) or outside (epi) the fixed circle.

With a fractional k (e.g. 7/3) the curve only closes after q full revolutions,
producing far more intricate patterns than integer-k variants.
"""

import math
import random
from math import gcd


def _trochoid_points(
    k_num: int,
    k_den: int,
    d_ratio: float,
    epi: bool,
    cx: float,
    cy: float,
    radius: float,
    rotation: float,
    steps: int,
) -> list[tuple[float, float]]:
    """Sample one closed trochoid centred at (cx, cy), scaled to fit `radius`.

    k = k_num / k_den   (R/r ratio)
    d_ratio             pen distance / r  (0 = circle, 1 = pointy)
    epi                 True = epitrochoid (rolling outside), False = hypotrochoid
    """
    R = float(k_num)
    r = float(k_den)
    d = r * max(0.05, d_ratio)

    if epi:
        # epitrochoid: rolling outside
        outer = R + r + d
        if outer == 0:
            return []
        scale = radius / outer
        total_t = k_den * 2 * math.pi
        pts = []
        for i in range(steps + 1):
            t = total_t * i / steps + rotation
            x = (R + r) * math.cos(t) - d * math.cos((R + r) / r * t)
            y = (R + r) * math.sin(t) - d * math.sin((R + r) / r * t)
            pts.append((cx + x * scale, cy + y * scale))
    else:
        # hypotrochoid: rolling inside
        outer = abs(R - r) + d
        if outer == 0:
            return []
        scale = radius / outer
        total_t = k_den * 2 * math.pi
        pts = []
        for i in range(steps + 1):
            t = total_t * i / steps + rotation
            x = (R - r) * math.cos(t) + d * math.cos((R - r) / r * t)
            y = (R - r) * math.sin(t) - d * math.sin((R - r) / r * t)
            pts.append((cx + x * scale, cy + y * scale))

    return pts if len(pts) >= 2 else []


class SpirographIndividual:
    """
    Parameters (all in [0, 1]):
      0 – k1 numerator     (R/r for layer 1, 2–13)
      1 – d1 ratio         (pen / r for layer 1: 0 = circle, 1 = star)
      2 – k2 offset        (k2 = k1 + 1..5, drives second overlapping layer)
      3 – d2 ratio         (pen / r for layer 2)
      4 – columns          (grid columns, 2–7)
      5 – rows             (grid rows, 1–4)
      6 – scale            (rosette size relative to cell, 0.4–0.98)
      7 – style            (encodes: denominator 1–5, epi/hypo, dual layer toggle)
    """

    NUM_PARAMS = 8

    def __init__(self, params=None):
        if params is None:
            self.params = [random.random() for _ in range(self.NUM_PARAMS)]
        else:
            self.params = list(params)

    # ------------------------------------------------------------------

    def compute_segments(
        self,
        canvas_width: float = 3200,
        canvas_height: float = 800,
        **_kwargs,
    ) -> list[list[tuple[float, float]]]:
        p = self.params

        # Decode style byte: denominator (1-5), epi flag, dual-layer flag
        style_raw   = int(p[7] * 30)          # 0-29
        k_den_raw   = (style_raw % 5) + 1     # 1-5
        epi         = (style_raw // 5) % 2 == 1
        dual_layer  = (style_raw // 10) >= 1

        # Layer 1
        k1_num_raw = max(2, int(p[0] * 12) + 2)   # 2-13
        g1 = gcd(k1_num_raw, k_den_raw)
        k1_num = k1_num_raw // g1
        k1_den = k_den_raw  // g1
        d1 = max(0.05, p[1])

        # Layer 2 (offset from layer 1)
        k2_offset  = int(p[2] * 5) + 1             # 1-5
        k2_num_raw = k1_num_raw + k2_offset
        g2 = gcd(k2_num_raw, k_den_raw)
        k2_num = k2_num_raw // g2
        k2_den = k_den_raw  // g2
        d2 = max(0.05, p[3])

        cols  = max(2, int(p[4] * 6) + 2)           # 2-7
        rows  = max(1, int(p[5] * 3) + 1)           # 1-4
        scale = 0.4 + p[6] * 0.58                   # 0.4-0.98

        cw = canvas_width  / cols
        ch = canvas_height / rows
        cell_r = min(cw, ch) / 2 * scale

        # Steps: enough for the most complex curve to look smooth
        max_den = max(k1_den, k2_den)
        max_num = max(k1_num, k2_num)
        steps = max(180, max_den * max_num * 30)

        paths: list[list[tuple[float, float]]] = []

        for row in range(rows):
            for col in range(cols):
                cx = (col + 0.5) * cw
                cy = (row + 0.5) * ch

                # Alternate rotation per cell for visual variety
                rotation = (col + row) * math.pi / max(k1_num, 2)

                # Layer 1
                pts = _trochoid_points(
                    k1_num, k1_den, d1, epi,
                    cx, cy, cell_r, rotation, steps,
                )
                if pts:
                    paths.append(pts)

                # Layer 2 (only when dual_layer)
                if dual_layer:
                    # Second layer uses opposite type and slightly smaller radius
                    pts2 = _trochoid_points(
                        k2_num, k2_den, d2, not epi,
                        cx, cy, cell_r * 0.72,
                        rotation + math.pi / max(k1_num, 2),
                        steps,
                    )
                    if pts2:
                        paths.append(pts2)

        return paths


class SpirographGeneration:
    def __init__(self, num_individuals: int = 12):
        self.individuals: list[SpirographIndividual] = [
            SpirographIndividual() for _ in range(num_individuals)
        ]
