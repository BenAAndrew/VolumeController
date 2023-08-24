from ctypes import cast, POINTER


class AudioSession:
    class Process:
        pid: int

        def name(self) -> str:
            pass

        def exe(self) -> str:
            pass


class AudioInterface:
    def __init__(self, session):
        if session:
            self.interface = session.SimpleAudioVolume

    def _set_volume(self, volume):
        self.interface.SetMasterVolume(volume, None)

    def get_volume(self, master_volume) -> int:
        return round(self.get_volume_percentage() * master_volume)

    def get_volume_percentage(self) -> float:
        return self.interface.GetMasterVolume()

    def change_volume(self, change):
        new_volume = self.get_volume_percentage() + change
        if new_volume >= 0 and new_volume <= 1:
            self._set_volume(new_volume)

    def is_muted(self) -> bool:
        return self.interface.GetMute() == 1

    def set_muted(self, is_muted):
        self.interface.SetMute(1 if is_muted else 0, None)


class MasterAudioInterface(AudioInterface):
    def __init__(self):
        super().__init__(None)
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        self.interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.master_volume = cast(self.interface, POINTER(IAudioEndpointVolume))

    def _set_volume(self, volume):
        self.master_volume.SetMasterVolumeLevelScalar(volume, None)

    def get_volume(self) -> int:
        return round(self.get_volume_percentage() * 100)

    def get_volume_percentage(self) -> float:
        return self.master_volume.GetMasterVolumeLevelScalar()

    def is_muted(self):
        return self.master_volume.GetMute() == 1

    def toggle_mute(self):
        self.master_volume.SetMute(1 if not self.is_muted() else 0, None)
