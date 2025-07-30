from aiohttp import ClientSession
from flespi_sdk.modules.devices.device import Device
from flespi_sdk.modules.flespi_session import FlespiSession


class Devices(FlespiSession):
    def __init__(self, session: ClientSession, cid: int | None = None):
        super().__init__(session=session, cid=cid)

    async def get(self, id: int, fields: list[str] = []):
        async with self.session.get(
            f"/gw/devices/{id}",
            params=dict(fields=super().prepare_fields(fields)),
            headers=self.get_headers(),
        ) as response:
            result = await self.get_result(response)
            device = result[0]
            return Device(
                id=device["id"],
                metadata=device["metadata"],
                fields={field: device[field] for field in fields},
                session=self.session,
                cid=self.cid,
            )

    async def list(self, selector: str = "all", fields: list[str] = []):
        async with self.session.get(
            f"/gw/devices/{selector}",
            headers=self.get_headers(),
            params=dict(fields=super().prepare_fields(fields)),
        ) as response:
            return [
                Device(
                    id=device["id"],
                    metadata=device["metadata"],
                    fields={field: device[field] for field in fields},
                    session=self.session,
                    cid=self.cid,
                )
                for device in await self.get_result(response)
            ]
