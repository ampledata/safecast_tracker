#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Safecast Tracker Class Definitions"""

import logging
import logging.handlers
import threading

import pygatt

import safecast_tracker

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2017 Greg Albrecht'


class BGeigieNanoPoller(threading.Thread):

    """Threadable Object for polling a Safecast Nano."""

    BGN_PROPERTIES = [
        'stype',
        'device_id',
        'date',
        'rad_1_min',
        'rad_5_secs',
        'rad_total_count',
        'rad_valid',
        'latitude',
        'hemisphere',
        'longitude',
        'east_west',
        'altitude',
        'gps_valid',
        'hdop',
        'checksum'
    ]

    SUB = 'a1e8f5b1-696b-4e4c-87c6-69dfe0b0093b'

    _logger = logging.getLogger(__name__)
    _logger.setLevel(safecast_tracker.LOG_LEVEL)
    _console_handler = logging.StreamHandler()
    _console_handler.setLevel(safecast_tracker.LOG_LEVEL)
    _console_handler.setFormatter(safecast_tracker.LOG_FORMAT)
    _logger.addHandler(_console_handler)
    _logger.propagate = False

    def __init__(self, mac):
        threading.Thread.__init__(self)
        self.mac = mac
        self.str_buffer = ''
        self.ble_adapter = None
        self.ble_device = None
        self.bgn_props = {}
        _ = [self.bgn_props.update({p: None}) for p in self.BGN_PROPERTIES]
        self._connect()

    def store(self, handle, handle_value):
        """
        Stores handle value in string buffer.

        :param handle:
        :param handle_value: Value from handle.
        """
        _ = handle
        handle_str = str(handle_value)

        if '$' in handle_str:
            self.bgn_props.update(
                dict(zip(self.BGN_PROPERTIES, self.str_buffer.split(','))))

            if self.bgn_props['altitude'] is not None:
                self.bgn_props['altitude'] = float(self.bgn_props['altitude'])

            if self.bgn_props['latitude'] is not None:
                self.bgn_props['latitude'] = float(self.bgn_props['latitude'])

            if self.bgn_props['longitude'] is not None:
                self.bgn_props['longitude'] = float(
                    self.bgn_props['longitude'])

            if self.bgn_props['rad_1_min'] is not None:
                self.bgn_props['rad_1_min'] = int(self.bgn_props['rad_1_min'])

            self.str_buffer = handle_str
        else:
            self.str_buffer = ''.join([self.str_buffer, handle_str])

    def run(self):
        self.ble_adapter = pygatt.GATTToolBackend()
        try:
            self.ble_adapter.start()
            self.ble_device = self.ble_adapter.connect(self.mac)
            self.ble_device.char_write_handle(32, bytearray([0x03, 0x00]))
            self.ble_device.subscribe(self.SUB, self.store)
        finally:
            self.ble_adapter.stop()

    def stop(self):
        """
        Stop the thread at the next opportunity.
        """
        if self.ble_adapter is not None:
            self.ble_adapter.stop()
