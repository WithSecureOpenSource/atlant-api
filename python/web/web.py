import click

from flask import Flask, jsonify, request

from authentication.token import fetch_token
from scanning.scan import scan_and_poll_until_done

app = Flask(__name__)


def get_token():
    return fetch_token(
        app.config["authorization_address"],
        app.config["client_id"],
        app.config["client_secret"],
        ["scan"],
    ).token


def scan_file(token, file):
    return scan_and_poll_until_done(
        app.config["scanning_address"], token, file
    )


# In a real application, we would not want to get a new token for each request,
# but instead reuse a single token until it expires.
@app.route("/scan", methods=["POST"])
def scan():
    file = request.files.get("file")
    if file is not None:
        token = get_token()
        results = scan_file(token, file)
        safe = results.result in ("clean", "whitelisted")
        response = {"safe": safe}
        if not safe:
            response["detections"] = [
                {"category": d.category, "name": d.name}
                for d in results.detections
            ]
        return jsonify(response)
    return "Bad request", 400


@app.route("/", methods=["GET"])
def index():
    return app.send_static_file("index.html")


@click.command(help="Example web app that allows clients to scan files.")
@click.argument("authorization_address")
@click.argument("scanning_address")
@click.argument("server_address")
@click.argument("client_id")
@click.argument("client_secret")
def main(
    authorization_address,
    scanning_address,
    server_address,
    client_id,
    client_secret,
):
    address, port = server_address.split(":")
    app.config.update(
        client_id=client_id,
        client_secret=client_secret,
        authorization_address=authorization_address,
        scanning_address=scanning_address,
    )
    app.run(host=address, port=int(port))
