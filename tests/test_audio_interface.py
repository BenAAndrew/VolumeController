from unittest import mock

from volume_controller.audio_interface import AudioInterface


@mock.patch('volume_controller.audio_interface.AudioInterface.get_volume_percentage')
def test_get_volume(get_volume_percentage):
    get_volume_percentage.return_value = 0.5
    master_volume = 100

    interface = AudioInterface(None)
    assert interface.get_volume(master_volume) == 50


@mock.patch('volume_controller.audio_interface.AudioInterface.get_volume_percentage')
@mock.patch('volume_controller.audio_interface.AudioInterface._set_volume')
def test_change_volume(_set_volume, get_volume_percentage):
    get_volume_percentage.return_value = 0.5
    change = 0.05

    interface = AudioInterface(None)
    interface.change_volume(change)
    _set_volume.assert_called_once_with(0.55)
