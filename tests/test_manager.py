from dataclasses import dataclass
from typing import List, Optional
from unittest import mock
from volume_controller.app import MenuOption
from volume_controller.controller import ControlEvent, ControlEventType

from volume_controller.manager import VOLUME_STEP, AudioApp, Manager


class MockedApp:
    options: List[MenuOption] = []

    def add_option(self, id, name, enabled, callback):
        self.options.append(MenuOption(id=id, enabled=enabled, callback=callback))


@dataclass
class MockedAudioController:
    event: Optional[ControlEvent]

    def poll(self):
        return self.event
    
    def delete_app(self):
        pass

    def send_volume(self, volume):
        pass


@dataclass
class MockedAudioInterface:
    muted: bool
    volume: int

    def is_muted(self):
        return self.muted
    
    def get_volume(self, master_volume):
        return self.volume


class MockedMasterAudioInterface(MockedAudioInterface):
    muted: bool
    volume: int

    def is_muted(self):
        return self.muted
    
    def get_volume(self):
        return self.volume


@dataclass
class MockedDisplayIcon:
    index: int
    muted: bool
    volume: int
    deleted: bool = False

    def draw_on_screen(self, index):
        pass

    def delete(self):
        self.deleted = True

    def set_mute(self):
        self.muted = True

    def send_volume(self, volume):
        self.volume = volume


@dataclass
class MockedProcess:
    pid: int
    process_name: str

    def name(self):
        return self.process_name
    
    def exe(self):
        return "path"


@dataclass
class MockedSession:
    Process: MockedProcess


@dataclass
class MockedAudioApp:
    id: int
    index: Optional[int]
    enabled: bool
    display: MockedDisplayIcon


@mock.patch('volume_controller.manager.AudioController')
@mock.patch('volume_controller.manager.MasterAudioInterface')
@mock.patch('volume_controller.manager.DisplayIcon.draw_on_screen')
def test_initialize_manager(draw_on_screen, MasterAudioInterface, AudioController):
    Manager(MockedApp())
    draw_on_screen.assert_called_once_with(0)


@mock.patch('volume_controller.manager.AudioController')
@mock.patch('volume_controller.manager.MasterAudioInterface')
@mock.patch('volume_controller.manager.AudioInterface')
@mock.patch('volume_controller.manager.DisplayIcon.draw_on_screen')
@mock.patch('volume_controller.manager.AudioUtilities.GetAllSessions')
@mock.patch('volume_controller.manager.fetch_icon')
def test_add_app(fetch_icon, GetAllSessions, draw_on_screen, AudioInterface, MasterAudioInterface, AudioController):
    mocked_session = MockedSession(MockedProcess(pid=1, process_name="app"))
    GetAllSessions.return_value = [mocked_session]
    AudioController.return_value = MockedAudioController(None)

    mocked_app = MockedApp()
    manager = Manager(mocked_app)
    manager.update()

    fetch_icon.assert_called_once_with("path", "app")
    AudioInterface.assert_called_once_with(mocked_session)
    draw_on_screen.assert_called_with(1)
    assert len(mocked_app.options) == 1
    assert mocked_app.options[0].id == 1
    assert mocked_app.options[0].enabled == True
    assert len(manager.audio_apps) == 1
    assert manager.audio_apps[0].id == 1
    assert manager.audio_apps[0].name == "app"
    assert manager.audio_apps[0].index == 1
    assert manager.audio_apps[0].enabled == True


@mock.patch('volume_controller.manager.AudioController')
@mock.patch('volume_controller.manager.MasterAudioInterface')
@mock.patch('volume_controller.manager.AudioInterface')
@mock.patch('volume_controller.manager.DisplayIcon.draw_on_screen')
@mock.patch('volume_controller.manager.AudioUtilities.GetAllSessions')
@mock.patch('volume_controller.manager.fetch_icon')
def test_add_app_without_render(fetch_icon, GetAllSessions, draw_on_screen, AudioInterface, MasterAudioInterface, AudioController):
    mocked_sessions = [MockedSession(MockedProcess(pid=i, process_name=f"{i}")) for i in range(1,5)]
    session = mocked_sessions[3]
    GetAllSessions.return_value = mocked_sessions
    AudioController.return_value = MockedAudioController(None)

    mocked_app = MockedApp()
    manager = Manager(mocked_app)
    manager.update()

    assert len(manager.audio_apps) == 4
    assert len(mocked_app.options) == 4
    AudioInterface.assert_called_with(session)
    assert mock.call(4) not in draw_on_screen.mock_calls
    assert not manager.audio_apps[3].enabled
    assert manager.audio_apps[3].index is None


