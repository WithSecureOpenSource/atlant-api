"""
Example demonstrating how to get setting values using F-Secure Atlant's
configuration API.
"""

import requests
import click
import urllib.parse
from pprint import pprint

# See authentication/token.py for example on how to get authentication tokens.
from authentication.token import fetch_token

from configuration.common import APIException

def get_setting(address, token, setting):
    response = requests.get(
        "https://{}/api/atlant/config/v1/{}".format(
            address, "/".join(urllib.parse.quote(p, safe="") for p in setting)
        ),
        headers={
            "Authorization": "Bearer {}".format(token)
        },
    )
    data = response.json()
    if response.status_code == 200:
        return data
    raise APIException(data["title"], data["message"])


@click.command(
    help="Get setting value using F-Secure Atlant's configuration API."
)
@click.argument("authorization_address")
@click.argument("management_address")
@click.argument("client_id")
@click.argument("client_secret")
@click.argument("setting", nargs=-1)
def main(
    authorization_address,
    management_address,
    client_id,
    client_secret,
    setting,
):
    token_info = fetch_token(
        authorization_address, client_id, client_secret, ["management"]
    )
    value = get_setting(management_address, token_info.token, setting)

    pprint(value)
