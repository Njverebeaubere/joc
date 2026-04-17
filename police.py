from ursina import *
import random

class PoliceManager:
    def __init__(self):
        self.enemies = []
        
    def spawn_raid(self):
        for _ in range(3):
            e = Entity(model='cube', collider='box', texture='white_cube', scale=(1, 2, 1), position=(random.randint(-20, 20), 1, random.randint(-20, 20)), color=color.azure)
            e.hp = 100
            self.enemies.append(e)

    def update(self, player):
        for e in list(self.enemies):
            vec = player.position - e.position
            vec.y = 0
            if vec.length() > 0: e.look_at(e.position + vec)
            if distance(e.position, player.position) > 3.0:
                e.position += e.forward * time.dt * 4.0

    def shoot_enemies(self, camera):
        hit_info = raycast(camera.world_position, camera.forward, distance=100)
        if hit_info.hit and hit_info.entity in self.enemies:
            e = hit_info.entity
            e.color = color.red
            invoke(setattr, e, 'color', color.azure, delay=0.1)
            e.hp -= 40
            if e.hp <= 0:
                self.enemies.remove(e)
                destroy(e)
