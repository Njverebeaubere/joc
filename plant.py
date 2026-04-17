import math
from ursina import *
from panda3d.core import TransparencyAttrib


class PlantActor(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='sphere',
            color=color.rgb(30, 120, 30),
            collider='box',
            **kwargs
        )
        self.set_transparency(TransparencyAttrib.MAlpha)
        self.scale = (0.15, 0.15, 0.15)

        self.growth = 0.0
        self.health = 100.0
        self.ph_level = 7.0
        self.water_level = 50.0
        self.light_cycle_on = True
        self.smell_radius = 0.0
        self.age = 0.0

        self._stem = Entity(
            parent=self,
            model='cylinder',
            color=color.rgb(80, 50, 20),
            scale=(0.3, 1.2, 0.3),
            position=(0, -0.5, 0)
        )

        self._pot = Entity(
            parent=self,
            model='cylinder',
            color=color.rgb(150, 90, 40),
            scale=(1.1, 0.9, 1.1),
            position=(0, -1.6, 0)
        )

        self._pot_soil = Entity(
            parent=self,
            model='cylinder',
            color=color.rgb(80, 55, 30),
            scale=(1.0, 0.2, 1.0),
            position=(0, -1.2, 0)
        )

        self._leaves = []
        self._create_leaves(10)

    def _create_leaves(self, count):
        for i in range(count):
            angle = (i / count) * 360
            dist = 0.55 + (i % 3) * 0.22
            lx = dist * math.cos(math.radians(angle))
            lz = dist * math.sin(math.radians(angle))
            ly = 0.05 + (i % 4) * 0.28

            leaf = Entity(
                parent=self,
                model='quad',
                color=color.rgb(25 + i * 4, 130 + i * 2, 25),
                scale=(0.55, 0.55, 0.55),
                position=(lx, ly, lz),
                rotation=(0, angle, 30 + i * 5),
                double_sided=True
            )
            self._leaves.append(leaf)

    def custom_update(self):
        if self.health <= 0:
            self.color = color.rgb(60, 60, 40)
            return

        dt = time.dt
        self.age += dt

        ph_eff = 1.0
        if self.ph_level < 6.0 or self.ph_level > 6.8:
            ph_eff = max(0.1, 1.0 - abs(self.ph_level - 6.4) * 0.4)

        water_eff = 1.0
        if self.water_level < 30:
            water_eff = 0.4
            self.health -= 2.5 * dt
        elif self.water_level > 85:
            water_eff = 0.2
            self.health -= 4.0 * dt

        if self.light_cycle_on and self.health > 0:
            growth_rate = 0.0008 * ph_eff * water_eff
            self.growth = min(1.0, self.growth + growth_rate * dt)
            self.smell_radius = self.growth * 12.0

        if self.water_level > 0:
            self.water_level -= 0.1 * dt

        s = 0.12 + self.growth * 1.8
        self.scale = (s, s, s)

        stage = int(self.growth * 4)
        if stage == 0:
            leaf_col = color.rgb(20, 100, 20)
        elif stage == 1:
            leaf_col = color.rgb(25, 130, 25)
        elif stage == 2:
            leaf_col = color.rgb(30, 150, 30)
        else:
            leaf_col = color.rgb(15, 110, 15)

        for leaf in self._leaves:
            leaf.color = leaf_col

        pulse = math.sin(self.age * 2.0) * 0.02
        self._stem.scale = (0.3 + pulse, 1.2, 0.3 + pulse)

    @property
    def maturity_pct(self):
        return min(100.0, self.growth * 100.0)

    @property
    def is_harvestable(self):
        return self.growth >= 1.0 and self.health > 20
