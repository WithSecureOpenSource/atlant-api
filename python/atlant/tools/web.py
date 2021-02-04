from argparse import ArgumentParser

from atlant.api import APIException, AuthClient, ScanClient, ScanResult
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_scanner():
    authenticator = AuthClient(
        app.config["authorization_address"],
        app.config["client_id"],
        app.config["client_secret"],
    )
    return ScanClient(app.config["scanner_address"], authenticator)


@app.route("/scan", methods=["POST"])
def scan():
    file = request.files.get("file")
    if file is not None:
        results = get_scanner().scan_until_complete(file)
        safe = results.result == ScanResult.CLEAN
        response = {"safe": safe}
        if not safe:
            response["detections"] = [
                {"category": d.category.name, "name": d.name}
                for d in results.detections
            ]
        return jsonify(response)
    return "Bad request", 400


@app.route("/", methods=["GET"])
def index():
    return app.send_static_file("index.html")


def parse_args():
    parser = ArgumentParser(
        description="Example web app that allows clients to scan files."
    )
    parser.add_argument("authorization_address", help="Authorization server address.")
    parser.add_argument("scanner_address", help="Scanning server address.")
    parser.add_argument("server_address", help="Local address to bind.")
    parser.add_argument("client_id", help="OAuth2 client ID")
    parser.add_argument("client_secret", help="OAuth2 client secret")
    return parser.parse_args()


def main():
    args = parse_args()
    address, port = args.server_address.split(":", 1)
    authenticator = AuthClient(
        args.authorization_address, args.client_id, args.client_secret
    )
    scanner = ScanClient(args.scanner_address, authenticator)
    app.config.update(
        client_id=args.client_id,
        client_secret=args.client_secret,
        authorization_address=args.authorization_address,
        scanner_address=args.scanner_address,
    )
    app.run(host=address, port=int(port))
