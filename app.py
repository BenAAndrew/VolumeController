from dataclasses import dataclass
import os
from PIL import Image
import pystray


ASSETS_FOLDER = "assets"
ICON_PATH = os.path.join(ASSETS_FOLDER, "icon.ico")
TITLE = "Audio Controller"


@dataclass
class Option:
    name: str
    enabled: bool

    def on_clicked(self):
        self.enabled = not self.enabled


class Application:
    options = {}

    def __init__(self):
        image = Image.open(ICON_PATH)
        self.menu_items = [pystray.MenuItem('Quit', self.quit_window)]
        self.icon = pystray.Icon("name", image, TITLE, pystray.Menu(*self.menu_items))

    def quit_window(self, icon, item):
        self.icon.stop()

    def update_options(self):
        self.icon.menu = pystray.Menu(*self.menu_items)
        self.icon.update_menu()

    def add_option(self, name):
        option = Option(name=name, enabled=True)
        new_menu_item = pystray.MenuItem(option.name, option.on_clicked, checked=lambda item: option.enabled)
        self.menu_items.insert(0, new_menu_item)
        self.update_options()

    def run(self):
        self.icon.run()
