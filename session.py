import random

import requests
from requests import exceptions


class Session(requests.Session):
    """Tiny mod for requests.session"""

    @property
    def free_proxy(self):
        if not getattr(self, "_free_proxy_list", None):
            with open("proxy.dat", "r") as infile:
                self._free_proxy_list = infile.read().split()

        return {'https': random.choice(self._free_proxy_list)}

    def get(self, *args, **kwargs):
        """Adding auto retry with different free proxy."""
        retries = 0

        while retries < 5:
            proxies = self.free_proxy
            try:
                response = super().get(*args,
                                       proxies=proxies,
                                       timeout=10,
                                       **kwargs)
            except (exceptions.ProxyError, exceptions.ConnectTimeout):
                retries -= 1
                continue

            if response.ok:
                return response

            retries += 1
