#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Constants for Safecast Tracker.
"""

import logging

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2017 Greg Albrecht'


LOG_LEVEL = logging.INFO
LOG_FORMAT = logging.Formatter(
    ('%(asctime)s %(levelname)s %(name)s.%(funcName)s:%(lineno)d '
     '- safecast_tracker - %(message)s'))

GPS_WARM_UP = 5
