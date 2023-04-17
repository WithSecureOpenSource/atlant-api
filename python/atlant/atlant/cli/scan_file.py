from argparse import ArgumentTypeError, FileType
from typing import Any, BinaryIO, Optional

import requests

from atlant.auth import Scope
from atlant.cli import config_file
from atlant.scan import ScanClient, ScanMetadata, ScanSettings


def parse_bool(value: str) -> bool:
    value = value.lower()
    if value in {"yes", "y", "true", "on", "1"}:
        return True
    elif value in {"no", "n", "false", "off", "0"}:
        return False
    else:
        raise ArgumentTypeError("Boolean expected")


def install(parser: Any) -> None:
    parser = parser.add_parser(
        "scan-file",
        description="Scan a file.",
    )

    parser.add_argument(
        "--scan-archives",
        metavar="BOOL",
        help="Extract archives while scanning.",
        type=parse_bool,
    )
    parser.add_argument(
        "--max-nested",
        metavar="INT",
        help="Maximum number of nested archives to scan.",
        type=int,
    )
    parser.add_argument(
        "--max-scan-time",
        metavar="INT",
        help="Maximum scan time.",
        type=int,
    )
    parser.add_argument(
        "--stop-on-first",
        metavar="BOOL",
        help="Stop scanning on first detection.",
        type=parse_bool,
    )
    parser.add_argument(
        "--allow-metadata-upstreaming",
        metavar="BOOL",
        help="Allow upstreaming metadata.",
        type=parse_bool,
    )

    parser.add_argument("file", type=FileType("rb"), help="File to scan.")

    parser.set_defaults(action=command)


def command(
    *,
    session: requests.Session,
    config: config_file.Config,
    scan_archives: Optional[bool],
    max_nested: Optional[int],
    max_scan_time: Optional[int],
    stop_on_first: Optional[bool],
    allow_metadata_upstreaming: Optional[bool],
    file: BinaryIO,
) -> None:
    client = ScanClient(
        session,
        config.scanning_url,
        config.get_authenticator(session, [Scope.SCAN]),
    )
    scan_settings = ScanSettings(
        scan_archives=scan_archives,
        max_nested=max_nested,
        max_scan_time=max_scan_time,
        stop_on_first=stop_on_first,
        allow_upstream_metadata=allow_metadata_upstreaming,
    )
    metadata = ScanMetadata(scan_settings=scan_settings)
    response = client.scan_until_completion(metadata, file)
    print(response.json(exclude={"poll_settings"}, indent=2))
