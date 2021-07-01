from tkinter import Tk, Label
from tkinter.ttk import Progressbar
from PIL.ImageTk import PhotoImage

from utils import get_apps, get_master_volume
from audio_application import ICON, ICON_PATH

UPDATE_DELAY = 10

window = Tk()
window.title("Audio Controller")
window.iconbitmap(ICON_PATH)
window.resizable(0, 0)
rows = []


class AppRow:
    def __init__(self, index, image, volume):
        img = PhotoImage(image)
        icon = Label(image=img)
        icon.image = img
        icon.grid(row=index, column=0, padx=5, pady=5)
        self.vol_bar = Progressbar(length=200, value=volume, mode="determinate")
        self.vol_bar.grid(row=index, column=1, padx=5, pady=5)
        self.vol_label = Label(text=volume)
        self.vol_label.grid(row=index, column=2, padx=5, pady=5)

    def update(self, volume):
        self.vol_bar["value"] = volume
        self.vol_label["text"] = volume


def redraw_apps(apps):
    global rows
    rows = []
    master_volume = get_master_volume()
    rows.append(AppRow(0, ICON, round(master_volume * 100)))

    for i in range(len(apps)):
        rows.append(AppRow(i + 1, apps[i].icon, round(apps[i].get_volume() * master_volume * 100)))


def update_volumes(apps):
    global rows
    master_volume = get_master_volume()
    rows[0].update(round(master_volume * 100))

    for i in range(len(apps)):
        rows[i + 1].update(round(apps[i].get_volume() * master_volume * 100))


def update():
    global rows

    # Check if app is minimised
    if window.winfo_ismapped():
        apps = get_apps()

        # Only redraw all rows if an app open/closes, otherwise just update volumes
        if len(apps) != len(rows) - 1:
            redraw_apps(apps)
        else:
            update_volumes(apps)

    window.after(UPDATE_DELAY, update)


update()
window.mainloop()
