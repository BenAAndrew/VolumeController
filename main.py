import threading
from comtypes import CoInitialize, CoUninitialize

from volume_controller.app import Application
from volume_controller.manager import Manager

def main():
    manager = Manager()
    CoInitialize()
    try:
        while True:
            manager.update()
    except Exception as e:
        CoUninitialize()
        raise e

thread = threading.Thread(target=main)
thread.start()
app = Application()
app.run()
