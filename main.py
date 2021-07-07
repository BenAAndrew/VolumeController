from tkinter import Tk

from utils import get_sessions, get_master_volume
from audio_application import ICON_PATH, AudioApplication, MasterAudioApplication
from controller import AudioController

UPDATE_DELAY = 10

window = Tk()
window.title("Audio Controller")
window.iconbitmap(ICON_PATH)
window.resizable(0, 0)

controller = AudioController()
master_audio_app = MasterAudioApplication(0, get_master_volume(), controller)
apps = []

def update():
    global apps

    # window.winfo_ismapped()
    master_volume = get_master_volume()
    sessions = get_sessions()

    # New app(s)
    if len(sessions) > len(apps):
        app_ids = [app.id for app in apps]
        for session in sessions:
            if session.Process.pid not in app_ids:
                apps.append(AudioApplication(len(apps)+1, session, master_volume, controller))
    # Closed app(s)
    elif len(sessions) < len(apps):
        session_ids = [session.Process.pid for session in sessions]
        for i in range(len(apps)):
            app = apps[i]
            if app.id not in session_ids:
                app.delete()
                apps.pop(i)

    # Update apps
    master_audio_app.update(master_volume, controller)
    for app in apps:
        app.update(master_volume, controller)

    window.after(UPDATE_DELAY, update)


def on_closing():
    controller.close()
    window.destroy()


update()
window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()
