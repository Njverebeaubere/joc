import random
from ursina import *


ROAD_COLOR = color.rgb(40, 40, 40)
SIDEWALK_COLOR = color.rgb(180, 170, 160)
BUILDING_COLORS = [
    color.rgb(220, 210, 195),
    color.rgb(200, 190, 175),
    color.rgb(180, 160, 140),
    color.rgb(210, 200, 185),
    color.rgb(160, 150, 135),
    color.rgb(230, 220, 210),
    color.rgb(195, 185, 170),
    color.rgb(240, 230, 215),
]
ROOF_COLORS = [
    color.rgb(80, 60, 50),
    color.rgb(100, 70, 50),
    color.rgb(60, 55, 50),
    color.rgb(90, 75, 60),
    color.rgb(120, 90, 70),
]
WINDOW_COLOR = color.rgb(180, 220, 255)
WINDOW_LIT_COLOR = color.rgb(255, 240, 180)
DOOR_COLOR = color.rgb(100, 70, 50)


class CityBuilder:
    def __init__(self):
        self.entities = []
        self.city_size = 120
        self.block_size = 20
        self.road_width = 6
        self.cell_size = self.block_size + self.road_width

    def build(self):
        self._build_ground()
        self._build_roads()
        self._build_city_blocks()
        self._build_streetlights()
        self._build_trees()
        self._build_parked_cars()
        print(f"[CITY] Built {len(self.entities)} city entities.")

    def _build_ground(self):
        ground = Entity(
            model='plane',
            scale=(self.city_size * 2, 1, self.city_size * 2),
            color=color.rgb(60, 80, 50),
            collider='box',
            name='ground'
        )
        ground.editable = False
        self.entities.append(ground)

    def _build_roads(self):
        num_blocks = self.city_size // self.cell_size
        half = self.city_size

        for i in range(-num_blocks, num_blocks + 1):
            offset = i * self.cell_size

            hz = Entity(
                model='cube',
                scale=(half * 2, 0.05, self.road_width),
                position=(0, 0.01, offset),
                color=ROAD_COLOR,
                collider='box'
            )
            self.entities.append(hz)

            vt = Entity(
                model='cube',
                scale=(self.road_width, 0.05, half * 2),
                position=(offset, 0.01, 0),
                color=ROAD_COLOR,
                collider='box'
            )
            self.entities.append(vt)

            # Sidewalks
            for side in [-1, 1]:
                sw_h = Entity(
                    model='cube',
                    scale=(half * 2, 0.08, 1.5),
                    position=(0, 0.02, offset + side * (self.road_width / 2 + 0.75)),
                    color=SIDEWALK_COLOR
                )
                self.entities.append(sw_h)

                sw_v = Entity(
                    model='cube',
                    scale=(1.5, 0.08, half * 2),
                    position=(offset + side * (self.road_width / 2 + 0.75), 0.02, 0),
                    color=SIDEWALK_COLOR
                )
                self.entities.append(sw_v)

    def _build_city_blocks(self):
        num_blocks = self.city_size // self.cell_size
        safehouse_block = (0, 0)

        for row in range(-num_blocks + 1, num_blocks):
            for col in range(-num_blocks + 1, num_blocks):
                cx = col * self.cell_size
                cz = row * self.cell_size

                if (row, col) == safehouse_block:
                    continue

                self._fill_block(cx, cz)

    def _fill_block(self, cx, cz):
        inner = self.block_size - 3
        rng = random.Random(int(cx * 1000 + cz))

        block_type = rng.choice(['dense', 'dense', 'mixed', 'park'])

        if block_type == 'park':
            self._build_park(cx, cz, rng)
            return

        sub = inner // 10
        sub = max(2, sub)

        positions = []
        for r in range(sub):
            for c in range(sub):
                bx = cx - inner / 2 + (c + 0.5) * (inner / sub)
                bz = cz - inner / 2 + (r + 0.5) * (inner / sub)
                positions.append((bx, bz))

        for bx, bz in positions:
            if block_type == 'dense':
                h = rng.uniform(4, 18)
            else:
                h = rng.uniform(3, 8)

            w = rng.uniform(3, inner / sub * 0.85)
            d = rng.uniform(3, inner / sub * 0.85)

            self._build_building(bx, bz, w, h, d, rng)

    def _build_building(self, x, z, w, h, d, rng):
        wall_col = rng.choice(BUILDING_COLORS)
        roof_col = rng.choice(ROOF_COLORS)

        body = Entity(
            model='cube',
            scale=(w, h, d),
            position=(x, h / 2, z),
            color=wall_col,
            collider='box'
        )
        self.entities.append(body)

        roof = Entity(
            model='cube',
            scale=(w + 0.3, 0.4, d + 0.3),
            position=(x, h + 0.2, z),
            color=roof_col
        )
        self.entities.append(roof)

        floors = max(1, int(h // 3))
        for floor in range(floors):
            fy = 1.5 + floor * 3
            if fy + 1.5 > h:
                break

            num_win_x = max(1, int(w // 2))
            num_win_z = max(1, int(d // 2))

            for wx in range(num_win_x):
                win_x = x - w / 2 + (wx + 0.5) * (w / num_win_x)
                lit = rng.random() > 0.4
                wc = WINDOW_LIT_COLOR if lit else WINDOW_COLOR

                Entity(
                    model='cube',
                    scale=(0.7, 0.9, 0.05),
                    position=(win_x, fy, z + d / 2 + 0.01),
                    color=wc
                )
                Entity(
                    model='cube',
                    scale=(0.7, 0.9, 0.05),
                    position=(win_x, fy, z - d / 2 - 0.01),
                    color=wc
                )

            for wz in range(num_win_z):
                win_z = z - d / 2 + (wz + 0.5) * (d / num_win_z)
                lit = rng.random() > 0.4
                wc = WINDOW_LIT_COLOR if lit else WINDOW_COLOR

                Entity(
                    model='cube',
                    scale=(0.05, 0.9, 0.7),
                    position=(x + w / 2 + 0.01, fy, win_z),
                    color=wc
                )
                Entity(
                    model='cube',
                    scale=(0.05, 0.9, 0.7),
                    position=(x - w / 2 - 0.01, fy, win_z),
                    color=wc
                )

        Entity(
            model='cube',
            scale=(1.2, 2.2, 0.1),
            position=(x, 1.1, z + d / 2 + 0.05),
            color=DOOR_COLOR
        )

    def _build_park(self, cx, cz, rng):
        Entity(
            model='cube',
            scale=(self.block_size - 1, 0.1, self.block_size - 1),
            position=(cx, 0.05, cz),
            color=color.rgb(50, 100, 40)
        )

        for _ in range(rng.randint(4, 8)):
            tx = cx + rng.uniform(-7, 7)
            tz = cz + rng.uniform(-7, 7)
            self._build_tree(tx, tz, rng)

        Entity(
            model='cube',
            scale=(self.block_size - 2, 0.12, 1.5),
            position=(cx, 0.06, cz),
            color=SIDEWALK_COLOR
        )
        Entity(
            model='cube',
            scale=(1.5, 0.12, self.block_size - 2),
            position=(cx, 0.06, cz),
            color=SIDEWALK_COLOR
        )

        Entity(
            model='cube',
            scale=(1.5, 0.5, 3),
            position=(cx + 3, 0.25, cz),
            color=color.rgb(139, 90, 40)
        )

    def _build_tree(self, x, z, rng=None):
        if rng is None:
            rng = random
        h = rng.uniform(3, 6)
        trunk = Entity(
            model='cylinder',
            scale=(0.3, h, 0.3),
            position=(x, h / 2, z),
            color=color.rgb(100, 70, 40)
        )
        self.entities.append(trunk)

        canopy_y = h + rng.uniform(1.2, 2.0)
        canopy_r = rng.uniform(1.5, 2.8)
        canopy = Entity(
            model='sphere',
            scale=(canopy_r, canopy_r * 0.9, canopy_r),
            position=(x, canopy_y, z),
            color=color.rgb(30 + rng.randint(0, 40), 100 + rng.randint(0, 40), 30 + rng.randint(0, 20))
        )
        self.entities.append(canopy)

    def _build_streetlights(self):
        num_blocks = self.city_size // self.cell_size
        for i in range(-num_blocks, num_blocks + 1):
            for j in range(-num_blocks, num_blocks + 1):
                ox = i * self.cell_size
                oz = j * self.cell_size

                for corner in [(3, 3), (-3, 3), (3, -3), (-3, -3)]:
                    lx = ox + corner[0]
                    lz = oz + corner[1]

                    pole = Entity(
                        model='cylinder',
                        scale=(0.1, 5, 0.1),
                        position=(lx, 2.5, lz),
                        color=color.rgb(120, 120, 120)
                    )
                    self.entities.append(pole)

                    arm = Entity(
                        model='cube',
                        scale=(0.08, 0.08, 1.2),
                        position=(lx, 5, lz + 0.6),
                        color=color.rgb(120, 120, 120)
                    )
                    self.entities.append(arm)

                    bulb = Entity(
                        model='sphere',
                        scale=(0.25, 0.25, 0.25),
                        position=(lx, 4.9, lz + 1.2),
                        color=color.rgb(255, 240, 180)
                    )
                    self.entities.append(bulb)

    def _build_trees(self):
        num_blocks = self.city_size // self.cell_size
        rng = random.Random(42)
        for i in range(-num_blocks * 2, num_blocks * 2):
            for j in range(-num_blocks * 2, num_blocks * 2):
                if rng.random() > 0.05:
                    continue
                tx = i * (self.cell_size / 2) + rng.uniform(-3, 3)
                tz = j * (self.cell_size / 2) + rng.uniform(-3, 3)
                ox = tx % self.cell_size
                oz = tz % self.cell_size
                if abs(ox) < self.road_width or abs(oz) < self.road_width:
                    continue
                self._build_tree(tx, tz, rng)

    def _build_parked_cars(self):
        num_blocks = self.city_size // self.cell_size
        rng = random.Random(99)
        CAR_COLORS = [
            color.rgb(200, 30, 30),
            color.rgb(30, 80, 200),
            color.rgb(220, 220, 220),
            color.rgb(30, 30, 30),
            color.rgb(200, 180, 30),
            color.rgb(50, 150, 50),
        ]

        for row in range(-num_blocks + 1, num_blocks):
            for col in range(-num_blocks + 1, num_blocks):
                if rng.random() > 0.4:
                    continue
                cx = col * self.cell_size
                cz = row * self.cell_size
                side = rng.choice(['N', 'S', 'E', 'W'])
                half_b = self.block_size / 2

                if side == 'N':
                    cx2 = cx + rng.uniform(-half_b + 2, half_b - 2)
                    cz2 = cz + half_b + self.road_width / 2 - 1
                    rot = 0
                elif side == 'S':
                    cx2 = cx + rng.uniform(-half_b + 2, half_b - 2)
                    cz2 = cz - half_b - self.road_width / 2 + 1
                    rot = 0
                elif side == 'E':
                    cx2 = cx + half_b + self.road_width / 2 - 1
                    cz2 = cz + rng.uniform(-half_b + 2, half_b - 2)
                    rot = 90
                else:
                    cx2 = cx - half_b - self.road_width / 2 + 1
                    cz2 = cz + rng.uniform(-half_b + 2, half_b - 2)
                    rot = 90

                car_col = rng.choice(CAR_COLORS)

                body = Entity(
                    model='cube',
                    scale=(2.0, 0.8, 4.0),
                    position=(cx2, 0.4, cz2),
                    rotation_y=rot,
                    color=car_col,
                    collider='box'
                )
                self.entities.append(body)

                cabin = Entity(
                    model='cube',
                    scale=(1.7, 0.6, 2.2),
                    position=(cx2, 0.95, cz2 - 0.3 if rot == 0 else cz2),
                    rotation_y=rot,
                    color=car_col
                )
                self.entities.append(cabin)

                for wx, wz in [(-0.85, 0.9), (0.85, 0.9), (-0.85, -0.9), (0.85, -0.9)]:
                    Entity(
                        model='cylinder',
                        scale=(0.35, 0.2, 0.35),
                        position=(cx2 + wx, 0.18, cz2 + wz),
                        rotation_z=90,
                        color=color.rgb(20, 20, 20)
                    )
