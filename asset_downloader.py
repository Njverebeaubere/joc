import os 
import requests 
import zipfile 
import io 
import threading 
import json
from ursina import * 
from ursina import Vec3, Func, mouse 

class AssetDownloader: 
    def __init__(self): 
        # API Endpoints
        self.poly_haven_api = "https://api.polyhaven.com/assets?t=models"
        self.ambient_cg_api = "https://api.ambientcg.com/v2/list?type=Material&limit=50"
        
        # Cache & Storage
        self.save_dir = os.path.join(os.path.dirname(__file__), "assets")
        self.texture_dir = os.path.join(self.save_dir, "textures")
        self.model_dir = os.path.join(self.save_dir, "models")
        self.thumb_dir = os.path.join(self.save_dir, "thumbnails")
        
        for d in [self.texture_dir, self.model_dir, self.thumb_dir]:
            os.makedirs(d, exist_ok=True)
        
        # Date incarcate din API
        self.poly_haven_assets = {}
        self.ambient_cg_assets = {}
        
        # Modele procedurale locale (cele de baza)
        self.model_configs = { 
            "Copac": {"model": "cube", "color": color.brown, "parts": [("sphere", color.green, Vec3(0, 1.5, 0), Vec3(2, 2, 2))], "emoji": "🌳"}, 
            "Casa": {"model": "cube", "color": color.rgb(245, 245, 220), "parts": [("cone", color.red, Vec3(0, 1, 0), Vec3(1.5, 1, 1.5))], "emoji": "🏠"}, 
            "Strada": {"model": "plane", "color": color.rgb(50, 50, 50), "scale": Vec3(5, 0.1, 5), "emoji": "🛣️"}, 
            "Gard": {"model": "cube", "color": color.rgb(200, 150, 50), "scale": Vec3(0.1, 1, 2), "emoji": "🚧"}, 
            "Stalp": {"model": "cylinder", "color": color.rgb(100, 100, 100), "parts": [("sphere", color.yellow, Vec3(0, 2, 0), Vec3(0.5, 0.5, 0.5))], "emoji": "💡"}, 
            "Fantana": {"model": "cylinder", "color": color.rgb(100, 100, 255), "scale": Vec3(1.5, 0.5, 1.5), "emoji": "⛲"}, 
            "Banca": {"model": "cube", "color": color.rgb(139, 69, 19), "scale": Vec3(1.5, 0.5, 0.5), "emoji": "🪑"}, 
            "Cos Gunoi": {"model": "cylinder", "color": color.rgb(50, 50, 50), "scale": Vec3(0.5, 0.8, 0.5), "emoji": "🗑️"}, 
            "Flori": {"model": "sphere", "color": color.rgb(255, 0, 255), "scale": Vec3(0.3, 0.3, 0.3), "emoji": "🌸"}, 
            "Piatra": {"model": "sphere", "color": color.rgb(128, 128, 128), "scale": Vec3(1, 0.8, 1.2), "emoji": "🪨"}, 
            "Casa Mare": {"model": "cube", "color": color.white, "scale": Vec3(2, 4, 2), "parts": [("cone", color.rgb(60, 60, 60), Vec3(0, 2.5, 0), Vec3(3, 1.5, 3))], "emoji": "🏢"}, 
            "Magazin": {"model": "cube", "color": color.rgb(0, 128, 255), "scale": Vec3(3, 2, 2), "parts": [("cube", color.black, Vec3(0, 0, 1.05), Vec3(2, 1, 0.1))], "emoji": "🏪"}, 
            "Sera": {"model": "cube", "color": color.color(0, 0, 1, 0.4), "scale": Vec3(4, 2, 3), "emoji": "🌿"}, 
            "Atelier": {"model": "cube", "color": color.rgb(200, 200, 200), "scale": Vec3(5, 3, 4), "emoji": "🛠️"}, 
            "Turn Paza": {"model": "cylinder", "color": color.rgb(150, 150, 150), "scale": Vec3(1.5, 6, 1.5), "emoji": "🏰"}, 
            "Butoi": {"model": "cylinder", "color": color.rgb(139, 69, 19), "scale": Vec3(0.8, 1.2, 0.8), "emoji": "🛢️"}, 
            "Ladita": {"model": "cube", "color": color.rgb(139, 69, 19), "scale": Vec3(1, 1, 1), "emoji": "📦"}, 
            "Scari": {"model": "cube", "color": color.rgb(180, 180, 180), "scale": Vec3(2, 0.2, 0.5), "emoji": "🪜"}, 
            "Podet": {"model": "cube", "color": color.rgb(139, 69, 19), "scale": Vec3(2, 0.1, 5), "emoji": "🌉"}, 
            "Foisor": {"model": "cylinder", "color": color.rgb(139, 69, 19), "scale": Vec3(3, 0.1, 3), "parts": [("cone", color.red, Vec3(0, 2, 0), Vec3(3.5, 1, 3.5))], "emoji": "⛺"}
        }

    def fetch_api_lists(self, callback=None):
        def thread_func():
            try:
                # 1. Poly Haven
                poly_res = requests.get(self.poly_haven_api, timeout=5)
                if poly_res.status_code == 200:
                    self.poly_haven_assets = poly_res.json()
                
                # 2. AmbientCG
                ambient_res = requests.get(self.ambient_cg_api, timeout=5)
                if ambient_res.status_code == 200:
                    data = ambient_res.json()
                    self.ambient_cg_assets = {item['assetId']: item for item in data.get('foundAssets', [])}
                
                if callback: callback()
            except Exception as e:
                print(f"[!] Eroare API: {e}")
                if callback: callback()

        threading.Thread(target=thread_func, daemon=True).start()

    def get_model_list(self):
        return list(self.model_configs.keys())

    def get_thumbnail(self, asset_id, source, callback):
        """Descarca thumbnail si returneaza calea locala."""
        ext = "png" if source == "poly" else "jpg"
        target_path = os.path.join(self.thumb_dir, f"{asset_id}.{ext}")
        
        if os.path.exists(target_path):
            callback(target_path)
            return
            
        def download_thumb():
            url = ""
            if source == "poly":
                url = f"https://cdn.polyhaven.com/asset_img/primary/{asset_id}.png?height=128"
            else:
                url = f"https://ambientcg.com/api/v2/thumbnail?asset={asset_id}&size=128&type=jpg"
            
            try:
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    with open(target_path, "wb") as f:
                        f.write(res.content)
                    callback(target_path)
                else:
                    callback(None)
            except:
                callback(None)
                
        threading.Thread(target=download_thumb, daemon=True).start()

    def download_poly_model(self, asset_id, callback):
        """Poly Haven necesita 2 pasi: 1. get files list, 2. download GLTF."""
        target_path = os.path.join(self.model_dir, f"{asset_id}.gltf")
        if os.path.exists(target_path):
            callback(target_path)
            return

        def task():
            try:
                # Pas 1: Gaseste link GLTF
                res = requests.get(f"https://api.polyhaven.com/files/{asset_id}", timeout=5)
                if res.status_code == 200:
                    files = res.json()
                    # Cautam in 'gltf' -> '1k' (sau 'low')
                    gltf_url = files.get('gltf', {}).get('1k', {}).get('url')
                    if gltf_url:
                        # Pas 2: Download real
                        r = requests.get(gltf_url, timeout=15)
                        with open(target_path, "wb") as f:
                            f.write(r.content)
                        callback(target_path)
                        return
                callback(None)
            except:
                callback(None)

        threading.Thread(target=task, daemon=True).start()

    def get_model_list(self):
        return list(self.model_configs.keys())

    def descarca_textura(self, nume, callback=None):
        target_path = os.path.join(self.texture_dir, f"{nume}_Color.jpg")
        if os.path.exists(target_path):
            if callback: callback(target_path)
            return target_path
            
        def download_thread():
            url = f"https://ambientcg.com/get?file={nume}_1K-JPG.zip"
            try:
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                        color_file = next((f for f in z.namelist() if "Color.jpg" in f or "Albedo.jpg" in f), None)
                        if color_file:
                            with z.open(color_file) as source, open(target_path, "wb") as target:
                                target.write(source.read())
                            if callback: callback(target_path)
                            return
                if callback: callback(None)
            except:
                if callback: callback(None)

        threading.Thread(target=download_thread, daemon=True).start()
        return None

