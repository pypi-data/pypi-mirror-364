# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor HTTP services wrapped into functions."""

import logging
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Iterator, cast
from uuid import UUID

import numpy as np
import numpy.typing as npt
import tango as tg

from lima2.client.exceptions import ConductorClientError, ConductorConnectionError
from lima2.client.session import ConductorSession
from lima2.common import pipelines, types
from lima2.common.devencoded.dense_frame import Frame
from lima2.common.devencoded.smx_sparse_frame import SmxSparseFrame
from lima2.common.devencoded.sparse_frame import SparseFrame
from lima2.common.progress_counter import ProgressCounter, SingleCounter
from lima2.common.state import RunState, State
from lima2.common.types import FrameInfo, ReducedDataInfo

logger = logging.getLogger(__name__)


class Acquisition:
    """Conductor /acquisition service requests."""

    def __init__(self, session: ConductorSession) -> None:
        self.session = session
        """The conductor session."""

    def prepare(
        self,
        control: dict[str, Any],
        receiver: dict[str, Any],
        processing: dict[str, Any],
    ) -> UUID:
        """Prepare for a new acquisition given control, receiver and processing params."""
        json = self.session.post(
            "/acquisition/prepare",
            json={
                "control": control,
                "receiver": receiver,
                "processing": processing,
            },
        ).json()
        return UUID(json["uuid"])

    def start(self) -> RunState:
        """Start the currently prepared acquisition."""
        return RunState(self.session.post("/acquisition/start").json())

    def stop(self) -> RunState:
        """Stop the currently running acquisition."""
        return RunState(self.session.post("/acquisition/stop").json())

    def trigger(self) -> RunState:
        """Trigger the detector in the currently running acquisition.

        Only useful in software-triggered acquisitions.
        """
        return RunState(self.session.post("/acquisition/trigger").json())

    def reset(self) -> RunState:
        """Call reset() on the Lima2 devices to attempt recovery from a FAULT state."""
        return RunState(self.session.post("/acquisition/reset").json())

    def state(self) -> RunState:
        """Get the acquisition system's current RunState."""
        return RunState(self.session.get("/acquisition/state").json())

    def default_params(self) -> tuple[dict[str, Any], dict[str, Any]]:
        """Get default acquisition parameters.

        Returns a tuple (control params, receiver params).
        """
        params = self.session.get("/acquisition/default_params").json()
        return (
            cast(dict[str, Any], params["control"]),
            cast(dict[str, Any], params["receiver"]),
        )

    def params_schema(self) -> dict[str, Any]:
        """Get the schema for acquisition parameters."""
        return cast(
            dict[str, Any], self.session.get("/acquisition/params_schema").json()
        )

    def nb_frames_acquired(self) -> SingleCounter:
        """Get the number of frames acquired in the current acquisition."""
        json_dict = self.session.get("/acquisition/nb_frames_acquired").json()
        return SingleCounter.fromdict(json_dict)

    def nb_frames_xferred(self) -> ProgressCounter:
        """Get the number of frames transferred in the current acquisition."""
        json_dict = self.session.get("/acquisition/nb_frames_xferred").json()
        return ProgressCounter.fromdict(json_dict)

    def errors(self) -> list[str]:
        """Get all error messages for the current acquisition.

        Can be used in case of failure during the acquisition to report
        the causes.
        """
        return cast(list[str], self.session.get("/acquisition/errors").json())


