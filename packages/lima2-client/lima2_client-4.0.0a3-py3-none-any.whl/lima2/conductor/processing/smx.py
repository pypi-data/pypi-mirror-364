# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""SMX pipeline subclass."""

import logging

from lima2.common.pipelines import smx
from lima2.conductor.processing.pipeline import Pipeline

logger = logging.getLogger(__name__)


class Smx(Pipeline):
    TANGO_CLASS = smx.class_name

    FRAME_SOURCES = smx.frame_sources
    """Available frame sources."""

    REDUCED_DATA_SOURCES = smx.reduced_data_sources
    """Available static reduced data sources."""
