import threading
import time
from comtypes import CoInitialize, CoUninitialize

from app import Application
from manager import Manager

UPDATE_DELAY = 10 / 1000

def main():
    manager = Manager()
    CoInitialize()
    while True:
        try:
            manager.update()
            time.sleep(UPDATE_DELAY)
        except Exception as e:
            raise e
        finally:
            CoUninitialize()

thread = threading.Thread(target=main)
thread.start()
app = Application()
app.run()
