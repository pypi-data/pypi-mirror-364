# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor client session."""


import requests

from lima2.client.exceptions import (
    ConductorClientError,
    ConductorServerError,
    ConductorUnhandledError,
    ConductorConnectionError,
)


class ConductorSession:
    def __init__(self, hostname: str, port: int) -> None:
        self.hostname = hostname
        self.port = port
        self.session = requests.Session()

    @property
    def base_url(self) -> str:
        return f"http://{self.hostname}:{self.port}"

    def get(self, endpoint: str, *args, **kwargs) -> requests.Response:
        """Make a GET request at /{endpoint}.

        Raises:
          ConductorConnectionError: if the conductor fails to respond.
          ConductorClientError: if the status code is in [400, 499].
          ConductorUnhandledError: if the status code is 500.
          ConductorServerError: if the status code is in [501, 599].
        """
        try:
            res = self.session.get(f"{self.base_url}{endpoint}", *args, **kwargs)
        except requests.ConnectionError as e:
            raise ConductorConnectionError(
                f"Conductor server at {self.base_url} is unreachable"
            ) from e

        if 400 <= res.status_code < 500:
            raise ConductorClientError(reason=res.reason, error=res.json()["error"])
        elif 501 <= res.status_code < 600:
            raise ConductorServerError(reason=res.reason, error=res.json()["error"])
        elif res.status_code == 500:
            json = res.json()
            raise ConductorUnhandledError(
                method=res.request.method or "?",
                url=res.request.url or "?",
                error=json["error"],
                trace=json["trace"],
            )
        else:
            return res

    def post(self, endpoint: str, *args, **kwargs) -> requests.Response:
        """Make a POST request at /{endpoint}.

        Raises:
          ConductorConnectionError: if the conductor fails to respond.
          ConductorClientError: if the status code is in [400, 499].
          ConductorUnhandledError: if the status code is 500.
          ConductorServerError: if the status code is in [501, 599].
        """
        try:
            res = self.session.post(f"{self.base_url}{endpoint}", *args, **kwargs)
        except requests.ConnectionError as e:
            raise ConductorConnectionError(
                f"Conductor server at {self.base_url} is unreachable"
            ) from e

        if 400 <= res.status_code < 500:
            raise ConductorClientError(reason=res.reason, error=res.json()["error"])
        elif 501 <= res.status_code < 600:
            raise ConductorServerError(reason=res.reason, error=res.json()["error"])
        elif res.status_code == 500:
            json = res.json()
            raise ConductorUnhandledError(
                method=res.request.method or "?",
                url=res.request.url or "?",
                error=json["error"],
                trace=json["trace"],
            )
        else:
            return res
