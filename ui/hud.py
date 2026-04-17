from ursina import *
from config import keybinds


class HUDManager:
    def __init__(self):
        # Plant status panel (top-left)
        self.panel_bg = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.32, 0.3),
            position=(-0.73, 0.33),
            color=color.rgba(0, 0, 0, 0.62),
            visible=False
        )
        self.ui_info = Text(
            text='',
            position=(-0.85, 0.46),
            scale=1.05,
            visible=False,
            color=color.rgb(220, 220, 220)
        )
        self.ui_hint = Text(
            text='',
            position=(0, -0.38),
            origin=(0, 0),
            scale=1.15,
            visible=False,
            color=color.rgb(180, 220, 255)
        )

        # Interaction prompt
        self.interact_prompt = Text(
            text='',
            position=(0, -0.28),
            origin=(0, 0),
            scale=1.3,
            visible=False,
            color=color.rgb(255, 240, 100)
        )

        # Heat / wanted bar (top center)
        self.heat_bar_bg = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.3, 0.022),
            position=(0, 0.475),
            color=color.rgba(0, 0, 0, 0.5)
        )
        self.heat_bar_fill = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.001, 0.018),
            position=(-0.15, 0.475),
            color=color.rgb(220, 60, 40),
            origin=(-0.5, 0)
        )
        self.heat_label = Text(
            text='HEAT: 0%',
            position=(0, 0.46),
            origin=(0, 0),
            scale=0.9,
            color=color.rgb(255, 120, 60)
        )

        # Day/time display (top right)
        self.time_label = Text(
            text='DAY 1  06:00',
            position=(0.72, 0.475),
            origin=(0, 0),
            scale=1.0,
            color=color.rgb(180, 220, 255)
        )

        # Crosshair
        self.crosshair_h = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.018, 0.003),
            position=(0, 0),
            color=color.rgba(255, 255, 255, 180)
        )
        self.crosshair_v = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.003, 0.022),
            position=(0, 0),
            color=color.rgba(255, 255, 255, 180)
        )
        self.crosshair_dot = Entity(
            parent=camera.ui,
            model='circle',
            scale=(0.005, 0.007),
            position=(0, 0),
            color=color.rgba(255, 255, 255, 220)
        )

        # Alert flash
        self.alert_text = Text(
            text='',
            position=(0, 0.3),
            origin=(0, 0),
            scale=1.8,
            visible=False,
            color=color.rgb(255, 60, 60)
        )
        self._alert_timer = 0.0

    def show_alert(self, msg, duration=3.0):
        self.alert_text.text = msg
        self.alert_text.visible = True
        self._alert_timer = duration

    def update_time_display(self, day, hour, minute):
        self.time_label.text = f'DAY {day}  {hour:02d}:{minute:02d}'

    def update_heat(self, heat_pct):
        clamped = max(0.0, min(1.0, heat_pct))
        bar_width = clamped * 0.3
        self.heat_bar_fill.scale_x = max(0.001, bar_width)
        self.heat_bar_fill.x = -0.15

        r = int(60 + clamped * 195)
        g = int(220 - clamped * 180)
        self.heat_bar_fill.color = color.rgb(r, g, 40)

        pct_int = int(clamped * 100)
        label = 'LOW' if pct_int < 30 else ('MED' if pct_int < 65 else 'HIGH')
        self.heat_label.text = f'HEAT: {pct_int}% [{label}]'
        if clamped > 0.65:
            self.heat_label.color = color.rgb(255, 80, 40)
        elif clamped > 0.3:
            self.heat_label.color = color.rgb(255, 180, 40)
        else:
            self.heat_label.color = color.rgb(120, 220, 80)

    def update_hud(self, hit_info, plant):
        dt = time.dt
        if self._alert_timer > 0:
            self._alert_timer -= dt
            if self._alert_timer <= 0:
                self.alert_text.visible = False

        looking_at_plant = hit_info.hit and (
            hit_info.entity == plant or
            (hit_info.entity and hit_info.entity.parent == plant)
        )

        if looking_at_plant:
            self.panel_bg.visible = True
            self.ui_info.visible = True
            self.ui_hint.visible = True

            if plant.health > 0:
                mat = plant.maturity_pct
                ph_ok = 6.0 <= plant.ph_level <= 6.8
                wat_ok = 30 <= plant.water_level <= 85
                ph_tag = 'OK' if ph_ok else 'BAD'
                wat_tag = 'OK' if wat_ok else 'LOW' if plant.water_level < 30 else 'HIGH'

                bar_mat = int(mat / 100 * 12)
                bar_h = int(plant.health / 100 * 12)
                mat_bar = '[' + '#' * bar_mat + '.' * (12 - bar_mat) + ']'
                hp_bar = '[' + '#' * bar_h + '.' * (12 - bar_h) + ']'

                s = f"== PLANT STATUS ==\n"
                s += f"Growth  {mat_bar} {mat:.0f}%\n"
                s += f"Health  {hp_bar} {plant.health:.0f}\n"
                s += f"pH      {plant.ph_level:.1f}  [{ph_tag}]\n"
                s += f"Water   {plant.water_level:.0f}%  [{wat_tag}]\n"
                s += f"Light   {'ON' if plant.light_cycle_on else 'OFF'}\n"
                s += f"Smell   {plant.smell_radius:.1f}\n"

                if plant.is_harvestable:
                    s += "\n[READY TO HARVEST - press H]"

                self.ui_hint.text = (
                    f"[{keybinds['apa'].upper()}] Water  "
                    f"[{keybinds['ph_up'].upper()}] pH+  "
                    f"[{keybinds['ph_down'].upper()}] pH-  "
                    f"[{keybinds['lumina'].upper()}] Light"
                )
            else:
                s = "== PLANT STATUS ==\n\nPLANT DEAD."
                self.ui_hint.text = ''

            self.ui_info.text = s
        else:
            self.panel_bg.visible = False
            self.ui_info.visible = False
            self.ui_hint.visible = False

    def set_interact_prompt(self, text):
        if text:
            self.interact_prompt.text = text
            self.interact_prompt.visible = True
        else:
            self.interact_prompt.visible = False
