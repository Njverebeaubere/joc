import random
import math
from ursina import *


POLICE_BODY_COLOR = color.rgb(20, 40, 100)
POLICE_BADGE_COLOR = color.rgb(220, 200, 50)
POLICE_SKIN_COLOR = color.rgb(220, 180, 140)
POLICE_BELT_COLOR = color.rgb(30, 25, 20)


def _build_officer(position):
    root = Entity(
        model='cube',
        scale=(0.001, 0.001, 0.001),
        position=position,
        color=color.clear,
        collider='box'
    )
    root.setScale(1, 1, 1)

    # Torso
    torso = Entity(
        parent=root,
        model='cube',
        scale=(0.55, 0.65, 0.32),
        position=(0, 1.2, 0),
        color=POLICE_BODY_COLOR
    )

    # Badge
    Entity(
        parent=root,
        model='cube',
        scale=(0.12, 0.1, 0.05),
        position=(0.15, 1.38, 0.18),
        color=POLICE_BADGE_COLOR
    )

    # Belt
    Entity(
        parent=root,
        model='cube',
        scale=(0.57, 0.1, 0.34),
        position=(0, 0.88, 0),
        color=POLICE_BELT_COLOR
    )

    # Head
    Entity(
        parent=root,
        model='cube',
        scale=(0.38, 0.38, 0.35),
        position=(0, 1.72, 0),
        color=POLICE_SKIN_COLOR
    )

    # Cap
    Entity(
        parent=root,
        model='cube',
        scale=(0.44, 0.12, 0.42),
        position=(0, 1.93, 0),
        color=POLICE_BODY_COLOR
    )
    # Cap brim
    Entity(
        parent=root,
        model='cube',
        scale=(0.5, 0.04, 0.2),
        position=(0, 1.86, 0.22),
        color=POLICE_BODY_COLOR
    )

    # Left arm
    Entity(
        parent=root,
        model='cube',
        scale=(0.18, 0.55, 0.18),
        position=(-0.37, 1.15, 0),
        rotation=(0, 0, 15),
        color=POLICE_BODY_COLOR
    )

    # Right arm (gun side - slightly forward)
    Entity(
        parent=root,
        model='cube',
        scale=(0.18, 0.55, 0.18),
        position=(0.37, 1.15, 0.1),
        rotation=(0, 0, -20),
        color=POLICE_BODY_COLOR
    )

    # Gun
    Entity(
        parent=root,
        model='cube',
        scale=(0.06, 0.18, 0.35),
        position=(0.55, 1.0, 0.15),
        rotation=(0, 0, -20),
        color=color.rgb(25, 25, 25)
    )

    # Left leg
    Entity(
        parent=root,
        model='cube',
        scale=(0.22, 0.65, 0.22),
        position=(-0.16, 0.38, 0),
        color=POLICE_BODY_COLOR
    )

    # Right leg
    Entity(
        parent=root,
        model='cube',
        scale=(0.22, 0.65, 0.22),
        position=(0.16, 0.38, 0),
        color=POLICE_BODY_COLOR
    )

    # Boots
    Entity(parent=root, model='cube', scale=(0.24, 0.12, 0.3), position=(-0.16, 0.06, 0.05), color=color.rgb(20, 15, 10))
    Entity(parent=root, model='cube', scale=(0.24, 0.12, 0.3), position=(0.16, 0.06, 0.05), color=color.rgb(20, 15, 10))

    return root


class PoliceOfficer:
    def __init__(self, position):
        self.entity = _build_officer(Vec3(*position))
        self.entity.hp = 100
        self.entity.collider = BoxCollider(self.entity, center=(0, 1.0, 0), size=(0.6, 2.0, 0.4))
        self._walk_anim = 0.0
        self._legs = [c for c in self.entity.children if hasattr(c, 'scale_y') and abs(c.y - 0.38) < 0.1]
        self.state = 'chase'
        self._shoot_timer = 0.0
        self._shoot_cooldown = 2.5

    def update(self, player, dt):
        vec = player.position - self.entity.position
        vec.y = 0
        dist = vec.length()

        if dist > 0.1:
            flat_target = self.entity.position + vec
            self.entity.look_at(flat_target)

        if self.state == 'chase':
            if dist > 4.0:
                self.entity.position += self.entity.forward * dt * 3.5
                self._walk_anim += dt * 8.0
                for i, leg in enumerate(self._legs):
                    leg.rotation_x = math.sin(self._walk_anim + i * math.pi) * 20
            else:
                self.state = 'shoot'

        elif self.state == 'shoot':
            if dist > 6.0:
                self.state = 'chase'
            self._shoot_timer -= dt
            if self._shoot_timer <= 0:
                self._shoot_timer = self._shoot_cooldown
                self._fire_at_player(player)

    def _fire_at_player(self, player):
        # Visual muzzle flash
        mf = Entity(
            model='sphere',
            scale=0.2,
            position=self.entity.position + Vec3(0, 1.1, 0) + self.entity.forward * 0.8,
            color=color.rgb(255, 220, 50)
        )
        destroy(mf, delay=0.08)


class PoliceManager:
    def __init__(self):
        self.officers = []
        self._wave = 0
        self._wanted_level = 0
        self._raid_cooldown = 0.0

    @property
    def enemies(self):
        return [o.entity for o in self.officers]

    def set_wanted(self, level):
        self._wanted_level = max(0, min(5, level))

    def spawn_raid(self):
        self._wave += 1
        count = 2 + self._wave
        count = min(count, 6)

        spawn_radius = 30 + self._wave * 5
        for _ in range(count):
            angle = random.uniform(0, 360)
            dist = random.uniform(spawn_radius * 0.6, spawn_radius)
            sx = math.cos(math.radians(angle)) * dist
            sz = math.sin(math.radians(angle)) * dist
            officer = PoliceOfficer((sx, 0.05, sz))
            self.officers.append(officer)

        print(f"[POLICE] RAID WAVE {self._wave} - {count} officers spawned.")

    def update(self, player):
        dt = time.dt
        for officer in list(self.officers):
            if officer.entity.hp <= 0:
                self._kill_officer(officer)
                continue
            officer.update(player, dt)

    def shoot_enemies(self, camera):
        hit_info = raycast(camera.world_position, camera.forward, distance=120)
        if hit_info.hit:
            for officer in list(self.officers):
                if hit_info.entity == officer.entity or hit_info.entity in officer.entity.children:
                    officer.entity.hp -= 35
                    self._flash_hit(officer.entity)
                    if officer.entity.hp <= 0:
                        self._kill_officer(officer)
                    return

    def _flash_hit(self, entity):
        orig_colors = {c: c.color for c in entity.children}
        for c in entity.children:
            c.color = color.rgb(255, 80, 80)
        def restore():
            for c2, col in orig_colors.items():
                if c2:
                    c2.color = col
        invoke(restore, delay=0.1)

    def _kill_officer(self, officer):
        if officer in self.officers:
            self.officers.remove(officer)
        destroy(officer.entity)
        print("[POLICE] Officer down.")

    def clear(self):
        for officer in list(self.officers):
            destroy(officer.entity)
        self.officers.clear()
        self._wave = 0
