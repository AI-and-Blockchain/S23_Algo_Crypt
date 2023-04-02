"""This module contains functions for generating
    marketplace listings for enemies and cards.
"""
from argparse import ArgumentParser


def generate_card_listing(
        name: str, description: str, image: str, price: int
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
    raise NotImplementedError


def generate_enemy_listing(
        name: str, description: str, stats: str, image: str, price: int
) -> str:
    """Generate a marketplace listing for an enemy.

    Args:
        name (str): name of enemy
        description (str): description of enemy
        stats (str): stats of enemy
        image (str): ipfs uri of image of enemy
        price (int): price of enemy in microalgos

    Returns:
        str: marketplace listing
    """
    raise NotImplementedError


def generate_listing(asset_id: int, price: int) -> str:
    """Generate a marketplace listing for an asset.

    Args:
        asset_id (int): asset id
        price (int): price of asset in microalgos

    Returns:
        str: marketplace listing

    if asset_id lookup -> card: generate_card_listing
    if asset_id lookup -> enemy: generate_enemy_listing

    """
    raise NotImplementedError


def main(asset_id: int, price: int):
    listing = generate_listing(asset_id, price)
    print(listing)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("asset_id", type=int)
    parser.add_argument("price", type=int)
    args = parser.parse_args()
    main(args.asset_id, args.price)
