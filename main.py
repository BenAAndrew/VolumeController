from tkinter import Tk
from pycaw.pycaw import AudioUtilities

from audio_application import ICON_PATH, AudioApplication, MasterAudioApplication
from controller import AudioController

UPDATE_DELAY = 10

window = Tk()
window.title("Audio Controller")
window.iconbitmap(ICON_PATH)
window.resizable(0, 0)

controller = AudioController()
master_audio = MasterAudioApplication(controller)
apps = []


def update():
    global apps

    # window.winfo_ismapped()
    master_volume = master_audio.get_volume()
    sessions = [session for session in AudioUtilities.GetAllSessions() if session.Process]

    # New app(s)
    if len(sessions) > len(apps):
        app_ids = [app.id for app in apps]
        for session in sessions:
            if session.Process.pid not in app_ids:
                apps.append(AudioApplication(len(apps)+1, session, master_volume, controller))
    # Closed app(s)
    elif len(sessions) < len(apps):
        session_ids = [session.Process.pid for session in sessions]
        apps_to_remove = [i for i in range(len(apps)) if apps[i].id not in session_ids]
        for i in apps_to_remove:
            apps[i].delete(controller)
            apps.pop(i)

    # Update controller
    controller.update(master_audio, apps)

    # Update apps
    master_audio.update(master_volume, controller)
    for i in range(len(apps)):
        app = apps[i]
        app.update(master_volume, controller)
        position_change = app.get_position_change()
        # Swap position
        if len(apps) > 1 and position_change != 0:
            other_index = i+position_change
            if other_index >= 0 and other_index < len(apps):
                apps[i].move(position_change, controller)
                apps[other_index].move(-position_change, controller)
                apps[i], apps[other_index] = apps[other_index], apps[i]
                app.reset_position_change()

    window.after(UPDATE_DELAY, update)


def on_closing():
    controller.close()
    window.destroy()


update()
window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()
