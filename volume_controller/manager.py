

import os
from typing import List, Optional
import psutil
from pycaw.pycaw import AudioUtilities, AudioSession

from volume_controller.audio_interface import AudioInterface, MasterAudioInterface
from volume_controller.controller import AudioController, ControlEvent, ControlEventType
from volume_controller.display_icon import DisplayIcon
from volume_controller.fetch_icon import get_icon


VOLUME_STEP = 0.02
MAX_SCREEN_ICONS = 4
ASSETS_FOLDER = "assets"


class AudioApp:
    id: int
    index: int
    name: str
    enabled: bool
    interface: AudioInterface
    display: Optional[DisplayIcon]

    def __init__(self, id, name, index, enabled, interface, display):
        self.id = id
        self.name = name
        self.index = index
        self.enabled = enabled
        self.interface = interface
        self.display = display

    def delete(self):
        if self.display:
            self.display.delete()


class Manager:
    apps: List[AudioApp] = []

    def __init__(self):
        self.controller = AudioController()
        self.master_audio = MasterAudioInterface()
        self.master_icon = DisplayIcon(
            os.path.join(ASSETS_FOLDER, "icon.png"),
            0,
            self.master_audio.get_volume(),
            self.master_audio.is_muted(),
            self.controller
        )

    def _add_app(self, session: AudioSession, master_volume: int):
        try:
            id = session.Process.pid
            name = session.Process.name().split(".")[0]
            path = session.Process.exe()
        except psutil.NoSuchProcess:
            return

        index = len(self.apps)+1
        enabled = index < MAX_SCREEN_ICONS
        
        if enabled:
            icon_path = get_icon(path, name)
            interface = AudioInterface(session)
            display = DisplayIcon(icon_path, index, interface.get_volume(master_volume), interface.is_muted(), self.controller)
        else:
            display = None

        app = AudioApp(id, name, index, enabled, interface, display)
        self.apps.append(app)

    def _delete_app(self, index):
        self.apps[index].delete()
        self.apps.pop(index)

    def _handle_controller_event(self, event: ControlEvent):
        index = event.app_index
        interface = self.master_audio if index == 0 else self.apps[index-1].interface
        if event.event_type == ControlEventType.VOLUME_UP or event.event_type == ControlEventType.VOLUME_DOWN:
            volume_change = VOLUME_STEP if event.event_type == ControlEventType.VOLUME_UP else -VOLUME_STEP
            interface.change_volume(volume_change)
        elif event.event_type == ControlEventType.TOGGLE_MUTE:
            interface.toggle_mute()

    def _handle_audio_change(self, display: DisplayIcon, volume: int, is_muted: bool):
        if not is_muted and volume != display.volume:
            display.send_volume(volume)
        elif is_muted != display.muted:
            if not is_muted:
                display.send_volume(volume)
                display.muted = False
            else:
                display.set_mute()

    def update(self):
        sessions = [session for session in AudioUtilities.GetAllSessions() if session.Process]
        master_volume = self.master_audio.get_volume()

        # New app
        if len(sessions) > len(self.apps):
            app_ids = [app.id for app in self.apps]
            for session in sessions:
                if session.Process.pid not in app_ids:
                    self._add_app(session, master_volume)
                    
        # Closed app
        elif len(sessions) < len(self.apps):
            session_ids = [session.Process.pid for session in sessions]
            apps_to_remove = [i for i in range(len(self.apps)) if self.apps[i].id not in session_ids]
            for i in apps_to_remove:
                self._delete_app(i)

        # Controller events
        event = self.controller.poll()
        if event:
            self._handle_controller_event(event)

        # Audio change events
        is_muted = self.master_audio.is_muted()
        self._handle_audio_change(self.master_icon, master_volume, is_muted)

        for app in self.apps:
            app_volume = app.interface.get_volume(master_volume)
            is_muted = app.interface.is_muted()
            self._handle_audio_change(app.display, app_volume, is_muted)
