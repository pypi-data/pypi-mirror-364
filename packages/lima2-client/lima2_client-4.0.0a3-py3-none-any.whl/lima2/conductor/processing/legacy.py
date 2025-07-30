# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Legacy pipeline subclass."""

import logging

from lima2.common.pipelines import legacy
from lima2.conductor.processing.pipeline import Pipeline

# Create a logger
logger = logging.getLogger(__name__)


class Legacy(Pipeline):
    TANGO_CLASS = legacy.class_name

    FRAME_SOURCES = legacy.frame_sources
    """Available frame sources."""

    REDUCED_DATA_SOURCES = legacy.reduced_data_sources
    """Available static reduced data sources."""
