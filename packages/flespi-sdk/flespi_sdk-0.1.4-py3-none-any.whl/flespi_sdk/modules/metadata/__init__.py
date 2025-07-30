import aiohttp

from flespi_sdk.modules.flespi_session import FlespiSession


class Metadata(FlespiSession):
    def __init__(
        self,
        item_path,
        metadata: dict | None,
        session: aiohttp.ClientSession,
        cid: int | None,
    ):
        super().__init__(session, cid)
        self.item_path = item_path
        self.metadata_cache = metadata

    async def get(self, use_cache: bool = True) -> dict:
        """
        Get metadata for the current account.
        :return: Metadata as a dictionary.
        """
        if self.metadata_cache and use_cache:
            return self.metadata_cache

        params = {"fields": "metadata"}
        async with self.session.get(
            self.item_path, params=params, headers=self.get_headers()
        ) as response:
            result = await self.get_result(response)
            metadata = result[0]["metadata"]
            self.metadata_cache = metadata
            return metadata

    async def set(self, metadata: dict) -> None:
        """ "
        "Set metadata for the current account.
        :param metadata: Metadata as a dictionary.
        """
        self.metadata_cache = None
        async with self.session.put(
            self.item_path,
            json={"metadata": metadata},
            headers=self.get_headers(),
        ) as response:
            await self.get_result(response)

    async def get_value(self, key_path: str, use_cache: bool = True):
        """
        Get a specific value from the metadata.
        :param key_path: The key path to the value in the metadata.
        :return: The value from the metadata.
        """
        metadata = await self.get(use_cache=use_cache)
        if not metadata:
            return None
        keys = key_path.split(".")
        value = metadata
        for key in keys:
            if key in value:
                value = value[key]
            else:
                return None
        return value

    async def set_value(self, key_path: str, value) -> None:
        """
        Set a specific value in the metadata.
        :param key_path: The key path to the value in the metadata.
        :param value: The value to set.
        """
        metadata = await self.get(use_cache=False) or {}
        keys = key_path.split(".")
        metadata_level = metadata
        for key in keys[:-1]:
            if key not in metadata_level:
                metadata_level[key] = {}
            metadata_level = metadata_level[key]
        metadata_level[keys[-1]] = value
        await self.set(metadata)

    async def delete_value(self, key_path: str) -> None:
        """
        Delete a specific key from the metadata.
        :param key_path: The key path to the value in the metadata.
        """
        metadata = await self.get(use_cache=False)
        if not metadata:
            return
        keys = key_path.split(".")
        metadata_level = metadata
        for key in keys[:-1]:
            if key in metadata_level:
                metadata_level = metadata_level[key]
            else:
                return None
        del metadata_level[keys[-1]]
        await self.set(metadata)
