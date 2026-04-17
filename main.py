import sys
import subprocess
import random
import math

try:
    from ursina import *
    from ursina.prefabs.first_person_controller import FirstPersonController
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ursina"])
    from ursina import *
    from ursina.prefabs.first_person_controller import FirstPersonController

try:
    import simplepbr
    _has_pbr = True
except ImportError:
    _has_pbr = False

from config import keybinds
from plant import PlantActor
from police import PoliceManager
from customer import CustomerManager
from ui.pause import PauseMenu
from ui.hud import HUDManager
from ui.inventory import Inventory
from ui.phone import PhoneUI
from world.city import CityBuilder
from world.safehouse import Safehouse
from world.day_night import DayNightCycle

SAFEHOUSE_POS = (0, 0, 0)

app = Ursina(development_mode=False)
window.title = 'DRUG SIM'
window.exit_button.visible = False
window.fps_counter.enabled = True

# Lighting
sun = DirectionalLight(y=30, rotation=(45, 45, 0), shadows=True)
sun.color = color.rgb(255, 245, 230)
ambient = AmbientLight(color=color.hsv(0, 0, 0.55))
sky = Sky()
sky.color = color.rgb(120, 170, 230)

if _has_pbr:
    try:
        simplepbr.init(max_lights=8, use_normal_maps=False, enable_shadows=True)
    except Exception as e:
        print(f"[PBR] Could not init: {e}")

# Day/night
day_night = DayNightCycle(sun, ambient, sky)

# World
city = CityBuilder()
city.build()
safehouse = Safehouse(position=SAFEHOUSE_POS)

# Ground
Entity(
    model='plane',
    scale=(400, 1, 400),
    position=(0, -0.02, 0),
    color=color.rgb(55, 85, 45),
    collider='box'
)

# Plant inside grow room
plant_pos = Vec3(SAFEHOUSE_POS[0], 0.9, SAFEHOUSE_POS[2] - 4)
plant = PlantActor(position=plant_pos)

# Player spawns outside safehouse
player = FirstPersonController(
    position=(SAFEHOUSE_POS[0], 2.0, SAFEHOUSE_POS[2] + 12)
)
player.speed = 10
player.jump_height = 2.5
player.is_crouching = False
player.camera_pivot.y = 2.0

# Gun viewmodel
gun_root = Entity(parent=camera, position=(0.38, -0.38, 0.7), rotation=(0, 0, 3))
gun_body = Entity(parent=gun_root, model='cube', scale=(0.07, 0.1, 0.5), color=color.rgb(30, 30, 30))
gun_slide = Entity(parent=gun_root, model='cube', scale=(0.063, 0.06, 0.45), position=(0, 0.038, 0), color=color.rgb(45, 45, 45))
gun_barrel = Entity(parent=gun_root, model='cylinder', scale=(0.022, 0.12, 0.022), position=(0, -0.04, 0.3), rotation=(90, 0, 0), color=color.rgb(20, 20, 20))
gun_grip = Entity(parent=gun_root, model='cube', scale=(0.055, 0.12, 0.04), position=(0, -0.11, 0.1), rotation=(15, 0, 0), color=color.rgb(55, 40, 30))

# Managers
police_mgr = PoliceManager()
customer_mgr = CustomerManager(SAFEHOUSE_POS)
hud_mgr = HUDManager()
pause_menu = PauseMenu()
inventory = Inventory()
phone_ui = PhoneUI()

# State
held_pot = None
_harvest_ready_notified = False
_gun_recoil = 0.0
_phone_msg_timer = random.uniform(60, 120)
_news_timer = random.uniform(90, 180)


def _do_crouch():
    if held_keys['control']:
        if not player.is_crouching:
            player.camera_pivot.y = 1.0
            player.speed = 5
            player.is_crouching = True
    else:
        if player.is_crouching:
            player.camera_pivot.y = 2.0
            player.speed = 10
            player.is_crouching = False


def _handle_heat():
    max_smell = 12.0
    heat_pct = min(1.0, plant.smell_radius / max_smell)
    hud_mgr.update_heat(heat_pct)
    if plant.smell_radius > 5.0 and len(police_mgr.officers) == 0:
        if random.random() < 0.0008:
            police_mgr.spawn_raid()
            hud_mgr.show_alert("!! POLICE RAID !!", 4.0)


def _check_interact_prompts():
    nearby = customer_mgr.get_nearby_customer(player.position, 4.0)
    if nearby:
        hud_mgr.set_interact_prompt(
            f"[E] Deal with {nearby.name}  ({nearby.demand} @ ${nearby.pay_per_unit:.0f}/unit)"
        )
        return

    hit = raycast(camera.world_position, camera.forward, distance=4)
    if hit.hit and (hit.entity == plant or (hit.entity and hit.entity.parent == plant)):
        if plant.is_harvestable:
            hud_mgr.set_interact_prompt("[H] Harvest plant")
            return
        elif held_pot is None:
            hud_mgr.set_interact_prompt("[F] Pick up pot")
            return

    if held_pot is not None:
        hud_mgr.set_interact_prompt("[F] Drop pot")
        return

    hud_mgr.set_interact_prompt('')


