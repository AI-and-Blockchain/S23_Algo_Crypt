"""This module contains functions for gameplay
    on the blockchain. Actions must be signed by
    the player's private key, and the action must
    be validated by the enemy contract, which   
    will return the result of the move, the enemy's
    move, and the new state of the game.
"""
from argparse import ArgumentParser
import typing
import os

from dotenv import load_dotenv

import pyteal as pt
from algosdk.v2client.algod import AlgodClient
from algosdk.atomic_transaction_composer import TransactionWithSigner
from algosdk import transaction
from beaker import consts

from algokit_utils import (
    ApplicationClient,
    get_account
)

load_dotenv(os.path.join(
    os.path.dirname(__file__),
    "../.env"
))


class GameState:
    """Class for storing the state of the game."""
    player_hp: int
    enemy_hp: int
    finished: bool


def challenge(
    algod_client: AlgodClient,
    enemy_app_id: int,
    address: str,
    player_hp: int,
    player_int: int,
    player_str: int,
    player_dex: int,
) -> bool:
    """Challenge the enemy contract.

    Args:
        address (str): address of the player
        enemy_contract (str): address of the enemy contract

    Returns:
        bool:
            True if the challenge was successful, False otherwise.
    """
    sender = get_account(algod_client, address)
    app_client = ApplicationClient(
        algod_client=algod_client,
        app_spec=os.path.join(
            os.path.dirname(__file__),
            "../blockchain/smart_contracts/artifacts/Enemy Contract/application.json"
        ),
        app_id=enemy_app_id,
        sender=sender
    )
    
    txn = TransactionWithSigner(
        transaction.PaymentTxn(
            sender=sender.address,
            sp=algod_client.suggested_params(),
            receiver=app_client.app_address,
            amt=0
        ),
        sender.signer
    )

    app_client.opt_in(txn=txn)

    txn = TransactionWithSigner(
        transaction.PaymentTxn(
            sender=sender.address,
            sp=algod_client.suggested_params(),
            receiver=app_client.app_address,
            amt=10*consts.algo
        ),
        sender.signer
    )

    app_client.call(
        "challenge",
        txn=txn,
        player_hp=player_hp,
        player_intelligence=player_int,
        player_strength=player_str,
        player_dexterity=player_dex
    )

    return True


def submit_turn(
    algod_client: AlgodClient,
    enemy_app_id: int,
    address: str,
    actions: typing.Tuple[
        typing.Tuple[str, str],
        typing.Tuple[str, str],
        typing.Tuple[str, str]
        ]
) -> GameState:
    """Submit a turn to the enemy contract.

    Args:
        address (str): address of the player
        enemy_contract (str): address of the enemy contract
        actions (Tuple[Tuple[str, str], Tuple[str, str], Tuple[str, str]]):
            the player's actions. Actions are submitted as a 3-Tuple of
            actions represented by 2-Tuples of action and attribute.

    Returns:
        GameState:
            the state of the game after the turn has been submitted.
    """
    app_client = ApplicationClient(
        algod_client=algod_client,
        app_spec=os.path.join(
            os.path.dirname(__file__),
            "../blockchain/smart_contracts/artifacts/Enemy Contract/application.json"
        ),
        app_id=enemy_app_id,
        sender=get_account(algod_client, address)
    )
    return app_client.call(
        "submit_plays",
        [x[0] for x in actions],
        [x[1] for x in actions],
    )


def main():
    """Main function for the module."""
    parser = ArgumentParser()
    parser.add_argument(
        "address",
        help="address of the player"
    )
    parser.add_argument(
        "enemy_contract",
        help="address of the enemy contract"
    )
    parser.add_argument(
        "action1",
        help="first action of the player"
    )
    parser.add_argument(
        "action2",
        help="second action of the player"
    )
    parser.add_argument(
        "action3",
        help="third action of the player"
    )
    parser.add_argument(
        "attribute1",
        help="attribute of the first action"
    )
    parser.add_argument(
        "attribute2",
        help="attribute of the second action"
    )
    parser.add_argument(
        "attribute3",
        help="attribute of the third action"
    )
    args = parser.parse_args()
    actions = (
        (args.action1, args.attribute1),
        (args.action2, args.attribute2),
        (args.action3, args.attribute3)
    )
    enemy_actions, game_state = submit_turn(
        args.address,
        args.enemy_contract,
        actions
    )
    print("Enemy actions:")
    print(enemy_actions)
    print("Game state:")
    print(game_state)


if __name__ == "__main__":
    main()
