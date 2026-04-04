import math
import random


class Individual:
    NUM_PARAMS = 8
    DEFAULT_RATING = 0.4

    def __init__(self, params=None):
        if params is None:
            self.params = [random.random() for _ in range(self.NUM_PARAMS)]
        else:
            self.params = list(params)
        self.rating = self.DEFAULT_RATING
        self.parents: list[int] = []

    # ------------------------------------------------------------------
    # Geometry
    # ------------------------------------------------------------------

    def compute_points(self) -> list[tuple[float, float]]:
        """Return list of (x, y) points in logical space (x: 0..total_x, y: 0..800).

        x values are NOT yet scaled to SVG/canvas width — callers do that.
        Returns empty list when parameters produce no drawable path.
        """
        p = self.params

        wavelength = max(1, int(p[1] * 1000))
        num_wave = int(200 * p[6])

        if num_wave == 0:
            return []

        wavelength = max(1, int(p[1] * 1000))
        step = max(1.0, wavelength / 40.0)
        total_x = num_wave * wavelength

        # Snap modulation wavelengths to the nearest integer divisor of total_x
        # so that all sine terms complete whole cycles → y_end == y_start (seamless on egg).
        raw_mod_wl1 = max(1, int(p[3] * 1000))
        n1 = max(1, round(total_x / raw_mod_wl1))
        mod_wl1 = total_x / n1

        raw_mod_wl2 = max(1, int(p[5] * 1000))
        n2 = max(1, round(total_x / raw_mod_wl2))
        mod_wl2 = total_x / n2

        use_second_mod = p[7] < 0.5

        def sample(xi: int) -> float:
            mod_y = p[2] * 250 * math.sin((xi % mod_wl1) / mod_wl1 * 2 * math.pi)
            if use_second_mod:
                mod_y += p[4] * 150 * math.sin((xi % mod_wl2) / mod_wl2 * 2 * math.pi)
            return 350 - p[0] * 250 * math.sin((xi % wavelength) / wavelength * 2 * math.pi) + mod_y

        points: list[tuple[float, float]] = []
        x = 0.0
        while x < total_x:
            points.append((x, sample(int(x))))
            x += step

        # Add the exact endpoint so all sines complete whole cycles (y_end == y_start).
        # total_x is a multiple of PASS_LENGTH so its screen x maps to 0; compute_segments
        # uses this to close the last segment precisely at canvas_width=3200.
        points.append((float(total_x), sample(total_x)))

        return points

    def compute_segments(
        self,
        canvas_width: float = 3200,
        canvas_height: float = 800,
        egg_width_mult: float = 1.6,
    ) -> list[list[tuple[float, float]]]:
        """Return the path split into segments for rendering.

        The original EggBot canvas wraps the x-axis: x is multiplied by
        egg_width_mult (1.6 for egg curvature) and then wraps modulo
        canvas_width.  Each wrap creates a new overlapping pass, producing
        the dense, interleaved pattern visible in the reference images.

        Every segment starts exactly at x=0 and ends exactly at x=canvas_width.
        The y coordinate is clamped to [0, canvas_height].
        Returns a list of segments; each segment is a list of (x, y) points
        already scaled to [0, canvas_width] × [0, canvas_height].
        """
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
                    # Wrap detected: interpolate the exact x=canvas_width boundary point.
                    # Find lx_b where lx_b * egg_width_mult == k * canvas_width
                    k = int(prev_lx * egg_width_mult / canvas_width) + 1
                    lx_b = k * canvas_width / egg_width_mult
                    dlx = lx - prev_lx
                    t = max(0.0, min(1.0, (lx_b - prev_lx) / dlx)) if dlx != 0 else 0.5
                    sy_b = (prev_ly + (ly - prev_ly) * t) * sy_scale  # type: ignore[operator]

                    current.append((canvas_width, sy_b))
                    if len(current) >= 2:
                        segments.append(current)
                    # New segment starts exactly at x=0
                    current = [(0.0, sy_b), (sx, sy)]
                else:
                    current.append((sx, sy))
            else:
                current.append((sx, sy))

            prev_lx, prev_ly = lx, ly

        if len(current) >= 2:
            segments.append(current)

        return segments

    # ------------------------------------------------------------------
    # GA operations
    # ------------------------------------------------------------------



    def mutate(self, probability: float = 0.1) -> None:
        for i in range(self.NUM_PARAMS):
            if random.random() < probability:
                self.params[i] = max(0.0, min(1.0, self.params[i] + random.gauss(0, 0.25)))

    def clone(self) -> "Individual":
        ind = Individual(self.params)
        # rating intentionally reset for new generation
        return ind
