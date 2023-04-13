"""This module contains functions for generating
    marketplace listings for enemies and cards.
"""
from ..blockchain.smart_contracts.nft_exchange import app as nft_app

from argparse import ArgumentParser
import os

from dotenv import load_dotenv

from beaker.sandbox import (
    get_algod_client,
    get_indexer_client,
)

from algokit_utils import (
    ApplicationClient,
    get_account,
)

load_dotenv(os.path.join(
    os.path.dirname(__file__),
    "../.env"
))


def generate_card_listing(
        name: str, description: str, image: str, asset_id: int, price: int, owner: str
) -> str:
    """Generate a marketplace listing for a card.

    Args:
        name (str): name of card
        description (str): description of card
        image (str): ipfs uri of image of card
        price (int): price of card in microalgos

    Returns:
        str: marketplace listing
    """
    algod_client = get_algod_client()
    owner_acct = get_account(algod_client, owner)
    app_client = ApplicationClient(
        algod_client=algod_client,
        app_spec=nft_app,
        signer=owner_acct
    )

    app_client.create()

    return app_client.call(
        "update",
        name=name,
        descr=description,
        image_uri=image,
        asset_id=asset_id,
        price=price,
    )


def lookup_and_generate(asset_id: int, price: int, owner: str) -> str:
    """Generate a marketplace listing for an asset.

    Args:
        asset_id (int): asset id
        price (int): price of asset in microalgos

    Returns:
        str: marketplace listing

    if asset_id lookup -> card: generate_card_listing
    if asset_id lookup -> enemy: generate_enemy_listing

    """
    algod_client = get_algod_client()
    indexer = get_indexer_client()
    owner = get_account(algod_client, owner)

    asset_info = indexer.asset_info(asset_id)
    return generate_card_listing(
        name=asset_info["asset_name"],
        description=asset_info["asset_unit_name"],
        image=asset_info["asset_url"],
        asset_id=asset_id,
        price=price,
        owner=owner
    )


def main(asset_id: int, price: int):
    listing = lookup_and_generate(asset_id, price)
    print(listing)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("asset_id", type=int)
    parser.add_argument("price", type=int)
    args = parser.parse_args()
    main(args.asset_id, args.price)
