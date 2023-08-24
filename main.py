import threading
from comtypes import CoInitialize, CoUninitialize

from volume_controller.app import Application
from volume_controller.manager import Manager

thread = None
stop_thread = False


def close():
    global thread, stop_thread
    stop_thread = True
    thread.join()


def main(app):
    CoInitialize()
    manager = Manager(app)
    try:
        while not stop_thread:
            manager.update()
    except Exception as e:
        CoUninitialize()
        raise e


app = Application(on_close=close)
thread = threading.Thread(target=main, args=(app,))
thread.start()
app.run()
