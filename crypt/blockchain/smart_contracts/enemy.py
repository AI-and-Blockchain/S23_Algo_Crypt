"""This contract contains logic for challenging an enemy
    and playing the game.
"""

import pyteal as pt
import beaker as bk

from beaker.lib.storage import BoxList, BoxMapping


class GameState(pt.abi.NamedTuple):
    player_hp: pt.abi.Field[pt.abi.Uint64]
    enemy_hp: pt.abi.Field[pt.abi.Uint64]
    game_over: pt.abi.Field[pt.abi.Bool]


class EnemyContractState:
    """State of the enemy contract."""

    owner = bk.GlobalStateValue(
        stack_type=pt.TealType.bytes,
        default=pt.Global.creator_address(),
        descr="Owner of the contract.",
    )

    name = bk.GlobalStateValue(
        stack_type=pt.TealType.bytes,
        default=pt.Bytes(""),
        descr="Name of the enemy.",
    )
    descr = bk.GlobalStateValue(
        stack_type=pt.TealType.bytes,
        default=pt.Bytes(""),
        descr="description of the enemy.",
    )

    image_uri = bk.GlobalStateValue(
        stack_type=pt.TealType.bytes,
        default=pt.Bytes(""),
        descr="IPFS URI of the image of the enemy.",
    )

    intelligence = bk.GlobalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="Intelligence of the enemy.",
    )
    strength = bk.GlobalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="Strength of the enemy.",
    )
    dexterity = bk.GlobalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="Dexterity of the enemy.",
    )

    hp = bk.GlobalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="Hit points of the enemy.",
    )

    price = bk.GlobalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="Price to challenge the enemy.",
    )

    current_challenger = bk.GlobalStateValue(
        stack_type=pt.TealType.bytes,
        default=pt.Bytes(""),
        descr="Address of the current challenger.",
    )

    current_enemy_hp = bk.LocalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="Current enemy hit points.",
    )

    current_player_hp = bk.LocalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="Current player hit points.",
    )

    game_active = bk.GlobalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="Boolean indicating if a game is active.",
    )


app = bk.Application(
    name="Enemy Contract",
    state=EnemyContractState,
)


@app.create
def create() -> pt.Expr:
    """Create the contract."""
    return app.initialize_global_state()


@app.external(authorize=bk.Authorize.only(app.state.owner.get()))
def bootstrap(
    name: pt.abi.String,
    descr: pt.abi.String,
    image_uri: pt.abi.String,
    intelligence: pt.abi.Uint64,
    strength: pt.abi.Uint64,
    dexterity: pt.abi.Uint64,
    hp: pt.abi.Uint64,
    price: pt.abi.Uint64,
) -> pt.Expr:
    """Bootstrap the contract."""
    return pt.Seq(
        app.state.name.set(name.get()),
        app.state.descr.set(descr.get()),
        app.state.image_uri.set(image_uri.get()),
        app.state.intelligence.set(intelligence.get()),
        app.state.strength.set(strength.get()),
        app.state.dexterity.set(dexterity.get()),
        app.state.hp.set(hp.get()),
        app.state.price.set(price.get()),
    )
