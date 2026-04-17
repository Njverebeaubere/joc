from ursina import *
from config import keybinds

class HUDManager:
    def __init__(self):
        self.ui_info = Text(text='', position=(-0.85, 0.45), scale=1, visible=False)
        self.ui_hint = Text(text="", position=(0, -0.35), origin=(0,0), scale=1.2, visible=False)

    def update_hud(self, hit_info, plant):
        if hit_info.hit and hit_info.entity == plant:
            self.ui_info.visible = True
            self.ui_hint.visible = True
            
            s = f"=== STATUS CULTURA ===\n\n"
            if plant.health > 0:
                s += f"Maturitate: {min(100, plant.growth*100):.1f}%\n"
                s += f"Sanatate:   {plant.health:.1f} HP\n"
                ph_col = "PERFECT" if 6.0 <= plant.ph_level <= 6.8 else "DEZECHILIBRU"
                s += f"Nivel PH:   {plant.ph_level:.2f} [{ph_col}]\n"
                wat_col = "OPTIM" if 40 <= plant.water_level <= 80 else "PERICOL"
                s += f"Nivel Apa:  {plant.water_level:.1f}% [{wat_col}]\n"
                s += f"Lampa UV:   {'ON' if plant.light_cycle_on else 'OFF'}\n\n"
                s += f"HEAT (Miros): +{plant.smell_radius:.1f}\n"
                
                self.ui_hint.text = f"[{keybinds['apa'].upper()}] Apa  |  [{keybinds['ph_up'].upper()}] PH+  |  [{keybinds['ph_down'].upper()}] PH-  |  [{keybinds['lumina'].upper()}] Lumina"
            else:
                s += "[*] CULTURA RATATA.\n"
            
            self.ui_info.text = s
        else:
            self.ui_info.visible = False
            self.ui_hint.visible = False
