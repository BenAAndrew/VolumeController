from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from tkinter import Label
from tkinter.ttk import Progressbar
from PIL.ImageTk import PhotoImage
import os
from icoextract import IconExtractor
from PIL import Image


ICONS_FOLDER = "icons"
os.makedirs(ICONS_FOLDER, exist_ok=True)
ICON_PATH = "icon.ico"
SIMPLE_ICON_PATH = "icon.png"
ICON = Image.open(ICON_PATH)
ICON_SIZE = 60
MAX_COLOURS = 30


class AppRow:
    def __init__(self, index, image, volume):
        img = PhotoImage(image)
        self.icon = Label(image=img)
        self.icon.image = img
        self.icon.grid(row=index, column=0, padx=5, pady=5)
        self.vol_bar = Progressbar(length=200, value=volume, mode="determinate")
        self.vol_bar.grid(row=index, column=1, padx=5, pady=5)
        self.vol_label = Label(text=volume)
        self.vol_label.grid(row=index, column=2, padx=5, pady=5)

    def update(self, volume):
        self.vol_bar["value"] = volume
        self.vol_label["text"] = volume

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
        self._get_icon()
        self.volume = self.get_volume(master_volume)
        self.app_row = AppRow(index, self.icon, self.volume)
        controller.send_icon(index, self.simple_icon_path)
        controller.send_volume(index, self.volume)

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

    def get_volume(self, master_volume):
        return round(self.get_volume_percentage() * master_volume)

    def get_volume_percentage(self):
        return self.session.SimpleAudioVolume.GetMasterVolume()

    def update(self, master_volume, controller):
        volume = self.get_volume(master_volume)
        if volume != self.volume:
            self.app_row.update(volume)
            controller.send_volume(self.index, volume)
            self.volume = volume

    def set_volume(self, volume):
        self.session.SimpleAudioVolume.SetMasterVolume(volume, None)

    def change_volume(self, change):
        new_volume = self.get_volume_percentage() + change
        if new_volume >= 0 and new_volume <= 1:
            self.set_volume(new_volume)

    def delete(self):
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

    def get_volume(self, volume=None):
        if volume:
            return volume
        else:
            return round(self.get_volume_percentage() * 100)

    def get_volume_percentage(self):
        return self.master_volume.GetMasterVolumeLevelScalar() 

    def set_volume(self, volume):
        self.master_volume.SetMasterVolumeLevelScalar(volume, None)
