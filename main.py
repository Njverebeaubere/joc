import sys
import subprocess
import random
import os

try:
    from ursina import *
    from ursina.prefabs.first_person_controller import FirstPersonController
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ursina", "requests"])
    from ursina import *
    from ursina.prefabs.first_person_controller import FirstPersonController
    import requests

# Import modules
from config import keybinds
from plant import PlantActor
from police import PoliceManager
from ui.pause import PauseMenu
from ui.hud import HUDManager
from ui.marketplace import AutoAssetBrowser
from world.map_manager import MapManager
from ui.inventory import Inventory

# Initializari Ursina
app = Ursina(development_mode=False)
window.title = 'DRUG SIM - REALISM'
window.exit_button.visible = False

# Map Setup
map_mgr = MapManager()
map_mgr.load_map()

# GFX & Environment
import simplepbr
simplepbr.init(max_lights=8, use_normal_maps=True, enable_shadows=True)
sun = DirectionalLight(y=20, rotation=(45, 45, 45), shadows=True)
sun.color = color.white 
AmbientLight(color=color.hsv(0, 0, 0.6))
Sky() # Cer albastru simplu

# Ground PBR
ground = Entity(model='plane', collider='box', scale=100, color=color.green)
from pbr_material import PBRMaterialLoader
pbr_grass = PBRMaterialLoader('../texture/grass/Grass', ground)
pbr_grass.load_and_apply()
for stage in ground.findAllTextureStages():
    ground.setTexScale(stage, 50, 50)

# Player & Tools
player = FirstPersonController(y=2)
player.speed = 12 # Redusa pentru realism
player.jump_height = 2
player.original_y = player.y
player.is_crouching = False

# Adaugam crouch in update-ul playerului (modificam clasa sau adaugam in main update)
def player_crouch_logic():
    if held_keys['control']:
        if not player.is_crouching:
            player.camera_pivot.y = 1.0 # Coboram camera
            player.speed = 6
            player.is_crouching = True
    else:
        if player.is_crouching:
            player.camera_pivot.y = 2.0 # Revenim la inaltimea normala
            player.speed = 12
            player.is_crouching = False

gun = Entity(parent=camera, model='cube', scale=(0.1, 0.1, 0.6), position=(0.4, -0.4, 0.8), color=color.dark_gray)
crosshair = Entity(parent=camera.ui, model='circle', scale=0.01, color=color.green)

# Gameplay Managers
plant = PlantActor(position=(0, 0, 5))
police_mgr = PoliceManager()
hud_mgr = HUDManager()
pause_menu = PauseMenu()
marketplace = AutoAssetBrowser()
inventory = Inventory()

# Picking up pot logic
held_pot = None

def update():
    if pause_menu.menu_bg.visible or marketplace.enabled: return
    
    player_crouch_logic()
    plant.custom_update() 
    
    # Repulsion logic: impinge jucatorul in spate daca e prea aproape de planta
    if held_pot is None:
        # Distanta pe plan orizontal (X, Z)
        dist_vec = Vec3(player.x - plant.x, 0, player.z - plant.z)
        dist = dist_vec.length()
        
        # Threshold-ul de respingere este acum fix si mic (0.6)
        # Nu mai creste odata cu planta pentru a te lasa sa te apropii de frunze
        repulsion_dist = 0.6 
        
        if dist < repulsion_dist:
            # Daca suntem fix peste ea, impingem intr-o directie
            if dist < 0.1:
                direction = Vec3(1, 0, 0)
            else:
                direction = dist_vec.normalized()
                
            # Impingem jucatorul cu o forta proportionala cu cat de aproape este
            push_force = (repulsion_dist - dist) * 15.0
            player.position += direction * push_force * time.dt

    # Spawn police if heat is high and no enemies exist
    if plant.smell_radius > 5.0 and len(police_mgr.enemies) == 0:
        if random.random() < 0.001:  # Chance to spawn raid per frame
            police_mgr.spawn_raid()
            hud_mgr.ui_info.text += "\n[!] POLICE RAID INCOMING!"
    
    hit_info_input = raycast(camera.world_position, camera.forward, distance=15)
    hud_mgr.update_hud(hit_info_input, plant)
    police_mgr.update(player)

def input(key):
    global held_pot
    # Marketplace Toggle
    if key == 'n':
        marketplace.toggle()
        return

    if marketplace.enabled: return

    # Key Bindings
    if pause_menu.current_bind_action is not None:
        pause_menu.handle_bind(key)
        return

    if key == 'escape':
        pause_menu.toggle()
        return

    if pause_menu.menu_bg.visible: return

    # Interaction
    hit_info_input = raycast(camera.world_position, camera.forward, distance=5, ignore=(held_pot,) if held_pot else ())
    
    # Pick up / Drop Pot (Tasta F)
    if key == 'f':
        if not held_pot:
            if hit_info_input.hit and hit_info_input.entity == plant:
                held_pot = plant
                held_pot.parent = camera
                held_pot.position = (0.5, -0.5, 1.2) 
                held_pot.rotation = (0, 0, 0)
                held_pot.collider = None
                held_pot.ignore = True 
                print("[+] Ghiveci ridicat!")
        else:
            # Drop - il punem un pic mai departe (3 unitati) ca sa nu ne blocam in el
            # Ne asiguram ca il punem in fata jucatorului
            drop_pos = player.position + player.forward * 3
            drop_pos.y = 0 # Fortam pe sol
            
            held_pot.parent = scene
            held_pot.position = drop_pos
            held_pot.rotation = (0, 0, 0)
            held_pot.collider = 'box'
            held_pot.ignore = False
            held_pot = None
            print("[-] Ghiveci lasat jos la distanta.")

    if hit_info_input.hit and hit_info_input.entity == plant:
        if key == keybinds['ph_up']: plant.ph_level = min(14.0, plant.ph_level + 0.5)
        elif key == keybinds['ph_down']: plant.ph_level = max(0.0, plant.ph_level - 0.5)
        elif key == keybinds['lumina']: plant.light_cycle_on = not plant.light_cycle_on
        elif key == keybinds['apa']: plant.water_level = min(100.0, plant.water_level + 20.0)

    if key == 'left mouse down':
        gun.z = 0.5
        invoke(setattr, gun, 'z', 0.8, delay=0.1)
        police_mgr.shoot_enemies(camera)

if __name__ == "__main__":
    app.run()
