from controller import AudioController
from tkinter import Label
from tkinter.ttk import Progressbar
from PIL.ImageTk import PhotoImage
import os
from icoextract import IconExtractor
from PIL import Image


ICONS_FOLDER = "icons"
os.makedirs(ICONS_FOLDER, exist_ok=True)
ICON_PATH = "icon.ico"
ICON_BITMAP_PATH = "icon.bmp"
ICON = Image.open(ICON_PATH)
ICON_SIZE = 48


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
        volume = self.get_volume(master_volume)
        self.app_row = AppRow(index, self.icon, volume)
        controller.send_icon(index, self.bitmap_path)
        controller.send_volume(index, volume)

    def _get_icon(self):
        icon_path = os.path.join(ICONS_FOLDER, self.name + ".png")
        self.bitmap_path = os.path.join(ICONS_FOLDER, self.name + ".bmp")
        if not os.path.isfile(icon_path):
            path = self.session.Process.exe()
            try:
                extractor = IconExtractor(path)
                extractor.export_icon(icon_path)
                self.icon = Image.open(icon_path).resize((ICON_SIZE, ICON_SIZE), Image.ANTIALIAS)
                self.icon.save(icon_path)
                self.icon.save(self.bitmap_path)
            except Exception:
                self.icon = ICON
        else:
            self.icon = Image.open(icon_path)

    def get_volume(self, master_volume):
        return round(self.session.SimpleAudioVolume.GetMasterVolume() * master_volume * 100)

    def update(self, master_volume, controller):
        volume = self.get_volume(master_volume)
        self.app_row.update(volume)
        controller.send_volume(self.index, volume)

    def set_volume(self, volume):
        self.session.SimpleAudioVolume.SetMasterVolume(volume, None)

    def delete(self):
        self.app_row.delete()


class MasterAudioApplication(AudioApplication):
    def __init__(self, index, master_volume, controller):
        self.id = 0
        super().__init__(index, None, master_volume, controller)
    
    def _get_icon(self):
        self.icon = ICON
        self.bitmap_path = ICON_BITMAP_PATH

    def get_volume(self, master_volume):
        return round(master_volume * 100)

    def set_volume(self, volume):
        pass
