"""Kraslice individual — generates traditional Czech/Slovak Easter-egg patterns.

All coordinates are already in screen space (0..canvas_width × 0..canvas_height).
compute_segments() returns one list-of-points per drawn line; the list can contain
many segments (one per lattice line, band row, etc.).
"""

import math
import random

PATTERN_TYPES = ("zigzag", "diamond", "waves", "chevron", "crosshatch")


class KrasliceIndividual:
    """
    Parameters (all in [0, 1]):
      0 – pattern type        (quantised to PATTERN_TYPES)
      1 – primary frequency   (repeat count across width)
      2 – amplitude           (height fraction used by the motif)
      3 – number of rows/bands
      4 – secondary parameter (slope for diamond, duty for chevron, …)
      5 – phase offset
      6 – line density        (lines per band / family density)
      7 – wave modulation     (adds subtle sine variation to straight lines)
    """

    NUM_PARAMS = 8

    def __init__(self, params=None):
        if params is None:
            self.params = [random.random() for _ in range(self.NUM_PARAMS)]
        else:
            self.params = list(params)

    # ------------------------------------------------------------------

    @property
    def pattern_type(self) -> str:
        idx = min(int(self.params[0] * len(PATTERN_TYPES)), len(PATTERN_TYPES) - 1)
        return PATTERN_TYPES[idx]

    # ------------------------------------------------------------------
    # Pattern generators (return list of paths in screen coords)
    # ------------------------------------------------------------------

    def _zigzag(self, W: float, H: float) -> list[list[tuple[float, float]]]:
        """Rows of alternating zigzag lines."""
        p = self.params
        num_rows = max(2, int(p[3] * 20) + 2)
        freq = max(1, int(p[1] * 24) + 1)          # full periods across width
        amp_frac = max(0.1, p[2])
        lines_per_row = max(1, int(p[6] * 4) + 1)
        phase = p[5]

        band_h = H / num_rows
        amp = band_h * 0.48 * amp_frac
        wavelength = W / freq
        step = max(1.0, wavelength / 60.0)

        paths = []
        for row in range(num_rows):
            for li in range(lines_per_row):
                cy = (row + (li + 0.5) / lines_per_row) * band_h
                ph = phase + row * 0.5          # alternate phase each row
                pts: list[tuple[float, float]] = []
                x = 0.0
                while x <= W + step:
                    t = ((x / wavelength) + ph) % 1.0
                    y_norm = 1.0 - 4.0 * abs(t - 0.5)  # triangle wave [-1, 1]
                    pts.append((min(x, W), cy + y_norm * amp))
                    x += step
                if len(pts) >= 2:
                    paths.append(pts)
        return paths

    def _diamond(self, W: float, H: float) -> list[list[tuple[float, float]]]:
        """Two families of diagonal lines crossing to form a diamond lattice."""
        p = self.params
        spacing = max(20, int(p[1] * 280) + 20)     # px between parallel lines
        slope = (p[4] * 0.7 + 0.15) * (H / W)       # dy/dx  (0.15–0.85 × H/W)
        wave_amp = p[7] * 30
        wave_freq = max(1, int(p[6] * 4) + 1)
        step = max(2.0, spacing / 30.0)

        paths = []

        def make_line(offset: float, sign: float) -> list[tuple[float, float]] | None:
            pts: list[tuple[float, float]] = []
            x = 0.0
            while x <= W:
                y = sign * slope * x + offset
                if wave_amp > 0:
                    y += wave_amp * math.sin(2 * math.pi * wave_freq * x / W)
                if 0 <= y <= H:
                    pts.append((x, y))
                elif pts:
                    break           # left canvas — stop tracing
                x += step
            return pts if len(pts) >= 2 else None

        # Family 1: positive slope (bottom-left → top-right on canvas)
        for offset in range(int(-H * 2), int(H * 2 + W * slope) + spacing, spacing):
            pts = make_line(float(offset), 1.0)
            if pts:
                paths.append(pts)

        # Family 2: negative slope (top-left → bottom-right)
        for offset in range(0, int(H + W * slope) + spacing, spacing):
            pts = make_line(float(offset), -1.0)
            if pts:
                paths.append(pts)

        return paths

    def _waves(self, W: float, H: float) -> list[list[tuple[float, float]]]:
        """Uniform parallel sine wave lines across the full height."""
        p = self.params
        num_lines = max(3, int(p[3] * 30) + 3)
        freq = max(1, int(p[1] * 20) + 1)
        amp = (H / num_lines) * 0.45 * p[2]
        phase = p[5]
        wavelength = W / freq
        step = max(1.0, wavelength / 60.0)

        paths = []
        for li in range(num_lines):
            cy = (li + 0.5) * H / num_lines
            ph = phase + li * (p[6] * 2 * math.pi / num_lines)  # per-line phase shift
            pts: list[tuple[float, float]] = []
            x = 0.0
            while x <= W + step:
                y = cy + amp * math.sin(2 * math.pi * x / wavelength + ph)
                pts.append((min(x, W), y))
                x += step
            if len(pts) >= 2:
                paths.append(pts)
        return paths

    def _chevron(self, W: float, H: float) -> list[list[tuple[float, float]]]:
        """Repeating V-shapes (chevrons) arranged in horizontal rows."""
        p = self.params
        num_rows = max(2, int(p[3] * 14) + 2)
        freq = max(1, int(p[1] * 16) + 1)
        amp_frac = max(0.1, p[2])
        lines_per_row = max(1, int(p[6] * 3) + 1)
        duty = max(0.1, min(0.9, p[4]))   # width of the V "peak" relative to period
        phase = p[5]

        band_h = H / num_rows
        amp = band_h * 0.48 * amp_frac
        wavelength = W / freq
        step = max(1.0, wavelength / 60.0)

        paths = []
        for row in range(num_rows):
            for li in range(lines_per_row):
                cy = (row + (li + 0.5) / lines_per_row) * band_h
                ph = phase + row * duty
                pts: list[tuple[float, float]] = []
                x = 0.0
                while x <= W + step:
                    t = ((x / wavelength) + ph) % 1.0
                    # Asymmetric triangle: fast rise (duty), slow fall (1-duty)
                    y_norm = (t / duty) if t < duty else (1.0 - (t - duty) / (1.0 - duty))
                    y_norm = y_norm * 2.0 - 1.0
                    pts.append((min(x, W), cy + y_norm * amp))
                    x += step
                if len(pts) >= 2:
                    paths.append(pts)
        return paths

    def _crosshatch(self, W: float, H: float) -> list[list[tuple[float, float]]]:
        """Two families of sine wave lines crossing at an angle."""
        p = self.params
        num_h = max(3, int(p[3] * 18) + 3)     # horizontal-family lines
        num_d = max(3, int(p[6] * 14) + 3)      # diagonal-family lines
        freq = max(1, int(p[1] * 12) + 1)
        amp_h = (H / num_h) * 0.4 * p[2]
        slope = (p[4] * 0.6 + 0.1) * (H / W)
        phase = p[5]
        wavelength = W / freq
        step = max(1.0, wavelength / 60.0)

        paths = []

        # Family 1: nearly-horizontal wave lines
        for li in range(num_h):
            cy = (li + 0.5) * H / num_h
            ph = phase + li * math.pi / num_h
            pts: list[tuple[float, float]] = []
            x = 0.0
            while x <= W + step:
                y = cy + amp_h * math.sin(2 * math.pi * x / wavelength + ph)
                pts.append((min(x, W), y))
                x += step
            if len(pts) >= 2:
                paths.append(pts)

        # Family 2: diagonal wave lines
        amp_d = (H / num_d) * 0.4 * p[2]
        diag_spacing = int(W / num_d)
        for li in range(num_d + 1):
            x_offset = li * diag_spacing
            ph = phase
            pts = []
            x = 0.0
            while x <= W:
                y = slope * (x - x_offset) + H / 2
                y += amp_d * math.sin(2 * math.pi * x / wavelength + ph)
                if 0 <= y <= H:
                    pts.append((x, y))
                elif pts:
                    break
                x += step
            if len(pts) >= 2:
                paths.append(pts)

        return paths

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def compute_segments(
        self,
        canvas_width: float = 3200,
        canvas_height: float = 800,
        **_kwargs,
    ) -> list[list[tuple[float, float]]]:
        """Return all drawn lines as a list of paths (screen coordinates)."""
        dispatch = {
            "zigzag":    self._zigzag,
            "diamond":   self._diamond,
            "waves":     self._waves,
            "chevron":   self._chevron,
            "crosshatch": self._crosshatch,
        }
        fn = dispatch.get(self.pattern_type, self._zigzag)
        return fn(canvas_width, canvas_height)


class KrasliceGeneration:
    def __init__(self, num_individuals: int = 12):
        self.individuals: list[KrasliceIndividual] = [
            KrasliceIndividual() for _ in range(num_individuals)
        ]
