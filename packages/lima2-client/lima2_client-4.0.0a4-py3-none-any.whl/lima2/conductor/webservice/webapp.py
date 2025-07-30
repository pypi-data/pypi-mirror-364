# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor server entrypoint.

This module defines the create_app function, used by uvicorn to instantiate
our Starlette app.

Here we also define endpoints located at the root (/).
"""

import contextlib
import logging
import traceback
from typing import AsyncIterator, TypedDict

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.schemas import SchemaGenerator

from lima2.conductor.acquisition_system import (
    AcquisitionSystem,
    CommandFailed,
    CommandInProgress,
    InvalidCommandInState,
    NoCurrentPipeline,
    PipelineNotFound,
)
from lima2.conductor.processing.pipeline import InvalidFrameSource
from lima2.conductor.processing.reduced_data import NoSuchChannelError
from lima2.conductor.tango.utils import DeviceError
from lima2.conductor.topology import FrameLookupError
from lima2.conductor.utils import ValidationError
from lima2.conductor.webservice import acquisition, detector, pipeline

logger = logging.getLogger(__name__)

DEFAULT_PORT = 58712
"""Webservice default port"""


ConductorState = TypedDict("ConductorState", {"lima2": AcquisitionSystem})


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[ConductorState]:
    """Lifespan generator.

    Makes contextual objects (state, ...) accessible in handlers as `request.state.*`.
    """

    # Can run concurrent tasks here
    # async def side_task():
    #     while True:
    #         logger.info("side_task!")
    #         await asyncio.sleep(0.5)
    #
    # asyncio.create_task(side_task())

    lima2: AcquisitionSystem = app.state.lima2

    yield {
        "lima2": lima2,
    }

    logger.info("Bye bye")


async def homepage(request: Request) -> JSONResponse:
    """
    summary: Says hi :)
    responses:
      200:
        description: OK
    """

    lima2: AcquisitionSystem = request.state.lima2
    state = await lima2.state()

    devices = [lima2.control, *lima2.receivers]
    dev_states = await lima2.device_states()

    return JSONResponse(
        {"hello": "lima2 :)", "state": state.name}
        | {"devices": {dev.name: state.name for dev, state in zip(devices, dev_states)}}
    )


async def ping(request: Request) -> JSONResponse:
    """
    summary: Ping all devices and return the latency in us.
    responses:
      202:
        description: OK
    """

    lima2: AcquisitionSystem = request.state.lima2
    ping_us = {dev.name: await dev.ping() for dev in [lima2.control, *lima2.receivers]}

    return JSONResponse(ping_us, status_code=202)


async def uncaught(request: Request) -> JSONResponse:
    raise RuntimeError("not good")


schemas = SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "Conductor API", "version": "0.1"}}
)


async def openapi_schema(request: Request) -> Response:
    return schemas.OpenAPIResponse(request=request)


async def system_state(request: Request) -> JSONResponse:
    """
    summary: Returns the system state.
    responses:
      200:
        description: OK
    """
    lima2: AcquisitionSystem = request.state.lima2
    state = await lima2.state()
    dev_states = await lima2.device_states()
    devices = [lima2.control, *lima2.receivers]
    return JSONResponse(
        {"state": state.name}
        | {"runstate": lima2.runstate.name}
        | {"devices": {dev.name: state.name for dev, state in zip(devices, dev_states)}}
    )


async def uncaught_exception_handler(
    request: Request, exception: Exception
) -> JSONResponse:
    """Handler for an exception that wasn't caught in a request handler.

    This handler is called as a last resort to try to display useful information
    on the client side when something unexpected happens in the conductor.

    To help debugging, the full conductor-side trace is returned to the client.
    """

    # NOTE(mdu) we could have telemetry here to help debug in production: when
    # an uncaught exception occurs, send a packet with the full trace, hostname,
    # timestamp and other useful info to some central monitoring/logging
    # service.

    # Unexpected server-side exception
    return JSONResponse(
        {
            "error": str(exception),
            "trace": traceback.format_exception(exception),
        },
        status_code=500,  # Internal Server Error
    )


async def bad_request_handler(request: Request, exception: Exception) -> JSONResponse:
    """Return a 400 response, e.g. when a request's params were malformed / invalid."""
    return JSONResponse(
        {"error": str(exception)},
        status_code=400,  # Bad Request
    )


async def not_found_handler(request: Request, exception: Exception) -> JSONResponse:
    """Return a 404 response, e.g. when a resource was unavailable."""
    return JSONResponse(
        {"error": str(exception)},
        status_code=404,  # Not Found
    )


async def too_early_handler(request: Request, exception: Exception) -> JSONResponse:
    """Return a 425 response, e.g. when getting concurrent user commands."""
    return JSONResponse(
        {"error": str(exception)},
        status_code=425,  # Too Early
    )


async def conflict_handler(request: Request, exception: Exception) -> JSONResponse:
    """Return a 409 response, e.g. when the current state forbids a command."""
    return JSONResponse(
        {"error": str(exception)},
        status_code=409,  # Conflict
    )


async def bad_gateway_handler(request: Request, exception: Exception) -> JSONResponse:
    """Return a 502 response, e.g. when a command fails on a lima2 device."""
    return JSONResponse(
        {"error": str(exception)},
        status_code=502,  # Bad Gateway
    )


def create_app(
    lima2: AcquisitionSystem,
) -> Starlette:
    """Build the web app.

    Returns the webapp instance, with Lima2 context assigned to app's state.
    """

    app = Starlette(
        routes=[
            Route("/", homepage, methods=["GET"]),
            Route("/ping", ping, methods=["POST"]),
            Route(
                "/schema",
                endpoint=openapi_schema,
                include_in_schema=False,
                methods=["GET"],
            ),
            # Mount("/benchmark", routes=benchmark.routes),
            Mount("/acquisition", routes=acquisition.routes),
            Route("/state", system_state, methods=["GET"]),
            Mount("/detector", routes=detector.routes),
            Mount("/pipeline", routes=pipeline.routes),
        ],
        debug=False,
        lifespan=lifespan,
        exception_handlers={
            500: uncaught_exception_handler,
            DeviceError: bad_gateway_handler,
            CommandFailed: bad_gateway_handler,
            CommandInProgress: too_early_handler,
            InvalidCommandInState: conflict_handler,
            NoCurrentPipeline: not_found_handler,
            PipelineNotFound: not_found_handler,
            NoSuchChannelError: not_found_handler,
            FrameLookupError: not_found_handler,
            InvalidFrameSource: not_found_handler,
            ValidationError: bad_request_handler,
        },
    )

    # Pass the AcquisitionSystem instance to the shared app state
    # This is necessary for handlers to be able to use the object.
    app.state.lima2 = lima2

    return app
