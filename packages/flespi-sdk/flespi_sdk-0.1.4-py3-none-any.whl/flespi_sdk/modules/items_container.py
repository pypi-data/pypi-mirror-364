# from aiohttp import ClientSession
# from flespi_sdk.modules.realms.users.user import User
# from flespi_sdk.modules.flespi_session import FlespiSession


# class ItemsContainer(FlespiSession):
#     """
#     The RealmUsers class provides methods to manage users in a specific realm.
#     It allows for the retrieval of user information and the management of user roles.
#     """

#     def __init__(
#         self,
#         items_path: str,
#         item_class: type,
#         client_session: ClientSession,
#         cid: int | None = None,
#     ):
#         """
#         Initializes the RealmUsers class with a client instance.

#         :param client: The client instance used to make API requests.
#         """
#         super().__init__(client_session, cid)
#         self.items_path = items_path
#         self.itemClass = item_class

#     async def list(self, selector: str = "all"):
#         """
#         List all users in the realm.
#         :param selector: The selector to filter users.
#         :return: A list of User objects.
#         """
#         async with self.session.get(
#             f"{self.items_path}/{selector}",
#             headers=self.get_headers(),
#         ) as response:
#             result = await self.get_result(response)
#             return [
#                 self.itemClass(self.realm_id, user["id"], self.session, self.cid)
#                 for user in result
#             ]
