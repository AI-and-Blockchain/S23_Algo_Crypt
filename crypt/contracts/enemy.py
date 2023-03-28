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

    Challenger Details: abi.NamedTuple (Local)
        name: str
        health: int
        strength: int
        intelligence: int
        dexterity: int

    Game State: abi.NamedTuple (Local)
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

from beaker import *
from pyteal import *

class Enemy(abi.NamedTuple):
    name: abi.Field[abi.String]
    health: abi.Field[abi.Uint64]
    strength: abi.Field[abi.Uint64]
    intelligence: abi.Field[abi.Uint64]
    dexterity: abi.Field[abi.Uint64]
    image_uri: abi.Field[abi.String]
    description: abi.Field[abi.String]

class Challenger(abi.NamedTuple):
    name: abi.Field[abi.String]
    user: abi.Field[abi.Address]
    health: abi.Field[abi.Uint64]
    strength: abi.Field[abi.Uint64]
    intelligence: abi.Field[abi.Uint64]
    dexterity: abi.Field[abi.Uint64]

class GameState(abi.NamedTuple):
    challenger: abi.Field[Challenger]
    enemy: abi.Field[Enemy]
    turn: abi.Field[abi.Uint64]
    current_enemy_health: abi.Field[abi.Uint64]
    current_challenger_health: abi.Field[abi.Uint64]
    challenger_won: abi.Field[abi.Bool]
    enemy_won: abi.Field[abi.Bool]

class EnemyState:
    owner: GlobalStateValue(
        stack_type=abi.Address,
        descr="Owner of the contract",
        default=Global.creator_address(),
    )

    enemy: GlobalStateValue(
        stack_type=Enemy,
        descr="Enemy Details",
        default=Enemy(
            name="",
            health=0,
            strength=0,
            intelligence=0,
            dexterity=0,
            image_uri="",
            description="",
        ),
    )
    game_state: LocalStateValue(
        stack_type=GameState,
        descr="Game State",
        default=GameState(
            challenger=Challenger(
                name="",
                user=Global.zero_address(),
                health=0,
                strength=0,
                intelligence=0,
                dexterity=0,
            ),
            enemy=Enemy(
                name="",
                health=0,
                strength=0,
                intelligence=0,
                dexterity=0,
                image_uri="",
                description="",
            ),
            turn=0,
            current_enemy_health=0,
            current_challenger_health=0,
            challenger_won=False,
            enemy_won=False,
        ),
    )

enemy = Application("Algocrypt Enemy Contract", EnemyState)

# Methods

@enemy.create
def create() -> Expr:
    return enemy.initialize_global_state()

@enemy.external(authorize=Authorize.only(enemy.owner))
def set_enemy_details(
    name: str, health: int, strength: int, intelligence: int, dexterity: int, image_uri: str, description: str
) -> Expr:
    return enemy.state.enemy.set(
        Enemy(
            name=name,
            health=health,
            strength=strength,
            intelligence=intelligence,
            dexterity=dexterity,
            image_uri=image_uri,
            description=description,
        )
    )

@enemy.external
def challenge(challenger: Challenger) -> Expr:
    return enemy.state.game_state.set(
        GameState(
            challenger=challenger,
            enemy=enemy.enemy.get(),
            turn=0,
            current_enemy_health=enemy.enemy.get().health,
            current_challenger_health=challenger.health,
            challenger_won=False,
            enemy_won=False,
        )
    )

@enemy.external
def play_turn(
    cards: abi.Tuple3[abi.Tuple2[abi.String, abi.String], 
                      abi.Tuple2[abi.String, abi.String], 
                      abi.Tuple2[abi.String, abi.String]]) -> Expr:
    game_state = enemy.state.game_state.get()
    enemy_details = game_state.enemy
    challenger_details = game_state.challenger

    phys_damage = 0
    mag_damage = 0
    phys_defense = 0
    mag_defense = 0
    for card in cards:
        if card[0] == "attack":
            if card[1] == "strength":
                phys_damage += challenger_details.strength
            elif card[1] == "intelligence":
                mag_damage += challenger_details.intelligence
        elif card[0] == "defense":
            if card[1] == "strength":
                phys_defense += challenger_details.strength
            elif card[1] == "intelligence":
                mag_defense += challenger_details.intelligence
        else:
            phys_defense += challenger_details.dexterity//2
            mag_defense += challenger_details.dexterity//2

    dex_diff = challenger_details.dexterity - enemy_details.dexterity
    str_diff = challenger_details.strength - enemy_details.strength
    int_diff = challenger_details.intelligence - enemy_details.intelligence

    preferred_def = "dodge" if dex_diff > 0 else "defense"
    if preferred_def == "defense":
        preferred_def = "strength" if str_diff > int_diff else "intelligence"
    preferred_att = "strength" if str_diff > int_diff else "intelligence"

    enemy_phys_damage = 0
    enemy_mag_damage = 0
    enemy_phys_defense = 0
    enemy_mag_defense = 0
    if preferred_att == "strength":
        enemy_phys_damage += enemy_details.strength
    else:
        enemy_mag_damage += enemy_details.intelligence

    if preferred_def == "intelligence":
        enemy_mag_defense += enemy_details.intelligence
    elif preferred_def == "strength":
        enemy_phys_defense += enemy_details.strength
    else:
        enemy_phys_defense += enemy_details.dexterity//2
        enemy_mag_defense += enemy_details.dexterity//2

    damage_to_enemy = max(0, phys_damage - enemy_phys_defense) + max(0, mag_damage - enemy_mag_defense)
    damage_to_challenger = max(0, enemy_phys_damage - phys_defense) + max(0, enemy_mag_damage - mag_defense)

    return enemy.state.game_state.set(
        game_state.set(
            turn=game_state.turn + 1,
            current_enemy_health=game_state.current_enemy_health - damage_to_enemy,
            current_challenger_health=game_state.current_challenger_health - damage_to_challenger,
        )
    )

@Subroutine(TealType.none)
def end_game() -> Expr:
    raise NotImplementedError

@Subroutine(TealType.none)
def attack_challenger(attack_type: abi.String) -> Expr:
    game_state = enemy.state.game_state.get()
    enemy_details = game_state.enemy
    challenger_details = game_state.challenger

    if attack_type == "strength":
        damage = enemy_details.strength
    elif attack_type == "intelligence":
        damage = enemy_details.intelligence
    else:
        return enemy.state.game_state.set(game_state)

    return enemy.state.game_state.set(
        game_state.set(
            current_challenger_health=game_state.current_challenger_health - damage,
        )
    ) 
    