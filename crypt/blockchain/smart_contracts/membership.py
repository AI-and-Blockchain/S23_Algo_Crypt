"""Smart Contract to track membership and meta-state of the game.

Named Tuples and Mappings

    Card
        name: str
        desc: str

    Address -> MembershipRecord
        intelligence: int
        strength: int
        dexterity: int
        library: card_asset_id: int -> Card
    card_descriptions: card_name: str -> card_description: str

"""
import beaker as bk
import pyteal as pt

from beaker.lib.storage import BoxList, BoxMapping


class Card(pt.abi.NamedTuple):
    name: pt.abi.Field[pt.abi.String]
    desc: pt.abi.Field[pt.abi.String]
    url: pt.abi.Field[pt.abi.String]


class MembershipRecord(pt.abi.NamedTuple):
    intelligence: pt.abi.Field[pt.abi.Uint8]
    strength: pt.abi.Field[pt.abi.Uint8]
    dexterity: pt.abi.Field[pt.abi.Uint8]
    library = BoxList(pt.abi.Uint64, 1000)  # card_asset_id
    # TODO: add deck mapping


class MembershipState:
    governor = bk.GlobalStateValue(
        stack_type=pt.TealType.bytes,
        default=pt.Global.creator_address(),
        descr="Address of the governor of the game.",
    )

    n_cards = bk.GlobalStateValue(
        stack_type=pt.TealType.uint64,
        default=pt.Int(0),
        descr="Number of card types in the game.",
    )

    def __init__(self, *, membership_record: type[pt.abi.BaseType], card_type: type[pt.abi.BaseType]):
        self.card_bank = BoxMapping(pt.abi.Uint64, pt.abi.Uint64)  # card_asset_id -> card_count
        self.membership = BoxMapping(pt.abi.Address, membership_record)  # address -> membership_record
        self.all_cards = BoxMapping(pt.abi.Uint64, card_type)  # card_asset_id -> card
        self.card_ids = BoxList(pt.abi.Uint64, 1000, "card_ids")  # card_asset_id


app = bk.Application(
    name="Algo Crypt Meta State",
    state=MembershipState(
        membership_record=MembershipRecord,
        card_type=Card,
    ),
)


