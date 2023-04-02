"""This module contains functions for gameplay
    on the blockchain. Actions must be signed by
    the player's private key, and the action must
    be validated by the enemy contract, which   
    will return the result of the move, the enemy's
    move, and the new state of the game.
"""
from argparse import ArgumentParser
import typing


class GameState:
    """Class for storing the state of the game."""
    player_hp: int
    enemy_hp: int
    finished: bool


def submit_turn(
        address: str, 
        enemy_contract: str,
        actions: typing.Tuple[
            typing.Tuple[str, str],
            typing.Tuple[str, str],
            typing.Tuple[str, str]
            ]
) -> typing.Tuple[
        typing.Tuple[
            typing.Tuple[str, str],
            typing.Tuple[str, str],
            typing.Tuple[str, str]
            ],
        GameState
        ]:
    """Submit a turn to the enemy contract.

    Args:
        address (str): address of the player
        enemy_contract (str): address of the enemy contract
        actions (Tuple[Tuple[str, str], Tuple[str, str], Tuple[str, str]]):
            the player's actions. Actions are submitted as a 3-Tuple of
            actions represented by 2-Tuples of action and attribute.

    Returns:
        Tuple[
            Tuple[Tuple[str, str],
            Tuple[str, str],
            Tuple[str, str]],
        GameState]:
            the enemy's actions, and the new game state
    """
    raise NotImplementedError


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
