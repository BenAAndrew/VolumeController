class DisplayIcon:
    def __init__(self, icon_path, index, volume, muted, controller):
        self.controller = controller
        self.icon_path = icon_path
        self.index = index
        self.draw_on_screen(volume, muted)

    def volume_change(self, volume):
        self.controller.send_volume(self.index, volume)

    def draw_on_screen(self, volume, muted):
        self.controller.send_icon(self.index, self.icon_path)
        if muted:
            self.controller.mute_app(self.index)
        else:
            self.controller.send_volume(self.index, volume)

    def delete(self):
        self.controller.delete_app(self.index)
