from argparse import ArgumentParser
from atlant.api import AuthClient, APIException


def parse_args():
    parser = ArgumentParser(
        description="Request access token from F-Secure Atlant's internal authorization server."
    )
    parser.add_argument("--scopes", metavar="SCOPE", nargs="+", help="Scopes.")
    parser.add_argument("authorization_address", help="Authorization server address.")
    parser.add_argument("client_id", help="OAuth2 client ID")
    parser.add_argument("client_secret", help="OAuth2 client secret")
    return parser.parse_args()


def main():
    args = parse_args()
    authenticator = AuthClient(
        args.authorization_address, args.client_id, args.client_secret
    )
    try:
        if not args.scopes:
            token_info = authenticator.fetch_token()
        else:
            token_info = authenticator.fetch_token(args.scopes)
        print("access token: {}".format(token_info.token))
    except APIException as err:
        print("{}: {}".format(err, err.long_description))
        exit(1)
