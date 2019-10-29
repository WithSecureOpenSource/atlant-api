"""
Example demonstrating how to get access tokens from F-Secure Atlant's
authorization server.
"""

import requests
import click
from collections import namedtuple

DEFAULT_SCOPES = ("scan", "management")

Token = namedtuple("Token", ("token", "expires"))


class AuthException(Exception):
    """Authentication error."""

    def __init__(self, message, error_type):
        super().__init__(message)
        self.error_type = error_type


def fetch_token(address, client_id, client_secret, scopes):
    """
    Request access token from F-Secure Atlant's internal authorization server.

    address -- Authorization server address.
    client_id -- Client ID
    client_secret -- Client secret
    scopes -- Scopes to request for token. Client must be allowed to access
              all of the requested scopes.
    """
    response = requests.post(
        "https://{}/api/token/v1".format(address),
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "audience": "f-secure-atlant",
            "scope": " ".join(scopes),
        },
    )
    data = response.json()
    if response.status_code == 200:
        return Token(token=data["access_token"], expires=data["expires_in"])
    raise AuthException(
        data.get("error_description", "unknown authentication error"),
        data.get("error"),
    )


@click.command(
    help="Request access token from F-Secure Atlant's internal authorization server."
)
@click.option(
    "scope",
    "-s",
    multiple=True,
    metavar="SCOPE",
    help="scope to request for token",
)
@click.argument("address")
@click.argument("client_id")
@click.argument("client_secret")
def main(scope, address, client_id, client_secret):
    if not scope:
        scope = DEFAULT_SCOPES
    try:
        token_info = fetch_token(address, client_id, client_secret, scope)
        print("access token: {}".format(token_info.token))
    except AuthException as err:
        print("{}: {}".format(err.error_type, err))