class AssetPlacer(Entity):
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
        self.preview_obj = None
        self.asset_name = None
        self.asset_type = None # 'model', 'texture', 'poly', 'ambient'
        self.enabled = False
        self.hint_text = Text(text="", position=(0, 0.4), origin=(0,0), color=color.yellow, visible=False)

    def set_asset(self, asset_name, asset_type):
        self.asset_name = asset_name
        self.asset_type = asset_type
        self.enabled = True
        self.hint_text.text = f"Plasare: {asset_name} (LMB: Pune | RMB: Anuleaza)"
        self.hint_text.visible = True
        
        if self.preview_obj:
            destroy(self.preview_obj)
            
        if asset_type == 'model':
            config = self.browser.downloader.model_configs[asset_name]
            self.preview_obj = Entity(
                model=config.get('model', 'cube'),
                color=config.get('color', color.white),
                scale=config.get('scale', Vec3(1,1,1)),
                alpha=0.5
            )
            if 'parts' in config:
                for p_model, p_color, p_pos, p_scale in config['parts']:
                    Entity(parent=self.preview_obj, model=p_model, color=p_color, position=p_pos, scale=p_scale, alpha=0.5)
        elif asset_type == 'poly':
            # Previzualizare sferica pana se descarca modelul real
            self.preview_obj = Entity(model='sphere', color=color.azure, scale=0.5, alpha=0.5)
        else:
            self.preview_obj = Entity(model='cube', color=color.white, alpha=0.5)

    def update(self):
        if not self.enabled or not self.preview_obj:
            return
            
        hit_info = raycast(camera.world_position, camera.forward, distance=100, ignore=(self.preview_obj,))
        if hit_info.hit:
            pos = hit_info.world_point
            if self.browser.editor.grid_snap:
                pos = Vec3(round(pos.x), round(pos.y), round(pos.z))
            self.preview_obj.position = pos
        else:
            self.preview_obj.position = camera.world_position + camera.forward * 10

    def input(self, key):
        if not self.enabled: return
        if key == 'left mouse down': self.place()
        elif key == 'right mouse down' or key == 'escape': self.cancel()

    def place(self):
        if not self.preview_obj: return
        pos = self.preview_obj.position
        
        if self.asset_type == 'model':
            config = self.browser.downloader.model_configs[self.asset_name]
            new_ent = Entity(model=config.get('model', 'cube'), color=config.get('color', color.white),
                             scale=config.get('scale', Vec3(1,1,1)), position=pos, collider='box', editable=True)
            new_ent.custom_model_path = config.get('model', 'cube')
            new_ent.custom_texture_path = 'none'
            if 'parts' in config:
                for p_model, p_color, p_pos, p_scale in config['parts']:
                    Entity(parent=new_ent, model=p_model, color=p_color, position=p_pos, scale=p_scale)
        
        elif self.asset_type == 'poly':
            def spawn_poly(path):
                if path:
                    e = Entity(model=path, position=pos, collider='box', editable=True)
                    e.custom_model_path = path
                    e.custom_texture_path = 'none'
            self.browser.downloader.download_poly_model(self.asset_name, spawn_poly)
            
        elif self.asset_type in ['texture', 'ambient']:
            hit_info = raycast(camera.world_position, camera.forward, distance=100, ignore=(self.preview_obj,))
            def apply_tex(path):
                if not path: return
                if hit_info.hit and getattr(hit_info.entity, 'editable', False):
                    hit_info.entity.texture = path
                    hit_info.entity.custom_texture_path = path
                else:
                    new_ent = Entity(model='cube', position=pos, collider='box', editable=True)
                    new_ent.custom_model_path = 'cube'
                    new_ent.texture = path
                    new_ent.custom_texture_path = path
            self.browser.downloader.descarca_textura(self.asset_name, callback=apply_tex)

    def cancel(self):
        self.enabled = False
        self.hint_text.visible = False
        if self.preview_obj: destroy(self.preview_obj)
        self.preview_obj = None

