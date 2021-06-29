from tkinter import Tk, Label
from tkinter.ttk import Progressbar
from PIL import Image, ImageTk

from utils import get_apps, get_master_volume

UPDATE_DELAY = 10

window = Tk()
window.title("Audio Controller")
window.iconbitmap("icon.ico")
rows = []


class AppRow:
    def __init__(self, index, image_path, volume):
        img = ImageTk.PhotoImage(Image.open(image_path).resize((32, 32), Image.ANTIALIAS))
        icon = Label(image=img)
        icon.image = img
        icon.grid(row=index, column=0, padx=5, pady=5)
        self.vol_bar = Progressbar(length=200, value=volume * 100, mode="determinate")
        self.vol_bar.grid(row=index, column=1, padx=5, pady=5)
        self.vol_label = Label(text="{:.2f}".format(volume))
        self.vol_label.grid(row=index, column=2, padx=5, pady=5)

    def update(self, volume):
        self.vol_bar["value"] = volume * 100
        self.vol_label["text"] = "{:.2f}".format(volume)


def redraw_apps(apps):
    global rows
    rows = []
    master_volume = get_master_volume()
    rows.append(AppRow(0, "icon.ico", int(master_volume * 100) / 100))

    for i in range(len(apps)):
        rows.append(AppRow(i + 1, apps[i].icon, int(apps[i].get_volume() * master_volume * 100) / 100))


def update_volumes(apps):
    global rows
    master_volume = get_master_volume()
    rows[0].update(int(master_volume * 100) / 100)

    for i in range(len(apps)):
        rows[i + 1].update(int(apps[i].get_volume() * master_volume * 100) / 100)


def update():
    global rows
    apps = get_apps()

    # Only redraw all rows if an app open/closes, otherwise just update volumes
    if len(apps) != len(rows) - 1:
        redraw_apps(apps)
    else:
        update_volumes(apps)

    window.after(UPDATE_DELAY, update)


window.after(UPDATE_DELAY, update)
window.mainloop()
