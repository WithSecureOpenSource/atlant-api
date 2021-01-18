#!/usr/bin/env python3

import os
import pprint
import socket
import sys
from urllib.parse import urlencode

import click

DEFAULT_PORT = 1344


class ICAPClient:
    def __init__(self, host, port=DEFAULT_PORT):
        self.s = socket.socket()
        self.host = host
        self.port = port
        if port == DEFAULT_PORT:
            self.hostport = host
        else:
            self.hostport = "{}:{}".format(host, port)
        self.s.connect((host, port))

    def request(self, method, uri_params, headers, body=b""):
        params = "?{}".format(urlencode(uri_params)) if uri_params else ""
        uri = "icap://{}/{}".format(self.hostport, params).encode("ASCII")
        h = [
            b"%s %s ICAP/1.0" % (method.encode("ASCII"), uri),
            b"Host: %s" % self.hostport.encode("ASCII"),
        ]
        for key, value in headers.items():
            h.append(
                b"%s: %s" % (key.encode("ASCII"), str(value).encode("ASCII"))
            )
        content = b"""%s\r\n\r\n%s""" % (b"\r\n".join(h), body)
        print(content)
        self.s.send(content)

    def get_response(self):
        response = self.s.recv(1000)
        header, body = response.split(b"\r\n\r\n", 1)
        headers = [h.split(b": ", 1) for h in header.split(b"\r\n")]
        return headers, body

    def options(self):
        self.request("OPTIONS", {}, {"Encapsulated": "null-body=0"})
        return self.get_response()

    def respmod(self, content, uri_params={}, extra_headers={}):
        self.request(
            "RESPMOD",
            uri_params,
            {
                "Allow": 204,
                "Encapsulated": "req-hdr=0, res-hdr=0, res-body=0",
                **extra_headers,
            },
            b"""%x\r
%s\r
0\r
\r
"""
            % (len(content), content),
        )
        return self.get_response()


@click.group()
def cli():
    pass


@cli.command("options")
@click.argument("host")
@click.argument("port", type=int, required=False, default=DEFAULT_PORT)
def options(host, port):
    c = ICAPClient(host, port)
    pp = pprint.PrettyPrinter()
    pp.pprint(c.options())


@cli.command("scan")
@click.option("--security-cloud", is_flag=True)
@click.option("--scan-embedded-urls", is_flag=True)
@click.option("--antispam", is_flag=True)
@click.option("--sha1")
@click.option("--uri")
@click.option("--content-type")
@click.option("--forbidden-uri-category", multiple=True)
@click.option("--ip")
@click.option("--sender")
@click.option("--recipient", multiple=True)
@click.argument("file", type=click.File("rb"))
@click.argument("host")
@click.argument("port", type=int, required=False, default=DEFAULT_PORT)
def scan(
    security_cloud,
    scan_embedded_urls,
    antispam,
    sha1,
    uri,
    content_type,
    forbidden_uri_category,
    ip,
    sender,
    recipient,
    file,
    host,
    port,
):
    uri_params = {}
    if security_cloud:
        uri_params["security_cloud"] = "1"
    if scan_embedded_urls:
        uri_params["scan_embedded_urls"] = "1"
    if antispam:
        uri_params["antispam"] = "1"
    extra_headers = {}
    if sha1:
        extra_headers["X-Meta-SHA1"] = sha1
    if uri:
        extra_headers["X-Meta-URI"] = uri
    if content_type:
        extra_headers["X-Meta-Content-Type"] = content_type
    if forbidden_uri_category:
        extra_headers["X-Forbidden-URI-Categories"] = ", ".join(
            forbidden_uri_category
        )
    if ip:
        extra_headers["X-Meta-IP"] = ip
    if sender:
        extra_headers["X-Meta-Sender"] = sender
    if recipient:
        extra_headers["X-Meta-Recipients"] = ", ".join(recipient)
    c = ICAPClient(host, port)
    pp = pprint.PrettyPrinter()
    pp.pprint(c.respmod(file.read(), uri_params, extra_headers))


def main():
    if sys.version_info < (3, 5):
        sys.stderr.write("Sorry, python 3.5 or later required\n")
        sys.exit(1)

    cli()


if __name__ == "__main__":
    cli()
