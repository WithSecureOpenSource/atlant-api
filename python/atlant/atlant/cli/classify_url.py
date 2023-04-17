import json
from typing import Any

import requests

from atlant.auth import Scope
from atlant.cli import config_file
from atlant.scan import ScanClient, ScanContentMetadata, ScanMetadata


def install(parser: Any) -> None:
    parser = parser.add_parser(
        "classify-url",
        description="Classify URL address.",
    )
    parser.add_argument("url", help="URL address to classify.")
    parser.set_defaults(action=command)


def command(
    *,
    session: requests.Session,
    config: config_file.Config,
    url: str,
) -> None:
    client = ScanClient(
        session,
        config.scanning_url,
        config.get_authenticator(session, [Scope.SCAN]),
    )
    content_meta = ScanContentMetadata(uri=url)
    metadata = ScanMetadata(content_meta=content_meta)
    response = client.scan_until_completion(metadata)
    print(json.dumps(response.uri_categories or [], indent=2))
