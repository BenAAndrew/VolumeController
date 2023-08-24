from dataclasses import dataclass
import os
from typing import List
from PIL import Image

from volume_controller.utils import resource


ICON_PATH = resource(os.path.join("assets", "icon.ico"))
TITLE = "Audio Controller"


@dataclass
class MenuOption:
    def __init__(self, id, enabled, callback, name):
        import pystray

        self.id = id
        self.enabled = enabled
        self.callback = callback
        self.menu_item = pystray.MenuItem(name, self.on_clicked, checked=lambda item: self.enabled)

    def on_clicked(self):
        self.enabled = not self.enabled
        self.callback(self.id, self.enabled)


class Application:
    options: List[MenuOption]

    def __init__(self, on_close: callable):
        import pystray

        self.options = []
        self.tray_app = pystray
        image = Image.open(ICON_PATH)
        self.quit_option = self.tray_app.MenuItem("Quit", self.quit_window)
        self.icon = self.tray_app.Icon("name", image, TITLE, self.tray_app.Menu(*[self.quit_option]))
        self.on_close = on_close

    def quit_window(self, icon, item):
        self.on_close()
        self.icon.stop()

    def update_options(self):
        options = [i.menu_item for i in self.options] + [self.quit_option]
        self.icon.menu = self.tray_app.Menu(*options)
        self.icon.update_menu()

    def add_option(self, id, name, enabled, callback):
        option = MenuOption(id=id, enabled=enabled, callback=callback, name=name)
        self.options.insert(0, option)
        self.update_options()
        return option

    def remove_option(self, id):
        matching_index = [index for index, item in enumerate(self.options) if item.id == id][0]
        del self.options[matching_index]
        self.update_options()

    def run(self):
        self.icon.run()
