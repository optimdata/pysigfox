# -*- coding: utf-8 -*-
import datetime
import re
import os
import sys

import pytest
import requests_mock

BASE_DIRECTORY = os.path.join(os.path.dirname(__file__), "..")  # NOQA
sys.path.insert(0, BASE_DIRECTORY)  # NOQA

from pysigfox import (
    Sigfox,
    SigfoxTooManyRequestsError,
    SigfoxBadStatusError,
    from_ms_timestamp,
    to_ms_timestamp,
    to_bytearray,
)

DEVICES = {
    "data": [
        {
            "id": "device_1",
            "name": "device_1",
            "lastCom": 1_559_802_207_000,
            "state": 0,
            "comState": 5,
            "deviceType": {"id": "1"},
            "group": {"id": "1"},
            "lqi": 4,
        }
    ],
    "paging": {},
}

DEVICE_MESSAGES = {
    "data": [
        {
            "device": {"id": "device_1"},
            "time": 1_613_984_321_000,
            "data": "010ea00cc764",
            "lqi": 2,
        },
        {
            "device": {"id": "device_1"},
            "time": 1_613_897_925_000,
            "data": "010e320ca664",
            "lqi": 2,
        },
    ],
    "paging": {},
}


# sigfox API mocker and pollux mocker
class SigfoxMocker(requests_mock.mock):
    def __init__(self, messages_status_code=200, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raise_error = messages_status_code
        self.call_nb = 0

        def device_messages(request, context):
            if self.call_nb == 0:
                self.call_nb += 1
                results = DEVICE_MESSAGES.copy()
                results["paging"] = {"next": request.url + "?page=2"}
                return results
            return DEVICE_MESSAGES

        # devices
        self.get(
            "https://api.sigfox.com/v2/devices",
            json=DEVICES,
            status_code=messages_status_code,
        )

        # device messages
        message_matcher = re.compile(
            r"^(https://api\.sigfox\.com/v2/devices/)(.*)(/messages)(.*)$"
        )
        self.get(
            message_matcher, json=device_messages, status_code=messages_status_code
        )

        # device
        message_matcher = re.compile(r"^(https://api\.sigfox\.com/v2/devices/)(\w+)$")
        self.get(message_matcher, json={}, status_code=messages_status_code)


def test_sigfox():
    client = Sigfox(username="test", password="test")
    print(client)
    with SigfoxMocker():
        assert len(client.devices(list_all=True)) == 1
        assert len(client.device_messages("device_1", list_all=True)) == 4
        assert client.device("device_1") == {}
    with SigfoxMocker():
        assert len(client.device_messages("device_1")) == 2

    with SigfoxMocker(messages_status_code=429):
        with pytest.raises(SigfoxTooManyRequestsError):
            client.devices()

    with SigfoxMocker(messages_status_code=404):
        with pytest.raises(SigfoxBadStatusError):
            client.devices()

    with requests_mock.mock() as mock:
        mock.get(
            "https://api.sigfox.com/v2/devices/device_1/messages",
            json={
                "data": [],
                "paging": {
                    "next": "https://api.sigfox.com/v2/devices/device_1/messages?page=2"
                },
            },
        )
        client.request("GET", "devices/device_1/messages")

    with requests_mock.mock() as mock:
        mock.get(
            "https://api.sigfox.com/v2/devices/device_1/messages",
            json={
                "data": [],
                "paging": {
                    "next": "https://api.sigfox.com/v2/devices/device_1/messages?"
                },
            },
        )
        client.request("GET", "devices/device_1/messages")


def test_utils():
    timestamp = 1_613_984_321_000
    dt = from_ms_timestamp(timestamp)
    my_dt = datetime.datetime(year=2021, month=2, day=22, hour=8, minute=58, second=41)
    assert dt == my_dt
    assert str(to_ms_timestamp(my_dt)) == str(timestamp)

    dt = from_ms_timestamp(timestamp)
    dt = dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=4)))
    timestamp = to_ms_timestamp(dt)

    my_dt = datetime.datetime(
        year=2021,
        month=2,
        day=22,
        hour=8,
        minute=58,
        second=41,
        tzinfo=datetime.timezone(datetime.timedelta(hours=4)),
    )
    assert dt == my_dt
    assert str(to_ms_timestamp(my_dt)) == str(timestamp)

    value = "010ea00cc764"
    assert to_bytearray(value).hex() == value

    assert to_ms_timestamp(None) is None
    assert from_ms_timestamp(None) is None
    assert to_bytearray(None) is None
