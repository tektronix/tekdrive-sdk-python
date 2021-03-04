"""Provide interface for HTTP request handling."""
import requests
from .settings import __version__
from .settings import TIMEOUT
from .exceptions import RequestException


class RequestWrapper(object):
    def __init__(
        self,
        base_url: str = "https://drive.api.tekcloud.com",
        session: requests.Session = None,
    ):
        """
        Args:
            base_url: The base URL for API requests. Default: https://drive.api.tekcloud.com.
            session: A session to handle requests
        """
        self._http = session or requests.Session()
        self._http.headers["User-Agent"] = f"pytekdrivecore/{__version__}"

        self.base_url = base_url

    def close(self):
        return self._http.close()

    def call(self, *args, timeout: float = TIMEOUT, **kwargs):
        """
        Make the HTTP request and capture errors, if any.
        """
        try:
            return self._http.request(*args, timeout=timeout, **kwargs)
        except Exception as exc:
            raise RequestException(exc, args, kwargs)
