from aiohttp import ClientSession
from flespi_sdk.modules.item_with_metadata import ItemWithMetadata


class Device(ItemWithMetadata):
    def __init__(
        self,
        id: int,
        metadata: dict,
        fields: dict,
        session: ClientSession,
        cid: int | None,
    ):
        super().__init__(
            id=id,
            metadata=metadata,
            fields=fields,
            item_path=f"gw/devices/{id}",
            session=session,
            cid=cid,
        )
