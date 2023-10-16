import os
from typing import Union
from unittest import mock

from volume_controller.controller import AudioController, ControlEventType


class MockedSerial:
    data: Union[int, bytes]
    write_calls = []

    def __init__(self, data: Union[int, bytes]):
        self.data = data

    def read(self):
        return self.data.to_bytes(2, "big") if isinstance(self.data, int) else self.data

    def write(self, data):
        self.write_calls.append(data)


@mock.patch("volume_controller.controller.serial.Serial")
@mock.patch("volume_controller.controller.time.sleep")
def test_volume_down(sleep, Serial):
    Serial.return_value = MockedSerial(1)

    controller = AudioController()
    controller.connect()
    event = controller.poll()
    assert event.event_type == ControlEventType.VOLUME_DOWN
    assert event.app_index == 0


@mock.patch("volume_controller.controller.serial.Serial")
@mock.patch("volume_controller.controller.time.sleep")
def test_volume_up(sleep, Serial):
    Serial.return_value = MockedSerial(2)

    controller = AudioController()
    controller.connect()
    event = controller.poll()
    assert event.event_type == ControlEventType.VOLUME_UP
    assert event.app_index == 0


@mock.patch("volume_controller.controller.serial.Serial")
@mock.patch("volume_controller.controller.time.sleep")
def test_mute(sleep, Serial):
    Serial.return_value = MockedSerial(3)

    controller = AudioController()
    controller.connect()
    event = controller.poll()
    assert event.event_type == ControlEventType.TOGGLE_MUTE
    assert event.app_index == 0


@mock.patch("volume_controller.controller.serial.Serial")
@mock.patch("volume_controller.controller.time.sleep")
def test_different_app(sleep, Serial):
    Serial.return_value = MockedSerial(11)

    controller = AudioController()
    controller.connect()
    event = controller.poll()
    assert event.event_type == ControlEventType.VOLUME_DOWN
    assert event.app_index == 1


@mock.patch("volume_controller.controller.serial.Serial")
@mock.patch("volume_controller.controller.time.sleep")
def test_send_icon(sleep, Serial):
    mocked_serial = MockedSerial(b"d")
    Serial.return_value = mocked_serial

    controller = AudioController()
    controller.connect()
    position = 0
    total_colours = 32
    controller.send_icon(position, os.path.join("assets", "icon.png"))

    assert mocked_serial.write_calls[0] == b"i"
    assert [b for b in mocked_serial.write_calls[1]] == [position, total_colours]

    # Check colours
    for i in range(2, 2 + total_colours):
        call = [b for b in mocked_serial.write_calls[i]]
        assert len(call) == 3

    # Check pixels
    total_pixels = len(mocked_serial.write_calls) - (2 + total_colours)
    assert total_pixels == 60 * 60
    for i in range(2 + total_colours, len(mocked_serial.write_calls)):
        call = [b for b in mocked_serial.write_calls[i]]
        assert len(call) == 1
        assert call[0] >= 0 and call[0] < 32
