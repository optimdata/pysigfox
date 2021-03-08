# -*- coding: utf-8 -*-
import datetime


def to_ms_timestamp(value):
    """
    Convert datetime to timestamp in milliseconds
    """
    if value and isinstance(value, datetime.datetime):
        value = to_timestamp(value) * 1000
    return value


def to_timestamp(value):
    """
    Convert datetime to timestamp
    """
    if value and isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            # naive UTC time
            value = value.replace(tzinfo=datetime.timezone.utc)
        value = value.timestamp()
    return value


def from_ms_timestamp(value):
    """
    Convert timestamp in milliseconds to datetime
    """
    if value and not isinstance(value, datetime.datetime):
        value = from_timestamp(value / 1000)
    return value


def from_timestamp(value):
    """
    Convert timestamp to datetime
    """
    if value and not isinstance(value, datetime.datetime):
        value = datetime.datetime.utcfromtimestamp(value)
    return value


def to_bytearray(value):
    """
    Convert hex to byte array
    """
    if value and isinstance(value, str):
        value = bytearray.fromhex(value)
    return value
