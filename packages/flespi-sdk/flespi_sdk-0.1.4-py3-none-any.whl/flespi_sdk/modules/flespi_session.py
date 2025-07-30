from aiohttp import ClientSession

from flespi_sdk.exception import FlespiException


class FlespiSession:
    def __init__(self, session: ClientSession, cid: int | None = None):
        self.cid = cid
        self.session = session

    def reset(self, cid: int):
        self.cid = cid

    def get_headers(self):
        if self.cid:
            return {"X-Flespi-CID": str(self.cid)}
        raise ValueError("CID is not set. Please set the CID before using this method.")

    async def get_result(self, response):
        if response.status != 200:
            raise FlespiException(
                status_code=response.status, errors=(await response.json())["errors"]
            )
        response_json = await response.json()
        result = response_json["result"]
        return result

    def prepare_fields(self, fields: list[str] = []):
        return ",".join(list(set(["id", "metadata"] + fields)))
