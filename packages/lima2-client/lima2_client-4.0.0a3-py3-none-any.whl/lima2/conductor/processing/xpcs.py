# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""XPCS pipeline subclass."""

import logging


from lima2.common.pipelines import xpcs
from lima2.conductor.processing.pipeline import Pipeline

# Create a logger
logger = logging.getLogger(__name__)


class Xpcs(Pipeline):
    TANGO_CLASS = xpcs.class_name

    FRAME_SOURCES = xpcs.frame_sources
    """Available frame sources."""

    REDUCED_DATA_SOURCES = xpcs.reduced_data_sources
    """Available static reduced data sources."""
