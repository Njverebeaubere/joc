import csv
import os
from ursina import *

class MapManager:
    def __init__(self, filename='map_data.csv'):
        self.filename = os.path.join(os.path.dirname(__file__), '..', filename)
        self.entities = []

    def save_map(self, scene_entities):
        """Salvează toate entitățile editabile în CSV."""
        with open(self.filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['model', 'texture', 'x', 'y', 'z', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz'])
            for e in scene_entities:
                if getattr(e, 'editable', False):
                    model_path = getattr(e, 'custom_model_path', e.model.name if e.model else 'none')
                    texture_path = getattr(e, 'custom_texture_path', e.texture.name if e.texture else 'none')
                    writer.writerow([
                        model_path,
                        texture_path,
                        e.x, e.y, e.z,
                        e.scale_x, e.scale_y, e.scale_z,
                        e.rotation_x, e.rotation_y, e.rotation_z
                    ])
        print(f"[!] Harta a fost salvată în {self.filename}")

    def load_map(self):
        """Încarcă entitățile din CSV în scenă."""
        if not os.path.exists(self.filename):
            return []

        # Cleanup: șterge entitățile editabile existente pentru a evita duplicatele la reload
        for e in list(scene.entities):
            if getattr(e, 'editable', False):
                destroy(e)

        loaded_entities = []
        with open(self.filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                mod = None if row['model'] == 'none' else row['model']
                tex = None if row['texture'] == 'none' else row['texture']
                e = Entity(
                    model=mod,
                    texture=tex,
                    position=(float(row['x']), float(row['y']), float(row['z'])),
                    scale=(float(row['sx']), float(row['sy']), float(row['sz'])),
                    rotation=(float(row['rx']), float(row['ry']), float(row['rz'])),
                    collider='box'
                )
                e.editable = True
                e.custom_model_path = row['model']
                e.custom_texture_path = row['texture']
                loaded_entities.append(e)
        print(f"[+] S-au încărcat {len(loaded_entities)} obiecte din hartă.")
        return loaded_entities
