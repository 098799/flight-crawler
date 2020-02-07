import functools

from flight_crawler import secrets  # luminati username/password, not on git naturally

import requests
from requests import exceptions


class Session(requests.Session):
    """Session with retries + timeout and proxy."""

    MAX_RETRIES = 5
    REQUEST_TIMEOUT = 15

    @property
    @functools.lru_cache()
    def luminati_proxy(self):
        """Cheap and effective, at least for this easy purpose. Please supply your own user and password."""
        proxy = f"https://{secrets.username}:{secrets.password}@zproxy.lum-superproxy.io:22225"
        return {"https": proxy, "http": proxy}

    def get(self, *args, **kwargs):
        retries = 0

        while retries < self.MAX_RETRIES:
            try:
                response = super().get(*args, proxies=self.luminati_proxy, timeout=self.REQUEST_TIMEOUT, **kwargs)

                if response.ok:
                    return response
            except (exceptions.ProxyError, exceptions.ConnectTimeout):
                pass

            retries += 1

        return response