class Detector:
    """Conductor /detector service requests."""

    def __init__(self, session: ConductorSession) -> None:
        self.session = session
        """The conductor session."""

    def info(self) -> dict[str, Any]:
        """Retrieve the detector info dictionary."""
        return cast(dict[str, Any], self.session.get("/detector/info").json())

    def status(self) -> dict[str, Any]:
        """Retrieve the detector status dictionary."""
        return cast(dict[str, Any], self.session.get("/detector/status").json())

    def capabilities(self) -> dict[str, Any]:
        """Retrieve the detector capabilities dictionary."""
        return cast(dict[str, Any], self.session.get("/detector/capabilities").json())

    def command(self, name: str, arg: Any = None) -> Any:
        """Execute a command on the Lima2 control device."""
        return self.session.post(
            "/detector/command", json={"name": name, "arg": arg}
        ).json()

    def write_attribute(self, name: str, value: Any) -> None:
        """Set the value of an attribute on the Lima2 control device."""
        self.session.post(f"/detector/attribute/{name}", json=value)

    def read_attribute(self, name: str) -> Any:
        """Get the value of an attribute from the Lima2 control device."""
        return self.session.get(f"/detector/attribute/{name}").json()


class Pipeline:
    """Conductor /pipeline service requests."""

    def __init__(self, session: ConductorSession) -> None:
        self.session = session
        """The conductor session."""

    def classes(self) -> list[str]:
        """Enumerate pipeline classes."""
        return cast(list[str], self.session.get("/pipeline/class").json())

    def default_params(self, processing_name: str) -> dict[str, Any]:
        """Fetch default processing params for a pipeline type."""
        json = self.session.get(f"/pipeline/class/{processing_name}").json()
        return cast(dict[str, Any], json["default_params"])

    def params_schema(self, processing_name: str) -> dict[str, Any]:
        """Fetch the JSON schema for a pipeline type."""
        json = self.session.get(f"/pipeline/class/{processing_name}/schema").json()
        return cast(dict[str, Any], json)

    def uuids(self) -> list[UUID]:
        """Get UUIDs for each alive pipeline."""
        return [UUID(uuid_str) for uuid_str in self.session.get("/pipeline/").json()]

    def current_pipeline(self) -> UUID:
        """Get the UUID of the current pipeline."""
        res = self.session.get("/pipeline/current")
        return UUID(res.json()["uuid"])

    def pipeline(self, uuid: UUID | str) -> dict[str, Any]:
        """Get a generic info dictionary for a given pipeline."""
        return cast(dict[str, Any], self.session.get(f"/pipeline/{str(uuid)}").json())

    def errors(self, uuid: str = "current") -> list[str]:
        """Get processing error messages, if any."""
        return cast(list[str], self.session.get(f"/pipeline/{uuid}/errors").json())

    def progress_counters(self, uuid: str = "current") -> dict[str, ProgressCounter]:
        """Get current progress counters for a given pipeline."""
        json = self.session.get(f"/pipeline/{uuid}/progress_counters").json()
        return {key: ProgressCounter.fromdict(value) for key, value in json.items()}

    def clear_previous_pipelines(
        self,
    ) -> list[str]:
        """Clear and free memory for all pipelines except the current one."""
        res = self.session.post("/pipeline/clear")
        return cast(list[str], res.json()["cleared"])

    def reduced_data_channels(
        self, uuid: str = "current"
    ) -> dict[str, list[ReducedDataInfo]]:
        """Enumerate reduced data channels for a given pipeline as a dictionary."""
        json = self.session.get(f"/pipeline/{uuid}/reduced_data").json()
        return {
            key: [ReducedDataInfo.fromdict(item) for item in channel_list]
            for key, channel_list in json.items()
        }

    def frame_channels(self, uuid: str = "current") -> dict[str, FrameInfo]:
        """Enumerate frame channels for a given pipeline as a dictionary."""
        json = self.session.get(f"/pipeline/{uuid}/frames").json()
        return {
            key: FrameInfo(
                num_channels=value["num_channels"],
                width=value["width"],
                height=value["height"],
                pixel_type=np.dtype(value["pixel_type"]),
            )
            for key, value in json.items()
        }

    def reduced_data(
        self, name: str, channel_idx: int, uuid: str = "current"
    ) -> Iterator[npt.NDArray]:
        """Get an iterator over a reduced data channel."""

        # NOTE raises if name or channel_idx is invalid
        res = self.session.get(
            f"/pipeline/{uuid}/reduced_data/{name}/{channel_idx}", stream=True
        )

        rdc = self.reduced_data_channels(uuid=uuid)
        dtype = rdc[name][channel_idx].dtype

        for i, chunk in enumerate(res.iter_content(chunk_size=None)):
            if i % 100 == 0:
                logger.debug(f"Decoding {name} for frame {i}")
            yield np.frombuffer(chunk, dtype=dtype)

    def num_available(self, source_name: str, uuid: str = "current") -> int:
        """Get the number of frames of a given source."""
        return cast(
            int,
            self.session.get(f"/pipeline/{uuid}/{source_name}/num_available").json(),
        )

    def lookup(self, frame_idx: int, uuid: str = "current") -> tuple[int, str]:
        """Look up a frame by index.

        Returns a tuple (frame index, receiver url).
        """
        try:
            json = self.session.get(f"/pipeline/{uuid}/lookup/{frame_idx}").json()
        except ConductorClientError as e:
            raise LookupError(f"Failed to lookup frame {frame_idx}: {e}") from e

        return (json["frame_idx"], json["receiver_url"])

    def get_frame(
        self, frame_idx: int, source: str, uuid: str = "current"
    ) -> Frame | SparseFrame | SmxSparseFrame:
        """Fetch a frame directly from a receiver device."""
        fidx, rcv_url = self.lookup(frame_idx=frame_idx, uuid=uuid)
        class_name = self.pipeline(uuid=uuid)["type"]
        try:
            pipeline_info = pipelines.by_name[class_name]
        except KeyError as e:
            raise NotImplementedError(class_name) from e

        try:
            frame_source = pipeline_info.frame_sources[source]
        except KeyError as e:
            raise ValueError(
                f"Invalid frame source '{source}' for pipeline {class_name}."
            ) from e

        device = tg.DeviceProxy(rcv_url)

        getter = getattr(device, frame_source.getter_name)

        try:
            raw_data: tuple[str, bytes] = getter(frame_idx)
        except tg.DevFailed as e:
            logger.error(
                f"Failed to get {source} {frame_idx} (resolved to {fidx} on {device.dev_name()})"
            )
            raise RuntimeError(
                f"Unable to get frame {fidx} from {device.dev_name()}:\n{e}"
            ) from e

        decoder = types.decoder_by_type[frame_source.frame_type]

        frm = decoder(raw_data)

        return frm


