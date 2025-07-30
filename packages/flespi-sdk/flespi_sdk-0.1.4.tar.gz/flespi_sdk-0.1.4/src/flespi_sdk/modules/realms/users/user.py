from aiohttp import ClientSession
from flespi_sdk.modules.item_with_metadata import ItemWithMetadata


class User(ItemWithMetadata):
    def __init__(
        self,
        id: int,
        realm_id: int,
        metadata: dict,
        fields: dict,
        session: ClientSession,
        cid: int | None = None,
    ):
        """
        Initializes the RealmUsers class with a client instance.

        :param client: The client instance used to make API requests.
        """
        self.realm_id = realm_id
        super().__init__(
            id=id,
            item_path=f"platform/realms/{realm_id}/users/{id}",
            metadata=metadata,
            fields=fields,
            session=session,
            cid=cid,
        )

    async def update_password(
        self,
        password: str,
    ) -> None:
        """
        Updates the password of the user.

        :param password: The new password for the user.
        """
        if len(password) < 16:
            raise ValueError("Password must be at least 16 characters long")

        async with self.session.put(
            self.item_path,
            json={"password": password},
            headers=self.get_headers(),
        ) as response:
            await self.get_result(response)
