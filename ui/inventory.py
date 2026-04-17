from ursina import *


SLOT_BG = color.rgb(30, 30, 30)
SLOT_SELECTED = color.rgb(200, 160, 40)
ITEM_COLORS = {
    'product': color.rgb(20, 160, 20),
    'water_can': color.rgb(40, 100, 200),
    'ph_up': color.rgb(200, 60, 60),
    'ph_down': color.rgb(60, 60, 200),
    'fertilizer': color.rgb(160, 100, 20),
}
ITEM_LABELS = {
    'product': 'PROD',
    'water_can': 'H2O',
    'ph_up': 'PH+',
    'ph_down': 'PH-',
    'fertilizer': 'FERT',
}


class InventoryItem:
    def __init__(self, item_type, quantity=1):
        self.item_type = item_type
        self.quantity = quantity

    @property
    def label(self):
        return ITEM_LABELS.get(self.item_type, self.item_type[:4].upper())

    @property
    def display_color(self):
        return ITEM_COLORS.get(self.item_type, color.gray)


class Inventory(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui)
        self.max_slots = 6
        self.slots_data = [None] * self.max_slots
        self.selected = 0
        self.money = 0.0

        self.money_text = Text(
            parent=camera.ui,
            text='$0',
            position=(0.82, 0.46),
            origin=(0, 0),
            scale=1.6,
            color=color.rgb(80, 220, 80)
        )

        Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.78, 0.082),
            position=(0, -0.46),
            color=color.rgba(0, 0, 0, 0.65)
        )

        self._slot_entities = []
        self._label_entities = []
        self._count_entities = []

        for i in range(self.max_slots):
            sx = -0.3 + i * 0.12
            slot_bg = Entity(
                parent=camera.ui,
                model='quad',
                scale=(0.1, 0.088),
                position=(sx, -0.46),
                color=SLOT_BG
            )
            self._slot_entities.append(slot_bg)

            lbl = Text(
                parent=camera.ui,
                text='',
                position=(sx, -0.46),
                origin=(0, 0),
                scale=1.1,
                color=color.white
            )
            self._label_entities.append(lbl)

            cnt = Text(
                parent=camera.ui,
                text='',
                position=(sx + 0.035, -0.435),
                origin=(0, 0),
                scale=0.8,
                color=color.rgb(200, 200, 200)
            )
            self._count_entities.append(cnt)

        self._update_visuals()

    def add_money(self, amount):
        self.money += amount
        self._update_visuals()

    def add_item(self, item_type, quantity=1):
        for item in self.slots_data:
            if item and item.item_type == item_type:
                item.quantity += quantity
                self._update_visuals()
                return True
        for i, slot in enumerate(self.slots_data):
            if slot is None:
                self.slots_data[i] = InventoryItem(item_type, quantity)
                self._update_visuals()
                return True
        return False

    def remove_product(self, quantity=1):
        for item in self.slots_data:
            if item and item.item_type == 'product':
                removed = min(quantity, item.quantity)
                item.quantity -= removed
                if item.quantity <= 0:
                    idx = self.slots_data.index(item)
                    self.slots_data[idx] = None
                self._update_visuals()
                return removed
        return 0

    def count_product(self):
        total = 0
        for item in self.slots_data:
            if item and item.item_type == 'product':
                total += item.quantity
        return total

    def get_selected(self):
        return self.slots_data[self.selected]

    def select_next(self):
        self.selected = (self.selected + 1) % self.max_slots
        self._update_visuals()

    def select_prev(self):
        self.selected = (self.selected - 1) % self.max_slots
        self._update_visuals()

    def _update_visuals(self):
        self.money_text.text = f'${self.money:.0f}'
        for i in range(self.max_slots):
            item = self.slots_data[i]
            slot_ent = self._slot_entities[i]
            lbl_ent = self._label_entities[i]
            cnt_ent = self._count_entities[i]

            slot_ent.color = SLOT_SELECTED if i == self.selected else SLOT_BG

            if item:
                lbl_ent.text = item.label
                lbl_ent.color = item.display_color
                cnt_ent.text = str(item.quantity) if item.quantity > 1 else ''
            else:
                lbl_ent.text = ''
                cnt_ent.text = ''
