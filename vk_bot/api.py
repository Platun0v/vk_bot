from typing import Optional, Dict, Union, List

import requests

from .logging import logger
from .exceptions import *

API_URL = 'https://api.vk.com/method/'


class Api:
    def __init__(self, token, api_version):
        self.token = token
        self.api_version = api_version

        self.session = requests.Session()
        self.session.headers.update({
            'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0'
        })

    def _make_request(self, method_name: str, params: Optional[Dict], http_method: str) -> Union[Dict, List]:
        request_url = API_URL + method_name
        params = params.copy() if params else {}

        if 'v' not in params:
            params['v'] = self.api_version
        if 'access_token' not in params:
            params['access_token'] = self.token

        logger.debug(f"Request: method={http_method} url={request_url} params={params}")
        response = self.session.request(http_method, request_url, params=params)
        logger.debug("The server returned: '{0}'".format(response.text.encode('utf8')))

        return self._check_result(http_method, params, response)

    @staticmethod
    def _check_result(http_method: str, params: Dict, response: requests.Response) -> Union[Dict, List]:
        if response.status_code != 200:
            raise HttpError(http_method, params, response)

        result = response.json()

        if 'error' in result:
            raise ApiError(http_method, params, result['error'])

        return result['response']

    def method(self, method_name: str, params: Optional[Dict] = None, *, http_method: str = 'get') -> Union[Dict, List]:
        return self._make_request(method_name, params, http_method)
