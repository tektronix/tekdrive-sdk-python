"""Provide Session class."""

import logging
from time import sleep
from copy import deepcopy
from typing import TYPE_CHECKING, Dict, Optional, Tuple, Union
from urllib.parse import urljoin

from .authorizer import BaseAuthorizer
from .request_wrapper import RequestWrapper
from .retry import RetryPolicy, RateLimit
from .exceptions import (
    InvalidAuthorizer,
    RequestException,
    BadJSON,
)
from .status_codes import (
    EXCEPTION_STATUS_CODES,
    NO_CONTENT,
    RETRY_EXCEPTIONS,
    RETRY_STATUS_CODES,
    STATUS_TO_EXCEPTION_MAPPING,
    SUCCESS_STATUS_CODES,
)
from .settings import TIMEOUT, BASE_URL

if TYPE_CHECKING:
    from requests import Response
    from .routing import Route

log = logging.getLogger(__name__)


class Session(object):
    def __init__(self, authorizer: BaseAuthorizer, base_url: str = BASE_URL):
        if not isinstance(authorizer, BaseAuthorizer):
            raise InvalidAuthorizer(f"Invalid Authorizer: {authorizer}")

        self._authorizer = authorizer
        self._rate_limit = RateLimit()
        self._request_wrapper = RequestWrapper(base_url=base_url)

    def _log_request(self, method, url, params, data, json) -> None:
        log.debug(
            f"Request: {method} {url}, data: {data}, json: {json}, params: {params}"
        )

    def __enter__(self):
        """Context manager enter"""
        return self

    def __exit__(self, *_args):
        """Context manager exit"""
        self.close()

    def _try_request(
        self,
        *,
        method,
        url,
        data,
        files,
        json,
        params,
        headers,
        retry_policy,
        timeout,
    ) -> Tuple[Optional["Response"], Optional[Exception]]:
        if not headers:
            headers = self._authorizer._get_auth_header()

        seconds_to_sleep = self._rate_limit.seconds_to_sleep()
        if seconds_to_sleep:
            log.debug(f"Sleeping for {seconds_to_sleep} seconds (rate limited)")
            sleep(seconds_to_sleep)
        try:
            response = self._request_wrapper.call(
                method,
                url,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=headers,
                timeout=timeout,
            )
            log.debug(f"Response status: {response.status_code}")

            # update the rate limit state from response headers
            self._rate_limit.update_from_headers(response.headers)

            return response, None
        except RequestException as exception:
            if not retry_policy.retries_remaining or not isinstance(
                exception.original_exception, RETRY_EXCEPTIONS
            ):
                raise
            return None, exception.original_exception

    def _request(
        self,
        *,
        method,
        url,
        data,
        files,
        json,
        params,
        headers,
        timeout,
    ):
        retry_policy = RetryPolicy()
        self._log_request(method, url, params, data, json)

        while retry_policy.retries_remaining:
            response, exc = self._try_request(
                method=method,
                url=url,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=headers,
                retry_policy=retry_policy,
                timeout=timeout,
            )
            if response is None or response.status_code not in RETRY_STATUS_CODES:
                break

            retry_policy.decrement_retries()
            sleep_seconds = retry_policy.seconds_to_sleep()
            if sleep_seconds > 0:
                sleep(sleep_seconds)

        status_code = repr(exc) if exc else response.status_code
        if status_code in EXCEPTION_STATUS_CODES:
            raise STATUS_TO_EXCEPTION_MAPPING[response.status_code](response)
        elif status_code == NO_CONTENT:
            return
        elif status_code not in SUCCESS_STATUS_CODES:
            raise Exception(f"Unknown status code: {status_code}")

        try:
            return response.json()
        except ValueError:
            return BadJSON(response)

    def close(self):
        self._request_wrapper.close()

    def safe_copy_dict(self, d: dict, sort: bool = False) -> dict:
        if isinstance(d, dict):
            d = deepcopy(d)
            if sort:
                return sorted(d.items())
        return d

    def request(
        self,
        route: "Route",
        data: dict = None,
        files: dict = None,
        json: object = None,
        params: Optional[Union[str, Dict[str, Union[str, int]]]] = None,
        headers: dict = None,
        timeout: float = TIMEOUT,
    ):
        """
        Return the json content from the resource at ``path``.

        Args:
            method: The request method such as GET, POST, PATCH, etc.
            path: The path of the request to be combined with the ``base_url``
                of the Requestor.
            data: Dictionary, bytes, or file-like object to send in the body
                of the request.
            files: Dictionary, mapping ``filename`` to file-like object.
            json: Object to be serialized to JSON in the body of the
                request.
            params: The query parameters to send with the request.
            headers: Overwrite all headers for the request.
        """
        params = deepcopy(params) or {}
        data = self.safe_copy_dict(data, sort=True)
        headers = self.safe_copy_dict(headers, sort=True)
        json = self.safe_copy_dict(json)

        return self._request(
            method=route.method,
            url=urljoin(self._request_wrapper.base_url, route.path),
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            timeout=timeout,
        )


def create_session(*, authorizer: BaseAuthorizer = None, base_url: str) -> Session:
    return Session(authorizer, base_url=base_url)
