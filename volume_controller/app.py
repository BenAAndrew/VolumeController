from dataclasses import dataclass
import os
from PIL import Image

from volume_controller.utils import resource


ICON_PATH = resource(os.path.join("assets", "icon.ico"))
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
    def __init__(self, on_close: callable):
        import pystray

        self.tray_app = pystray
        image = Image.open(ICON_PATH)
        self.menu_items = [self.tray_app.MenuItem("Quit", self.quit_window)]
        self.icon = self.tray_app.Icon("name", image, TITLE, self.tray_app.Menu(*self.menu_items))
        self.on_close = on_close

    def quit_window(self, icon, item):
        self.on_close()
        self.icon.stop()

    def update_options(self):
        self.icon.menu = self.tray_app.Menu(*self.menu_items)
        self.icon.update_menu()

    def add_option(self, id, name, enabled, callback):
        option = MenuOption(id=id, enabled=enabled, callback=callback)
        new_menu_item = self.tray_app.MenuItem(name, option.on_clicked, checked=lambda item: option.enabled)
        self.menu_items.insert(0, new_menu_item)
        self.update_options()
        return option

    def run(self):
        self.icon.run()
