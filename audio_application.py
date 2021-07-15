from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from tkinter import Label
from tkinter.ttk import Progressbar
from PIL.ImageTk import PhotoImage
from PIL import Image
import os
from icoextract import IconExtractor


ICONS_FOLDER = "icons"
os.makedirs(ICONS_FOLDER, exist_ok=True)
ASSETS_FOLDER = "assets"
ICON_PATH = os.path.join(ASSETS_FOLDER, "icon.ico")
SIMPLE_ICON_PATH = os.path.join(ASSETS_FOLDER, "icon.png")
ICON = Image.open(ICON_PATH)
ICON_SIZE = 60
MAX_COLOURS = 30
DRAG_THRESHOLD = 80
MAX_SCREEN_ICONS = 4
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


class AudioApplication:
    def __init__(self, index, session, master_volume, controller):
        self.index = index
        if session:
            self.session = session
            self.id = self.session.Process.pid
            self.name = self.session.Process.name().split(".")[0]
            self.interface = self.session.SimpleAudioVolume
        self._get_icon()
        self.volume = self.get_volume(master_volume)
        self.muted = self.is_muted()
        self.app_row = AppRow(index, self.icon, self.volume, self.muted)
        self.draw_on_screen(controller)

    def draw_on_screen(self, controller):
        if self.index < MAX_SCREEN_ICONS:
            controller.send_icon(self.index, self.simple_icon_path)
            controller.send_volume(self.index, self.volume)

    def _get_icon(self):
        icon_path = os.path.join(ICONS_FOLDER, self.name + ".png")
        self.simple_icon_path = os.path.join(ICONS_FOLDER, self.name + "-simple.png")
        if not os.path.isfile(icon_path):
            path = self.session.Process.exe()
            try:
                extractor = IconExtractor(path)
                extractor.export_icon(icon_path)
                self.icon = Image.open(icon_path).resize((ICON_SIZE, ICON_SIZE), Image.ANTIALIAS)
                self.icon.save(icon_path)
                self.icon.quantize(MAX_COLOURS).save(self.simple_icon_path)
            except Exception:
                self.icon = ICON
        else:
            self.icon = Image.open(icon_path)

    def _set_volume(self, volume):
        self.interface.SetMasterVolume(volume, None)

    def get_volume(self, master_volume):
        return round(self.get_volume_percentage() * master_volume)

    def get_volume_percentage(self):
        return self.interface.GetMasterVolume()

    def update(self, master_volume, controller):
        volume = self.get_volume(master_volume)
        muted = self.is_muted()
        if muted != self.muted:
            if muted:
                self.app_row.set_mute()
            else:
                self.app_row.set_volume(volume)
            self.muted = muted
        elif not self.muted and volume != self.volume:
            self.app_row.set_volume(volume)
            controller.send_volume(self.index, volume)
            self.volume = volume

    def change_volume(self, change):
        new_volume = self.get_volume_percentage() + change
        if new_volume >= 0 and new_volume <= 1:
            self._set_volume(new_volume)

    def is_muted(self):
        return self.interface.GetMute()

    def get_position_change(self):
        return self.app_row.position_change

    def reset_position_change(self):
        self.app_row.position_change = 0
        self.app_row.dragging = False

    def move(self, change, controller):
        self.index += change
        self.app_row.move(change)
        self.draw_on_screen(controller)

    def toggle_mute(self):
        self.interface.SetMute(1 if not self.is_muted() else 0, None)

    def delete(self, controller):
        controller.delete_app(self.index)
        self.app_row.delete()


class MasterAudioApplication(AudioApplication):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    master_volume = cast(interface, POINTER(IAudioEndpointVolume))

    def __init__(self, controller):
        self.id = 0
        volume = self.get_volume()
        super().__init__(0, None, volume, controller)
    
    def _get_icon(self):
        self.icon = ICON
        self.simple_icon_path = SIMPLE_ICON_PATH

    def _set_volume(self, volume):
        self.master_volume.SetMasterVolumeLevelScalar(volume, None)

    def get_volume(self, volume=None):
        if volume:
            return volume
        else:
            return round(self.get_volume_percentage() * 100)

    def get_volume_percentage(self):
        return self.master_volume.GetMasterVolumeLevelScalar()

    def is_muted(self):
        return self.master_volume.GetMute()

    def toggle_mute(self):
        self.master_volume.SetMute(1 if not self.is_muted() else 0, None)