class ConnectionState(Enum):
    ONLINE = auto()
    CONDUCTOR_OFFLINE = auto()
    DEVICES_OFFLINE = auto()


@dataclass
class ConductorServices:
    acquisition: Acquisition
    detector: Detector
    pipeline: Pipeline
    session: ConductorSession

    @staticmethod
    def from_session(session: ConductorSession) -> "ConductorServices":
        """Populate a ConductorServices instance from a ConductorSession."""
        return ConductorServices(
            acquisition=Acquisition(session=session),
            detector=Detector(session=session),
            pipeline=Pipeline(session=session),
            session=session,
        )

    def system_state(self) -> dict[str, Any]:
        """Get the state of every Lima2 component."""
        return cast(dict[str, Any], self.session.get("/state").json())

    def conductor_state(self) -> State:
        """Get the state of the conductor (aggregated from devices)."""
        return State[self.system_state()["state"]]

    def connection_state(self) -> ConnectionState:
        """Get the connection state."""
        try:
            cu_state = self.conductor_state()
        except ConductorConnectionError:
            return ConnectionState.CONDUCTOR_OFFLINE

        if cu_state == State.DISCONNECTED:
            return ConnectionState.DEVICES_OFFLINE

        return ConnectionState.ONLINE


def init(hostname: str, port: int = 58712) -> ConductorServices:
    """Initialize a conductor session.

    Returns a namespace of conductor services (`acquisition`, `detector`,
    `pipeline`), and the ConductorSession instance (`session`).
    """

    return ConductorServices.from_session(
        session=ConductorSession(hostname=hostname, port=port)
    )
