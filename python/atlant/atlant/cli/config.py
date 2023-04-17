import json
from argparse import ArgumentTypeError
from typing import Any, List

import requests

from atlant.auth import Scope
from atlant.cli import config_file
from atlant.config import ConfigClient


def parse_json(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError as err:
        raise ArgumentTypeError("Value must be valid JSON.") from err


def install(parser: Any) -> None:
    parser = parser.add_parser(
        "config",
        description="Manage configuration.",
    )

    subparsers = parser.add_subparsers(required=True)

    # Set sub-command
    set_parser = subparsers.add_parser("set", description="Set setting's value.")
    set_parser.add_argument("setting", nargs="*")
    set_parser.add_argument("value", type=parse_json)
    set_parser.set_defaults(action=set_command)

    # Get sub-command
    get_parser = subparsers.add_parser("get", description="Get setting's value.")
    get_parser.add_argument("setting", nargs="*")
    get_parser.set_defaults(action=get_command)


def set_command(
    *,
    session: requests.Session,
    config: config_file.Config,
    setting: List[str],
    value: str,
) -> None:
    if config.management_url is None:
        raise Exception("Management URL must be specified.")
    client = ConfigClient(
        session,
        config.management_url,
        config.get_authenticator(session, [Scope.MANAGEMENT]),
    )
    client.set(setting, value)


def get_command(
    *,
    session: requests.Session,
    config: config_file.Config,
    setting: List[str],
) -> None:
    if config.management_url is None:
        raise Exception("Management URL must be specified.")
    client = ConfigClient(
        session,
        config.management_url,
        config.get_authenticator(session, [Scope.MANAGEMENT]),
    )
    value = client.get(setting)
    print(json.dumps(value, indent=2))
