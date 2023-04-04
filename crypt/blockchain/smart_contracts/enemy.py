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

    current_player_intelligence = bk.LocalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="Current player intelligence.",
    )

    current_player_strength = bk.LocalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="Current player strength.",
    )

    current_player_dexterity = bk.LocalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="Current player dexterity.",
    )

    game_active = bk.GlobalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="Boolean indicating if a game is active.",
    )

    enemy_defeated = bk.GlobalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="Boolean indicating if the enemy has been defeated.",
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


@app.external
def challenge(
    txn: pt.abi.PaymentTransaction,
    player_hp: pt.abi.Uint64,
    player_intelligence: pt.abi.Uint64,
    player_strength: pt.abi.Uint64,
    player_dexterity: pt.abi.Uint64,
) -> pt.Expr:
    """Challenge the enemy."""
    return pt.Seq(
        pt.Assert(
            pt.And(
                app.state.game_active.get() == 0,
                app.state.enemy_defeated.get() == 0,
                app.state.price.get() >= txn.amount(),
            )
        ),
        pt.Seq(
            app.state.game_active.set(1),
            app.state.current_challenger.set(txn.sender()),
            app.state.current_enemy_hp.set(app.state.hp.get()),
            app.state.current_player_hp.set(player_hp.get()),
            app.state.current_player_intelligence.set(player_intelligence.get()),
            app.state.current_player_strength.set(player_strength.get()),
            app.state.current_player_dexterity.set(player_dexterity.get()),
        ),
    )


@pt.Subroutine
def player_win(address: pt.abi.Address) -> pt.Expr:
    """Player wins."""
    raise NotImplementedError


@app.external(authorize=bk.Authorize.only(app.state.current_challenger.get()))
def submit_plays(
    actions: pt.abi.Tuple3[
        pt.abi.Tuple2[pt.abi.String, pt.abi.String],
        pt.abi.Tuple2[pt.abi.String, pt.abi.String],
        pt.abi.Tuple2[pt.abi.String, pt.abi.String],
    ],
    *,
    output: GameState,
) -> pt.Expr:
    """Submit a hand of three cards.

    Args:
        action1: action of first card
        action2: action of second card
        action3: action of third card
        attribute1: attribute of first card
        attribute2: attribute of second card
        attribute3: attribute of third card

    Returns:
        A GameState object.
    """
    enemy_mag_dmg = pt.ScratchVar(pt.TealType.uint64)
    enemy_phys_dmg = pt.ScratchVar(pt.TealType.uint64)
    player_mag_dmg = pt.ScratchVar(pt.TealType.uint64)
    player_phys_dmg = pt.ScratchVar(pt.TealType.uint64)
    enemy_mag_def = pt.ScratchVar(pt.TealType.uint64)
    enemy_phys_def = pt.ScratchVar(pt.TealType.uint64)
    player_mag_def = pt.ScratchVar(pt.TealType.uint64)
    player_phys_def = pt.ScratchVar(pt.TealType.uint64)
    i = pt.ScratchVar(pt.TealType.uint64)
    return pt.Seq(
        pt.Assert(app.state.game_active.get() == 1),
        pt.For(
            i.store(0),
            i.load() < 3,
            i.store(i.load() + 1),
        ).Do(
            (action := actions[i.load()][0]),
            (attribute := actions[i.load()][1]),
            pt.If(
                action == "attack",
            ).Then(
                pt.If(
                    attribute == "intelligence",
                ).Then(
                    player_mag_dmg.store(
                        player_mag_dmg.load() + app.state.current_player_intelligence.get()
                    ),
                ).Else(
                    player_phys_dmg.store(
                        player_phys_dmg.load() + app.state.current_player_strength.get()
                    ),
                )
            ).ElseIf(
                action == "defend",
            ).Then(
                pt.If(
                    attribute == "intelligence",
                ).Then(
                    player_mag_def.store(
                        player_mag_def.load() + app.state.current_player_intelligence.get()
                    ),
                ).Else(
                    player_phys_def.store(
                        player_phys_def.load() + app.state.current_player_strength.get()
                    ),
                )
            ).Else(
                player_mag_def.store(
                    player_mag_def.load() + pt.Div(app.state.current_player_dexterity.get(), pt.Int(2))
                ),
                player_phys_def.store(
                    player_phys_def.load() + pt.Div(app.state.current_player_dexterity.get(), pt.Int(2))
                ),
            )
        ),
        enemy_mag_def.store(
            pt.Div(app.state.current_enemy_dexterity.get(), pt.Int(2))
        ),
        enemy_phys_def.store(
            pt.Div(app.state.current_enemy_dexterity.get(), pt.Int(2))
        ),
        enemy_mag_dmg.store(
            app.state.current_enemy_intelligence.get()
        ),
        enemy_phys_dmg.store(
            app.state.current_enemy_strength.get()
        ),
        pt.If(
            player_mag_dmg.load() > enemy_mag_def.load(),
        ).Then(
            app.state.current_enemy_hp.set(
                app.state.current_enemy_hp.get() - (player_mag_dmg.load() - enemy_mag_def.load())
            )
        )
        pt.If(
            player_phys_dmg.load() > enemy_phys_def.load(),
        ).Then(
            app.state.current_enemy_hp.set(
                app.state.current_enemy_hp.get() - (player_phys_dmg.load() - enemy_phys_def.load())
            )
        ),
        pt.If(
            enemy_mag_dmg.load() > player_mag_def.load(),
        ).Then(
            app.state.current_player_hp.set(
                app.state.current_player_hp.get() - (enemy_mag_dmg.load() - player_mag_def.load())
            )
        ),
        pt.If(
            enemy_phys_dmg.load() > player_phys_def.load(),
        ).Then(
            app.state.current_player_hp.set(
                app.state.current_player_hp.get() - (enemy_phys_dmg.load() - player_phys_def.load())
            )
        ),
        pt.If(
            app.state.current_enemy_hp.get() <= pt.Int(0),
        ).Then(
            app.state.game_active.set(0),
            app.state.enemy_defeated.set(1),
            player_win(app.state.current_challenger.get()),
        )
    )
