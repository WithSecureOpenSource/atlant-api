import os
from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint

from atlant.api.icap import DEFAULT_PORT, ICAPClient


def parse_args():
    parser = ArgumentParser(
        description="Scan files using F-Secure Atlant's ICAP scanning API."
    )
    parser.add_argument("host")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True
    options_cmd = subparsers.add_parser("options")
    options_cmd.set_defaults(command=options)
    scan_cmd = subparsers.add_parser("scan")
    scan_cmd.add_argument("--security-cloud", action="store_true")
    scan_cmd.add_argument("--scan-embedded-urls", action="store_true")
    scan_cmd.add_argument("--antispam", action="store_true")
    scan_cmd.add_argument("--sha1", metavar="HASH")
    scan_cmd.add_argument("--uri")
    scan_cmd.add_argument("--content-type")
    scan_cmd.add_argument("--forbidden-uri-categories", nargs="+", metavar="CATEGORY")
    scan_cmd.add_argument("--ip", metavar="ADDRESS")
    scan_cmd.add_argument("--sender", metavar="ADDRESS")
    scan_cmd.add_argument("--recipients", nargs="+", metavar="ADDRESS")
    scan_cmd.add_argument("file", type=Path)
    scan_cmd.set_defaults(command=scan)
    return parser.parse_args()


def main():
    args = parse_args()
    args.command(args)


def options(args):
    client = ICAPClient(args.host, args.port)
    pprint(client.options())


def scan(args):
    uri_params = {}
    if args.security_cloud:
        uri_params["security_cloud"] = "1"
    if args.scan_embedded_urls:
        uri_params["scan_embedded_urls"] = "1"
    if args.antispam:
        uri_params["antispam"] = "1"
    extra_headers = {}
    if args.sha1:
        extra_headers["X-Meta-SHA1"] = args.sha1
    if args.uri:
        extra_headers["X-Meta-URI"] = args.uri
    if args.content_type:
        extra_headers["X-Meta-Content-Type"] = args.content_type
    if args.forbidden_uri_categories:
        extra_headers["X-Forbidden-URI-Categories"] = ", ".join(
            args.forbidden_uri_categories
        )
    if args.ip:
        extra_headers["X-Meta-IP"] = args.ip
    if args.sender:
        extra_headers["X-Meta-Sender"] = args.sender
    if args.recipients:
        extra_headers["X-Meta-Recipients"] = ", ".join(args.recipients)
    client = ICAPClient(args.host, args.port)
    pprint(client.respmod(args.file.read_bytes(), uri_params, extra_headers))