@mock.patch('volume_controller.manager.AudioController')
@mock.patch('volume_controller.manager.MasterAudioInterface')
@mock.patch('volume_controller.manager.AudioInterface')
@mock.patch('volume_controller.manager.DisplayIcon')
@mock.patch('volume_controller.manager.AudioUtilities.GetAllSessions')
@mock.patch('volume_controller.manager.fetch_icon')
def test_remove_app(fetch_icon, GetAllSessions, DisplayIcon, AudioInterface, MasterAudioInterface, AudioController):
    mocked_display_icon = MockedDisplayIcon(1, False, 50)
    DisplayIcon.return_value = mocked_display_icon
    AudioController.return_value = MockedAudioController(None)

    mocked_session = MockedSession(MockedProcess(pid=1, process_name="app"))
    mocked_app = MockedApp()
    manager = Manager(mocked_app)

    manager._add_app(mocked_session, 100)
    assert len(manager.audio_apps) == 1

    GetAllSessions.return_value = []
    manager.update()
    assert len(manager.audio_apps) == 0
    assert mocked_display_icon.deleted


@mock.patch('volume_controller.manager.AudioController')
@mock.patch('volume_controller.manager.MasterAudioInterface')
@mock.patch('volume_controller.manager.AudioInterface')
@mock.patch('volume_controller.manager.DisplayIcon')
@mock.patch('volume_controller.manager.AudioUtilities.GetAllSessions')
@mock.patch('volume_controller.manager.fetch_icon')
def test_handle_control_event_master_volume(fetch_icon, GetAllSessions, DisplayIcon, AudioInterface, MasterAudioInterface, AudioController):
    event = ControlEvent(ControlEventType.VOLUME_UP, 0)
    AudioController.return_value = MockedAudioController(event)

    mocked_app = MockedApp()
    manager = Manager(mocked_app)
    manager.update()

    manager.master_audio.change_volume.assert_called_with(VOLUME_STEP)


@mock.patch('volume_controller.manager.AudioController')
@mock.patch('volume_controller.manager.MasterAudioInterface')
@mock.patch('volume_controller.manager.AudioInterface')
@mock.patch('volume_controller.manager.DisplayIcon')
@mock.patch('volume_controller.manager.AudioUtilities.GetAllSessions')
@mock.patch('volume_controller.manager.fetch_icon')
def test_handle_control_event_volume(fetch_icon, GetAllSessions, DisplayIcon, AudioInterface, MasterAudioInterface, AudioController):
    mocked_session = MockedSession(MockedProcess(pid=1, process_name="app"))
    GetAllSessions.return_value = [mocked_session]
    event = ControlEvent(ControlEventType.VOLUME_DOWN, 1)
    AudioController.return_value = MockedAudioController(event)

    mocked_app = MockedApp()
    manager = Manager(mocked_app)
    manager.update()

    assert len(manager.audio_apps) == 1
    manager.audio_apps[0].interface.change_volume.assert_called_with(-VOLUME_STEP)


@mock.patch('volume_controller.manager.AudioController')
@mock.patch('volume_controller.manager.MasterAudioInterface')
@mock.patch('volume_controller.manager.AudioInterface')
@mock.patch('volume_controller.manager.DisplayIcon')
@mock.patch('volume_controller.manager.AudioUtilities.GetAllSessions')
@mock.patch('volume_controller.manager.fetch_icon')
def test_handle_control_event_toggle_mute(fetch_icon, GetAllSessions, DisplayIcon, AudioInterface, MasterAudioInterface, AudioController):
    event = ControlEvent(ControlEventType.TOGGLE_MUTE, 0)
    AudioController.return_value = MockedAudioController(event)

    mocked_app = MockedApp()
    manager = Manager(mocked_app)
    manager.update()

    manager.master_audio.toggle_mute.assert_called()


