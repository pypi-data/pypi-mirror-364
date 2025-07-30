from aiohttp import ClientSession
from flespi_sdk.modules.flespi_session import FlespiSession
from flespi_sdk.modules.metadata import Metadata


class ItemWithMetadata(FlespiSession):
    def __init__(
        self,
        id: int,
        item_path: str,
        session: ClientSession,
        metadata: dict | None = None,
        fields: dict = {},
        cid: int | None = None,
    ):
        super().__init__(session, cid)
        self.id = id
        self.item_path = item_path
        self.initial_fields = fields
        self.metadata = Metadata(
            item_path=item_path, metadata=metadata, session=session, cid=cid
        )

    async def get_name(self) -> str:
        """
        Get the name of the item.
        :return: The name of the item.
        """
        async with self.session.get(
            f"/{self.item_path}",
            headers=self.get_headers(),
        ) as response:
            result = await self.get_result(response)
            return result[0]["name"]

    def get_initial_fields(self):
        return self.initial_fields

    async def get_fields(self, fields: list[str]) -> dict:
        """
        Get fields for the current device.
        :return: Dictionary with fields.
        """
        async with self.session.get(
            self.item_path,
            params=dict(fields=fields),
            headers=self.get_headers(),
        ) as response:
            result = await self.get_result(response)
            return result[0]
