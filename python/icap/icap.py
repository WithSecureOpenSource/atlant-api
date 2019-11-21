#!/usr/bin/env python3

import pprint
import socket
import sys
import os

DEFAULT_PORT=1344
EICAR = "X5O!P%@AP[4\\PZX54(P^)7CC)7}" \
        "$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"

def main():
    if sys.version_info < (3, 5):
        sys.stderr.write("Sorry, python 3.5 or later required\n")
        sys.exit(1)
    if len(sys.argv) < 3:
        bad_usage()
    if sys.argv[1] == "--options":
        if len(sys.argv) > 4:
            bad_usage()
        if len(sys.argv) == 4:
            do_options(sys.argv[2], int(sys.argv[3]))
        else:
            do_options(sys.argv[2])
    elif sys.argv[1] == "--scan":
        if len(sys.argv) < 4 or len(sys.argv) > 5:
            bad_usage()
        if len(sys.argv) == 5:
            do_scan(sys.argv[2], sys.argv[3], int(sys.argv[4]))
        else:
            do_scan(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "--eicar":
        if len(sys.argv) > 4:
            bad_usage()
        if len(sys.argv) == 4:
            do_eicar(sys.argv[2], int(sys.argv[3]))
        else:
            do_eicar(sys.argv[2])
    elif sys.argv[1] == "--help":
        usage(sys.stdout)
        return
    else:
        bad_usage()

def bad_usage():
    usage(sys.stderr)
    sys.exit(1)

def usage(f):
    f.write("""
A simple test program to exercise F-Secure's ICAP service.

Usage: {} ( --options | --scan file | --eicar ) serverhost [ port ]

""".format(os.path.basename(sys.argv[0])))

def do_options(host, port=DEFAULT_PORT):
    c = ICAPClient(host, port)
    pp = pprint.PrettyPrinter()
    pp.pprint(c.options())

def do_scan(pathname, host, port=DEFAULT_PORT):
    c = ICAPClient(host, port)
    pp = pprint.PrettyPrinter()
    with open(pathname, "rb") as contentf:
        pp.pprint(c.respmod(contentf.read()))

def do_eicar(host, port=DEFAULT_PORT):
    c = ICAPClient(host, port)
    pp = pprint.PrettyPrinter()
    pp.pprint(c.respmod(EICAR.encode("ASCII")))

class ICAPClient:
    def __init__(self, host, port=DEFAULT_PORT):
        self.s = socket.socket()
        self.host = host
        self.port = port
        if port == DEFAULT_PORT:
            self.hostport = host.encode("ASCII")
        else:
            self.hostport = "{}:{}".format(host, port).encode("ASCII")
        self.uri = b"icap://" + self.hostport + b"/"
        self.s.connect((host, port))

    def request(self, method, headers, body=b""):
        h = [ b"%s %s ICAP/1.0" % (method.encode("ASCII"), self.uri),
              b"Host: %s" % self.hostport ]
        for key, value in headers.items():
            h.append(b"%s: %s" % (
                key.encode("ASCII"), str(value).encode("ASCII")))
        self.s.send(b"""%s\r\n\r\n%s""" % (b"\r\n".join(h), body))

    def get_response(self):
        response = self.s.recv(1000)
        header, body = response.split(b"\r\n\r\n", 1)
        headers = [ h.split(b": ", 1) for h in header.split(b"\r\n") ]
        return headers, body

    def options(self):
        self.request(
            "OPTIONS", {
                "Encapsulated": "null-body=0"
            })
        return self.get_response()

    def respmod(self, content):
        self.request(
            "RESPMOD", {
                "Allow": 204,
                "Encapsulated": "req-hdr=0, res-hdr=0, res-body=0"
            },
            b"""%x\r
%s\r
0\r
\r
""" % (len(content), content))
        return self.get_response()

if __name__ == '__main__':
    main()
