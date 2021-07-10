from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from tkinter import Label
from tkinter.ttk import Progressbar, Button
from PIL.ImageTk import PhotoImage
from PIL import Image
import os
from icoextract import IconExtractor


ICONS_FOLDER = "icons"
os.makedirs(ICONS_FOLDER, exist_ok=True)
ICON_PATH = "icon.ico"
SIMPLE_ICON_PATH = "icon.png"
ICON = Image.open(ICON_PATH)
ICON_SIZE = 60
MAX_COLOURS = 30
DISABLED_APPS_FILE = "disabled.txt"


with open(DISABLED_APPS_FILE) as f:
    disabled_apps = set([line[:-1] for line in f.readlines()])


def save_disable_apps():
    with open(DISABLED_APPS_FILE, 'w') as f:
        for app in disabled_apps:
            f.write(app+'\n')


class AppRow:
    def __init__(self, index, image, volume, muted):
        img = PhotoImage(image)
        self.icon = Label(image=img)
        self.icon.image = img
        self.icon.grid(row=index, column=1, padx=5, pady=5)
        self.vol_bar = Progressbar(length=200, value=0 if muted else volume, mode="determinate")
        self.vol_bar.grid(row=index, column=2, padx=5, pady=5)
        self.vol_label = Label(text="🔇" if muted else volume, font=('Helvetica bold',14))
        self.vol_label.grid(row=index, column=3, padx=5, pady=5)

    def set_volume(self, volume):
        self.vol_bar["value"] = volume
        self.vol_label["text"] = volume

    def set_mute(self):
        self.vol_bar["value"] = 0
        self.vol_label["text"] = "🔇"

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
            self.enabled = self.name not in disabled_apps
            self.interface = self.session.SimpleAudioVolume
            self.button = Button(text="Disable" if self.enabled else "Enable", command=self._toggle_enable)
            self.button.grid(row=index, column=0, padx=5, pady=5)
        else:
            self.enabled = True
        self._get_icon()
        self.volume = self.get_volume(master_volume)
        self.muted = self.is_muted()
        self.app_row = AppRow(index, self.icon, self.volume, self.muted)
        controller.send_icon(index, self.simple_icon_path)
        controller.send_volume(index, self.volume)

    def _toggle_enable(self):
        if self.enabled:
            self._disable()
        else:
            self._enable()
        self.enabled = not self.enabled

    def _enable(self):
        disabled_apps.remove(self.name)
        self.button["text"] = "Disable"

    def _disable(self):
        disabled_apps.add(self.name)
        self.button["text"] = "Enable"

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
        elif volume != self.volume:
            self.app_row.set_volume(volume)
            controller.send_volume(self.index, volume)
            self.volume = volume

    def change_volume(self, change):
        new_volume = self.get_volume_percentage() + change
        if new_volume >= 0 and new_volume <= 1:
            self._set_volume(new_volume)

    def is_muted(self):
        return self.interface.GetMute()

    def toggle_mute(self):
        self.interface.SetMute(1 if not self.is_muted() else 0, None)

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