@mock.patch('volume_controller.manager.AudioController')
@mock.patch('volume_controller.manager.MasterAudioInterface')
@mock.patch('volume_controller.manager.AudioInterface')
@mock.patch('volume_controller.manager.DisplayIcon')
@mock.patch('volume_controller.manager.AudioUtilities.GetAllSessions')
@mock.patch('volume_controller.manager.fetch_icon')
def test_handle_audio_change_volume(fetch_icon, GetAllSessions, DisplayIcon, AudioInterface, MasterAudioInterface, AudioController):
    MasterAudioInterface.return_value = MockedMasterAudioInterface(False, 10)
    AudioController.return_value = MockedAudioController(None)

    mocked_app = MockedApp()
    manager = Manager(mocked_app)
    manager.master_audio = MockedMasterAudioInterface(False, 20)
    manager.update()

    manager.master_icon.send_volume.assert_called_with(20)


@mock.patch('volume_controller.manager.AudioController')
@mock.patch('volume_controller.manager.MasterAudioInterface')
@mock.patch('volume_controller.manager.AudioInterface')
@mock.patch('volume_controller.manager.DisplayIcon')
@mock.patch('volume_controller.manager.AudioUtilities.GetAllSessions')
@mock.patch('volume_controller.manager.fetch_icon')
def test_handle_audio_change_mute(fetch_icon, GetAllSessions, DisplayIcon, AudioInterface, MasterAudioInterface, AudioController):
    MasterAudioInterface.return_value = MockedMasterAudioInterface(False, 10)
    AudioController.return_value = MockedAudioController(None)

    mocked_app = MockedApp()
    manager = Manager(mocked_app)
    manager.master_audio = MockedMasterAudioInterface(True, 10)
    manager.update()

    manager.master_icon.set_mute.assert_called_once()


@mock.patch('volume_controller.manager.AudioController')
@mock.patch('volume_controller.manager.MasterAudioInterface')
@mock.patch('volume_controller.manager.AudioInterface')
@mock.patch('volume_controller.manager.DisplayIcon')
@mock.patch('volume_controller.manager.AudioUtilities.GetAllSessions')
@mock.patch('volume_controller.manager.fetch_icon')
def test_handle_audio_change_unmute(fetch_icon, GetAllSessions, DisplayIcon, AudioInterface, MasterAudioInterface, AudioController):
    MasterAudioInterface.return_value = MockedMasterAudioInterface(True, 10)
    AudioController.return_value = MockedAudioController(None)
    DisplayIcon.return_value = MockedDisplayIcon(1, True, 0)

    mocked_app = MockedApp()
    manager = Manager(mocked_app)
    manager.master_audio = MockedMasterAudioInterface(False, 10)
    manager.update()

    assert manager.master_icon.volume == 10
    assert not manager.master_icon.muted


@mock.patch('volume_controller.manager.AudioController')
@mock.patch('volume_controller.manager.MasterAudioInterface')
@mock.patch('volume_controller.manager.AudioInterface')
@mock.patch('volume_controller.manager.DisplayIcon')
@mock.patch('volume_controller.manager.AudioUtilities.GetAllSessions')
@mock.patch('volume_controller.manager.fetch_icon')
def test_handle_audio_change_apps(fetch_icon, GetAllSessions, DisplayIcon, AudioInterface, MasterAudioInterface, AudioController):
    GetAllSessions.return_value = [MockedSession(MockedProcess(pid=1, process_name="app"))]
    AudioInterface.return_value = MockedAudioInterface(False, 10)
    AudioController.return_value = MockedAudioController(None)

    mocked_app = MockedApp()
    manager = Manager(mocked_app)
    manager.update()
    
    manager.audio_apps[0].interface = MockedAudioInterface(False, 20)
    manager.update()
    
    manager.audio_apps[0].display.send_volume.assert_called_with(20)


@mock.patch('volume_controller.manager.AudioController')
def test_menu_action_enable_app(AudioController):
    mocked_app = MockedApp()
    manager = Manager(mocked_app)
    manager.audio_apps = [MockedAudioApp(1, None, False, MockedDisplayIcon(1, False, 100, False))]
    manager.menu_action(1, True)

    assert manager.queued_display_task == (manager.audio_apps[0].display.draw_on_screen, 1)


@mock.patch('volume_controller.manager.AudioController')
def test_menu_action_delete_app(AudioController):
    mocked_app = MockedApp()
    manager = Manager(mocked_app)
    manager.audio_apps = [MockedAudioApp(1, None, True, MockedDisplayIcon(1, False, 100, False))]
    manager.menu_action(1, False)

    assert manager.queued_display_task == (manager.audio_apps[0].display.delete, None)
    assert manager.audio_apps[0].index is None
