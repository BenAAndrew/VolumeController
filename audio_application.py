import os
from icoextract import IconExtractor


class AudioApplication:
    def __init__(self, session):
        self.session = session
        self.id = self.session.Process.pid
        self.name = self.session.Process.name().split(".")[0]
        self.icon = os.path.join("icons", self.name + ".png")
        if not os.path.isfile(self.icon):
            path = self.session.Process.cmdline()[0]
            extractor = IconExtractor(path)
            extractor.export_icon(self.icon)

    def get_volume(self):
        return self.session.SimpleAudioVolume.GetMasterVolume()

    def set_volume(self, volume):
        self.session.SimpleAudioVolume.SetMasterVolume(volume, None)
