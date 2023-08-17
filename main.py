import threading
from comtypes import CoInitialize, CoUninitialize

from volume_controller.app import Application, MenuOption
from volume_controller.manager import Manager

app = Application()


def main():
    manager = Manager(app)
    CoInitialize()
    try:
        while True:
            manager.update()
    except Exception as e:
        CoUninitialize()
        raise e


thread = threading.Thread(target=main)
thread.start()

app.run()
