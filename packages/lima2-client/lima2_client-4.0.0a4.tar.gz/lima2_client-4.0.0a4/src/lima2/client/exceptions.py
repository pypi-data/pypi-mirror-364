# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor client exceptions."""


from dataclasses import dataclass


@dataclass
class ConductorClientError(RuntimeError):
    """Request couldn't be fulfilled for a specific reason.

    Raised when the server returns a status code between 400 and 499 to indicate
    a likely user-induced error, such as wrong arguments, an invalid command or
    query, an untimely request, etc.

    Should be accompanied by a helpful user-facing message.
    """

    reason: str
    """String equivalent of the HTTP status code (e.g. 404 -> "Not Found")."""
    error: str
    """Error message, displayed to the caller."""

    def __str__(self) -> str:
        return self.error


@dataclass
class ConductorServerError(RuntimeError):
    """Request couldn't be fulfilled for a specific reason.

    Raised when the server returns a status code between 501 and 599 to indicate
    a likely conductor-side error, such as a loss of communication with the
    lima2 devices.

    Should be accompanied by a helpful user-facing message.
    """

    reason: str
    """String equivalent of the HTTP status code (e.g. 404 -> "Not Found")"""
    error: str
    """Error message, displayed to the caller."""

    def __str__(self) -> str:
        return f"{self.error}"


@dataclass
class ConductorUnhandledError(RuntimeError):
    """Request couldn't be fulfilled for an unknown reason.

    Raised when an uncaught server-side error occurs (signaled by a status code
    500).

    Contains the server-side exception message and a full trace. The trace can
    be also found in the conductor logs.

    Indicates a flaw in error handling code on the server side.
    """

    method: str
    url: str
    error: str
    trace: str

    def __str__(self) -> str:
        return (
            f"Exception raised while handling {self.method.upper()} request "
            f"at {self.url}.\n\n" + "".join(self.trace)
        )


class ConductorConnectionError(RuntimeError):
    """Raised by all client functions when the conductor can't be reached."""
