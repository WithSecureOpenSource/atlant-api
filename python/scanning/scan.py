"""
Example demonstrating how to scan files using F-Secure Atlant's
scanning API.
"""

import json
import time
from collections import namedtuple
from pprint import pprint

import click
import requests

# See authentication/token.py for example on how to get authentication tokens.
from authentication.token import fetch_token


class ScanException(Exception):
    """Scanning Error"""

    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code


Detection = namedtuple("Detection", ("category", "name", "member_name"))

Response = namedtuple(
    "Response", ("status", "result", "detections", "task_url", "retry_after")
)


def make_response(response):
    # These will be set in the case status_code is 202
    task_url = response.headers.get("Location")
    retry_after = response.headers.get("Retry-After")
    if retry_after is not None:
        retry_after = int(retry_after)
    data = response.json()
    return Response(
        status=data.get("status"),
        result=data.get("scan_result"),
        detections=[
            Detection(
                category=detection.get("category"),
                name=detection.get("name"),
                member_name=detection.get("member_name"),
            )
            for detection in data.get("detections", [])
        ],
        task_url=task_url,
        retry_after=retry_after,
    )


def scan_file(address, token, path):
    metadata = {}
    with open(path, "rb") as f:
        parts = (
            ("metadata", (None, json.dumps(metadata))),
            ("data", (None, f.read())),
        )
    response = requests.post(
        "https://{}/api/scan/v1".format(address),
        files=parts,
        headers={"Authorization": "Bearer {}".format(token)},
    )

    if response.status_code in (200, 202):
        return make_response(response)

    raise ScanException("scan error", response.status_code)


def poll_task(address, token, task_url):
    response = requests.get(
        "https://{}{}".format(address, task_url),
        headers={"Authorization": "Bearer {}".format(token)},
    )
    if response.status_code == 200:
        return make_response(response)
    raise ScanException(
        "unknown response form scanning API", response.status_code
    )


def scan_and_poll_until_done(address, token, path):
    """
    Scan file and poll until completion.
    """
    response = scan_file(address, token, path)
    if response.status == "complete":
        return response
    elif response.status == "pending":
        task_url = response.task_url
        time.sleep(response.retry_after)
        while True:
            response = poll_task(address, token, task_url)
            if response.status == "complete":
                return response
            elif response.status == "pending":
                time.sleep(response.retry_after)
            else:
                break
    raise ScanException(
        "unknown response from scanning API", response.status_code
    )


@click.command(help="Scan files using F-Secure Atlant's scanning API.")
@click.argument("authorization_address")
@click.argument("scanning_address")
@click.argument("client_id")
@click.argument("client_secret")
@click.argument(
    "file", type=click.Path(exists=True, dir_okay=False, resolve_path=True)
)
def main(
    authorization_address, scanning_address, client_id, client_secret, file
):
    token_info = fetch_token(
        authorization_address, client_id, client_secret, ["scan"]
    )
    response = scan_and_poll_until_done(
        scanning_address, token_info.token, file
    )
    pprint(response)
