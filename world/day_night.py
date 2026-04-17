import math
from ursina import *


DAY_SPEED = 0.5


class DayNightCycle:
    def __init__(self, sun_light, ambient_light, sky=None):
        self.sun = sun_light
        self.ambient = ambient_light
        self.sky = sky

        self.day = 1
        self.time_of_day = 8.0  # 0-24 hour clock
        self._day_seconds = 60 * (24 / DAY_SPEED)

        self._callbacks = []

    def on_new_day(self, cb):
        self._callbacks.append(cb)

    def update(self):
        dt = time.dt
        self.time_of_day += dt * DAY_SPEED * (24 / 60)
        if self.time_of_day >= 24.0:
            self.time_of_day -= 24.0
            self.day += 1
            for cb in self._callbacks:
                cb(self.day)

        self._apply_lighting()

    def _apply_lighting(self):
        t = self.time_of_day
        norm = t / 24.0

        sun_angle = (norm * 360) - 90
        sun_rad = math.radians(sun_angle)
        self.sun.rotation = (sun_angle, 45, 0)

        # Sky / ambient color transition
        if 6 <= t < 12:
            f = (t - 6) / 6.0
            sky_col = _lerp_color((40, 30, 70), (135, 180, 255), f)
            sun_col = _lerp_color((255, 180, 100), (255, 255, 240), f)
            amb_val = _lerp_float(0.25, 0.65, f)
        elif 12 <= t < 18:
            f = (t - 12) / 6.0
            sky_col = _lerp_color((135, 180, 255), (255, 140, 60), f)
            sun_col = _lerp_color((255, 255, 240), (255, 180, 80), f)
            amb_val = _lerp_float(0.65, 0.35, f)
        elif 18 <= t < 21:
            f = (t - 18) / 3.0
            sky_col = _lerp_color((255, 140, 60), (30, 20, 60), f)
            sun_col = _lerp_color((255, 180, 80), (80, 60, 120), f)
            amb_val = _lerp_float(0.35, 0.12, f)
        else:
            # night (21-6)
            if t >= 21:
                f = (t - 21) / 9.0
            else:
                f = (t + 3) / 9.0
            sky_col = _lerp_color((30, 20, 60), (15, 15, 35), min(f, 1.0))
            sun_col = (40, 50, 80)
            amb_val = 0.10

        r, g, b = sky_col
        self.sun.color = color.rgb(*sun_col)
        self.ambient.color = color.hsv(0, 0, amb_val)

        if self.sky:
            self.sky.color = color.rgb(r, g, b)

    @property
    def hour(self):
        return int(self.time_of_day)

    @property
    def minute(self):
        return int((self.time_of_day % 1.0) * 60)

    @property
    def is_night(self):
        return self.time_of_day < 6 or self.time_of_day >= 21


def _lerp_float(a, b, t):
    t = max(0.0, min(1.0, t))
    return a + (b - a) * t


def _lerp_color(a, b, t):
    t = max(0.0, min(1.0, t))
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )
