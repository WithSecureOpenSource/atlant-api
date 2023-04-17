import logging
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Dict

import requests

from . import classify_url, config, config_file, get_access_token, scan_dir, scan_file


def parse_args() -> Dict[str, Any]:
    parser = ArgumentParser(description="Simple command-line client for Atlant.")
    parser.add_argument(
        "-c",
        "--config",
        metavar="PATH",
        type=Path,
        help="Configuration file path",
    )
    subparsers = parser.add_subparsers(required=True)
    get_access_token.install(subparsers)
    config.install(subparsers)
    classify_url.install(subparsers)
    scan_file.install(subparsers)
    scan_dir.install(subparsers)
    return vars(parser.parse_args())


def main() -> None:
    args = parse_args()
    sub_command = args.pop("action")
    config_path = args.pop("config")
    config = config_file.read_config_file(config_path)
    if config.log_level is not None:
        logging.basicConfig(
            level=config.log_level.to_numeric_level(),
            format="%(asctime)-15s (%(threadName)-0s) [%(levelname)s]: %(message)s",
        )
    with requests.Session() as session:
        if config.certificate_path is not None:
            session.verify = str(config.certificate_path)
        sub_command(session=session, config=config, **args)
