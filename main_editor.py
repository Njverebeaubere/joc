import sys 
import subprocess 
import os 
import random 

try: 
    from ursina import * 
    import simplepbr 
    import requests 
except ImportError: 
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ursina", "requests", "simplepbr"]) 
    from ursina import * 
    import simplepbr 
    import requests 

# Import custom modules 
from world.map_manager import MapManager 
from world.editor import AdminEditor 
from ui.marketplace import AutoAssetBrowser 
from asset_downloader import AssetBrowser 

from ursina.prefabs.first_person_controller import FirstPersonController

# Initializare Aplicatie Editor 
app = Ursina(development_mode=True) 
window.title = 'DRUG SIM - LEVEL EDITOR' 
window.exit_button.visible = True  # Schimbat în True pentru debug 

# Setup Scene 
map_mgr = MapManager() 
map_mgr.load_map() 

# PBR & Environment 
simplepbr.init(max_lights=8, use_normal_maps=True, enable_shadows=True) 
sun = DirectionalLight(y=20, rotation=(45, 45, 45), shadows=True) 
sun.color = color.white 
AmbientLight(color=color.hsv(0, 0, 0.6)) 
Sky() 

# Ground - VERSIUNE FĂRĂ PBRMaterialLoader 
ground = Entity(model='plane', collider='box', scale=100, color=color.green) 
grass_path = '../texture/grass/Grass_albedo.jpg'
if os.path.exists(os.path.join(os.path.dirname(__file__), grass_path)):
    try: 
        ground.texture = load_texture(grass_path) 
        ground.texture_scale = (50, 50) 
    except: 
        print("Textură grass negăsită, se folosește culoarea verde") 
else:
    print(f"Fișierul texturii {grass_path} nu există la calea specificată.")

# Editor Elements 
player = FirstPersonController(position=(0, 2, 0), enabled=False) 
admin_editor = AdminEditor(map_mgr, player) 
admin_editor.toggle() 
marketplace = AutoAssetBrowser() 
asset_browser = AssetBrowser(admin_editor)

def update():
    # Necesar pentru Ursina (pentru held_keys și animații)
    if admin_editor.enabled:
        admin_editor.update()
    
    if hasattr(asset_browser, 'placer'):
        asset_browser.placer.update()

def input(key): 
    if key == 'tab': # Toggle Editor Mode
        admin_editor.toggle()

    if admin_editor.enabled: 
        admin_editor.handle_input(key) 
    
    if key == 'n': 
        asset_browser.toggle() 
        
    if key == 'k': # Mutam vechiul marketplace pe K
        marketplace.toggle()
        
    if key == 's' and held_keys['control']: 
        save_current_map()

def save_current_map():
    editable_entities = [e for e in scene.entities if hasattr(e, 'editable') and e.editable] 
    if editable_entities: 
        map_mgr.save_map(editable_entities) 
        print(f"Salvate {len(editable_entities)} entități") 
    else: 
        print("Nicio entitate editabilă de salvat") 

application.on_quit = save_current_map

if __name__ == "__main__": 
    print("--- [MOD EDITOR] ---") 
    print("TAB - Toggle Editor | M - Spawn | C - Clone | G - Grid Snap") 
    print("N - Asset Browser | K - Marketplace | CTRL+S - Salvare") 
    app.run()
