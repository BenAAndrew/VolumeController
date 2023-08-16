import threading
import time
from comtypes import CoInitialize, CoUninitialize
from pycaw.pycaw import AudioUtilities
from app import Application

from manager import Manager

UPDATE_DELAY = 10 / 1000

manager = Manager()
app = Application()

def update():
    global manager
    sessions = [session for session in AudioUtilities.GetAllSessions() if session.Process]
    master_volume = manager.master_audio.get_volume()

    # New app(s)
    if len(sessions) > len(manager.apps):
        app_ids = [app.id for app in manager.apps]
        for session in sessions:
            if session.Process.pid not in app_ids:
                manager.add_app(session, master_volume)
                
    # Closed app(s)
    elif len(sessions) < len(manager.apps):
        session_ids = [session.Process.pid for session in sessions]
        apps_to_remove = [i for i in range(len(manager.apps)) if manager.apps[i].id not in session_ids]
        for i in apps_to_remove:
            manager.delete_app(i)

    # Update controller
    manager.update()

    # controller.update(master_audio, apps)

    # # Update apps
    # master_audio.update(master_volume, controller)
    # for i in range(len(apps)):
    #     app = apps[i]
    #     app.update(master_volume, controller)
    #     position_change = app.get_position_change()
    #     # Swap position
    #     if len(apps) > 1 and position_change != 0:
    #         other_index = i+position_change
    #         if other_index >= 0 and other_index < len(apps):
    #             apps[i].move(position_change, controller)
    #             apps[other_index].move(-position_change, controller)
    #             apps[i], apps[other_index] = apps[other_index], apps[i]
    #             app.reset_position_change()


def main():
    CoInitialize()
    while True:
        try:
            update()
            time.sleep(UPDATE_DELAY)
        except Exception as e:
            raise e
        finally:
            CoUninitialize()


thread = threading.Thread(target=main)
thread.start()
app.run()
