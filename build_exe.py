import os
import shutil
import PyInstaller.__main__


if __name__ == "__main__":
    if os.path.isdir("dist"):
        shutil.rmtree("dist")
    icon_path = os.path.join("assets", "icon.ico")
    assert os.path.isfile(icon_path)
    PyInstaller.__main__.run(
        ["main.py", "--onefile", "--clean", f"--icon={icon_path}", "--add-data=assets/;assets/",]
    )
    shutil.rmtree("build")
