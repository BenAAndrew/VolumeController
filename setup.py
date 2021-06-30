from cx_Freeze import setup, Executable

shortcut_table = [
    (
        "DesktopShortcut",  # Shortcut
        "StartMenuFolder",  # Directory_
        "Volume Controller",  # Name
        "TARGETDIR",  # Component_
        "[TARGETDIR]main.exe",  # Target
        None,  # Arguments
        None,  # Description
        None,  # Hotkey
        None,  # Icon
        None,  # IconIndex
        None,  # ShowCmd
        "TARGETDIR",  # WkDir
    )
]

setup(
    name="Volume Controller",
    version="0.1",
    description="Utility for the physical volume controller",
    options={
        "build_exe": {"include_files": ["icon.ico"]},
        "bdist_msi": {"data": {"Shortcut": shortcut_table}, "summary_data": {"author": "Ben Andrew"}},
    },
    executables=[Executable("main.py", base="Win32GUI", icon="icon.ico")],
)
