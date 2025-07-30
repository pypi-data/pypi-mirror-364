# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Lima2 pipeline types, defining class name, frame and reduced data sources."""

from dataclasses import dataclass
from lima2.common.types import (
    FILL_FACTOR_DTYPE,
    PEAK_COUNTER_DTYPE,
    FrameSource,
    FrameType,
    ReducedDataSource,
    ScalarDataSource,
)


@dataclass
class Pipeline:
    class_name: str
    frame_sources: dict[str, FrameSource]
    """Available frame sources."""
    reduced_data_sources: dict[str, ReducedDataSource]
    """Available static reduced data sources."""


legacy = Pipeline(
    class_name="LimaProcessingLegacy",
    frame_sources={
        "input_frame": FrameSource(
            getter_name="getInputFrame",
            frame_type=FrameType.DENSE,
            saving_channel=None,
            label="input",
        ),
        "frame": FrameSource(
            getter_name="getFrame",
            frame_type=FrameType.DENSE,
            saving_channel="saving",
            label="processed",
        ),
    },
    reduced_data_sources={},
)

failing = Pipeline(
    class_name="LimaProcessingFailing",
    frame_sources={},
    reduced_data_sources={},
)

smx = Pipeline(
    class_name="LimaProcessingSmx",
    frame_sources={
        "frame": FrameSource(
            getter_name="getFrame",
            frame_type=FrameType.DENSE,
            saving_channel="saving_dense",
            label="input",
        ),
        "sparse_frame": FrameSource(
            getter_name="getSparseFrame",
            frame_type=FrameType.SMX_SPARSE,
            saving_channel="saving_sparse",
            label="sparse",
        ),
        "acc_corrected": FrameSource(
            getter_name="getAccCorrected",
            frame_type=FrameType.DENSE,
            saving_channel="saving_accumulation_corrected",
            label=None,
        ),
        "acc_peaks": FrameSource(
            getter_name="getAccPeaks",
            frame_type=FrameType.DENSE,
            saving_channel="saving_accumulation_peak",
            label=None,
        ),
    },
    reduced_data_sources={
        "peak_counter": ScalarDataSource(
            getter_name="popPeakCounters",
            src_dtype=PEAK_COUNTER_DTYPE,
            exposed_cols=["nb_peaks"],
            count=1,
        )
    },
)


xpcs = Pipeline(
    class_name="LimaProcessingXpcs",
    frame_sources={
        "input_frame": FrameSource(
            getter_name="getInputFrame",
            frame_type=FrameType.DENSE,
            saving_channel=None,
            label="input",
        ),
        "frame": FrameSource(
            getter_name="getFrame",
            frame_type=FrameType.DENSE,
            saving_channel="saving_dense",
            label="processed",
        ),
        "sparse_frame": FrameSource(
            getter_name="getSparseFrame",
            frame_type=FrameType.SPARSE,
            saving_channel="saving_sparse",
            label="sparse",
        ),
    },
    reduced_data_sources={
        "fill_factor": ScalarDataSource(
            getter_name="popFillFactors",
            src_dtype=FILL_FACTOR_DTYPE,
            exposed_cols=["fill_factor"],
            count=1,
        )
    },
)

by_name = {pipeline.class_name: pipeline for pipeline in (legacy, failing, smx, xpcs)}