class AssetBrowser(Entity):
    def __init__(self, editor):
        super().__init__(parent=camera.ui)
        self.editor = editor
        self.downloader = AssetDownloader()
        self.placer = AssetPlacer(self)
        
        # UI Setup
        self.panel = Entity(parent=camera.ui, model='quad', scale=(0.4, 1), position=(-0.65, 0), color=color.black66, enabled=False, collider='box')
        self.title = Text("ADVANCED ASSET BROWSER", parent=self.panel, y=0.48, x=-0.45, scale=1.1, color=color.orange)
        self.button_container = Entity(parent=self.panel, y=0.4)
        self.scroll_max = 0
        
        # Initializam cu lista locala
        self.refresh_ui()
        
        # Incarcam din API asincron
        self.downloader.fetch_api_lists(callback=self.refresh_ui)

    def refresh_ui(self):
        # Stergem butoanele vechi
        for c in self.button_container.children:
            destroy(c)
            
        y_pos = 0
        
        # 1. MODELE LOCALE
        y_pos = self.add_header("--- MODELE LOCALE ---", y_pos)
        for mod in self.downloader.model_configs:
            emoji = self.downloader.model_configs[mod].get('emoji', '📦')
            btn = Button(parent=self.button_container, text=f"{emoji} {mod}", y=y_pos, scale=(0.9, 0.04), 
                         on_click=Func(self.select_asset, mod, 'model'))
            y_pos -= 0.045
            
        # 2. POLY HAVEN (MODELE 3D)
        if self.downloader.poly_haven_assets:
            y_pos = self.add_header("--- POLY HAVEN (3D) ---", y_pos)
            # Luam primele 20 pentru performanta UI
            ids = list(self.downloader.poly_haven_assets.keys())[:20]
            for aid in ids:
                btn = Button(parent=self.button_container, text=aid[:20], y=y_pos, scale=(0.9, 0.04),
                             on_click=Func(self.select_asset, aid, 'poly'))
                # Incarcam thumbnail asincron
                self.downloader.get_thumbnail(aid, 'poly', lambda path, b=btn: setattr(b, 'icon', path) if path else None)
                y_pos -= 0.045

        # 3. AMBIENT CG (TEXTURI)
        if self.downloader.ambient_cg_assets:
            y_pos = self.add_header("--- AMBIENT CG (TEXTURI) ---", y_pos)
            ids = list(self.downloader.ambient_cg_assets.keys())[:20]
            for aid in ids:
                btn = Button(parent=self.button_container, text=aid[:20], y=y_pos, scale=(0.9, 0.04),
                             on_click=Func(self.select_asset, aid, 'ambient'))
                self.downloader.get_thumbnail(aid, 'ambient', lambda path, b=btn: setattr(b, 'icon', path) if path else None)
                y_pos -= 0.045
                
        self.scroll_max = abs(y_pos) - 0.8

    def add_header(self, text, y):
        Text(text, parent=self.button_container, y=y, x=-0.45, scale=0.8, color=color.yellow)
        return y - 0.04

    def input(self, key):
        if not self.panel.enabled: return
        if key == 'scroll up': self.button_container.y += 0.1
        if key == 'scroll down': self.button_container.y -= 0.1
        self.button_container.y = clamp(self.button_container.y, 0.4, 0.4 + self.scroll_max)

    def select_asset(self, name, asset_type):
        self.placer.set_asset(name, asset_type)
        self.toggle()

    def toggle(self):
        self.panel.enabled = not self.panel.enabled
        mouse.visible = self.panel.enabled
        self.editor.block_input = self.panel.enabled
