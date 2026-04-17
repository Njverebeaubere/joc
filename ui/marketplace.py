# marketplace.py
import requests
import os
from ursina import *

class AutoAssetBrowser(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui, enabled=False)
        self.projects_url = "https://raw.githubusercontent.com/ToxSam/open-source-3d-assets/main/data/projects.json"
        self.current_assets = []
        self.buttons = []
        self.bg = Panel(parent=self, scale=(0.4, 0.9), color=color.black66)
        self.title = Text(parent=self, text="MARKETPLACE (HDRI ASSETS)", origin=(0,0), y=0.45)
        
    def toggle(self):
        self.enabled = not self.enabled
        mouse.visible = self.enabled
        if self.enabled:
            # La pornire, incarcam colectiile
            cols = self.fetch_collections()
            if cols:
                # Incarcam prima colectie automat pentru demo
                self.fetch_assets_from_collection(cols[0]['id'])

    def fetch_collections(self):
        try:
            response = requests.get(self.projects_url)
            collections = response.json()
            return collections
        except Exception as e:
            print(f"[!] Eroare marketplace: {e}")
            return []
            
    def fetch_assets_from_collection(self, collection_id):
        asset_url = f"https://raw.githubusercontent.com/ToxSam/open-source-3d-assets/main/data/assets/{collection_id}.json"
        try:
            response = requests.get(asset_url)
            assets = response.json()
            self.current_assets = assets
            self._display_buttons()
        except Exception as e:
            print(f"[!] Nu s-a putut accesa colectia: {e}")
            
    def _display_buttons(self):
        for btn in self.buttons:
            destroy(btn)
        self.buttons.clear()
        
        y = 0.35
        for asset in self.current_assets[:10]:
            btn = Button(
                parent=self,
                text=asset.get('name', 'Unnamed')[:25],
                position=(0, y),
                scale=(0.3, 0.05),
                on_click=Func(self.download_and_spawn, asset)
            )
            self.buttons.append(btn)
            y -= 0.06
            
    def download_and_spawn(self, asset):
        model_url = asset.get('model_file_url')
        if not model_url: return
            
        print(f"[↓] Descarcare model: {asset.get('name')}...")
        
        # Folder local
        folder = os.path.join(os.path.dirname(__file__), '..', 'assets', 'downloaded')
        os.makedirs(folder, exist_ok=True)
        model_name = f"{asset.get('id', 'temp')}.glb"
        model_path = os.path.join(folder, model_name)
        
        try:
            response = requests.get(model_url)
            with open(model_path, 'wb') as f:
                f.write(response.content)
            
            # Spawn in scena
            new_obj = Entity(
                model=f"../assets/downloaded/{model_name}",
                position=camera.world_position + camera.forward * 10,
                collider='box',
                scale=1.0,
                editable=True # Sa poata fi mutat cu editorul admin
            )
            new_obj.custom_model_path = f"../assets/downloaded/{model_name}"
            new_obj.custom_texture_path = "none"
            print(f"[+] Succes! Modelul a fost plasat in scena.")
            self.toggle() # Inchidem meniul dupa spawn
        except Exception as e:
            print(f"[!] Eroare download: {e}")
