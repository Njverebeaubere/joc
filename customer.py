import random
import math
from ursina import *


CUSTOMER_COLORS = [
    color.rgb(220, 180, 140),
    color.rgb(180, 130, 90),
    color.rgb(240, 200, 160),
    color.rgb(160, 110, 70),
]

SHIRT_COLORS = [
    color.rgb(180, 60, 60),
    color.rgb(60, 80, 160),
    color.rgb(50, 120, 50),
    color.rgb(120, 100, 60),
    color.rgb(60, 60, 60),
    color.rgb(160, 140, 100),
]

CUSTOMER_NAMES = [
    "Mike", "Tony", "Dave", "Carl", "Ray", "Sam",
    "Lou", "Pete", "Jake", "Bo", "Rex", "Al"
]


def _build_customer_model(skin, shirt):
    root = Entity(
        model='cube',
        scale=(0.001, 0.001, 0.001),
        color=color.clear
    )
    root.setScale(1, 1, 1)

    Entity(parent=root, model='cube', scale=(0.5, 0.6, 0.3), position=(0, 1.15, 0), color=shirt)
    Entity(parent=root, model='cube', scale=(0.38, 0.36, 0.33), position=(0, 1.65, 0), color=skin)

    for sx in [-0.32, 0.32]:
        Entity(parent=root, model='cube', scale=(0.17, 0.5, 0.17), position=(sx, 1.1, 0), color=shirt)
    for lx in [-0.15, 0.15]:
        Entity(parent=root, model='cube', scale=(0.2, 0.6, 0.2), position=(lx, 0.35, 0), color=color.rgb(50, 50, 80))
        Entity(parent=root, model='cube', scale=(0.22, 0.1, 0.28), position=(lx, 0.06, 0.04), color=color.rgb(30, 25, 20))

    return root


class Customer:
    def __init__(self, position, safehouse_pos):
        self.name = random.choice(CUSTOMER_NAMES)
        self.demand = random.randint(1, 4)
        self.patience = random.uniform(30, 90)
        self.pay_per_unit = random.uniform(80, 160)
        self.state = 'walking'
        self._timer = 0.0
        self._wait_timer = 0.0
        self.safehouse_pos = Vec3(*safehouse_pos)
        self.active = True

        skin = random.choice(CUSTOMER_COLORS)
        shirt = random.choice(SHIRT_COLORS)
        self.entity = _build_customer_model(skin, shirt)
        self.entity.position = Vec3(*position)
        self.entity.collider = BoxCollider(self.entity, center=(0, 1.0, 0), size=(0.5, 2.0, 0.3))

        self.label = Text(
            text=self.name,
            parent=self.entity,
            scale=6,
            position=(0, 2.3, 0),
            origin=(0, 0),
            color=color.rgb(255, 220, 80),
            billboard=True,
            visible=False
        )

    def update(self, dt, player_pos):
        if not self.active:
            return

        if self.state == 'walking':
            target = self.safehouse_pos
            vec = target - self.entity.position
            vec.y = 0
            dist = vec.length()

            if dist > 1.5:
                self.entity.position += vec.normalized() * dt * 2.8
                if dist > 0.5:
                    self.entity.look_at(self.entity.position + vec.normalized())
            else:
                self.state = 'waiting'
                self._wait_timer = self.patience
                self.label.visible = True

        elif self.state == 'waiting':
            self._wait_timer -= dt
            player_dist = (Vec3(*player_pos) - self.entity.position).length()
            if player_dist < 3.0:
                self.state = 'ready_to_deal'

            if self._wait_timer <= 0:
                self.state = 'leaving'
                self.label.visible = False
                self.label.text = self.name
                print(f"[CUSTOMER] {self.name} got tired and left.")

        elif self.state == 'leaving':
            target = self.entity.position + Vec3(random.uniform(-1, 1), 0, 1).normalized() * 30
            vec = target - self.entity.position
            vec.y = 0
            dist = vec.length()
            if dist > 1.0:
                self.entity.position += vec.normalized() * dt * 3.5
            else:
                self.active = False
                destroy(self.entity)

    def trigger_deal(self, inventory):
        if self.state != 'ready_to_deal':
            return 0
        available = inventory.count_product()
        units_sold = min(self.demand, available)
        if units_sold == 0:
            self.label.text = "Nothing?"
            return 0

        earnings = units_sold * self.pay_per_unit
        inventory.remove_product(units_sold)
        self.state = 'leaving'
        self.label.visible = False
        print(f"[DEAL] Sold {units_sold} to {self.name} for ${earnings:.0f}")
        return earnings


class CustomerManager:
    def __init__(self, safehouse_pos):
        self.safehouse_pos = safehouse_pos
        self.customers = []
        self._spawn_timer = 0.0
        self._spawn_interval = 45.0
        self.total_sales = 0.0

    def update(self, player):
        dt = time.dt
        self._spawn_timer -= dt
        if self._spawn_timer <= 0:
            self._spawn_timer = self._spawn_interval + random.uniform(-10, 10)
            self._try_spawn()

        for c in list(self.customers):
            if not c.active:
                self.customers.remove(c)
                continue
            c.update(dt, player.position)

    def _try_spawn(self):
        if len(self.customers) >= 3:
            return
        sx = self.safehouse_pos[0]
        sz = self.safehouse_pos[2]
        angle = random.uniform(0, 360)
        dist = random.uniform(35, 55)
        spawn_x = sx + math.cos(math.radians(angle)) * dist
        spawn_z = sz + math.sin(math.radians(angle)) * dist
        c = Customer((spawn_x, 0.05, spawn_z), self.safehouse_pos)
        self.customers.append(c)
        print(f"[CUSTOMER] {c.name} is heading over (wants {c.demand} units).")

    def try_deal(self, player, inventory):
        for c in self.customers:
            if c.state == 'ready_to_deal':
                dist = (Vec3(*player.position) - c.entity.position).length()
                if dist < 3.5:
                    earnings = c.trigger_deal(inventory)
                    self.total_sales += earnings
                    return earnings
        return 0

    def get_nearby_customer(self, player_pos, radius=3.5):
        for c in self.customers:
            if c.state == 'ready_to_deal':
                dist = (Vec3(*player_pos) - c.entity.position).length()
                if dist < radius:
                    return c
        return None