@app.external(authorize=bk.Authorize.only_creator())
def bootstrap(
    seed: pt.abi.PaymentTransaction,
    card_list: pt.abi.DynamicArray[pt.abi.Tuple3[pt.abi.String, pt.abi.String, pt.abi.String]],
) -> pt.Expr:
    """Bootstrap the game with a list of cards.

    Args:
        seed (pt.abi.PaymentTransaction): seeded transaction
        card_list (pt.abi.Array[
            pt.abi.Tuple3[pt.abi.String, pt.abi.String, pt.abi.String]
            ]): List of cards (name, description, url)

    Returns:
        pt.Expr: pyteal expression
    """
    n_cards = pt.ScratchVar(pt.TealType.uint64)
    i = pt.ScratchVar(pt.TealType.uint64)
    created_asset_id = pt.ScratchVar(pt.TealType.uint64)
    return pt.Seq(
        pt.Assert(
            seed.get().receiver() == pt.Global.current_application_address(),
            comment="Seed transaction must be sent to the application address.",
        ),
        n_cards.store(card_list.length()),
        pt.For(
            i.store(pt.Int(0)),
            i.load() < n_cards.load(),
            i.store(i.load() + pt.Int(1)),
        ).Do(
            pt.Seq(
                (card_details := pt.abi.make(pt.abi.Tuple3[pt.abi.String, pt.abi.String, pt.abi.String])).set(
                    pt.abi.String(), pt.abi.String(), pt.abi.String()
                ),
                card_list[i.load()].store_into(card_details),
                (card_name := pt.abi.make(pt.abi.String)).set(pt.abi.String()),
                (card_desc := pt.abi.make(pt.abi.String)).set(pt.abi.String()),
                (card_url := pt.abi.make(pt.abi.String)).set(pt.abi.String()),
                card_details[0].store_into(card_name),
                card_details[1].store_into(card_desc),
                card_details[2].store_into(card_url),
                pt.InnerTxnBuilder.Execute(
                    {
                        pt.TxnField.type_enum: pt.TxnType.AssetConfig,
                        pt.TxnField.config_asset_name: card_name.get(),
                        pt.TxnField.config_asset_unit_name: pt.Bytes("CRPT-Card-{i}"),
                        pt.TxnField.config_asset_total: pt.Int(10000),
                        pt.TxnField.config_asset_decimals: pt.Int(0),
                        pt.TxnField.config_asset_default_frozen: pt.Int(0),
                        pt.TxnField.config_asset_manager: pt.Global.current_application_address(),
                        pt.TxnField.config_asset_reserve: pt.Global.current_application_address(),
                        pt.TxnField.config_asset_freeze: pt.Global.current_application_address(),
                        pt.TxnField.config_asset_clawback: pt.Global.current_application_address(),
                        pt.TxnField.fee: pt.Int(0),
                    }
                ),
                (card_obj := Card()).set(card_name, card_desc, card_url),
                created_asset_id.store(pt.InnerTxn.created_asset_id()),
                (asset_uint := pt.abi.make(pt.abi.Uint64)).set(created_asset_id.load()),
                app.state.all_cards[pt.Itob(pt.InnerTxn.created_asset_id())].set(card_obj),
                app.state.card_ids[app.state.n_cards].set(asset_uint),
                app.state.card_bank[pt.Itob(pt.InnerTxn.created_asset_id())].set(pt.Itob(pt.Int(10000))),
                app.state.n_cards.set(app.state.n_cards + pt.Int(1)),
            ),
        ),
    )


@app.external(authorize=bk.Authorize.only_creator())
def add_card(card_name: pt.abi.String, card_desc: pt.abi.String, card_url: pt.abi.String) -> pt.Expr:
    """Add a new card to the game.

    Args:
        card_name (pt.abi.String): Name of the card
        card_desc (pt.abi.String): Description of the card
        card_url (pt.abi.String): URL of the card

    Returns:
        pt.Expr: pyteal expression
    """
    return pt.Seq(
        pt.Assert(
            app.state.n_cards < pt.Int(1000),
            comment="Cannot add more than 1000 cards.",
        ),
        pt.InnerTxnBuilder.Execute(
            {
                pt.TxnField.type_enum: pt.TxnType.AssetConfig,
                pt.TxnField.config_asset_name: card_name.get(),
                pt.TxnField.config_asset_unit_name: pt.Bytes("CRPT-Card-{app.state.n_cards}"),
                pt.TxnField.config_asset_total: pt.Int(10000),
                pt.TxnField.config_asset_decimals: pt.Int(0),
                pt.TxnField.config_asset_default_frozen: pt.Int(0),
                pt.TxnField.config_asset_manager: pt.Global.current_application_address(),
                pt.TxnField.config_asset_reserve: pt.Global.current_application_address(),
                pt.TxnField.config_asset_freeze: pt.Global.current_application_address(),
                pt.TxnField.config_asset_clawback: pt.Global.current_application_address(),
                pt.TxnField.fee: pt.Int(0),
            }
        ),
        (card_obj := Card()).set(card_name, card_desc, card_url),
        (asset_uint := pt.abi.make(pt.abi.Uint64)).set(pt.InnerTxn.created_asset_id()),
        app.state.all_cards[pt.Itob(pt.InnerTxn.created_asset_id())].set(card_obj),
        app.state.card_ids[app.state.n_cards].set(asset_uint),
        app.state.card_bank[pt.Itob(pt.InnerTxn.created_asset_id())].set(pt.Itob(pt.Int(10000))),
        app.state.n_cards.set(app.state.n_cards + pt.Int(1)),
    )
