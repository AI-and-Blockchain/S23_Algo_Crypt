"""Contract for signing up for the game. Will mint the starting deck and transfer it to the player.

Fields:
    description: str (Global)

    starting_deck: List[str] (Global)
        List of card names to be minted for the player.

Methods:
    signup: () -> ()
        Mints the starting deck and transfers it to the player.

    update_description: (str) -> ()
        Updates the description of the contract.

    update_starting_deck: (List[str]) -> ()
        Updates the starting deck of the contract.
"""