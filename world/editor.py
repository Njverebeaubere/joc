from ursina import *
from ursina.prefabs.editor_camera import EditorCamera

class AdminEditor:
    def __init__(self, map_manager, game_player):
        self.map_manager = map_manager
        self.game_player = game_player
        self.enabled = False
        self.editor_camera = None
        self.selected_entity = None
        self.block_input = False # Flag pentru a bloca input-ul cand UI-ul e deschis
        
        # Indicator vizual
        self.ui_text = Text(
            text="[ MOD EDITOR ACTIV ]\nWASD+QE - Fly Cam | TAB - Iesire | N - Asset Browser | C - Clone\nG - Grid Snap | B - Model | V - Textura | Delete - Sterge\nSageti - Muta | CTRL+Sageti - Scala | SHIFT+Sageti - Roteste", 
            position=(0, 0.45), 
            origin=(0,0), 
            scale=1, 
            color=color.yellow, 
            visible=False
        )
        
        # Modele disponibile pentru spawn rapid (M)
        self.available_models = ['cube', 'sphere', 'plane', 'quad', 'circle', '../texture/marijuana/pot/bush_obj.obj']
        # Texturi disponibile (V)
        self.available_textures = [
            'white_cube', 'brick', 'grass', 'grass_albedo', 'dirt', 'wood', 'stone', 
            '../texture/grass/Grass_albedo.jpg', '../texture/marijuana/pot/bush_albedo.jpg'
        ]
        
        self.grid_snap = True # Activam snapping-ul pentru aliniere perfecta

    def toggle(self):
        self.enabled = not self.enabled
        self.ui_text.visible = self.enabled
        
        if self.enabled:
            # Activăm Editor
            self.game_player.enabled = False
            self.editor_camera = EditorCamera()
            self.editor_camera.move_speed = 20 # Viteza de miscare WASD
            self.editor_camera.rotation_speed = 100 # Viteza de rotatie mouse
            mouse.visible = True
            mouse.locked = False
            # Facem si ground-ul selectabil daca nu e deja
            for e in scene.entities:
                if e.model and e.model.name == 'plane' and e.scale_x > 50:
                    e.editable = True
                    if not hasattr(e, 'custom_model_path'): e.custom_model_path = 'plane'
            print("[EDITOR] Admin Mode ACTIVAT.")
        else:
            # Revenim la Joc
            if self.editor_camera:
                destroy(self.editor_camera)
            self.game_player.enabled = True
            mouse.visible = False
            mouse.locked = True
            # Salvăm automat la ieșire
            editable_entities = [e for e in scene.entities if getattr(e, 'editable', False)]
            if editable_entities:
                self.map_manager.save_map(editable_entities)
                print("[EDITOR] Admin Mode DEZACTIVAT. Map saved.")
            else:
                print("[EDITOR] Admin Mode DEZACTIVAT. Nothing to save.")

    def update(self):
        if not self.enabled or not self.editor_camera:
            return

        # Mișcare Fly-Cam (WASD + QE pentru înălțime)
        # Ursina EditorCamera are mișcare de bază, dar o îmbunătățim
        dt = time.dt
        speed = self.editor_camera.move_speed
        
        if held_keys['w']: self.editor_camera.position += self.editor_camera.forward * speed * dt
        if held_keys['s']: self.editor_camera.position += self.editor_camera.back * speed * dt
        if held_keys['a']: self.editor_camera.position += self.editor_camera.left * speed * dt
        if held_keys['d']: self.editor_camera.position += self.editor_camera.right * speed * dt
        if held_keys['e']: self.editor_camera.position += self.editor_camera.up * speed * dt
        if held_keys['q']: self.editor_camera.position += self.editor_camera.down * speed * dt

    def spawn_object(self, model='cube', texture='white_cube', position=None):
        if position is None:
            position = self.editor_camera.world_position + self.editor_camera.forward * 5
            
        if self.grid_snap:
            position = Vec3(round(position.x), round(position.y), round(position.z))

        new_obj = Entity(
            model=model,
            texture=texture,
            position=position,
            collider='box',
            editable=True
        )
        new_obj.custom_model_path = model
        new_obj.custom_texture_path = texture
        self.selected_entity = new_obj
        print(f"[EDITOR] Obiect nou creat la {new_obj.position}")
        return new_obj

    def handle_input(self, key):
        if not self.enabled or self.block_input:
            return

        if key == 'm': # Meniu Modele (Spawn rapid)
            self.spawn_object()

        if key == 'c' and self.selected_entity: # CLONE / DUPLICATE
            e = self.selected_entity
            new_pos = e.position + Vec3(2, 0, 0) # Muta-l un pic la dreapta
            cloned = self.spawn_object(
                model=getattr(e, 'custom_model_path', 'cube'),
                texture=getattr(e, 'custom_texture_path', 'white_cube'),
                position=new_pos
            )
            cloned.scale = e.scale
            cloned.rotation = e.rotation
            print(f"[EDITOR] Obiect duplicat!")
            
        if key == 'g': # Toggle Grid Snap
            self.grid_snap = not self.grid_snap
            print(f"[EDITOR] Grid Snap: {'ON' if self.grid_snap else 'OFF'}")
        
        if key == 'b' and self.selected_entity: # Schimba modelul obiectului selectat
            current_mod_idx = 0
            if hasattr(self.selected_entity, 'custom_model_path'):
                try: current_mod_idx = self.available_models.index(self.selected_entity.custom_model_path)
                except: pass
            next_mod = self.available_models[(current_mod_idx + 1) % len(self.available_models)]
            self.selected_entity.model = next_mod
            self.selected_entity.custom_model_path = next_mod
            self.selected_entity.collider = 'box'
            print(f"[EDITOR] Model schimbat la: {next_mod}")
        
        if key == 'v' and self.selected_entity: # Schimba textura obiectului selectat
            current_tex_idx = 0
            if hasattr(self.selected_entity, 'custom_texture_path'):
                try: current_tex_idx = self.available_textures.index(self.selected_entity.custom_texture_path)
                except: pass
            elif self.selected_entity.texture:
                try: current_tex_idx = self.available_textures.index(self.selected_entity.texture.name)
                except: pass
            next_tex = self.available_textures[(current_tex_idx + 1) % len(self.available_textures)]
            self.selected_entity.texture = next_tex
            self.selected_entity.custom_texture_path = next_tex
            print(f"[EDITOR] Textura schimbata la: {next_tex}")

        if key == 'delete' and self.selected_entity:
            destroy(self.selected_entity)
            self.selected_entity = None
            print("[EDITOR] Obiect sters.")

        if key == 'left mouse down':
            if mouse.hovered_entity and getattr(mouse.hovered_entity, 'editable', False):
                self.selected_entity = mouse.hovered_entity
                print(f"[EDITOR] Selectat: {self.selected_entity.model.name if self.selected_entity.model else 'none'}")

        # Control Gizmo simplificat
        if self.selected_entity:
            step = 1.0 if self.grid_snap else 0.5
            if held_keys['control']:
                if key == 'up arrow': self.selected_entity.scale += Vec3(0.5, 0.5, 0.5)
                if key == 'down arrow': self.selected_entity.scale -= Vec3(0.5, 0.5, 0.5)
                if key == 'left arrow': self.selected_entity.scale_x -= 0.5
                if key == 'right arrow': self.selected_entity.scale_x += 0.5
            elif held_keys['shift']:
                if key == 'up arrow': self.selected_entity.rotation_x += 45 if self.grid_snap else 10
                if key == 'down arrow': self.selected_entity.rotation_x -= 45 if self.grid_snap else 10
                if key == 'left arrow': self.selected_entity.rotation_y -= 45 if self.grid_snap else 10
                if key == 'right arrow': self.selected_entity.rotation_y += 45 if self.grid_snap else 10
            else:
                if key == 'up arrow': self.selected_entity.y += step
                if key == 'down arrow': self.selected_entity.y -= step
                if key == 'left arrow': self.selected_entity.x -= step
                if key == 'right arrow': self.selected_entity.x += step
                if key == 'page up': self.selected_entity.z += step
                if key == 'page down': self.selected_entity.z -= step

            # Final snap if grid is on
            if self.grid_snap and not held_keys['control'] and not held_keys['shift']:
                self.selected_entity.position = Vec3(
                    round(self.selected_entity.x), 
                    round(self.selected_entity.y), 
                    round(self.selected_entity.z)
                )
