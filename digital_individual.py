import math
import random


# Signal type is determined by params[0] quantised to these 5 bins
SIGNAL_TYPES = ("square", "sawtooth", "triangle", "pcm", "staircase")


class DigitalIndividual:
    """Individual whose phenotype is a digital-style waveform.

    Parameters (all in [0, 1]):
      0 – signal type  (quantised to SIGNAL_TYPES)
      1 – wavelength   (× 1000 px logical)
      2 – amplitude    (fraction of half-canvas height)
      3 – duty cycle   (square / PCM high-time fraction)
      4 – step count   (staircase / PCM bit depth, scaled to 2–16)
      5 – PCM seed     (determines the random bit pattern)
      6 – number of wave repetitions (× 200)
      7 – unused / reserved
    """

    NUM_PARAMS = 8

    def __init__(self, params=None):
        if params is None:
            self.params = [random.random() for _ in range(self.NUM_PARAMS)]
        else:
            self.params = list(params)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def signal_type(self) -> str:
        idx = min(int(self.params[0] * len(SIGNAL_TYPES)), len(SIGNAL_TYPES) - 1)
        return SIGNAL_TYPES[idx]

    def _pcm_bits(self, n: int) -> list[bool]:
        rng = random.Random(int(self.params[5] * 1_000_000))
        return [rng.random() > 0.5 for _ in range(n)]

    # ------------------------------------------------------------------
    # Geometry
    # ------------------------------------------------------------------

    def compute_points(self) -> list[tuple[float, float]]:
        """Return (x, y) points in logical space (x: 0..total_x, y: 0..800)."""
        p = self.params

        wavelength = max(4, int(p[1] * 1000))
        num_wave = max(1, int(200 * p[6]))
        total_x = num_wave * wavelength

        amplitude = p[2] * 350          # 0–350 px
        center = 400.0
        duty = max(0.05, min(0.95, p[3]))
        num_steps = max(2, int(p[4] * 14) + 2)  # 2–16

        sig = self.signal_type
        bits = self._pcm_bits(64) if sig == "pcm" else []

        # For crisp edges we insert explicit transition points (same x, two y-values).
        # Regular sampling step is coarser; transitions are added precisely.
        coarse = max(1.0, wavelength / 60.0)

        def y_at(xi: float) -> float:
            pos = (xi % wavelength) / wavelength   # 0..1 within cycle
            if sig == "square":
                return center - amplitude if pos < duty else center + amplitude
            elif sig == "sawtooth":
                return center - amplitude + 2 * amplitude * pos
            elif sig == "triangle":
                return (center - amplitude + 4 * amplitude * pos) if pos < 0.5 \
                    else (center + amplitude - 4 * amplitude * (pos - 0.5))
            elif sig == "pcm":
                return center - amplitude if bits[int(pos * len(bits)) % len(bits)] else center + amplitude
            elif sig == "staircase":
                si = int(pos * num_steps)
                return center - amplitude + 2 * amplitude * si / max(1, num_steps - 1)
            return center

        # Collect transition x-values within [0, total_x] where y jumps
        transitions: list[float] = []
        if sig in ("square", "pcm"):
            slot = wavelength / (len(bits) if sig == "pcm" else 1)
            slots = len(bits) if sig == "pcm" else 1
            for k in range(num_wave):
                base = k * wavelength
                if sig == "square":
                    transitions += [base, base + duty * wavelength]
                else:
                    for b in range(slots):
                        transitions.append(base + b * slot)
        elif sig == "staircase":
            for k in range(num_wave):
                for s in range(num_steps):
                    transitions.append(k * wavelength + s * wavelength / num_steps)

        trans_set = set(round(t, 6) for t in transitions if 0 <= t < total_x)

        # Build points: coarse grid + precise transition inserts
        xs: list[float] = []
        x = 0.0
        while x < total_x:
            xs.append(x)
            x += coarse
        xs.append(float(total_x))

        points: list[tuple[float, float]] = []
        for x in sorted(set(xs)):
            xi = round(x, 6)
            if xi in trans_set:
                # Add a point just before (keeps old y) then one at new y
                if points:
                    points.append((x, points[-1][1]))   # hold previous y
            points.append((x, y_at(x)))

        return points

    def compute_segments(
        self,
        canvas_width: float = 3200,
        canvas_height: float = 800,
        egg_width_mult: float = 1.6,
    ) -> list[list[tuple[float, float]]]:
        """Same wrapping logic as organic individual."""
        points = self.compute_points()
        if not points:
            return []

        sy_scale = canvas_height / 800.0
        segments: list[list[tuple[float, float]]] = []
        current: list[tuple[float, float]] = []
        prev_lx: float | None = None
        prev_ly: float | None = None

        for lx, ly in points:
            sx = (lx * egg_width_mult) % canvas_width
            sy = ly * sy_scale

            if prev_lx is not None:
                prev_sx = (prev_lx * egg_width_mult) % canvas_width
                if (prev_sx - sx) > canvas_width * 0.5:
                    k = int(prev_lx * egg_width_mult / canvas_width) + 1
                    lx_b = k * canvas_width / egg_width_mult
                    dlx = lx - prev_lx
                    t = max(0.0, min(1.0, (lx_b - prev_lx) / dlx)) if dlx != 0 else 0.5
                    sy_b = (prev_ly + (ly - prev_ly) * t) * sy_scale  # type: ignore[operator]
                    current.append((canvas_width, sy_b))
                    if len(current) >= 2:
                        segments.append(current)
                    current = [(0.0, sy_b), (sx, sy)]
                else:
                    current.append((sx, sy))
            else:
                current.append((sx, sy))

            prev_lx, prev_ly = lx, ly

        # Discard last incomplete segment (may not reach canvas_width)
        return segments


class DigitalGeneration:
    def __init__(self, num_individuals: int = 12):
        self.individuals: list[DigitalIndividual] = [
            DigitalIndividual() for _ in range(num_individuals)
        ]
