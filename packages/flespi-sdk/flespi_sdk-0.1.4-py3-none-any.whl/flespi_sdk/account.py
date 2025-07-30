from aiohttp import ClientSession

from flespi_sdk.exception import FlespiException
from flespi_sdk.modules.devices import Devices
from flespi_sdk.modules.metadata import Metadata
from flespi_sdk.modules.mqtt import MQTT
from flespi_sdk.modules.realms import Realms
from flespi_sdk.modules.subaccounts import Subaccounts


class Account:
    def __init__(
        self, session: ClientSession | None = None, id: int | None = None
    ) -> None:
        self.id = id
        self.session = session or ClientSession("https://flespi.io")

        self._init_modules()

    async def stop(self) -> None:
        """
        Close the aiohttp session.
        """
        await self.session.close()

    async def set_token(self, token: str) -> None:
        await self._reset(token)

    async def realm_login(
        self,
        realm_public_id: str,
        realm_username: str,
        realm_password: str,
    ) -> None:
        """
        Login to a realm and set the Authorization header for subsequent requests.
        :param realm_public_id: Public ID of the realm.
        :param realm_username: Username for the realm.
        :param realm_password: Password for the realm.
        :raises Exception: If the login fails.
        """
        if not realm_public_id or not realm_username or not realm_password:
            raise ValueError("All parameters are required")

        async with self.session.post(
            f"/realm/{realm_public_id}/login",
            json={"username": realm_username, "password": realm_password},
        ) as response:
            if response.status != 200:
                raise Exception("Login failed")
            response_json = await response.json()

            token = response_json["result"][0]["token"]

            await self._reset(token)

    async def _reset(self, token: str | None = None) -> None:
        """
        Reset the account by resetting token and clearing the CID from all subsystems.
        """
        async with self.session.get(
            "/platform/customer", headers=dict(Authorization=f"FlespiToken {token}")
        ) as response:
            if response.status != 200:
                raise FlespiException(
                    status_code=response.status,
                    errors=(await response.json())["errors"],
                )
            response_json = await response.json()
            result = response_json["result"]
            id = result[0]["id"]
            if not id:
                raise Exception("Failed to get account ID: " + response_json)
            self.id = id
            self.session.headers["Authorization"] = f"FlespiToken {token}"
            self._init_modules()

    def _init_modules(self):
        self.metadata = Metadata(
            item_path="platform/customer",
            metadata=None,
            session=self.session,
            cid=self.id,
        )
        self.subaccounts = Subaccounts(self.session, self.id)
        self.realms = Realms(self.session, self.id)
        self.mqtt = MQTT(self.session, self.id)
        self.devices = Devices(self.session, self.id)
