import aiohttp

from flespi_sdk.modules.flespi_session import FlespiSession


class Subaccounts(FlespiSession):
    def __init__(self, session: aiohttp.ClientSession, cid: int | None = None):
        super().__init__(session, cid)

    async def get(self, id: str):
        from flespi_sdk.account import Account

        async with self.session.get(
            f"/platform/subaccounts/{id},cid={self.cid}", headers=self.get_headers()
        ) as response:
            result = await self.get_result(response)
            subacc = result[0]
            return Account(
                self.session,
                id=subacc["id"],
            )

    async def list(self, selector: str = "all"):
        from flespi_sdk.account import Account

        async with self.session.get(
            f"/platform/subaccounts/{selector},cid={self.cid}",
            headers=self.get_headers(),
        ) as response:
            result = await self.get_result(response)
            return [Account(self.session, id=subacc["id"]) for subacc in result]
