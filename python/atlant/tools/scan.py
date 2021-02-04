from pprint import pprint

from pathlib import Path
from argparse import ArgumentParser
from atlant.api import AuthClient, ScanClient, APIException


def parse_args():
    parser = ArgumentParser(
        description="Scan files using F-Secure Atlant's scanning API."
    )
    parser.add_argument("authorization_address", help="Authorization server address.")
    parser.add_argument("scanner_address", help="Scanning server address.")
    parser.add_argument("client_id", help="OAuth2 client ID")
    parser.add_argument("client_secret", help="OAuth2 client secret")
    parser.add_argument("file", type=Path, help="File to scan")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        authenticator = AuthClient(
            args.authorization_address, args.client_id, args.client_secret
        )
        scanner = ScanClient(args.scanner_address, authenticator)
        pprint(scanner.scan_until_complete(args.file.read_bytes()))
    except APIException as err:
        print("{}: {}".format(err, err.long_description))
        exit(1)
