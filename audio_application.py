import os
from icoextract import IconExtractor
from PIL import Image


ICONS_FOLDER = "icons"
os.makedirs(ICONS_FOLDER, exist_ok=True)


class AudioApplication:
    def __init__(self, session):
        self.session = session
        self.id = self.session.Process.pid
        self.name = self.session.Process.name().split(".")[0]
        icon_path = os.path.join(ICONS_FOLDER, self.name + ".png")
        if not os.path.isfile(icon_path):
            path = self.session.Process.cmdline()[0]
            extractor = IconExtractor(path)
            extractor.export_icon(icon_path)
            self.icon = Image.open(icon_path).resize((32, 32), Image.ANTIALIAS)
            self.icon.save(icon_path)
        else:
            self.icon = Image.open(icon_path)

    def get_volume(self):
        return self.session.SimpleAudioVolume.GetMasterVolume()

    def set_volume(self, volume):
        self.session.SimpleAudioVolume.SetMasterVolume(volume, None)
