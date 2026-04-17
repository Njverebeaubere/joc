from ursina import *


WALL_COLOR = color.rgb(230, 215, 195)
FLOOR_COLOR = color.rgb(180, 160, 130)
CEILING_COLOR = color.rgb(240, 230, 215)
DOOR_COLOR = color.rgb(110, 80, 55)
WINDOW_FRAME_COLOR = color.rgb(200, 180, 150)
FURNITURE_COLOR = color.rgb(160, 120, 80)
TILE_COLOR = color.rgb(200, 195, 185)
GROW_LIGHT_COLOR = color.rgb(255, 100, 100)


class Safehouse:
    def __init__(self, position=(0, 0, 0)):
        self.position = Vec3(*position)
        self.entities = []
        self.entry_door = None
        self.grow_room_door = None
        self.plant_position = Vec3(self.position.x, 0.05, self.position.z - 2)

        self._build()

    def _build(self):
        px, py, pz = self.position.x, self.position.y, self.position.z

        W = 12
        D = 16
        H = 3.2
        WT = 0.25

        e = Entity(
            model='cube',
            scale=(W + 0.5, 0.3, D + 0.5),
            position=(px, -0.15, pz),
            color=color.rgb(160, 150, 140),
            collider='box'
        )
        self.entities.append(e)

        floor = Entity(
            model='cube',
            scale=(W, 0.1, D),
            position=(px, 0.05, pz),
            color=FLOOR_COLOR,
            collider='box'
        )
        self.entities.append(floor)

        ceiling = Entity(
            model='cube',
            scale=(W, 0.15, D),
            position=(px, H, pz),
            color=CEILING_COLOR
        )
        self.entities.append(ceiling)

        roof = Entity(
            model='cube',
            scale=(W + 0.6, 0.35, D + 0.6),
            position=(px, H + 0.17, pz),
            color=color.rgb(100, 80, 60)
        )
        self.entities.append(roof)

        # Front wall with door gap
        front_left = Entity(
            model='cube',
            scale=((W / 2 - 1.2), H, WT),
            position=(px - (W / 4 + 0.6), H / 2, pz + D / 2),
            color=WALL_COLOR,
            collider='box'
        )
        self.entities.append(front_left)

        front_right = Entity(
            model='cube',
            scale=((W / 2 - 1.2), H, WT),
            position=(px + (W / 4 + 0.6), H / 2, pz + D / 2),
            color=WALL_COLOR,
            collider='box'
        )
        self.entities.append(front_right)

        Entity(
            model='cube',
            scale=(2.4, 0.8, WT),
            position=(px, H - 0.4, pz + D / 2),
            color=WALL_COLOR,
            collider='box'
        )

        self.entry_door = Entity(
            model='cube',
            scale=(1.1, 2.2, 0.08),
            position=(px - 0.6, 1.1, pz + D / 2 + 0.04),
            color=DOOR_COLOR,
            collider='box',
            name='entry_door'
        )
        self.entities.append(self.entry_door)

        back = Entity(
            model='cube',
            scale=(W, H, WT),
            position=(px, H / 2, pz - D / 2),
            color=WALL_COLOR,
            collider='box'
        )
        self.entities.append(back)

        left = Entity(
            model='cube',
            scale=(WT, H, D),
            position=(px - W / 2, H / 2, pz),
            color=WALL_COLOR,
            collider='box'
        )
        self.entities.append(left)

        right = Entity(
            model='cube',
            scale=(WT, H, D),
            position=(px + W / 2, H / 2, pz),
            color=WALL_COLOR,
            collider='box'
        )
        self.entities.append(right)

        # Interior divider
        div_left = Entity(
            model='cube',
            scale=((W / 2 - 1.0), H, WT),
            position=(px - (W / 4 + 0.5), H / 2, pz),
            color=WALL_COLOR,
            collider='box'
        )
        self.entities.append(div_left)

        div_right = Entity(
            model='cube',
            scale=((W / 2 - 1.0), H, WT),
            position=(px + (W / 4 + 0.5), H / 2, pz),
            color=WALL_COLOR,
            collider='box'
        )
        self.entities.append(div_right)

        Entity(
            model='cube',
            scale=(2.0, 0.8, WT),
            position=(px, H - 0.4, pz),
            color=WALL_COLOR
        )

        self.grow_room_door = Entity(
            model='cube',
            scale=(1.0, 2.2, 0.08),
            position=(px - 0.5, 1.1, pz + 0.04),
            color=color.rgb(80, 55, 35),
            collider='box',
            name='grow_room_door'
        )
        self.entities.append(self.grow_room_door)

        # Windows
        for wx in [px - W / 2 + 2.5, px + W / 2 - 2.5]:
            Entity(
                model='cube',
                scale=(1.6, 1.4, 0.1),
                position=(wx, H / 2 + 0.3, pz + D / 2 + 0.01),
                color=WINDOW_FRAME_COLOR
            )
            Entity(
                model='cube',
                scale=(1.4, 1.2, 0.06),
                position=(wx, H / 2 + 0.3, pz + D / 2 + 0.02),
                color=color.rgb(150, 200, 240)
            )

        # Grow room UV lights
        grow_z = pz - D / 4
        for lx in [px - 1.5, px + 1.5]:
            Entity(
                model='cube',
                scale=(1.0, 0.12, 0.5),
                position=(lx, H - 0.1, grow_z),
                color=GROW_LIGHT_COLOR
            )
            Entity(
                model='sphere',
                scale=(0.25, 0.25, 0.25),
                position=(lx, H - 0.22, grow_z),
                color=color.rgb(255, 50, 50)
            )

        # Tile floor in grow room
        for ti in range(-2, 3):
            for tj in range(-3, 0):
                tc = TILE_COLOR if (ti + tj) % 2 == 0 else color.rgb(185, 180, 170)
                Entity(
                    model='cube',
                    scale=(1.0, 0.06, 1.0),
                    position=(px + ti * 1.0, 0.06, pz + tj * 1.0 - 1),
                    color=tc
                )

        # Couch
        Entity(model='cube', scale=(3.5, 0.5, 1.0), position=(px, 0.25, pz + D / 2 - 2), color=color.rgb(100, 80, 60))
        Entity(model='cube', scale=(3.5, 0.7, 0.25), position=(px, 0.6, pz + D / 2 - 2.55), color=color.rgb(100, 80, 60))

        # Coffee table
        Entity(model='cube', scale=(1.5, 0.08, 0.8), position=(px, 0.4, pz + D / 2 - 3.2), color=FURNITURE_COLOR)
        for tx, tz in [(-0.5, -0.2), (0.5, -0.2), (-0.5, 0.2), (0.5, 0.2)]:
            Entity(model='cube', scale=(0.07, 0.38, 0.07), position=(px + tx, 0.2, pz + D / 2 - 3.2 + tz), color=color.rgb(120, 90, 55))

        # TV
        Entity(model='cube', scale=(2.2, 1.3, 0.1), position=(px, 1.5, pz - 0.35), color=color.rgb(20, 20, 20))
        Entity(model='cube', scale=(2.0, 1.1, 0.05), position=(px, 1.5, pz - 0.3), color=color.rgb(10, 30, 60))

        # Bookshelf
        Entity(model='cube', scale=(1.5, 2.0, 0.35), position=(px - W / 2 + 0.9, 1.0, pz + D / 2 - 1.5), color=FURNITURE_COLOR)

        # Floor lamp
        Entity(model='cylinder', scale=(0.05, 1.2, 0.05), position=(px - W / 2 + 1.5, 0.6, pz + D / 2 - 0.8), color=color.rgb(180, 150, 100))
        Entity(model='sphere', scale=(0.3, 0.4, 0.3), position=(px - W / 2 + 1.5, 1.3, pz + D / 2 - 0.8), color=color.rgb(250, 240, 200))

        # Workbench in grow room
        Entity(model='cube', scale=(3.0, 0.1, 0.8), position=(px, 0.85, pz - D / 4 - 1), color=color.rgb(140, 100, 60))
        for lx2 in [-1.3, 1.3]:
            Entity(model='cube', scale=(0.08, 0.85, 0.08), position=(px + lx2, 0.42, pz - D / 4 - 1), color=color.rgb(120, 85, 50))

        # Exterior steps
        for step_i in range(3):
            Entity(
                model='cube',
                scale=(2.4, 0.18, 0.4),
                position=(px, 0.09 + step_i * 0.18, pz + D / 2 + 0.2 + step_i * 0.4),
                color=color.rgb(160, 150, 140),
                collider='box'
            )

        print("[SAFEHOUSE] Built.")
