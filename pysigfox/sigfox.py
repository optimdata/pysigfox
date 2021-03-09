import functools
import json
import logging
import time

import requests
import urllib.parse

from .exceptions import (
    SigfoxConnectionError,
    SigfoxBadStatusError,
    SigfoxResponseError,
    SigfoxTooManyRequestsError,
)
from .utils import to_ms_timestamp


# The rate limit for the device messages end point (unit: query/seconds)
RATE_LIMIT_DEVICE_MESSAGES = 1

logger = logging.getLogger("client")


class Sigfox(object):
    """
    `Sigfox V2 API client <https://support.sigfox.com/apidocs>`_

    Inspired from https://github.com/mjuenema/python-sigfox-backend-api
    """

    def next(self, *args, **kwargs):
        """Fetch the next page of results for some methods.

           Call this method whenever another method has returned only
           a subset of the results.

           >>> messages = s.device_messages('4d3091a05ee16b3cc86699ab')
           >>> while s.next:
           ...     messages += s.next()
           >>> len(messages)
           310
           >>> devices = s.devices()
           >>> while s.next:
           ...     devices += s.next()
           >>> len(devices)
           22

           .. warning:: Be mindful that this may return a huge number of
                        results if used exactly as in the example above.

        """

        # `Sigfox.next()` will be set in `Sigfox.request()` to ``None`` or
        # a `functool.partial(...)` method matching the original method.
        # The code here is only for documentation purposes.
        pass  # pragma: no cover

    def __init__(self, username, password):
        self.account = username
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.base_url = "https://api.sigfox.com/v2/"
        self.client_type = "Sigfox"
        self.next = None

    def _build_url(self, url):
        return self.base_url + url

    def request(self, method, route, params=None, **kwargs):
        """
        Base request method that can be used if a route is not configured in this client.
        This method handles the pagination and perform the query using a `request.request <https://requests.readthedocs.io/en/latest/api/#requests.request>`_

        It returns the `data` stored in the response and update the `next` method if there is a pagination.

        """
        url = self._build_url(route)
        try:
            response = self.session.request(
                method=method, url=url, params=params, **kwargs
            )
        except requests.exceptions.ConnectionError as e:  # pragma: nocover
            raise SigfoxConnectionError(str(e))  # pragma: nocover

        # HTTP 429: too many requests
        if response.status_code == 429:
            raise SigfoxTooManyRequestsError()

        if response.status_code != 200:  # pragma: nocover
            raise SigfoxBadStatusError(
                f"Bad status {response.status_code} : {response.text}"
            )

        try:
            response = response.json()
        except json.decoder.JSONDecodeError:  # pragma: nocover
            raise SigfoxResponseError(
                "Cannot deserialize json from %s" % response.content
            )

        data = response.get("data", response)

        # Set `Sigfox.next()` by extracting the parameters from the 'next' URL and
        # currying the self.request().
        self.next = None
        if "paging" in response and "next" in response["paging"]:
            next_params = dict(
                urllib.parse.parse_qsl(response["paging"]["next"].split("?")[1])
            )
            if next_params:
                if params:
                    params.update(next_params)
                else:
                    params = next_params
                self.next = functools.partial(
                    self.request, method, route, params, **kwargs
                )
            else:
                self.next = None

        return data

    def devices(self, list_all=False, **kwargs):
        """
        `Retrieve a list of devices according to visibility permissions and request filters. <https://support.sigfox.com/apidocs#operation/listDevices>`_

        :param bool list_all: extract all devices (this endpoint is paginated).
        """
        params = kwargs.pop("params", {})
        results = self.request("GET", "devices", params=params, **kwargs)
        if list_all:
            self._handle_next_pages(results)

        return results

    def device(self, device_code, **kwargs):
        """
        `Retrieve information about a given device <https://support.sigfox.com/apidocs#operation/getDevice>`_

        :param str device_code: The device identifier.
        """
        return self.request("GET", f"devices/{device_code}", **kwargs)

    def device_messages(
        self, device_code, list_all=False, since=None, before=None, **kwargs
    ):
        """
        `Retrieve a list of messages for a given device according to request filters, with a 3-day history. <https://support.sigfox.com/apidocs#operation/getDeviceMessagesListForDevice>`_
        Messages are retrieved from the newest to the oldest.


        :param str device_code: The device identifier.
        :param bool list_all: If ``list_all``, extract all the devices (this endpoint is paginated). This api has a `rate limiting <https://support.sigfox.com/docs/api-rate-limiting>`_ of 1 request per second.
        :param datetime.datetime since: the starting date time of the period to fetch. can be null.
        :param datetime.datetime before: the ending date time of the period to fetch. can be null.
        """
        # process period
        since = to_ms_timestamp(since)
        before = to_ms_timestamp(before)
        params = kwargs.pop("params", {})
        params.update({"since": since, "before": before})
        results = self.request(
            "GET", f"devices/{device_code}/messages", params=params, **kwargs
        )
        if list_all:
            self._handle_next_pages(results, rate_limit=RATE_LIMIT_DEVICE_MESSAGES)
        return results

    def _handle_next_pages(self, results, rate_limit=None):
        """
        Handle pagination of some end point by making sure we retrieve all the data
        (even if the endpoint has a rate limitation)

        :param list results: The list where to append the paginated results.
        :param int rate_limit: The rate limit (duration in seconds between two calls for this end point).
        """
        while self.next:
            try:
                results += self.next()
            except SigfoxTooManyRequestsError:  # pragma: no cover
                logger.debug(
                    f"Too many requests on the API. Sleep for {rate_limit} seconds."
                )
                time.sleep(rate_limit)
                continue
        return results
