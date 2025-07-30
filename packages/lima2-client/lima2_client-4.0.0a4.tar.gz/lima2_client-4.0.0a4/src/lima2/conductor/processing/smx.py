# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""SMX pipeline subclass."""

import logging
from typing import Any

from lima2.common.pipelines import smx
from lima2.conductor.processing.pipeline import Pipeline

logger = logging.getLogger(__name__)


class Smx(Pipeline):
    TANGO_CLASS = smx.class_name

    FRAME_SOURCES = smx.frame_sources
    """Available frame sources."""

    REDUCED_DATA_SOURCES = smx.reduced_data_sources
    """Available static reduced data sources."""

    @staticmethod
    def distribute_acq(
        cls: type[Pipeline],
        ctl_params: dict[str, Any],
        acq_params: list[dict[str, Any]],
        proc_params: list[dict[str, Any]],
    ) -> tuple[dict, list[dict], list[dict]]:
        """Initialize pipeline-specific parameters for distributed acquisition"""
        ctl_params, acq_params, proc_params = Pipeline.distribute_acq(
            cls, ctl_params, acq_params, proc_params
        )

        num_receivers = len(proc_params)

        def correct_acc_frames(proc, param):
            fai = proc["fai"]
            nb_frames = fai[param]
            if nb_frames % num_receivers != 0:
                raise ValueError(
                    f"FAI {param}={nb_frames} is not multiple of {num_receivers=}"
                )
            fai[param] //= num_receivers

        for i, proc in enumerate(proc_params):
            # Correct FAI accumulation parameters
            correct_acc_frames(proc, "acc_nb_frames_reset")
            correct_acc_frames(proc, "acc_nb_frames_xfer")

        return ctl_params, acq_params, proc_params
