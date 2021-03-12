"""Provide retry policy"""
import logging
import time
from dataclasses import dataclass
from random import random

log = logging.getLogger(__name__)


@dataclass
class RetryPolicy:
    """
    Track retries for API requests
    """

    retries: int = 2
    max_backoff: int = 32

    def seconds_to_sleep(self):
        return min(((2 ** self.retries) + random()), self.max_backoff)

    @property
    def retries_remaining(self):
        return self.retries >= 1

    def decrement_retries(self):
        self.retries -= 1


@dataclass
class RateLimit:
    reset_timestamp = None
    next_request_timestamp = None
    remaining: int = None
    used: int = None
    limit: int = None

    def update_from_headers(self, headers: dict):
        """
        Update rate limit fields
        """
        log.debug(f"Update rate limit from headers: {headers}")
        if "x-ratelimit-remaining" not in headers:
            if self.remaining is not None:
                self.remaining -= 1
                self.used += 1
            return

        now = time.time()

        self.reset_timestamp = int(headers["x-ratelimit-reset"])
        self.limit = int(headers["x-ratelimit-limit"])
        self.remaining = int(headers["x-ratelimit-remaining"])
        self.used = self.limit - self.remaining

        if self.remaining <= 0:
            self.next_request_timestamp = self.reset_timestamp
            return

        self.next_request_timestamp = now

    def seconds_to_sleep(self):
        """
        How many seconds to sleep to avoid rate limit throttling?
        """
        if self.next_request_timestamp is None:
            return
        sleep_seconds = self.next_request_timestamp - time.time()
        if sleep_seconds <= 0:
            return
        return sleep_seconds
