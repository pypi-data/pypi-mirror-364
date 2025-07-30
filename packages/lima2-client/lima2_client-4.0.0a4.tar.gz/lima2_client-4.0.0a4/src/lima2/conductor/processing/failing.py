# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Failing pipeline subclass."""

import logging

from lima2.common.pipelines import failing
from lima2.conductor.processing.pipeline import Pipeline

logger = logging.getLogger(__name__)


class Failing(Pipeline):
    TANGO_CLASS = failing.class_name

    FRAME_SOURCES = failing.frame_sources
    """Available frame sources."""

    REDUCED_DATA_SOURCES = failing.reduced_data_sources
    """Available static reduced data sources."""
