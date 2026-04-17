import random
from ursina import *


PHONE_BG = color.rgb(18, 18, 22)
PHONE_SCREEN = color.rgb(10, 12, 18)
PHONE_HEADER = color.rgb(25, 35, 60)
PHONE_GREEN = color.rgb(40, 200, 80)
PHONE_TEXT = color.rgb(220, 220, 220)
PHONE_DIM = color.rgb(120, 120, 120)

CONTACTS = [
    ("Mike", "Need the usual, man. You around?"),
    ("Tony", "Got cash. 3 units ASAP. Call me."),
    ("Dave", "Hook me up. Paying premium tonight."),
    ("Carl", "My guy! 2 units when you're free."),
    ("Ray", "Heard youre holding. 4 units?"),
    ("Sam", "Need a re-up. You got stock?"),
]

NEWS_ITEMS = [
    "Police increase patrols downtown.",
    "City reports unusual odors near residential.",
    "Drug bust on east side - 3 arrested.",
    "K9 units deployed to 5th district.",
    "Anonymous tip leads to safehouse raid.",
    "Market prices up 20% this week.",
    "New buyers flooding the south block.",
]


class PhoneUI(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui, enabled=False)
        self.messages = []
        self._build_ui()
        self._generate_initial_messages()

    def _build_ui(self):
        # Phone frame
        self.phone_frame = Entity(
            parent=self,
            model='quad',
            scale=(0.28, 0.52),
            position=(0.62, 0),
            color=color.rgb(35, 35, 40)
        )

        # Screen
        self.screen = Entity(
            parent=self,
            model='quad',
            scale=(0.24, 0.46),
            position=(0.62, 0),
            color=PHONE_SCREEN
        )

        # Status bar
        Entity(
            parent=self,
            model='quad',
            scale=(0.24, 0.04),
            position=(0.62, 0.225),
            color=PHONE_HEADER
        )
        self.time_text = Text(
            parent=self,
            text='12:00',
            position=(0.62, 0.225),
            origin=(0, 0),
            scale=0.9,
            color=PHONE_GREEN
        )

        # App title
        Text(
            parent=self,
            text='MESSAGES',
            position=(0.62, 0.19),
            origin=(0, 0),
            scale=0.9,
            color=PHONE_GREEN
        )

        # Message container
        self.msg_container = Entity(parent=self, position=(0.62, 0.13))
        self.msg_texts = []
        for i in range(8):
            t = Text(
                parent=self.msg_container,
                text='',
                position=(0, -i * 0.055),
                origin=(-1, 0),
                scale=0.72,
                color=PHONE_TEXT
            )
            self.msg_texts.append(t)

        # Notification dot
        self.notif_dot = Entity(
            parent=camera.ui,
            model='circle',
            scale=(0.018, 0.025),
            position=(0.88, 0.44),
            color=color.rgb(255, 50, 50),
            visible=False
        )

    def _generate_initial_messages(self):
        for name, msg in random.sample(CONTACTS, 3):
            self.messages.append({
                'from': name,
                'text': msg,
                'read': False,
                'time': f'{random.randint(8,11)}:{random.randint(10,59):02d}'
            })
        self._refresh_display()

    def add_message(self, sender, text):
        self.messages.insert(0, {
            'from': sender,
            'text': text,
            'read': False,
            'time': '??:??'
        })
        self.notif_dot.visible = True
        self._refresh_display()

    def add_news(self):
        item = random.choice(NEWS_ITEMS)
        self.add_message("NEWS", item)

    def _refresh_display(self):
        for i, t in enumerate(self.msg_texts):
            if i < len(self.messages):
                m = self.messages[i]
                read_marker = '' if m['read'] else '* '
                preview = m['text'][:22] + ('...' if len(m['text']) > 22 else '')
                t.text = f"{read_marker}{m['from']}: {preview}"
                t.color = PHONE_TEXT if not m['read'] else PHONE_DIM
            else:
                t.text = ''

    def update_time(self, hour, minute):
        self.time_text.text = f'{hour:02d}:{minute:02d}'

    def toggle(self):
        self.enabled = not self.enabled
        if self.enabled:
            for m in self.messages:
                m['read'] = True
            self.notif_dot.visible = False
            self._refresh_display()
        mouse.visible = self.enabled
