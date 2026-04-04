"""Truchet tile individual — quarter-arc or diagonal tiling patterns.

Each cell in a grid is randomly assigned one of two orientations.
Quarter-arc arcs naturally connect across tile boundaries, forming
flowing curves that traverse the whole canvas.
"""

import math
import random


class TruchetIndividual:
    """
    Parameters (all in [0, 1]):
      0 – random seed       (determines tile orientations)
      1 – columns           (grid width in tiles)
      2 – rows              (grid height in tiles)
      3 – lines per tile    (concentric arcs/lines inside each tile)
      4 – type bias         (0 = all type-B, 0.5 = 50/50, 1 = all type-A)
      5 – style             (< 0.6 = arcs, >= 0.6 = diagonal lines)
      6 – arc smoothness    (points sampled per arc)
      7 – unused
    """

    NUM_PARAMS = 8

    def __init__(self, params=None):
        if params is None:
            self.params = [random.random() for _ in range(self.NUM_PARAMS)]
        else:
            self.params = list(params)

    # ------------------------------------------------------------------

    def _arc(
        self,
        cx: float, cy: float,
        rx: float, ry: float,
        a_start: float, a_end: float,
        steps: int,
    ) -> list[tuple[float, float]]:
        pts = []
        for i in range(steps + 1):
            a = a_start + (a_end - a_start) * i / steps
            pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
        return pts

    # ------------------------------------------------------------------

    def compute_segments(
        self,
        canvas_width: float = 3200,
        canvas_height: float = 800,
        **_kwargs,
    ) -> list[list[tuple[float, float]]]:
        p = self.params

        seed       = int(p[0] * 1_000_000)
        cols       = max(4, int(p[1] * 44) + 4)        # 4–48
        rows       = max(2, int(p[2] * 14) + 2)        # 2–16
        n_lines    = max(1, int(p[3] * 4) + 1)         # 1–5 concentric arcs
        bias       = p[4]                               # P(type A)
        use_arcs   = p[5] < 0.6
        arc_steps  = max(8, int(p[6] * 24) + 8)        # 8–32 pts per arc

        cw = canvas_width  / cols
        ch = canvas_height / rows

        rng = random.Random(seed)

        paths: list[list[tuple[float, float]]] = []

        for row in range(rows):
            for col in range(cols):
                x0 = col * cw
                y0 = row * ch
                type_a = rng.random() < bias

                for li in range(n_lines):
                    t  = (li + 1) / n_lines   # 1/n … 1
                    rx = cw / 2 * t
                    ry = ch / 2 * t

                    if use_arcs:
                        if type_a:
                            # top-left corner: top-mid → left-mid
                            paths.append(self._arc(x0,      y0,      rx, ry, 0,          math.pi/2,   arc_steps))
                            # bottom-right corner: bottom-mid → right-mid
                            paths.append(self._arc(x0 + cw, y0 + ch, rx, ry, math.pi,    3*math.pi/2, arc_steps))
                        else:
                            # top-right corner: right-mid → top-mid
                            paths.append(self._arc(x0 + cw, y0,      rx, ry, math.pi/2,  math.pi,     arc_steps))
                            # bottom-left corner: left-mid → bottom-mid
                            paths.append(self._arc(x0,      y0 + ch, rx, ry, 3*math.pi/2, 2*math.pi,  arc_steps))
                    else:
                        # Diagonal line variant
                        mx, my = x0 + cw / 2, y0 + ch / 2
                        if type_a:
                            paths.append([(mx - rx, my - ry), (mx + rx, my + ry)])
                        else:
                            paths.append([(mx + rx, my - ry), (mx - rx, my + ry)])

        return paths


class TruchetGeneration:
    def __init__(self, num_individuals: int = 12):
        self.individuals: list[TruchetIndividual] = [
            TruchetIndividual() for _ in range(num_individuals)
        ]
