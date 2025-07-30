import aiohttp

from flespi_sdk.modules.realms.realm import Realm
from flespi_sdk.modules.flespi_session import FlespiSession


class Realms(FlespiSession):
    def __init__(self, session: aiohttp.ClientSession, cid: int | None = None):
        super().__init__(session, cid)

    async def get(self, id: int, fields: list[str] = []):
        async with self.session.get(
            f"/platform/realms/{id}",
            params=dict(fields=super().prepare_fields(fields)),
            headers=self.get_headers(),
        ) as response:
            result = await self.get_result(response)
            realm = result[0]
            return Realm(
                id=realm["id"],
                metadata=realm["metadata"],
                fields={field: realm[field] for field in fields},
                session=self.session,
                cid=self.cid,
            )

    async def list(self, selector: str = "all", fields: list[str] = []):
        async with self.session.get(
            f"/platform/realms/{selector}",
            params=dict(fields=super().prepare_fields(fields)),
            headers=self.get_headers(),
        ) as response:
            result = await self.get_result(response)
            return [
                Realm(
                    id=realm["id"],
                    metadata=realm["metadata"],
                    fields={field: realm[field] for field in fields},
                    session=self.session,
                    cid=self.cid,
                )
                for realm in result
            ]
