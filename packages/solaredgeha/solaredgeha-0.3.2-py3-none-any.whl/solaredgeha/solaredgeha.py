from xml.etree import ElementTree

import logging

import aiohttp
import yarl

_LOGIN_URL = yarl.URL("https://api.solaredge.com/solaredge-apigw/api")
_BASE_URL = yarl.URL("https://ha.monitoring.solaredge.com/api/homeautomation/v1.0")

_COOKIE_NAME = "SPRING_SECURITY_REMEMBER_ME_COOKIE"

_LOGGER = logging.getLogger(__name__)

class SolarEdgeHa:
    """SolarEdgeHa API client."""

    def __init__(self, username: str, password: str,
                 session: aiohttp.ClientSession | None = None, timeout: int = 10) -> None:
        """Initialise the SolarEdge HA API client."""
        self.username = username
        self.password = password

        self.session = session or aiohttp.ClientSession()
        self._created_session = not session
        self.timeout = timeout

        self.sites = []
        self.token = None

    async def close(self) -> None:
        """Close the SolarEdge HA API client."""
        if self._created_session:
            await self.session.close()

    async def login(self) -> bool:
        """Login to service."""

        url = _LOGIN_URL / "login"

        params = {
            "j_username": self.username,
            "j_password": self.password
        }

        _LOGGER.debug("Calling login")
        response = await self.session.post(url, data=params, timeout=self.timeout, allow_redirects=False)
        _LOGGER.debug("Response from %s: %s", url, response.status)
        response.raise_for_status()

        if (response.status != 302):
            return False

        self.token = response.cookies[_COOKIE_NAME].value

        _LOGGER.debug("Token: %s", self.token)

        return await self.update_sites()

    async def update_sites(self) -> bool:
        """Update available sites."""
        if (self.token == None):
            return False

        url = _LOGIN_URL / "fields" / "list"
        _LOGGER.debug("URL: %s", url)

        cookies = {
            _COOKIE_NAME: self.token
        }

        _LOGGER.debug("Calling fields/list")
        response = await self.session.get(url, cookies=cookies)
        _LOGGER.debug("Response from %s: %s", url, response.status)
        response.raise_for_status()

        if (response.status != 200):
            self.sites = []
            return False

        content = await response.text()
        # _LOGGER.debug("Response: %s", content)

        tree = ElementTree.fromstring(content)

        self.sites = []
        for id in tree.iter('id'):
            self.sites.append(id.text)

        return True

    async def ensure_session(self) -> bool:
        if (self.token == None):
            await self.login()

        return self.token != None

    def get_sites(self) -> []:
        """Get list of site ids."""

        return self.sites

    async def get_devices(self, site) -> dict:
        """Request devices."""

        if (await self.ensure_session() == False):
            return None

        url = _BASE_URL / "sites" / site / "devices"

        cookies = {
            _COOKIE_NAME: self.token
        }

        response = await self.session.get(url, cookies=cookies)
        _LOGGER.debug("Response from %s: %s", url, response.status)
        response.raise_for_status()

        if (response.status != 200):
            return {}

        return await response.json()

    async def activate_device(self, reporterId, level, duration=None) -> dict:
        """Activate devices."""

        if (await self.ensure_session() == False):
            return None

        url = _BASE_URL / self.sites[0] / "devices" / str(reporterId) / "activationState"

        cookies = {
            _COOKIE_NAME: self.token
        }

        params = {
            "mode": "MANUAL",
            "level": level,
            "duration": duration
        }

        response = await self.session.put(url, json=params, cookies=cookies)
        _LOGGER.debug("Response from %s: %s", url, response.status)
        response.raise_for_status()

        if (response.status != 200):
            return {}

        return await response.json()

