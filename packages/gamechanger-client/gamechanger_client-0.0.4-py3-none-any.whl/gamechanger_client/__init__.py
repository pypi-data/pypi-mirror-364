# -*- coding: utf-8 -*-
"""
Community-developed Python SDK for interacting with Gamechanger APIs.
"""

import base64
import logging
import os
import random
import string
import time
import uuid

import requests

from gamechanger_client.http_session import HttpSession

from .endpoints.clips import ClipsEndpoint
from .endpoints.game_streams import GameStreamsEndpoint
from .endpoints.me import MeEndpoint
from .endpoints.organizations import OrganizationsEndpoint
from .endpoints.players import PlayersEndpoint
from .endpoints.public import PublicEndpoint
from .endpoints.search import SearchEndpoint
from .endpoints.teams import TeamsEndpoint
from .version import __version__

# Expose version at package level
__all__ = [
    'GameChangerClient',
    'HttpSession',
    'ClipsEndpoint',
    'MeEndpoint', 
    'OrganizationsEndpoint',
    'PlayersEndpoint',
    'PublicEndpoint',
    'SearchEndpoint',
    'TeamsEndpoint',
    '__version__'
]

logger = logging.getLogger(__name__)

logging.basicConfig(format='%(asctime)s %(name)s [%(levelname)s] %(message)s')
logger = logging.getLogger('gamechanger-client')
logger.setLevel(os.getenv('LOG_LEVEL', logging.INFO))


class GameChangerClient:

    def __init__(self,
                 username=None,
                 password=None,
                 token=None):


        self._gc_username = username or os.getenv('GC_USERNAME')
        self._gc_password = password or os.getenv('GC_PASSWORD')
        self._gc_token = token or os.getenv('GC_TOKEN')

        self._client_id = uuid.uuid1()
        # self._client_key = self._ge

        # Create a new requests session
        self._session = HttpSession(self._gc_token)

        self.clips = ClipsEndpoint(self._session)
        self.game_streams = GameStreamsEndpoint(self._session)
        self.me = MeEndpoint(self._session)
        self.organizations = OrganizationsEndpoint(self._session)
        self.players = PlayersEndpoint(self._session)
        self.public = PublicEndpoint(self._session)
        self.search = SearchEndpoint(self._session)
        self.teams = TeamsEndpoint(self._session)


    def _generate_random_hex(self, length = 32):
        random_string = ''.join(random.SystemRandom().choice(string.hexdigits) for _ in range(length))

        return random_string

    def _generate_random_string(self, length = 32):
        random_string = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))

        return random_string

    def _generate_random_base64(self, length = 32):
        random_string = self._generate_random_string(length)
        random_string_bytes = random_string.encode('ascii')

        random_base64_bytes = base64.b64encode(random_string_bytes)
        random_base64_string = random_base64_bytes.decode('ascii')

        return random_base64_string

    def auth(self):
        auth_url = f'{self._session._base_url}/auth'

        # Build the request headers
        auth_init_headers = {}
        auth_init_headers['Content-Type'] = 'application/json; charset=utf-8'
        auth_init_headers['Gc-App-Name'] = 'web'
        auth_init_headers['Gc-App-Version'] = '0.0.0'
        auth_init_headers['Gc-Client-Id'] = "741d24bc-e058-46c8-a52a-ee6b885acd4b" #str(self._client_id)
        auth_init_headers['Gc-Device-Id'] = "03a6ba4221f3c8dc4c335650c3ac4e89" #self._generate_random_hex().lower()
        auth_init_headers['Gc-Signature'] = "urdQEYjF8dyT6/rbxXdEhY92/61p/B8LGIecJsBt4Mk=.yCivrdC0j0uSf+yq2SbQfl1N8qCLYmos0ceyPucxU1s=" #  f'{self._generate_random_base64()}.{self._generate_random_base64()}'
        auth_init_headers['Gc-Timestamp'] = str(int(time.time()))

        auth_init_payload = {
            'type': 'client-auth',
            'client_id': str(self._client_id)
        }

        response = requests.post(url=auth_url, headers=auth_init_headers, json=auth_init_payload)

        print(response.request.headers)
        print(response.request.body)

        print(response.headers)
        print(response.text)
        exit()
