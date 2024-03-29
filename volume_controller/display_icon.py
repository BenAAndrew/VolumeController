from typing import Optional


class DisplayIcon:
    index: Optional[int]

    def __init__(self, icon_path, volume, muted, controller):
        self.controller = controller
        self.icon_path = icon_path
        self.volume = volume
        self.muted = muted

    def send_volume(self, volume):
        self.controller.send_volume(self.index, volume)
        self.volume = volume

    def set_mute(self):
        self.controller.mute_app(self.index)
        self.muted = True

    def draw_on_screen(self, index):
        self.index = index
        self.controller.send_icon(index, self.icon_path)
        if self.muted:
            self.controller.mute_app(index)
        else:
            self.controller.send_volume(index, self.volume)

    def delete(self):
        if self.index:
            self.controller.delete_app(self.index)
