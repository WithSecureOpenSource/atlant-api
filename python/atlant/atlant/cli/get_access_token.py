from argparse import ArgumentTypeError
from enum import Enum
from typing import Any, Callable, List, Type, TypeVar

import requests

from atlant.auth import DEFAULT_SCOPES, OAuthClientCredentialsClient, Scope
from atlant.cli import config_file

EnumT = TypeVar("EnumT", bound=Enum)


def enum_parser(enum: Type[EnumT]) -> Callable[[str], EnumT]:
    values = {variant.value: variant for variant in enum}

    def parser(value: str) -> EnumT:
        if (result := values.get(value)) is not None:
            return result
        raise ArgumentTypeError(f"Value must be one of {', '.join(values)}.")

    return parser


def install(parser: Any) -> None:
    parser = parser.add_parser(
        "get-access-token",
        description="Get OAuth access token from authorization service.",
    )
    parser.add_argument(
        "--scopes",
        metavar="SCOPE",
        nargs="+",
        type=enum_parser(Scope),
        help="Specify desired scopes for the token.",
        default=list(DEFAULT_SCOPES),
    )
    parser.set_defaults(action=command)


def command(
    *,
    session: requests.Session,
    config: config_file.Config,
    scopes: List[Scope],
) -> None:
    if not isinstance(config.authentication, config_file.OAuthConfig):
        raise Exception("Command requires OAuth based authentication to be used.")
    client = OAuthClientCredentialsClient(
        session,
        config.authentication.authorization_url,
    )
    token = client.get_access_token(
        config.authentication.client_id,
        config.authentication.client_secret,
        config.authentication.audience,
        scopes,
    )
    print(token.access_token)
