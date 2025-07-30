from aiohttp import ClientSession

from flespi_sdk.modules.realms.realm_home import RealmHome
from flespi_sdk.modules.realms.realm_token_params import RealmTokenParams
from flespi_sdk.modules.realms.users import Users
from flespi_sdk.modules.item_with_metadata import ItemWithMetadata


class Realm(ItemWithMetadata):
    """
    Represents a realm in the Flespi system.
    """

    def __init__(
        self,
        id: int,
        metadata: dict,
        fields: dict,
        session: ClientSession,
        cid: int | None = None,
    ):
        super().__init__(
            id=id,
            item_path=f"platform/realms/{id}",
            metadata=metadata,
            fields=fields,
            session=session,
            cid=cid,
        )
        self.users = Users(
            realm_id=id,
            client_session=session,
            cid=cid,
        )

        self.home = RealmHome(realm_id=id, session=session, cid=cid)
        self.token_params = RealmTokenParams(realm_id=id, session=session, cid=cid)
