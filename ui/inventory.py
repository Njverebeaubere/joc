from ursina import *

class Inventory(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui)
        self.items = []
        self.max_slots = 5
        self.selected_slot = 0
        
        # UI
        self.bg = Entity(parent=self, model='quad', scale=(0.5, 0.1), position=(0, -0.45), color=color.black66)
        self.slots = []
        for i in range(self.max_slots):
            slot = Entity(parent=self.bg, model='quad', scale=(0.18, 0.8), position=(-0.4 + i*0.2, 0), color=color.dark_gray)
            self.slots.append(slot)
        
        self.update_visuals()

    def add_item(self, item_name):
        if len(self.items) < self.max_slots:
            self.items.append(item_name)
            self.update_visuals()
            return True
        return False

    def remove_item(self, index):
        if 0 <= index < len(self.items):
            item = self.items.pop(index)
            self.update_visuals()
            return item
        return None

    def update_visuals(self):
        for i, slot in enumerate(self.slots):
            if i == self.selected_slot:
                slot.color = color.yellow
            else:
                slot.color = color.dark_gray
            
            # Text in slot (simulat)
            if i < len(self.items):
                slot.texture = 'white_cube' # Placeholder
            else:
                slot.texture = None
