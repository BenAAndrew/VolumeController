import os
from typing import Any, List, Optional, Tuple
import psutil
from volume_controller.app import Application

from volume_controller.audio_interface import AudioSession, AudioInterface, MasterAudioInterface
from volume_controller.controller import AudioController, ControlEvent, ControlEventType
from volume_controller.display_icon import DisplayIcon
from volume_controller.fetch_icon import fetch_icon
from volume_controller.utils import resource


VOLUME_STEP = 0.02
MAX_SCREEN_ICONS = 4
ASSETS_FOLDER = "assets"


class AudioApp:
    id: int
    index: Optional[int]
    name: str
    enabled: bool
    interface: AudioInterface
    display: DisplayIcon

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
    audio_apps: List[AudioApp]
    queued_display_task: Optional[Tuple[callable, Any]]

    def __init__(self, app: Application):
        self.app = app
        self.audio_apps = []
        self.queued_display_task = None
        self.controller = AudioController()
        self.master_audio = MasterAudioInterface()
        self.master_icon_image = resource(os.path.join(ASSETS_FOLDER, "icon.png"))
        self.master_icon = DisplayIcon(
            self.master_icon_image,
            self.master_audio.get_volume(),
            self.master_audio.is_muted(),
            self.controller,
        )
        self.master_icon.draw_on_screen(0)

    def _get_first_available_index(self):
        app_indexes = [app.index for app in self.audio_apps]
        for i in range(1, MAX_SCREEN_ICONS):
            if i not in app_indexes:
                return i

    def _add_app(self, session: AudioSession, master_volume: int):
        try:
            id = session.Process.pid
            name = session.Process.name().split(".")[0]
            path = session.Process.exe()
        except psutil.NoSuchProcess:
            return

        index = self._get_first_available_index()
        enabled = index is not None
        try:
            icon_path = fetch_icon(path, name)
        except:
            icon_path = self.master_icon_image
        interface = AudioInterface(session)
        volume = interface.get_volume(master_volume)
        is_muted = interface.is_muted()
        display = DisplayIcon(icon_path, volume, is_muted, self.controller)
        self.app.add_option(id, name, enabled, self.menu_action)
        if enabled:
            display.draw_on_screen(index)

        app = AudioApp(id, name, index, enabled, interface, display)
        self.audio_apps.append(app)

    def _delete_app(self, index):
        matching_app = self.audio_apps[index]
        self.audio_apps[index].delete()
        self.audio_apps.pop(index)
        self.app.remove_option(matching_app.id)

    def _handle_controller_event(self, event: ControlEvent):
        index = event.app_index
        interface = self.master_audio if index == 0 else self.audio_apps[index - 1].interface
        if event.event_type == ControlEventType.VOLUME_UP or event.event_type == ControlEventType.VOLUME_DOWN:
            volume_change = VOLUME_STEP if event.event_type == ControlEventType.VOLUME_UP else -VOLUME_STEP
            interface.change_volume(volume_change)
        elif event.event_type == ControlEventType.TOGGLE_MUTE:
            interface.toggle_mute()

    def _get_sessions(self):
        from pycaw.pycaw import AudioUtilities

        return AudioUtilities.GetAllSessions()

    def _handle_audio_change(self, display: DisplayIcon, volume: int, is_muted: bool):
        if not is_muted and (volume != display.volume or is_muted != display.muted):
            display.send_volume(volume)

        if is_muted != display.muted:
            if not is_muted:
                display.muted = False
            else:
                display.set_mute()

    def menu_action(self, id, enabled):
        matching_app = next((app for app in self.audio_apps if app.id == id), None)

        if enabled and not matching_app.enabled:
            index = self._get_first_available_index()
            if index:
                self.queued_display_task = (matching_app.display.draw_on_screen, index)
                matching_app.index = index
                matching_app.enabled = True
        elif not enabled and matching_app.enabled:
            self.queued_display_task = (matching_app.display.delete, None)
            matching_app.index = None
            matching_app.enabled = False

        return matching_app.enabled

    def update(self):
        sessions = [session for session in self._get_sessions() if session.Process]
        master_volume = self.master_audio.get_volume()

        # New app
        if len(sessions) > len(self.audio_apps):
            app_ids = [app.id for app in self.audio_apps]
            for session in sessions:
                if session.Process.pid not in app_ids:
                    self._add_app(session, master_volume)

        # Closed app
        elif len(sessions) < len(self.audio_apps):
            session_ids = [session.Process.pid for session in sessions]
            audio_apps_to_remove = [i for i in range(len(self.audio_apps)) if self.audio_apps[i].id not in session_ids]
            for i in audio_apps_to_remove:
                self._delete_app(i)

        # Menu action
        if self.queued_display_task:
            func, arg = self.queued_display_task
            if arg:
                func(arg)
            else:
                func()
            self.queued_display_task = None

        # Controller events
        event = self.controller.poll()
        if event:
            self._handle_controller_event(event)

        # Audio change events
        is_muted = self.master_audio.is_muted()
        self._handle_audio_change(self.master_icon, master_volume, is_muted)

        for app in self.audio_apps:
            app_volume = app.interface.get_volume(master_volume)
            is_muted = app.interface.is_muted()
            self._handle_audio_change(app.display, app_volume, is_muted)
