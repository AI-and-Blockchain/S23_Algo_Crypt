"""This module contains functions for signing up
    users to the game. It includes interacting with
    the membership contract, opting into all assets,
    storing the private key, etc.
"""
from argparse import ArgumentParser
import os
from dotenv import load_dotenv

from crypt.blockchain.smart_contracts.membership import app as membership_app
from algokit_utils.application_client import ApplicationClient
from algokit_utils import get_algod_client
from beaker import client, sandbox 

load_dotenv("../.env")


accts = sandbox.get_accounts()

acct1 = accts.pop() #admin address?

algod_client = get_algod_client()
app_client = client.ApplicationClient(
    client=algod_client,
    app_spec=membership_app,
    app_id=os.getenv("METASTATE_APP_ID"),
    signer = acct1
)


def opt_in(asset_id: int) -> None:
    """Opt into an asset.

    Args:
        asset_id (int): asset id
    """
    raise NotImplementedError


def opt_in_all() -> None:
    """Opt into all assets."""
    raise NotImplementedError


def register_membership(address: str) -> None:
    """Register address with membership contract.

    Args:
        address (str): address to register
    """
    app_client.opt_in()
    app_client.call("signup", address = address, strengh = 5, intelligence = 5, dexterity = 5)
    


def store_private_key(private_key: str) -> None:
    """Store private key in a file.

    Args:
        private_key (str): private key
    """
    with(open(".env", "w+")) as f:
        f.write("PRIVATE_KEY={}".format(private_key))

def main(address: str, private_key: str):
    opt_in_all()
    register_membership(address)
    store_private_key(private_key)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("address", type=str)
    parser.add_argument("private_key", type=str)
    args = parser.parse_args()

    main(args.address, args.private_key)
