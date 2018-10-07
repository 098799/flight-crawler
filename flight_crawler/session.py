import random

from flight_crawler import utils

import requests
from requests import exceptions


class Session(requests.Session):
    """Tiny mod for requests.session"""

    PROXY_FILE = "data/proxy.dat"
    REQUEST_TIMEOUT = 15

    @property
    def free_proxy(self):
        return {'https': random.choice(self.proxy_list)}

    def get(self, *args, **kwargs):
        """Adding auto retry with different free proxy."""
        retries = 0

        while retries < 10:
            try:
                response = super().get(
                    *args,
                    proxies=self.free_proxy,
                    timeout=self.REQUEST_TIMEOUT,
                    **kwargs
                )
                if response.ok:
                    return response
            except (exceptions.ProxyError, exceptions.ConnectTimeout):
                pass

            retries += 1

    @property
    def proxy_list(self):
        if not getattr(self, "_proxy_list", None):
            self._proxy_list = utils.read_from_file(self.PROXY_FILE).split()

        return self._proxy_list
