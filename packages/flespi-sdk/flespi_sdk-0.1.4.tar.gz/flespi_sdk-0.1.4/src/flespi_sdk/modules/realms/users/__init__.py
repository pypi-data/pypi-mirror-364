from aiohttp import ClientSession
from flespi_sdk.modules.realms.users.user import User
from flespi_sdk.modules.flespi_session import FlespiSession


class Users(FlespiSession):
    """
    The RealmUsers class provides methods to manage users in a specific realm.
    It allows for the retrieval of user information and the management of user roles.
    """

    def __init__(
        self,
        realm_id: int,
        client_session: ClientSession,
        cid: int | None = None,
    ):
        """
        Initializes the RealmUsers class with a client instance.

        :param client: The client instance used to make API requests.
        """
        super().__init__(client_session, cid)
        self.realm_id = realm_id

    async def get(self, id: int, fields: list[str] = []) -> User:
        """
        Get a user by ID.
        :param user_id: The ID of the user to retrieve.
        :return: A User object.
        """
        async with self.session.get(
            f"/platform/realms/{self.realm_id}/users/{id}",
            params=dict(fields=super().prepare_fields(fields)),
            headers=self.get_headers(),
        ) as response:
            result = await self.get_result(response)
            user = result[0]
            return User(
                id=user["id"],
                realm_id=self.realm_id,
                metadata=user["metadata"],
                fields={field: user[field] for field in fields},
                session=self.session,
                cid=self.cid,
            )

    async def list(self, selector: str = "all", fields: list[str] = []) -> list[User]:
        """
        List all users in the realm.
        :param selector: The selector to filter users.
        :return: A list of User objects.
        """
        async with self.session.get(
            f"/platform/realms/{self.realm_id}/users/{selector}",
            params=dict(fields=super().prepare_fields(fields)),
            headers=self.get_headers(),
        ) as response:
            result = await self.get_result(response)
            return [
                User(
                    id=user["id"],
                    realm_id=self.realm_id,
                    metadata=user["metadata"],
                    fields={field: user[field] for field in fields},
                    session=self.session,
                    cid=self.cid,
                )
                for user in result
            ]
