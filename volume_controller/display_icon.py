class DisplayIcon:
    def __init__(self, icon_path, index, volume, muted, controller):
        self.controller = controller
        self.icon_path = icon_path
        self.index = index
        self.volume = volume
        self.muted = muted
        self.draw_on_screen(volume, muted)

    def send_volume(self, volume):
        self.controller.send_volume(self.index, volume)
        self.volume = volume

    def set_mute(self):
        self.controller.mute_app(self.index)
        self.muted = True

    def draw_on_screen(self, volume, muted):
        self.controller.send_icon(self.index, self.icon_path)
        if muted:
            self.controller.mute_app(self.index)
        else:
            self.controller.send_volume(self.index, volume)

    def delete(self):
        self.controller.delete_app(self.index)
