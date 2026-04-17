from ursina import *
from config import keybinds

class PauseMenu:
    def __init__(self):
        self.current_bind_action = None
        self.menu_bg = Entity(parent=camera.ui, model='quad', scale=(0.8, 0.8), color=color.black90, visible=False, collider='box')
        Text("SETTINGS / KEYBINDS", parent=self.menu_bg, y=0.35, origin=(0,0), scale=2, color=color.orange)
        Text("Apasa din nou tasta ESCAPE pentru a te intoarce", parent=self.menu_bg, y=0.25, origin=(0,0), scale=1, color=color.gray)
        
        self.bind_buttons = {}
        y_pos = 0.1
        for action in ['apa', 'ph_up', 'ph_down', 'lumina']:
            Text(f"Actiune {action.upper()}:", parent=self.menu_bg, x=-0.2, y=y_pos, origin=(0,0))
            btn = Button(parent=self.menu_bg, text=keybinds[action], x=0.2, y=y_pos, scale=(0.3, 0.08))
            btn.on_click = Func(self.set_bind_action, action)
            self.bind_buttons[action] = btn
            y_pos -= 0.12
            
        def quit_game(): application.quit()
        Button(parent=self.menu_bg, text="QUIT GAME", y=-0.35, scale=(0.4, 0.1), color=color.dark_gray, on_click=quit_game)

    def set_bind_action(self, action):
        self.current_bind_action = action
        self.bind_buttons[action].text = "[ APASA ]"
        self.bind_buttons[action].color = color.red

    def handle_bind(self, key):
        if key not in ['left mouse down', 'right mouse down', 'escape']:
            keybinds[self.current_bind_action] = key
            self.bind_buttons[self.current_bind_action].text = key.upper()
            self.bind_buttons[self.current_bind_action].color = color.black90
            self.current_bind_action = None
            
    def toggle(self):
        self.menu_bg.visible = not self.menu_bg.visible
        mouse.locked = not self.menu_bg.visible
        if self.menu_bg.visible:
            self.current_bind_action = None
