"""
Example demonstrating how to change setting values using F-Secure Atlant's
configuration API.
"""

import requests
import click
import json
import urllib.parse

# See authentication/token.py for example on how to get authentication tokens.
from authentication.token import fetch_token

from configuration.common import APIException


def set_setting(address, token, setting, value):
    response = requests.put(
        "https://{}/api/atlant/config/v1/{}".format(
            address, "/".join(urllib.parse.quote(p, safe="") for p in setting)
        ),
        headers={"Authorization": "Bearer {}".format(token)},
        json=value,
    )
    if response.status_code != 200:
        error = response.json()
        raise APIException(error["title"], error["message"])


@click.command(
    help="Change setting value using F-Secure Atlant's configuration API."
)
@click.argument("authorization_address")
@click.argument("management_address")
@click.argument("client_id")
@click.argument("client_secret")
@click.argument("setting", nargs=-1)
@click.argument("value", nargs=1)
def main(
    authorization_address,
    management_address,
    client_id,
    client_secret,
    setting,
    value,
):
    token_info = fetch_token(
        authorization_address, client_id, client_secret, ["management"]
    )
    value = json.loads(value)
    set_setting(management_address, token_info.token, setting, value)
