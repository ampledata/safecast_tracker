#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Safecast Tracker Class Definitions"""

__author__ = 'Greg Albrecht W2GMD <gba@orionlabs.co>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2015 Orion Labs, Inc.'


import logging
import logging.handlers
import threading

import pygatt
import pygatt.util

import safecast_tracker.constants


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
    _logger.setLevel(safecast_tracker.constants.LOG_LEVEL)
    _console_handler = logging.StreamHandler()
    _console_handler.setLevel(safecast_tracker.constants.LOG_LEVEL)
    _console_handler.setFormatter(safecast_tracker.constants.LOG_FORMAT)
    _logger.addHandler(_console_handler)
    _logger.propagate = False

    def __init__(self, mac):
        threading.Thread.__init__(self)
        self.mac = mac
        self.str_buf = ''
        self.bgn = None
        self.bgn_props = {}
        [self.bgn_props.update({p: None}) for p in self.BGN_PROPERTIES]
        self._connect()

    def _connect(self):
        pygatt.util.reset_bluetooth_controller()
        self.bgn = pygatt.BluetoothLEDevice(self.mac)
        self.bgn.connect()
        self.bgn.char_write(32, bytearray([0x03, 0x00]))
        self.bgn.subscribe(self.SUB, self.store)

    def _disconnect(self):
        if self.bgn is not None:
            self.bgn.disconnect()
        pygatt.util.reset_bluetooth_controller()

    def store(self, x, y):
        str_y = str(y)
        if '$' in str_y:
            self.bgn_props.update(
                dict(zip(self.BGN_PROPERTIES, self.str_buf.split(','))))

            if self.bgn_props['altitude'] is not None:
                self.bgn_props['altitude'] = float(self.bgn_props['altitude'])
            if self.bgn_props['latitude'] is not None:
                self.bgn_props['latitude'] = float(self.bgn_props['latitude'])
            if self.bgn_props['longitude'] is not None:
                self.bgn_props['longitude'] = float(
                    self.bgn_props['longitude'])
            if self.bgn_props['rad_1_min'] is not None:
                self.bgn_props['rad_1_min'] = int(self.bgn_props['rad_1_min'])

            self.str_buf = str_y
        else:
            self.str_buf = ''.join([self.str_buf, str_y])

    def run(self):
        self.bgn.run()

    def stop(self):
        """
        Stop the thread at the next opportunity.
        """
        self._disconnect()
        return True
