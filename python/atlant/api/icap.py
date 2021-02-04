import socket
from urllib.parse import urlencode

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
            h.append(b"%s: %s" % (key.encode("ASCII"), str(value).encode("ASCII")))
        content = b"""%s\r\n\r\n%s""" % (b"\r\n".join(h), body)
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
