from flespi_sdk.account import Account


def main() -> None:
    print("Hello from plespi!")


async def login_with_token(token: str) -> Account:
    """
    Login to flespi with token
    :param token: token
    :return: Account object
    """
    if not token:
        raise ValueError("Token is required")
    if not isinstance(token, str):
        raise ValueError("Token must be a string")

    account = Account()
    await account.set_token(token)
    return account


async def login_with_realm(
    realm_public_id: str, realm_username: str, realm_password: str
):
    """
    Login to flespi with realm
    :param realm_public_id: realm public id
    :param realm_username: realm username
    :param realm_password: realm password
    :return: Account object
    """
    if not realm_public_id:
        raise ValueError("Realm public id is required")
    if not isinstance(realm_public_id, str):
        raise ValueError("Realm public id must be a string")
    if not realm_username:
        raise ValueError("Realm username is required")
    if not isinstance(realm_username, str):
        raise ValueError("Realm username must be a string")
    if not realm_password:
        raise ValueError("Realm password is required")
    if not isinstance(realm_password, str):
        raise ValueError("Realm password must be a string")

    account = Account()
    await account.realm_login(realm_public_id, realm_username, realm_password)
    return account