def update():
    global _phone_msg_timer, _news_timer, _harvest_ready_notified, _gun_recoil

    _block = pause_menu.menu_bg.visible or phone_ui.enabled
    if _block:
        return

    _do_crouch()
    plant.custom_update()
    _handle_heat()

    # Plant repulsion
    if held_pot is None:
        dv = Vec3(player.x - plant.x, 0, player.z - plant.z)
        dist = dv.length()
        if dist < 0.7:
            direction = dv.normalized() if dist > 0.05 else Vec3(1, 0, 0)
            player.position += direction * (0.7 - dist) * 14.0 * time.dt

    customer_mgr.update(player)
    police_mgr.update(player)

    day_night.update()
    hud_mgr.update_time_display(day_night.day, day_night.hour, day_night.minute)
    phone_ui.update_time(day_night.hour, day_night.minute)

    # Gun recoil recovery
    if _gun_recoil > 0:
        _gun_recoil = max(0.0, _gun_recoil - time.dt * 9.0)
        gun_root.rotation_x = _gun_recoil * -18

    hit_info = raycast(camera.world_position, camera.forward, distance=12)
    hud_mgr.update_hud(hit_info, plant)
    _check_interact_prompts()

    # Harvest notification
    if plant.is_harvestable and not _harvest_ready_notified:
        _harvest_ready_notified = True
        hud_mgr.show_alert("PLANT READY TO HARVEST!", 5.0)
        phone_ui.add_message("Tony", "Heard youre holding. Come through.")

    # Phone messages
    _phone_msg_timer -= time.dt
    if _phone_msg_timer <= 0:
        _phone_msg_timer = random.uniform(80, 160)
        name, msg = random.choice([
            ("Mike", "Still waiting bro"),
            ("Carl", "You got anything?"),
            ("Ray", "Need product ASAP"),
            ("Dave", "Hit me when ready"),
            ("Sam", "Got cash, need supply"),
        ])
        phone_ui.add_message(name, msg)

    _news_timer -= time.dt
    if _news_timer <= 0:
        _news_timer = random.uniform(120, 240)
        phone_ui.add_news()


def input(key):
    global held_pot, _gun_recoil, _harvest_ready_notified

    if pause_menu.current_bind_action is not None:
        pause_menu.handle_bind(key)
        return

    if key == 'escape':
        if phone_ui.enabled:
            phone_ui.toggle()
        else:
            pause_menu.toggle()
        return

    if pause_menu.menu_bg.visible:
        return

    # Phone
    if key == 'm':
        phone_ui.toggle()
        return

    if phone_ui.enabled:
        return

    # Inventory scroll
    if key == 'scroll up':
        inventory.select_prev()
    elif key == 'scroll down':
        inventory.select_next()

    # Deal with customer
    if key == 'e':
        earnings = customer_mgr.try_deal(player, inventory)
        if earnings > 0:
            inventory.add_money(earnings)
            hud_mgr.show_alert(f"+${earnings:.0f}", 2.5)

    # Harvest
    if key == 'h':
        if plant.is_harvestable:
            units = max(1, int(plant.growth * 5))
            inventory.add_item('product', units)
            plant.growth = 0.0
            plant.health = 100.0
            plant.water_level = 50.0
            plant.smell_radius = 0.0
            _harvest_ready_notified = False
            hud_mgr.show_alert(f"Harvested {units} units!", 3.0)

    # Pick up / Drop pot
    if key == 'f':
        if held_pot is None:
            hit = raycast(camera.world_position, camera.forward, distance=4)
            if hit.hit and (hit.entity == plant or (hit.entity and hit.entity.parent == plant)):
                held_pot = plant
                held_pot.parent = camera
                held_pot.position = (0.5, -0.5, 1.2)
                held_pot.rotation = (0, 0, 0)
                held_pot.collider = None
        else:
            drop_pos = player.position + player.forward * 2.5
            drop_pos.y = 0.9
            held_pot.parent = scene
            held_pot.position = drop_pos
            held_pot.rotation = (0, 0, 0)
            held_pot.collider = 'box'
            held_pot = None

    # Plant controls
    hit = raycast(camera.world_position, camera.forward, distance=5)
    looking = hit.hit and (hit.entity == plant or (hit.entity and hit.entity.parent == plant))

    if looking:
        if key == keybinds['ph_up']:
            plant.ph_level = min(14.0, plant.ph_level + 0.5)
        elif key == keybinds['ph_down']:
            plant.ph_level = max(0.0, plant.ph_level - 0.5)
        elif key == keybinds['lumina']:
            plant.light_cycle_on = not plant.light_cycle_on
        elif key == keybinds['apa']:
            plant.water_level = min(100.0, plant.water_level + 25.0)

    # Shoot
    if key == 'left mouse down':
        _gun_recoil = 1.0
        mf = Entity(
            model='sphere',
            scale=0.15,
            position=camera.world_position + camera.forward * 0.9 + camera.right * 0.14 + camera.down * 0.1,
            color=color.rgb(255, 230, 80)
        )
        destroy(mf, delay=0.06)
        police_mgr.shoot_enemies(camera)


if __name__ == "__main__":
    print("=== DRUG SIM ===")
    print("WASD - Move | CTRL - Crouch | Space - Jump")
    print("F - Pick up/drop pot | H - Harvest plant")
    print("E - Deal with customer | M - Phone")
    print("LMB - Shoot | Scroll - Select item | ESC - Pause")
    app.run()
