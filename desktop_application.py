import os
from PIL import Image
from tkinter import Label
from tkinter.ttk import Progressbar
from PIL.ImageTk import PhotoImage

MAX_SCREEN_ICONS = 4
DRAG_THRESHOLD = 80
ASSETS_FOLDER = "assets"
EYE_ICON = Image.open(os.path.join(ASSETS_FOLDER, "eye.png"))
CLOSED_EYE_ICON = Image.open(os.path.join(ASSETS_FOLDER, "eye-slash.png"))
MUTE_ICON = Image.open(os.path.join(ASSETS_FOLDER, "mute.png"))

class AppRow:
    def __init__(self, index, image, volume, muted):
        self.index = index
        self.eye_icon = self._add_image(EYE_ICON if index < MAX_SCREEN_ICONS else CLOSED_EYE_ICON)
        self.eye_icon.grid(row=index, column=0, padx=5, pady=5)
        self.icon = self._add_image(image)
        self.icon.grid(row=index, column=1, padx=5, pady=5)
        if index != 0:
            self.icon.bind("<Button-1>", self.on_drag_start)
            self.icon.bind("<B1-Motion>", self.on_drag_motion)
        self.vol_bar = Progressbar(length=200, value=0 if muted else volume, mode="determinate")
        self.vol_bar.grid(row=index, column=2, padx=5, pady=5)
        if muted:
            self.set_mute()
        else:
            self.set_volume(volume)
        self.position_change = 0
        self.dragging = False

    def _add_image(self, image):
        img = PhotoImage(image)
        icon = Label(image=img)
        icon.image = img
        return icon

    def on_drag_start(self, event):
        widget = event.widget
        widget._drag_start_y = event.y
        self.dragging = True

    def on_drag_motion(self, event):
        if self.dragging:
            widget = event.widget
            y = event.y - widget._drag_start_y
            if y >= DRAG_THRESHOLD:
                self.position_change = 1
            elif y <= - DRAG_THRESHOLD:
                self.position_change = -1

    def move(self, change):
        current_row = self.icon.grid_info()["row"]
        new_row = current_row + change
        self.icon.grid(row=new_row)
        self.vol_bar.grid(row=new_row)
        self.vol_label.grid(row=new_row)

    def set_volume(self, volume):
        self.vol_bar["value"] = volume
        self.vol_label = Label(text=str(volume).ljust(4), font=('Helvetica bold',14))
        self.vol_label.grid(row=self.index, column=3, padx=5, pady=5)

    def set_mute(self):
        self.vol_bar["value"] = 0
        self.vol_label = self._add_image(MUTE_ICON)
        self.vol_label.grid(row=self.index, column=3, padx=5, pady=5)

    def delete(self):
        self.icon.grid_forget()
        self.vol_bar.grid_forget()
        self.vol_label.grid_forget()
