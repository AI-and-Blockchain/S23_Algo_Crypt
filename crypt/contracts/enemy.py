""" Enemy contract.

Fields:
    Enemy Details: abi.NamedTuple (Global)
        name: str
        health: int
        strength: int
        intelligence: int
        dexterity: int
        image_uri: str
        description: str

    Challenger Details: abi.NamedTuple
        name: str
        health: int
        strength: int
        intelligence: int
        dexterity: int

    Game State: abi.NamedTuple
        challenger: Challenger Details
        enemy: Enemy Details
        turn: int
        current_enemy_health: int
        current_challenger_health: int
        challenger_won: bool
        enemy_won: bool

Methods:
    challenge: (Challenger Details) -> (Game State)
        Starts a new game with the given challenger details.
    
    attack: (str) -> (Game State)
        Attacks the enemy with the given attack type.
        Valid attack types are "strength" and "intelligence".

    defend: (str) -> (Game State)
        Defends against the enemy's attack with the given defense type.
        Valid defense types are "strength" and "intelligence".

    dodge: () -> (Game State)
        Dodges the enemy's attack.

    surrender: () -> (Game State)
        Surrenders the game.

    reset: () -> (Game State)
        Resets the game to the initial state.
"""