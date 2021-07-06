from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
master_volume = cast(interface, POINTER(IAudioEndpointVolume))

def get_master_volume():
    return master_volume.GetMasterVolumeLevelScalar()


def get_sessions():
    return [session for session in AudioUtilities.GetAllSessions() if session.Process]
