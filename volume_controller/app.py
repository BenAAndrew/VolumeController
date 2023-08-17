from dataclasses import dataclass
import os
from PIL import Image
import pystray


ICON_PATH = os.path.join("assets", "icon.ico")
TITLE = "Audio Controller"


@dataclass
class MenuOption:
    id: int
    enabled: bool
    callback: callable

    def on_clicked(self):
        self.enabled = not self.enabled
        self.callback(self.id, self.enabled)


class Application:
    def __init__(self):
        image = Image.open(ICON_PATH)
        self.menu_items = [pystray.MenuItem("Quit", self.quit_window)]
        self.icon = pystray.Icon("name", image, TITLE, pystray.Menu(*self.menu_items))

    def quit_window(self, icon, item):
        self.icon.stop()

    def update_options(self):
        self.icon.menu = pystray.Menu(*self.menu_items)
        self.icon.update_menu()

    def add_option(self, id, name, enabled, callback):
        option = MenuOption(id=id, enabled=enabled, callback=callback)
        new_menu_item = pystray.MenuItem(name, option.on_clicked, checked=lambda item: option.enabled)
        self.menu_items.insert(0, new_menu_item)
        self.update_options()
        return option

    def run(self):
        self.icon.run()
